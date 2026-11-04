"""Connector extents along the port edge (and the SD reader on the audio-end edge) from 06-board-underside.
Samples the foreground (not table) just outside the PCB edge in board mm via the homography."""
import sys, json, cv2, numpy as np
sys.argv = ["x"]; sys.path.insert(0, "tools"); import to_mm
Hm, _, _ = to_mm.fit_homography(145.0); Hi = np.linalg.inv(Hm)
img = cv2.imread("photos/06-board-underside-full.jpg"); hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV); S, V = hsv[..., 1], hsv[..., 2]
fg = ((S > 60) | (V < 150)).astype(np.uint8)          # anything that is not the white table
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
def px(X, Y):
    p = Hi @ np.array([X, Y, 1.0]); return int(p[0] / p[2]), int(p[1] / p[2])
def runs(samples, step):
    out = []; start = None
    for i, v in enumerate(list(samples) + [0]):
        if v and start is None: start = i
        if not v and start is not None: out.append((round(start * step, 1), round(i * step, 1))); start = None
    return out
step = 0.5
# port edge: connector bodies cover the PCB green in the strip Y = 1 .. 4 mm inside the edge
green = cv2.inRange(hsv, (30, 40, 20), (100, 255, 255)) | cv2.inRange(hsv, (5, 80, 40), (28, 255, 255))
notgreen = (green == 0).astype(np.uint8)
Xs = np.arange(0, 203.5, step)
prof = [np.mean([notgreen[px(X, Y)[1], px(X, Y)[0]] for Y in np.arange(1.0, 4.1, 0.5)]) > 0.6 for X in Xs]
ports = [r for r in runs(prof, step) if r[1] - r[0] > 3]
print("port edge, X extents (mm):", ports)
# protrusion past the edge per port: how far the foreground extends in -Y at the port's center
prot = {}
for a, b in ports:
    Xc = (a + b) / 2; d = 0.0
    while d < 15 and fg[px(Xc, -d - 0.5)[1], px(Xc, -d - 0.5)[0]]: d += 0.5
    prot[f"{a}-{b}"] = d
print("protrusion past PCB edge (mm):", prot)
# audio-end edge (X = 203.5): strip X = 199.5 .. 202.5 inside the edge, along Y
Ys = np.arange(0, 145, step)
prof2 = [np.mean([notgreen[px(X, Y)[1], px(X, Y)[0]] for X in np.arange(199.5, 202.6, 0.5)]) > 0.6 for Y in Ys]
side = [r for r in runs(prof2, step) if r[1] - r[0] > 3]
print("audio-end edge, Y extents (mm):", side)
json.dump({"port_edge_X": ports, "protrusion": prot, "audio_end_Y": side}, open("measurements/ports_mm.json", "w"), indent=1)
