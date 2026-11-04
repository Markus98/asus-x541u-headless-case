"""Fit the six board edges to the contour pixels, build a homography from the bounding
rectangle (port edge = L mm, width = W mm) and map outline corners and holes to mm.

Frame: X along the port edge from the DC-jack end (0) to the audio-jack end (L),
Y perpendicular from the port edge inward. In 06-board-underside (back side) X runs right-to-left, Y upward.
Usage: python3 tools/to_mm.py [W_mm]
"""
import sys, json, cv2, numpy as np
L = 203.5

def fit_homography(W=145.0):
    """Return (Hm, px_per_mm, corners): homography 06-board-underside px -> board mm, and the port-edge scale."""
    green = cv2.imread("measurements/06-board-underside_green.png", 0)
    green = cv2.morphologyEx(green, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))

    def fit(p, q, band=40):
        """Fit the PCB edge between rough endpoints p, q: per sample along the edge, take the
        outermost green pixel across the band; fit a line favouring the outer envelope
        (connectors overhanging the edge hide green, which only pulls points inward)."""
        p, q = np.array(p, float), np.array(q, float); d = q - p; ln = np.linalg.norm(d); d /= ln
        n = np.array([-d[1], d[0]])   # left normal; board interior is to the left of p->q (contour is clockwise in image coords)
        pts = []
        for t in np.arange(0.03 * ln, 0.97 * ln, 2.0):
            c = p + t * d
            best = None
            for s_ in np.arange(-band, band, 1.0):
                x, y = (c + s_ * n).astype(int)
                if 0 <= y < green.shape[0] and 0 <= x < green.shape[1] and green[y, x]:
                    best = s_; break       # first green from the outside (most negative s = outermost)
            if best is not None: pts.append((t, best))
        pts = np.array(pts)
        sel = pts
        for _ in range(5):   # keep outer envelope: drop points well inside the current line
            A = np.c_[sel[:, 0], np.ones(len(sel))]; k, b = np.linalg.lstsq(A, sel[:, 1], rcond=None)[0]
            res = pts[:, 1] - (k * pts[:, 0] + b); sel = pts[(res < 6) & (res > -6)]
            if len(sel) < 20: sel = pts[res < np.percentile(res, 40)]
        A = np.c_[sel[:, 0], np.ones(len(sel))]; k, b = np.linalg.lstsq(A, sel[:, 1], rcond=None)[0]
        p0 = p + b * n; dvec = d + k * n; dvec /= np.linalg.norm(dvec)
        return (p0, dvec, len(sel))
    def meet(a, b):
        (p1, d1, _), (p2, d2, _) = a, b
        cr = lambda u, v: u[0] * v[1] - u[1] * v[0]
        return p1 + cr(p2 - p1, d2) / cr(d1, d2) * d1

    E = {
     "top":     fit((1303, 350), (3301, 369)),
     "right":   fit((3301, 369), (3270, 2438)),
     "bottom":  fit((3270, 2438), (390, 2443)),
     "leftlow": fit((390, 2443), (414, 1383)),
     "step":    fit((414, 1383), (1285, 1389)),
     "leftup":  fit((1285, 1389), (1303, 350)),
    }
    for k, v in E.items(): print(f"# edge {k:8s} angle {np.degrees(np.arctan2(v[1][1], v[1][0])):7.2f}  n={v[2]}")
    BR = meet(E["right"], E["bottom"]); BL = meet(E["bottom"], E["leftlow"]); TR = meet(E["top"], E["right"])
    TLv = meet(E["top"], E["leftlow"]); STEP = meet(E["step"], E["leftup"]); SL = meet(E["leftlow"], E["step"]); TLu = meet(E["leftup"], E["top"])
    px_per_mm = np.linalg.norm(BR - BL) / L
    Hm = cv2.getPerspectiveTransform(np.float32([BR, BL, TR, TLv]), np.float32([[0, 0], [L, 0], [0, W], [L, W]]))

    return Hm, px_per_mm, dict(BR=BR, BL=BL, TR=TR, TLu=TLu, STEP=STEP, SL=SL)

if __name__ == "__main__":
    W = float(sys.argv[1]) if len(sys.argv) > 1 else 145.0
    Hm, px_per_mm, C = fit_homography(W)
    BR, BL, TR, TLu, STEP, SL = C["BR"], C["BL"], C["TR"], C["TLu"], C["STEP"], C["SL"]
    mm = lambda p: cv2.perspectiveTransform(np.float32([[p]]), Hm)[0, 0]
    holes = {"H1": (3251, 2170), "H2": (2798, 2294), "H3": (2015, 2115), "H4": (1430, 2150), "H5": (528, 2140),
             "H6": (547, 1439), "H7": (2348, 1748), "H8": (2020, 578), "H9": (3012, 454), "H10": (1332, 396)}
    out = {"L": L, "W": round(float(W), 1), "outline": {}, "holes": {}}
    print("outline (mm): X along port edge from DC end, Y inward from port edge")
    for k, p in {"DC end / port edge": BR, "audio end / port edge": BL, "DC end / far edge": TR,
                 "audio end upper part / far edge": TLu, "inner L corner": STEP, "audio end / step edge": SL}.items():
        x, y = mm(p); out["outline"][k] = [round(float(x), 1), round(float(y), 1)]; print(f"  {k:34s} X={x:6.1f} Y={y:6.1f}")
    print("holes (mm):")
    for k, p in holes.items():
        x, y = mm(p); out["holes"][k] = [round(float(x), 1), round(float(y), 1)]; print(f"  {k:4s} X={x:6.1f} Y={y:6.1f}")
    json.dump(out, open("measurements/board_mm.json", "w"), indent=1)

    # overlay: outline and holes mapped back onto the photo
    inv = np.linalg.inv(Hm)
    img = cv2.imread("photos/06-board-underside-full.jpg")
    o = out["outline"]; ring = [o["DC end / port edge"], o["audio end / port edge"], o["audio end / step edge"], o["inner L corner"], o["audio end upper part / far edge"], o["DC end / far edge"]]
    px = cv2.perspectiveTransform(np.float32([ring]), inv)[0].astype(int)
    cv2.polylines(img, [px.reshape(-1, 1, 2)], True, (255, 0, 255), 3)
    for k, (x, y) in out["holes"].items():
        p = cv2.perspectiveTransform(np.float32([[[x, y]]]), inv)[0, 0].astype(int)
        cv2.circle(img, tuple(p), 45, (0, 255, 255), 3); cv2.putText(img, k, (p[0] + 50, p[1] + 15), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 255, 255), 3)
    # 10 mm grid
    for gx in range(0, int(L) + 1, 10):
        a = cv2.perspectiveTransform(np.float32([[[gx, 0], [gx, W]]]), inv)[0].astype(int); cv2.line(img, tuple(a[0]), tuple(a[1]), (255, 255, 0), 1)
    for gy in range(0, int(W) + 1, 10):
        a = cv2.perspectiveTransform(np.float32([[[0, gy], [L, gy]]]), inv)[0].astype(int); cv2.line(img, tuple(a[0]), tuple(a[1]), (255, 255, 0), 1)
    cv2.imwrite("measurements/06-board-underside_overlay.jpg", cv2.resize(img, None, fx=0.5, fy=0.5), [cv2.IMWRITE_JPEG_QUALITY, 85])
