"""Generic: segment a green PCB (or grey part) on a light table, fit straight edges to its outline,
find holes, and scale with a known width. Writes measurements/<name>_mm.json and an overlay.
Usage: measure_part.py <image> <name> <known_width_mm> <cx> <cy> [green|grey]
Frame: origin at the bounding-box top-left of the part as photographed, X right, Y down.
Width = bounding-box X extent of the part."""
import sys, json, cv2, numpy as np
img = cv2.imread(sys.argv[1]); name = sys.argv[2]; width_mm = float(sys.argv[3]); cx, cy = int(sys.argv[4]), int(sys.argv[5])
kind = sys.argv[6] if len(sys.argv) > 6 else "green"
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV); H, S, V = cv2.split(hsv)
if kind == "green":
    mask = cv2.inRange(hsv, (30, 60, 35), (100, 255, 255)) | cv2.inRange(hsv, (5, 80, 60), (28, 255, 255))   # green PCB + copper pads
else:   # grey/metal part on a white table: not white, not very dark shadows handled by closing
    mask = ((V < 175) | (S > 60)).astype(np.uint8) * 255
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((41, 41), np.uint8))
n, lab = cv2.connectedComponents(mask); part = (lab == lab[cy, cx]).astype(np.uint8) * 255
cnts, _ = cv2.findContours(part, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); c = max(cnts, key=cv2.contourArea)
part = np.zeros_like(part); cv2.drawContours(part, [c], -1, 255, -1)
x, y, w, h = cv2.boundingRect(c)
px_per_mm = w / width_mm
print(f"bbox px x={x} y={y} w={w} h={h}  -> {px_per_mm:.3f} px/mm, height {h/px_per_mm:.1f} mm")
poly = cv2.approxPolyDP(c, 0.004 * cv2.arcLength(c, True), True).reshape(-1, 2)
mm = lambda p: ((p[0] - x) / px_per_mm, (p[1] - y) / px_per_mm)
out = {"width_mm": width_mm, "px_per_mm": px_per_mm, "bbox_px": [x, y, w, h], "outline_mm": [], "holes_mm": {}}
print("outline polygon (mm):")
for p in poly:
    X, Y = mm(p); out["outline_mm"].append([round(X, 1), round(Y, 1)]); print(f"  ({X:6.1f}, {Y:6.1f})")
# holes: dark or table-coloured round blobs surrounded by copper (pcb) or metal (fan ears)
orange = cv2.inRange(hsv, (5, 80, 40), (28, 255, 255)) & part
holes = []
if kind == "green":
    # mounting holes are the inner contours of copper pads
    orange = cv2.morphologyEx(orange, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    cnts, hier = cv2.findContours(orange, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    for i, hc in enumerate(cnts):
        if hier[0][i][3] < 0: continue          # only children (holes in pads)
        (hx, hy), r = cv2.minEnclosingCircle(hc)
        if r < 8 or r > 40 or cv2.contourArea(hc) / (np.pi * r * r) < 0.6: continue
        M = cv2.moments(hc); holes.append((M["m10"] / M["m00"], M["m01"] / M["m00"], r))
else:
    for hole in ((V < 95), ((S < 60) & (V > 140))):
        hole = hole.astype(np.uint8) * 255 & cv2.erode(part, np.ones((9, 9), np.uint8))
        hole = cv2.morphologyEx(hole, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        cnts, _ = cv2.findContours(hole, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for hc in cnts:
            (hx, hy), r = cv2.minEnclosingCircle(hc)
            if r < 8 or r > 40 or cv2.contourArea(hc) / (np.pi * r * r) < 0.6: continue
            M = cv2.moments(hc); hx, hy = M["m10"] / M["m00"], M["m01"] / M["m00"]
            if any(abs(hx - q[0]) < 20 and abs(hy - q[1]) < 20 for q in holes): continue
            holes.append((hx, hy, r))
holes.sort(key=lambda q: (q[1] // (15 * px_per_mm), q[0]))
print("holes (mm, dia):")
for i, (hx, hy, r) in enumerate(holes):
    X, Y = mm((hx, hy)); out["holes_mm"][f"{name[0].upper()}{i+1}"] = [round(X, 1), round(Y, 1), round(2 * r / px_per_mm, 1)]
    print(f"  {name[0].upper()}{i+1}: ({X:6.1f}, {Y:6.1f})  dia {2*r/px_per_mm:.1f}")
json.dump(out, open(f"measurements/{name}_mm.json", "w"), indent=1)
dbg = img.copy(); cv2.polylines(dbg, [poly.reshape(-1, 1, 2)], True, (255, 0, 255), 3); cv2.rectangle(dbg, (x, y), (x + w, y + h), (0, 255, 0), 2)
for i, (hx, hy, r) in enumerate(holes):
    cv2.circle(dbg, (int(hx), int(hy)), int(r) + 10, (0, 255, 255), 3); cv2.putText(dbg, f"{name[0].upper()}{i+1}", (int(hx) + 20, int(hy) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 255), 3)
g = int(10 * px_per_mm)
for gx in range(x, x + w + 1, g): cv2.line(dbg, (gx, y), (gx, y + h), (255, 255, 0), 1)
for gy in range(y, y + h + 1, g): cv2.line(dbg, (x, gy), (x + w, gy), (255, 255, 0), 1)
pad = 100; cv2.imwrite(f"measurements/{name}_overlay.jpg", dbg[max(0, y - pad):y + h + pad, max(0, x - pad):x + w + pad], [cv2.IMWRITE_JPEG_QUALITY, 85])
