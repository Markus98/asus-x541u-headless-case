"""SSD position relative to the ODD board, from the chassis photo (img1108) where the SSD is plugged in.
Rectifies the photo to board mm with the chassis affine, detects the SSD rectangle and the ODD board's
pad holes, fits the ODD frame (odd_mm.json, BOT view; the chassis shows TOP so the fit is mirrored) and
writes the SSD outline in the ODD frame and in the case frame to measurements/ssd_mm.json."""
import json, cv2, numpy as np
Af = np.load("measurements/img1108_affine.npy"); A3 = np.vstack([Af, [0, 0, 1]])
img = cv2.imread("photos/img1108-full.jpg")
s = 10; X0, X1, Y0, Y1 = 60, 215, 120, 350
T = np.array([[s, 0, -X0 * s], [0, -s, Y1 * s], [0, 0, 1.0]])
w = cv2.warpPerspective(img, T @ np.linalg.inv(A3), ((X1 - X0) * s, (Y1 - Y0) * s))
mm = lambda px, py: (X0 + px / s, Y1 - py / s)
hsv = cv2.cvtColor(w, cv2.COLOR_BGR2HSV)
# SSD: bright, unsaturated rectangle
ssd = cv2.inRange(hsv, (0, 0, 120), (180, 60, 255))
ssd = cv2.morphologyEx(ssd, cv2.MORPH_OPEN, np.ones((15, 15), np.uint8)); ssd = cv2.morphologyEx(ssd, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
cnts, _ = cv2.findContours(ssd, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
c = max(cnts, key=cv2.contourArea); rect = cv2.minAreaRect(c); box = cv2.boxPoints(rect)
print("SSD rect (mm):", [tuple(round(v, 1) for v in mm(*p)) for p in box], "size", tuple(round(v / s, 1) for v in rect[1]))
# ODD holes: dark/bright round blobs inside copper pads on the green board
green = cv2.inRange(hsv, (30, 50, 30), (100, 255, 255)); copper = cv2.inRange(hsv, (5, 80, 60), (28, 255, 255))
board = cv2.morphologyEx(green | copper, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
cnts, _ = cv2.findContours(copper, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
holes = []
for c in cnts:
    if cv2.contourArea(c) < 8 * s * s: continue           # pads are ~8x8 mm or bigger
    x, y, ww, hh = cv2.boundingRect(c); sub = w[y:y + hh, x:x + ww]; m = np.zeros(sub.shape[:2], np.uint8); cv2.drawContours(m, [c - [x, y]], -1, 255, -1)
    hsub = cv2.cvtColor(sub, cv2.COLOR_BGR2HSV)
    inner = ((hsub[..., 1] < 70) | (hsub[..., 2] < 90)).astype(np.uint8) * 255 & m     # not copper inside the pad
    inner = cv2.morphologyEx(inner, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    for ic in cv2.findContours(inner, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
        a = cv2.contourArea(ic)
        if 1.5 * s * s < a < 20 * s * s:
            (cx, cy), r = cv2.minEnclosingCircle(ic); holes.append((*mm(x + cx, y + cy), round(2 * r / s, 1)))
holes = sorted(holes); print("pad holes (X, Y, dia):", [tuple(round(v, 1) for v in h) for h in holes])
overlay = w.copy(); cv2.drawContours(overlay, [box.astype(int)], -1, (0, 0, 255), 3)
for X, Y, d in holes: cv2.circle(overlay, (int((X - X0) * s), int((Y1 - Y) * s)), 12, (255, 0, 255), 3)
cv2.imwrite("measurements/ssd_overlay.jpg", overlay)
json.dump({"ssd_rect_mm": [[round(float(v), 2) for v in mm(*p)] for p in box], "pad_holes": [[round(float(v), 2) for v in h] for h in holes]},
          open("/tmp/claude-1000/-home-markus-repos-asus-headless-case/8a8e3165-4361-422a-87a4-b16a82cc745e/scratchpad/ssd_raw.json", "w"), indent=1)

# --- SSD outline into the case frame ---
# The SSD top sits ~5 mm above the chassis posts the affine was fitted on, so its outline is enlarged radially from the camera
# nadir (image centre). The measured length (vs 100.0 standard) gives the factor; shrink the corners toward the nadir by it.
cx, cy = img.shape[1] / 2, img.shape[0] / 2
nad = np.linalg.solve(A3, [cx, cy, 1.0])[:2]
L_std, W_std = 100.0, 69.85
corners = np.array([mm(*p) for p in box]); length = max(rect[1]) / s
k = L_std / length
corr = nad + (corners - nad) * k
print(f"nadir (board mm) {nad.round(1)}, length factor {k:.3f}")
# ODD holes seen in the chassis (TOP up): O1 corner, O2 along the SATA edge, O5 along the side, O6 the far pad
hm = {k_: np.array(v[:2]) for k_, v in zip(["O6", "O2", "O1", "O5"], [h for h in holes if h[2] > 3.2 and h[1] < 240])}
odd = json.load(open("measurements/odd_mounts_mm.json"))["holes"]
# the flip over the main board mirrors Y and keeps X: fit Y' = a - Y, X' = X + b on the four holes
a = np.mean([odd[k_][1] + hm[k_][1] for k_ in hm]); bb = np.mean([odd[k_][0] - hm[k_][0] for k_ in hm])
res = {k_: (round(odd[k_][0] - (hm[k_][0] + bb), 1), round(odd[k_][1] - (a - hm[k_][1]), 1)) for k_ in hm}
print("flip fit: Y' = %.1f - Y, X' = X + %.1f, residuals (mm)" % (a, bb), res)
case = np.c_[corr[:, 0] + bb, a - corr[:, 1]]
xa, xb = case[:, 0].min(), case[:, 0].max(); yc = case[:, 1].max()           # connector end is the +Y end after the flip
xa = (xa + xb) / 2 - W_std / 2                                                 # standard width centred on the measured sides
out = {"note": "SSD in the case frame, bottom (hole side) up, connector end toward +Y, from img1108 via tools/measure_ssd.py",
       "x_from": round(float(xa), 1), "x_to": round(float(xa + W_std), 1), "y_connector_end": round(float(yc), 1), "y_far_end": round(float(yc - L_std), 1),
       "z_top": 23.0, "thickness": 7.0,
       "bottom_holes": [[round(float(xa + dx), 1), round(float(yc - dy), 1)] for dy in (14.0, 90.6) for dx in (4.07, W_std - 4.07)],
       "hole_std": "SFF-8201 bottom holes M3: 14.0 and 90.6 from the connector end, 4.07 from each side"}
print(out)
json.dump(out, open("measurements/ssd_mm.json", "w"), indent=1)
