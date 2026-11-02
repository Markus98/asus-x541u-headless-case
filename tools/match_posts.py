"""Fit the measured hole pattern (mm) to detected chassis posts (px) with a similarity transform
(scale, rotation, translation, optional mirror) by exhaustive 2-point hypotheses + inlier count.
Usage: match_posts.py <posts.npy> [tol_px]"""
import sys, json, itertools, numpy as np
posts = np.load(sys.argv[1])[:, :2]; tol = float(sys.argv[2]) if len(sys.argv) > 2 else 25
holes = json.load(open("measurements/board_mm.json"))["holes"]; names = list(holes); H = np.array([holes[k] for k in names], float)
best = None
for mirror in (False, True):
    Hm = H.copy()
    if mirror: Hm[:, 0] *= -1
    for (i, j) in itertools.combinations(range(len(Hm)), 2):
        d = Hm[j] - Hm[i]; dn = np.linalg.norm(d)
        for (a, b) in itertools.permutations(range(len(posts)), 2):
            e = posts[b] - posts[a]; en = np.linalg.norm(e)
            s = en / dn
            if not (8 < s < 13): continue
            ang = np.arctan2(e[1], e[0]) - np.arctan2(d[1], d[0])
            R = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]]) * s
            t = posts[a] - R @ Hm[i]
            P = (R @ Hm.T).T + t
            dist = np.linalg.norm(P[:, None, :] - posts[None, :, :], axis=2)
            inl = (dist.min(axis=1) < tol).sum()
            if best is None or inl > best[0]: best = (inl, mirror, R, t)
inl, mirror, R, t = best
print(f"best: {inl}/{len(H)} inliers, mirror={mirror}, scale={np.sqrt(abs(np.linalg.det(R))):.3f} px/mm, rot={np.degrees(np.arctan2(R[1,0],R[0,0])):.1f} deg")
Hm = H.copy()
if mirror: Hm[:, 0] *= -1
P = (R @ Hm.T).T + t
for k, p in zip(names, P):
    dist = np.linalg.norm(posts - p, axis=1); a = dist.argmin()
    print(f"  {k:4s} -> px ({p[0]:.0f},{p[1]:.0f})  nearest post P{a} at {dist[a]:.0f} px ({dist[a]/np.sqrt(abs(np.linalg.det(R))):.1f} mm)")
np.save("measurements/post_fit.npy", np.array([R[0,0], R[0,1], R[1,0], R[1,1], t[0], t[1], float(mirror)]))
