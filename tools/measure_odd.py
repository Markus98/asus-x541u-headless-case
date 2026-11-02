"""Measure the ODD daughterboard from img1108 using the 2.5" SSD (100 x 69.85 mm) as scale.
Frame: X along the SSD long side, Y along its short side, origin at the SSD corner nearest the board.
Prints ODD outline corners and hole centers in mm and writes measurements/odd_mm.json + overlay."""
import json, cv2, numpy as np
img = cv2.imread("photos/img1108-full.jpg"); hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV); H, S, V = cv2.split(hsv)
s = 4032 / 2000
def roi_mask(m, x0, y0, x1, y1):
    r = np.zeros_like(m); r[int(y0*s):int(y1*s), int(x0*s):int(x1*s)] = 255; return m & r
# SSD: bright, unsaturated rectangle
ssd = roi_mask(((S < 60) & (V > 120)).astype(np.uint8) * 255, 1260, 900, 1790, 1310)
ssd = cv2.morphologyEx(ssd, cv2.MORPH_OPEN, np.ones((15, 15), np.uint8)); ssd = cv2.morphologyEx(ssd, cv2.MORPH_CLOSE, np.ones((61, 61), np.uint8))
cnts, _ = cv2.findContours(ssd, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); c = max(cnts, key=cv2.contourArea)
rect = cv2.minAreaRect(c); box = cv2.boxPoints(rect)
print("SSD rect px size", rect[1], "angle", rect[2])
# order corners: sort by x then assign
box = box[np.argsort(box[:, 0])]; left = box[:2][np.argsort(box[:2, 1])]; right = box[2:][np.argsort(box[2:, 1])]
TL, BL, TR, BR = left[0], left[1], right[0], right[1]
long_px = (np.linalg.norm(TR - TL) + np.linalg.norm(BR - BL)) / 2; short_px = (np.linalg.norm(BL - TL) + np.linalg.norm(BR - TR)) / 2
print(f"SSD px long {long_px:.0f} short {short_px:.0f} ratio {long_px/short_px:.3f} (expect {100/69.85:.3f})")
# SSD long side is horizontal in the photo; origin at TL (nearest the ODD board), X right, Y down
Hm = cv2.getPerspectiveTransform(np.float32([TL, TR, BR, BL]), np.float32([[0, 0], [100, 0], [100, 69.85], [0, 69.85]]))
mm = lambda p: cv2.perspectiveTransform(np.float32([[p]]), Hm)[0, 0]
# ODD board: green in ROI
green = roi_mask(cv2.inRange(hsv, (35, 70, 30), (95, 255, 255)), 760, 740, 1300, 1300)
green &= 255 - roi_mask(np.full_like(green, 255), 1240, 650, 1500, 870)   # drop the WiFi card
green = cv2.morphologyEx(green, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
green = cv2.morphologyEx(green, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
n, lab = cv2.connectedComponents(green); cx, cy = int(1000 * s), int(950 * s)
board = (lab == lab[cy, cx]).astype(np.uint8) * 255
cnts, _ = cv2.findContours(board, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); bc = max(cnts, key=cv2.contourArea)
poly = cv2.approxPolyDP(bc, 0.01 * cv2.arcLength(bc, True), True).reshape(-1, 2)
print("ODD polygon (px -> mm):")
out = {"outline": [], "holes": {}}
for p in poly:
    x, y = mm(p); out["outline"].append([round(float(x), 1), round(float(y), 1)]); print(f"  px {p[0]:5d} {p[1]:5d}  -> X={x:6.1f} Y={y:6.1f}")
# holes: dark/bright round blob surrounded by copper, inside board
orange = cv2.inRange(hsv, (5, 90, 40), (18, 255, 255)) & board
holes = []
for hole in ((V < 95), ((S < 60) & (V > 150))):
    hole = hole.astype(np.uint8) * 255 & board
    hole = cv2.morphologyEx(hole, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cnts, _ = cv2.findContours(hole, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        (x, y), r = cv2.minEnclosingCircle(c)
        if r < 15 or r > 45 or cv2.contourArea(c) / (np.pi * r * r) < 0.6: continue
        m = np.zeros(img.shape[:2], np.uint8); cv2.circle(m, (int(x), int(y)), int(r * 2.4), 255, -1); cv2.circle(m, (int(x), int(y)), int(r * 1.15), 0, -1)
        if cv2.countNonZero(orange & m) / cv2.countNonZero(m) < 0.3: continue
        M = cv2.moments(c); x, y = M["m10"] / M["m00"], M["m01"] / M["m00"]
        if any(abs(x - q[0]) < 30 and abs(y - q[1]) < 30 for q in holes): continue
        holes.append((x, y, r))
holes.sort(key=lambda h: (h[1] // 150, h[0]))
print("ODD holes:")
for i, (x, y, r) in enumerate(holes):
    X, Y = mm((x, y)); out["holes"][f"D{i+1}"] = [round(float(X), 1), round(float(Y), 1)]; print(f"  D{i+1} px {x:.0f} {y:.0f} r={r:.0f} -> X={X:6.1f} Y={Y:6.1f}")
json.dump(out, open("measurements/odd_mm.json", "w"), indent=1)
dbg = img.copy(); cv2.polylines(dbg, [poly.reshape(-1, 1, 2)], True, (255, 0, 255), 4); cv2.polylines(dbg, [box.astype(int).reshape(-1, 1, 2)], True, (0, 255, 0), 4)
for i, p in enumerate(poly): cv2.putText(dbg, f"c{i}", (int(p[0]) + 10, int(p[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 0, 255), 3)
for i, (x, y, r) in enumerate(holes): cv2.circle(dbg, (int(x), int(y)), 40, (0, 255, 255), 3); cv2.putText(dbg, f"D{i+1}", (int(x) + 45, int(y) + 15), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 255), 3)
cv2.imwrite("measurements/img1108_overlay.jpg", dbg[int(650*s):int(1350*s), int(700*s):int(1850*s)], [cv2.IMWRITE_JPEG_QUALITY, 85])
