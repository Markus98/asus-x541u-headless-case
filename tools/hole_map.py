"""Combined reference image with the current hole names: main board underside (H), chassis (H + fan M),
ODD board (O) and the CAD plan with everything. Output: measurements/hole_map.jpg"""
import sys, json, cv2, numpy as np
sys.argv = ["x"]; sys.path.insert(0, "tools"); import to_mm
b = json.load(open("measurements/board_mm.json")); H = b["holes"]
f = json.load(open("measurements/fan_mm.json")); M = f["mounts"]
o = json.load(open("measurements/odd_mm.json")); od = json.load(open("measurements/odd_mounts_mm.json"))
FONT = cv2.FONT_HERSHEY_SIMPLEX

def label(img, x, y, text, color, scale=1.0, r=14):
    cv2.circle(img, (int(x), int(y)), r, color, 3)
    (w, h), _ = cv2.getTextSize(text, FONT, scale, 3)
    tx, ty = int(x) + r + 4, int(y) + h // 2
    cv2.rectangle(img, (tx - 3, ty - h - 4), (tx + w + 3, ty + 4), (255, 255, 255), -1)
    cv2.putText(img, text, (tx, ty), FONT, scale, color, 3)

def title(img, text):
    cv2.rectangle(img, (0, 0), (img.shape[1], 70), (255, 255, 255), -1)
    cv2.putText(img, text, (15, 50), FONT, 1.4, (0, 0, 0), 3)

RED, BLUE, GREEN, GREY = (0, 0, 255), (255, 80, 0), (0, 160, 0), (120, 120, 120)

# A: main board underside, H labels via the homography
Hm, _, _ = to_mm.fit_homography(145.0); Hi = np.linalg.inv(Hm)
A = cv2.imread("photos/img1109-full.jpg")
for k, (X, Y) in H.items():
    p = Hi @ np.array([X, Y, 1.0]); label(A, p[0] / p[2], p[1] / p[2], k, GREY if k in ("H2", "H7") else RED, 1.6, 20)
title(A, "Main board, underside (img1109). H2, H7 unused")

# B: chassis without the board, H and M labels via the affine fit
Af = np.load("measurements/img1108_affine.npy")
B = cv2.imread("photos/img1108-full.jpg")
for k, (X, Y) in H.items():
    p = Af @ np.array([X, Y, 1.0]); label(B, p[0], p[1], k, GREY if k in ("H2", "H7") else RED, 1.6, 20)
for k, (X, Y) in M.items():
    p = Af @ np.array([X, Y, 1.0]); label(B, p[0], p[1], k, BLUE, 1.6, 20)
title(B, "Chassis without the board (img1108): H = board holes, M = fan mounts")

# C: ODD board, O labels
C = cv2.imread("photos/img1111-full.jpg"); bx, by, _, _ = o["bbox_px"]; s = o["px_per_mm"]
for k, (X, Y, _) in o["holes_mm"].items():
    label(C, bx + X * s, by + Y * s, k, GREEN if k in ("O1", "O6", "O7") else GREY, 1.6, 20)
title(C, "ODD board, BOT side (img1111): O1, O7 on bosses, O6 on H8")

# D: CAD plan in the board frame (X right, Y up), everything
sc = 6; W_, H_ = int(230 * sc), int(260 * sc)
D = np.full((H_, W_, 3), 255, np.uint8)
def P(X, Y): return int((X + 12) * sc), int(H_ - (Y + 8) * sc)
cv2.rectangle(D, P(-7 - 2.4, -1 - 2.4), P(203.5 + 1 + 2.4, f["envelope"]["Y_max"] + 2 + 2.4), (0, 0, 0), 2)
poly = np.array([P(*p) for p in [(0, 0), (203.5, 0), (203.5, 70.9), (142.2, 70.9), (142.2, 145), (0, 145)]], np.int32)
cv2.polylines(D, [poly], True, (0, 120, 0), 2)
e = f["envelope"]; cv2.rectangle(D, P(e["X_min"], e["Y_min"]), P(e["X_max"], e["Y_max"]), BLUE, 2)
H8 = H["H8"]; O6 = o["holes_mm"]["O6"]
opoly = np.array([P(H8[0] + (O6[0] - X), H8[1] + (Y - O6[1])) for X, Y in o["outline_mm"]], np.int32)
cv2.polylines(D, [opoly], True, GREEN, 2)
for cx in (25.5, 88.0): cv2.line(D, P(cx, -1), P(cx, 138), (0, 0, 0), 2)
sd = json.load(open("measurements/ssd_mm.json")); cv2.rectangle(D, P(sd["x_from"], sd["y_far_end"]), P(sd["x_to"], sd["y_connector_end"]), (0, 140, 140), 2)
for X, Y in sd["bottom_holes"]: label(D, *P(X, Y), "SSD", (0, 140, 140), 0.7, 7)
for k, (X, Y) in H.items(): label(D, *P(X, Y), k, GREY if k in ("H2", "H7") else RED, 0.9, 9)
for k, (X, Y) in M.items(): label(D, *P(X, Y), k, BLUE, 0.9, 9)
for k, (X, Y) in od["holes"].items():
    if k != "O6": label(D, *P(X, Y), k, GREEN if k in ("O1", "O7") else GREY, 0.9, 9)
cv2.putText(D, "ports", P(95, -6)[0:1] + (P(95, -6)[1] + 8,), FONT, 0.8, (0, 0, 0), 2)
cv2.putText(D, "DC end", (P(-7, 60)[0] - 0, P(-7, 60)[1]), FONT, 0.7, (0, 0, 0), 2)
title(D, "CAD plan, board frame (X right, Y up). Green = boards, blue = fan, dark yellow = SSD")

# combine: scale each panel to the same width, 2 x 2
def fit(img, w=1400):
    h = int(img.shape[0] * w / img.shape[1]); return cv2.resize(img, (w, h))
A, B, C, D = fit(A), fit(B), fit(C), fit(D)
def pad(img, h): return cv2.copyMakeBorder(img, 0, h - img.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
h1 = max(A.shape[0], B.shape[0]); h2 = max(C.shape[0], D.shape[0])
top = np.hstack([pad(A, h1), pad(B, h1)]); bot = np.hstack([pad(C, h2), pad(D, h2)])
out = np.vstack([top, bot])
cv2.imwrite("measurements/hole_map.jpg", out, [cv2.IMWRITE_JPEG_QUALITY, 85])
print(out.shape)
