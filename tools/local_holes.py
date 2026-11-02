"""Locally refine hole centers: in a window around a rough guess, the hole is the
non-copper, non-green blob nearest the guess. Prints refined centers (px).
Usage: python3 local_holes.py <image> name=x,y name=x,y ..."""
import sys, cv2, numpy as np
img = cv2.imread(sys.argv[1]); hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
W = 70
for arg in sys.argv[2:]:
    name, xy = arg.split("="); gx, gy = map(int, xy.split(","))
    crop = hsv[gy - W:gy + W, gx - W:gx + W]
    H, S, V = cv2.split(crop)
    copper = cv2.inRange(crop, (5, 90, 40), (18, 255, 255))
    green = cv2.inRange(crop, (30, 40, 20), (100, 255, 255))
    hole = 255 - (copper | green)
    hole = cv2.morphologyEx(hole, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, stats, cents = cv2.connectedComponentsWithStats(hole)
    best = None
    for i in range(1, n):
        a = stats[i, cv2.CC_STAT_AREA]
        if a < 400 or a > 6000: continue
        w, h = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
        if max(w, h) / min(w, h) > 1.5: continue
        d = np.hypot(cents[i][0] - W, cents[i][1] - W)
        if best is None or d < best[0]: best = (d, i, a, w, h)
    if best is None: print(name, "not found"); continue
    d, i, a, w, h = best
    cx, cy = cents[i][0] + gx - W, cents[i][1] + gy - W
    print(f"{name} {cx:.0f} {cy:.0f} r~{np.sqrt(a/np.pi):.0f} wh={w}x{h} dist={d:.0f}")
