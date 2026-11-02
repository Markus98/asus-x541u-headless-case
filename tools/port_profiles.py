"""Port heights and vertical positions from the side profile photo (img1106).
The PCB edge is fitted as a line; around a seed box per connector the four silhouette edges are refined to the
strongest intensity gradient; the known connector width gives the local scale (the photo has strong perspective).
Writes measurements/port_profiles_mm.json: per port X range (from ports_mm.json), z range relative to the PCB
underside (positive up), shape and nominal face size. Overlay: measurements/port_profiles_overlay.jpg"""
import json, cv2, numpy as np
im = cv2.imread('photos/img1106-full.jpg'); H, W = im.shape[:2]; x0, y0 = int(W * 0.03), int(H * 0.36)
crop = im[y0:y0 + 484, x0:x0 + 3347]; gray = cv2.GaussianBlur(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), (3, 3), 0).astype(float)
hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
g = cv2.morphologyEx(cv2.inRange(hsv, (35, 40, 60), (90, 255, 255)), cv2.MORPH_OPEN, np.ones((3, 9), np.uint8))
ys, xs = np.nonzero(g); k, b = np.polyfit(xs, ys, 1)
pcb = lambda x: k * x + b                       # centre of the 1 mm PCB edge in the crop
ports = json.load(open('measurements/ports_mm.json'))['port_edge_X']
# seed boxes (crop px, from the gridded crops), nominal face width (mm), shape, nominal face height (mm, for the cutter)
seeds = {
 'dc':    dict(box=(112, 268, 128, 240), w=8.0, i=0, shape='circle', d=9.0, note='barrel jack, upper side; round plug hole centred on the face'),
 'usbc':  dict(box=(300, 452, 133, 202), w=8.9, i=1, shape='stadium', note='upper side'),
 'rj45':  dict(box=(1508, 1742, 172, 392), w=16.0, i=2, shape='rect', note='mid-mount, mostly below'),
 'vga':   dict(box=(1878, 2165, 245, 355), w=16.9, i=3, shape='dsub',  note='D-sub shell'),
 'hdmi':  dict(box=(2255, 2470, 232, 302), w=15.0, i=4, shape='hdmi',  note='mid-mount', r=12),
 'usb3':  dict(box=(2548, 2702, 238, 306), w=13.1, i=5, shape='rect',  note='mid-mount'),
 'usb2':  dict(box=(2810, 2965, 238, 335), w=13.1, i=6, shape='rect',  note='mid-mount', r=12),
 'audio': dict(box=(3098, 3165, 248, 332), w=None, i=7, shape='circle', note='scale from usb2'),
}
gx = np.abs(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)); gy = np.abs(cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3))
def refine(seed, r=22):
    xa, xb, ya, yb = seed
    col = gx[ya:yb, :].mean(axis=0); row = gy[:, xa:xb].mean(axis=1)
    f = lambda prof, c: int(np.argmax(prof[c - r:c + r]) + c - r)
    return f(col, xa), f(col, xb), f(row, ya), f(row, yb)
out = {}; ov = crop.copy(); scale_usb2 = None
for name, s in seeds.items():
    xa, xb, ya, yb = refine(s['box'], s.get('r', 22)); xc = (xa + xb) / 2
    if s['w']: ppm = (xb - xa) / s['w']
    else: ppm = scale_usb2
    if name == 'usb2': scale_usb2 = ppm
    top = (pcb(xc) - ya) / ppm - 0.5          # mm above the PCB underside (line centre is PCB mid-thickness)
    bot = (pcb(xc) - yb) / ppm - 0.5
    out[name] = dict(x=ports[s['i']], z_top=round(top, 1), z_bottom=round(bot, 1), width_px=xb - xa, px_per_mm=round(ppm, 2),
                     face_w=s['w'] or round((xb - xa) / ppm, 1), face_h=round(top - bot, 1), shape=s['shape'], note=s['note'], **({'d': s['d']} if 'd' in s else {}))
    print(f"{name:6s} X {ports[s['i']]}  px x {xa}-{xb} y {ya}-{yb}  {ppm:5.1f} px/mm  z top {top:+5.1f} bottom {bot:+5.1f}  (rel. PCB underside)")
    cv2.rectangle(ov, (xa, ya), (xb, yb), (0, 0, 255), 2); cv2.putText(ov, name, (xa, ya - 5), 0, 0.7, (0, 0, 255), 2)
cv2.line(ov, (0, int(b)), (3346, int(k * 3346 + b)), (0, 255, 255), 1)
cv2.imwrite('measurements/port_profiles_overlay.jpg', ov)
json.dump({'note': 'z relative to the PCB underside, positive up (PCB top = +1.0). From img1106 via tools/port_profiles.py', 'ports': out},
          open('measurements/port_profiles_mm.json', 'w'), indent=1)
