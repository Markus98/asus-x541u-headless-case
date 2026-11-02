"""Find the px/mm scale from a caliper lying in the photo with its outer jaws open to `gap` mm.
Looks for the two jaw tips in a horizontal band (y0..y1, full-res px): the left jaw's right face and
the right jaw's left face are the two strongest dark->light / light->dark vertical edges of grey metal.
Usage: caliper_scale.py <image> <gap_mm> <y0> <y1> [x0 x1]"""
import sys, cv2, numpy as np
img = cv2.imread(sys.argv[1]); gap = float(sys.argv[2]); y0, y1 = int(sys.argv[3]), int(sys.argv[4])
x0, x1 = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (0, img.shape[1])
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV); S, V = hsv[..., 1], hsv[..., 2]
band = img[y0:y1, x0:x1]
metal = ((S[y0:y1, x0:x1] < 70) & (V[y0:y1, x0:x1] < 175) & (V[y0:y1, x0:x1] > 40)).astype(np.uint8) * 255
metal = cv2.morphologyEx(metal, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
col = metal.mean(axis=0) > 127           # columns that are mostly metal in the band
# runs of metal columns
runs = []; start = None
for i, c in enumerate(list(col) + [False]):
    if c and start is None: start = i
    if not c and start is not None: runs.append((start, i - 1)); start = None
runs = [r for r in runs if r[1] - r[0] > 40]
print("metal column runs (full-res x):", [(a + x0, b + x0) for a, b in runs])
if len(runs) < 2: sys.exit("need two jaw runs")
left_face = runs[0][1] + x0; right_face = runs[-1][0] + x0
px_per_mm = (right_face - left_face) / gap
print(f"jaw faces x={left_face} x={right_face}  gap {right_face-left_face} px  -> {px_per_mm:.3f} px/mm")
dbg = img.copy(); cv2.line(dbg, (left_face, y0 - 200), (left_face, y1 + 200), (0, 0, 255), 3); cv2.line(dbg, (right_face, y0 - 200), (right_face, y1 + 200), (0, 0, 255), 3)
cv2.rectangle(dbg, (x0, y0), (x1, y1), (0, 255, 0), 2)
cv2.imwrite(sys.argv[1].replace("photos/", "measurements/").replace("-full.jpg", "_caliper.jpg"), cv2.resize(dbg[max(0,y0-600):y1+600], None, fx=0.5, fy=0.5))
