"""px/mm from the engraved mm ticks on a caliper beam in a photo.
Usage: tick_scale.py <image> <x0> <x1> <ymin> <ymax>  (full-res; x-range along the beam, y-range to search)
Scans 22 px tall row bands; for each, finds the tick period by autocorrelation at 1 mm and 10 mm lags.
Reports the band where both agree best."""
import sys, cv2, numpy as np
img = cv2.imread(sys.argv[1], 0); x0, x1, ymin, ymax = map(int, sys.argv[2:6])
def period(strip):
    prof = -(strip.mean(axis=0)); prof -= prof.mean()
    ac = np.correlate(prof, prof, "full")[len(prof) - 1:]
    def refine(k): a, b, c = ac[k - 1], ac[k], ac[k + 1]; return k + 0.5 * (a - c) / (a - 2 * b + c)
    k = 8 + int(np.argmax(ac[8:30])); k1 = refine(k)
    if not np.isfinite(k1) or k1 < 8 or k1 > 30: return 0.0, 0.0, 0.0
    k10 = int(round(k1 * 10))
    if k10 + 8 >= len(ac) or k10 < 7: return k1, 0.0, 0.0
    k10 = k10 - 6 + int(np.argmax(ac[k10 - 6:k10 + 7])); k10 = refine(k10)
    return k1, k10 / 10, ac[int(round(k1))] / ac[0]
best = None
for y in range(ymin, ymax - 22, 4):
    k1, k10, strength = period(img[y:y + 22, x0:x1].astype(np.float64))
    if abs(k1 - k10) < 0.15 and (best is None or strength > best[0]): best = (strength, y, k1, k10)
if best is None: sys.exit("no consistent tick band found")
s, y, k1, k10 = best
print(f"tick band y={y}..{y+22}: 1 mm lag {k1:.3f} px, 10 mm lag {k10:.3f} px/mm, strength {s:.2f}")
