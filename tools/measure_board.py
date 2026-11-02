"""Measure PCB outline and screw pad positions from a top-down photo of a bare PCB on a light table.

Usage: uv run --with opencv-python-headless --with numpy python3 tools/measure_board.py <image> <out_prefix> <cx> <cy>
cx,cy: a pixel inside the board. Prints polygon corners and pad centroids (px). Writes debug overlays.
"""
import sys, cv2, numpy as np

img = cv2.imread(sys.argv[1]); out = sys.argv[2]; cx, cy = int(sys.argv[3]), int(sys.argv[4])
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
H, S, V = cv2.split(hsv)

# green PCB, closed across silkscreen and small components
green = cv2.inRange(hsv, (30, 40, 20), (100, 255, 255))
green = cv2.morphologyEx(green, cv2.MORPH_CLOSE, np.ones((81, 81), np.uint8))
n, lab = cv2.connectedComponents(green)
core = (lab == lab[cy, cx]).astype(np.uint8) * 255
cnts, _ = cv2.findContours(core, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
core = np.zeros_like(core); cv2.drawContours(core, [max(cnts, key=cv2.contourArea)], -1, 255, -1)
# add dark components attached to the board edge (ports, connectors), but not the orange ribbon
bg = ((S < 70) & (V > 140)).astype(np.uint8) * 255
fg = 255 - bg
ribbon = cv2.inRange(hsv, (5, 100, 50), (25, 255, 255))
ribbon = cv2.morphologyEx(ribbon, cv2.MORPH_OPEN, np.ones((41, 41), np.uint8))  # big orange blobs only
near = cv2.dilate(core, np.ones((121, 121), np.uint8))
mask = core | (fg & near & (255 - ribbon))
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((41, 41), np.uint8))
n, lab = cv2.connectedComponents(mask)
mask = (lab == lab[cy, cx]).astype(np.uint8) * 255
cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
board = max(cnts, key=cv2.contourArea)
board_mask = np.zeros_like(mask); cv2.drawContours(board_mask, [board], -1, 255, -1)
cv2.imwrite(out + "_mask.png", cv2.resize(board_mask, None, fx=0.25, fy=0.25))
cv2.imwrite(out + "_green.png", cv2.inRange(hsv, (30, 40, 20), (100, 255, 255)) & board_mask)
poly = cv2.approxPolyDP(board, 0.006 * cv2.arcLength(board, True), True).reshape(-1, 2)
print("board area px", cv2.contourArea(board))
print("polygon corners (px):")
for i, p in enumerate(poly): print(f"  c{i} {p[0]} {p[1]}")

# screw holes: round blob (black, or the table showing through) surrounded by copper
orange = cv2.inRange(hsv, (5, 90, 40), (18, 255, 255)) & board_mask
pads = []
for name, hole in (("dark", (V < 95)), ("bright", (S < 60) & (V > 150))):
    hole = hole.astype(np.uint8) * 255 & board_mask
    hole = cv2.morphologyEx(hole, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cnts, _ = cv2.findContours(hole, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        (x, y), r = cv2.minEnclosingCircle(c)
        if r < 18 or r > 45: continue
        a = cv2.contourArea(c)
        if a / (np.pi * r * r) < 0.65: continue
        m = np.zeros(img.shape[:2], np.uint8)
        cv2.circle(m, (int(x), int(y)), int(r * 2.2), 255, -1); cv2.circle(m, (int(x), int(y)), int(r * 1.15), 0, -1)
        cov = cv2.countNonZero(orange & m) / cv2.countNonZero(m)
        if cov < 0.35: continue
        M = cv2.moments(c); x, y = M["m10"] / M["m00"], M["m01"] / M["m00"]
        if any(abs(x - q[0]) < 30 and abs(y - q[1]) < 30 for q in pads): continue
        pads.append((x, y, r, cov))
pads.sort(key=lambda p: (p[1] // 200, p[0]))
print("pads (x y r circ):")
for i, p in enumerate(pads): print("  p%d %.0f %.0f %.0f %.2f" % ((i,) + p))

dbg = img.copy()
cv2.polylines(dbg, [poly.reshape(-1, 1, 2)], True, (255, 0, 255), 4)
for i, p in enumerate(poly):
    cv2.putText(dbg, f"c{i}", (int(p[0]) + 10, int(p[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), 3)
for i, (x, y, r, c) in enumerate(pads):
    cv2.circle(dbg, (int(x), int(y)), int(r), (0, 255, 255), 3)
    cv2.putText(dbg, f"p{i}", (int(x) + 15, int(y) + 15), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
cv2.imwrite(out + "_debug.jpg", dbg, [cv2.IMWRITE_JPEG_QUALITY, 85])
cv2.imwrite(out + "_debug_small.jpg", cv2.resize(dbg, None, fx=0.5, fy=0.5), [cv2.IMWRITE_JPEG_QUALITY, 85])
np.save(out + "_poly.npy", poly); np.save(out + "_pads.npy", np.array(pads))

# refine corners: fit a line to contour points near each polygon edge, intersect neighbours
pts = board.reshape(-1, 2).astype(np.float64)
def fit_edge(p, q):
    d = q - p; n = np.array([-d[1], d[0]]) / np.linalg.norm(d)
    t = (pts - p) @ d / (d @ d)
    dist = np.abs((pts - p) @ n)
    sel = pts[(dist < 20) & (t > 0.08) & (t < 0.92)]
    vx, vy, x0, y0 = cv2.fitLine(sel.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    return np.array([x0, y0]), np.array([vx, vy]), len(sel)
def meet(l1, l2):
    (p1, d1), (p2, d2) = l1, l2
    cr = lambda a, b: a[0] * b[1] - a[1] * b[0]
    t = cr(p2 - p1, d2) / cr(d1, d2); return p1 + t * d1
polyf = poly.astype(np.float64)
lines = [fit_edge(polyf[i], polyf[(i + 1) % len(polyf)]) for i in range(len(polyf))]
print("refined corners (intersection of fitted edge lines), edge angle deg, n points:")
for i in range(len(polyf)):
    c = meet(lines[i - 1][:2], lines[i][:2]); ang = np.degrees(np.arctan2(lines[i][1][1], lines[i][1][0]))
    print(f"  c{i} {c[0]:.0f} {c[1]:.0f}   edge c{i}->c{(i+1)%len(polyf)} angle {ang:.2f} n={lines[i][2]}")
np.save(out + "_contour.npy", pts)
