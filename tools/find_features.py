"""Find screw heads (silver, round) and copper pads with holes in a photo; print and label them.
Usage: find_features.py <image> <out_debug_jpg> [rmin rmax]"""
import sys, cv2, numpy as np
img = cv2.imread(sys.argv[1]); hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV); H, S, V = cv2.split(hsv)
rmin, rmax = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (16, 40)
feats = []
# screw heads: unsaturated, bright-ish, round
silver = ((S < 60) & (V > 150)).astype(np.uint8) * 255
silver = cv2.morphologyEx(silver, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
cnts, _ = cv2.findContours(silver, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
for c in cnts:
    (x, y), r = cv2.minEnclosingCircle(c)
    if r < rmin or r > rmax: continue
    if cv2.contourArea(c) / (np.pi * r * r) < 0.72: continue
    feats.append(("screw", x, y, r))
# copper pads with a dark or bright hole
orange = cv2.inRange(hsv, (5, 80, 40), (28, 255, 255))
for hole in ((V < 95), ((S < 60) & (V > 150))):
    hole = hole.astype(np.uint8) * 255; hole = cv2.morphologyEx(hole, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cnts, _ = cv2.findContours(hole, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        (x, y), r = cv2.minEnclosingCircle(c)
        if r < rmin * 0.6 or r > rmax or cv2.contourArea(c) / (np.pi * r * r) < 0.65: continue
        m = np.zeros(img.shape[:2], np.uint8); cv2.circle(m, (int(x), int(y)), int(r * 2.4), 255, -1); cv2.circle(m, (int(x), int(y)), int(r * 1.15), 0, -1)
        if cv2.countNonZero(orange & m) / cv2.countNonZero(m) < 0.35: continue
        if any(abs(x - f[1]) < 30 and abs(y - f[2]) < 30 for f in feats): continue
        feats.append(("pad", x, y, r))
feats.sort(key=lambda f: (f[2] // 300, f[1]))
for i, (k, x, y, r) in enumerate(feats): print(f"f{i:<3d} {k:5s} {x:6.0f} {y:6.0f} r={r:.0f}")
dbg = img.copy()
for i, (k, x, y, r) in enumerate(feats):
    cv2.circle(dbg, (int(x), int(y)), int(r) + 8, (0, 255, 255) if k == "pad" else (255, 0, 255), 3)
    cv2.putText(dbg, f"f{i}", (int(x) + 20, int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 255) if k == "pad" else (255, 0, 255), 3)
cv2.imwrite(sys.argv[2], cv2.resize(dbg, None, fx=0.5, fy=0.5), [cv2.IMWRITE_JPEG_QUALITY, 85])
