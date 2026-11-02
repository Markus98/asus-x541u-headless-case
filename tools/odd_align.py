"""Re-derive the ODD board frame from its own edges instead of the photo's bounding box.
Finds the dominant edge direction of the board outline in img1111-full, rotates the outline and the holes
into that frame, and rescales so the extent along the SATA edge is 109 mm. Updates measurements/odd_mm.json."""
import json, cv2, numpy as np
o = json.load(open("measurements/odd_mm.json")); bx, by, bw, bh = o["bbox_px"]
if "holes_mm_bbox_frame" in o: o["holes_mm"] = o["holes_mm_bbox_frame"]; o["px_per_mm"] = o["px_per_mm_bbox_frame"]
s = o["px_per_mm"]; o["px_per_mm_bbox_frame"] = s
img = cv2.imread("photos/img1111-full.jpg"); hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, (30, 60, 35), (100, 255, 255)) | cv2.inRange(hsv, (5, 80, 60), (28, 255, 255))
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((41, 41), np.uint8))
seed = (int(bx + o["holes_mm"]["O6"][0] * s), int(by + o["holes_mm"]["O6"][1] * s))
n, lab = cv2.connectedComponents(mask); part = (lab == lab[seed[1], seed[0]]).astype(np.uint8) * 255
c = max(cv2.findContours(part, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0], key=cv2.contourArea).reshape(-1, 2).astype(float)
# dominant edge direction: length-weighted angle histogram (mod 90 deg) of the polygon segments
poly = cv2.approxPolyDP(c.astype(np.float32), 3.0, True).reshape(-1, 2)
seg = np.roll(poly, -1, 0) - poly; ln = np.hypot(seg[:, 0], seg[:, 1]); ang = np.degrees(np.arctan2(seg[:, 1], seg[:, 0])) % 90
keep = ln > 150
hist, edges = np.histogram(ang[keep], bins=np.arange(0, 90.5, 0.5), weights=ln[keep]); i = np.argmax(hist)
sel = keep & (np.abs(((ang - edges[i] + 45) % 90) - 45) < 1.5)
theta = np.average(ang[sel], weights=ln[sel]); theta = theta if theta < 45 else theta - 90    # rotation of the board edges in the photo, deg
print(f"board rotation in photo: {theta:.2f} deg  (from {sel.sum()} segments, {ln[sel].sum():.0f} px of edge)")
R = cv2.getRotationMatrix2D((float(bx), float(by)), theta, 1.0)       # rotate by +theta to align (cv2 rotates CCW for positive angle in image coords)
def rot(p): return (R @ np.c_[p, np.ones(len(p))].T).T
cr = rot(c); x0, y0 = cr[:, 0].min(), cr[:, 1].min(); w = cr[:, 0].max() - x0
s2 = w / o["width_mm"]
O7_REF = 96.0      # user: O7 centre is 96 mm from the SATA-edge PCB edge (ruler)
ROW_REF = 4.0      # user: O1..O4 are on one line 4 mm from that edge (ruler). Together they give the Y offset and scale; X uses the 109 mm width
print(f"aligned width {w:.0f} px -> {s2:.3f} px/mm (was {s:.3f}), height {(cr[:,1].max()-y0)/s2:.1f} mm")
holes_px = np.array([[bx + X * s, by + Y * s] for X, Y, _ in o["holes_mm"].values()]); hr = rot(holes_px)
raw = {k: [(x - x0) / s2, (y - y0) / s2] for k, (x, y) in zip(o["holes_mm"], hr)}
row = np.mean([raw[k][1] for k in ("O1", "O2", "O3", "O4")])
ky = (O7_REF - ROW_REF) / (raw["O7"][1] - row); y_edge = row - ROW_REF / ky
print(f"Y calibration: scale {ky:.4f}, PCB edge at {y_edge:.2f} in the photo frame (row of O1..O4 at {row:.2f})")
new = {}
for (k, (X, Y, d)), (x, y) in zip(o["holes_mm"].items(), hr):
    new[k] = [round((x - x0) / s2, 1), round(((y - y0) / s2 - y_edge) * ky, 1), d]; print(f"  {k}: ({X:6.1f},{Y:6.1f}) -> ({new[k][0]:6.1f},{new[k][1]:6.1f})")
pr = rot(cv2.approxPolyDP(c.astype(np.float32), 0.004 * cv2.arcLength(c.astype(np.float32), True), True).reshape(-1, 2))
o["holes_mm_bbox_frame"] = o["holes_mm"]; o["holes_mm"] = new
o["outline_mm"] = [[round((x - x0) / s2, 1), round(((y - y0) / s2 - y_edge) * ky, 1)] for x, y in pr]
o["px_per_mm"] = s2; o["rotation_deg"] = round(float(theta), 2); o["y_scale"] = round(float(ky), 4); o["y_edge_offset"] = round(float(y_edge), 2)
o["frame_note"] = "frame aligned to the board edges (tools/odd_align.py); X along the SATA edge, Y from the SATA-edge PCB edge toward the pointy end, calibrated on O7 = 96 and the O1..O4 row = 4 (user, ruler)"
json.dump(o, open("measurements/odd_mm.json", "w"), indent=1)
