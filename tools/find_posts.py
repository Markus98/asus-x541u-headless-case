"""Detect screw posts (dark round holes, often with a metal ring) in the chassis photo.
Usage: find_posts.py <image> <debug_out> [rmin rmax]"""
import sys, cv2, numpy as np
img = cv2.imread(sys.argv[1]); hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV); H, S, V = cv2.split(hsv)
rmin, rmax = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (10, 30)
dark = (V < 70).astype(np.uint8) * 255
dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
cnts, _ = cv2.findContours(dark, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
posts = []
for c in cnts:
    (x, y), r = cv2.minEnclosingCircle(c)
    if r < rmin or r > rmax: continue
    a = cv2.contourArea(c)
    if a / (np.pi * r * r) < 0.6: continue
    # surrounded by a lighter ring (metal insert or boss top): mean V in annulus r*1.3..r*2.2 should exceed centre
    m = np.zeros(img.shape[:2], np.uint8); cv2.circle(m, (int(x), int(y)), int(r * 2.2), 255, -1); cv2.circle(m, (int(x), int(y)), int(r * 1.3), 0, -1)
    ring_v = cv2.mean(V, m)[0]
    if ring_v < 90: continue
    M = cv2.moments(c); posts.append((M["m10"] / M["m00"], M["m01"] / M["m00"], r, ring_v))
posts.sort(key=lambda p: (p[1] // 250, p[0]))
for i, (x, y, r, rv) in enumerate(posts): print(f"P{i:<3d} {x:6.0f} {y:6.0f} r={r:.0f} ring_v={rv:.0f}")
dbg = img.copy()
for i, (x, y, r, rv) in enumerate(posts):
    cv2.circle(dbg, (int(x), int(y)), int(r) + 10, (0, 255, 255), 3); cv2.putText(dbg, f"P{i}", (int(x) + 15, int(y) - 12), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 255), 3)
cv2.imwrite(sys.argv[2], cv2.resize(dbg, None, fx=0.5, fy=0.5), [cv2.IMWRITE_JPEG_QUALITY, 85])
np.save(sys.argv[2].replace(".jpg", ".npy"), np.array(posts))
