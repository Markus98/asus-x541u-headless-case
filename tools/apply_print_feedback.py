"""Apply the hole corrections measured on the printed base v3 (DESIGN.md, 2026-11-02) to measurements/*.json.
H1 and H5 are the references. Other-hole names give directions only. Writes board_mm.json (holes),
fan_mm.json (mounts, envelope) and odd_mounts_mm.json (ODD board holes in the board frame)."""
import json, math

def unit(a, b):
    d = (b[0] - a[0], b[1] - a[1]); n = math.hypot(*d); return (d[0] / n, d[1] / n)
def step(p, toward, dist):
    u = unit(p, toward); return [p[0] + dist * u[0], p[1] + dist * u[1]]
def r(p): return [round(p[0], 1), round(p[1], 1)]

b = json.load(open("measurements/board_mm.json"))
H = b.get("holes_photo", b["holes"]); b["holes_photo"] = H       # keep the photo-derived values
N = dict(H)
N["H6"] = [H["H5"][0], H["H6"][1] - 1.5 + 0.5]                   # same line as H5, 1.5 closer to H5, then 0.5 back out (jig v4)
N["H4"] = step(H["H4"], H["H5"], 0.8)
N["H3"] = step(H["H3"], H["H5"], 0.8)
N["H8"] = step([H["H8"][0] + (N["H3"][0] - H["H3"][0]), H["H8"][1] + (N["H3"][1] - H["H3"][1])], H["H8"], 0.0)
N["H8"] = step(N["H8"], [N["H8"][0] + (N["H8"][0] - N["H3"][0]), N["H8"][1] + (N["H8"][1] - N["H3"][1])], 0.5)   # 0.5 further from H3
N["H10"] = step(H["H10"], N["H4"], 1.5)
N["H10"] = step(N["H10"], [2 * N["H10"][0] - H["H9"][0], 2 * N["H10"][1] - H["H9"][1]], 1.0)                 # 1 away from H9
N["H10"][0] -= 0.5                                                # jig v5: the H11/H10/O7 row 0.5 toward the DC end (H11 and O7 follow H10's X)
N["H9"] = step(H["H9"], [2 * H["H9"][0] - H["H2"][0], 2 * H["H9"][1] - H["H2"][1]], 1.5)                     # 1.5 away from H2
N["H9"][1] = N["H10"][1]                                                                                      # same line as H10
N["H11"] = [N["H10"][0], N["H10"][1] - 45.0]                      # missing hole, 45 from H10 toward the port edge, same X as H10
N["H12"] = [1.0, 71.0]                                            # edge half hole next to the battery connector (img1109, tools scan)
b["holes"] = {k: r(v) for k, v in N.items()}
b["holes_note"] = "corrected from the v3 test print (tools/apply_print_feedback.py); holes_photo are the raw photo values"
json.dump(b, open("measurements/board_mm.json", "w"), indent=1)

f = json.load(open("measurements/fan_mm.json"))
M = f.get("mounts_photo", f["mounts"]); f["mounts_photo"] = M
M3 = step(b["holes"]["H8"], M["M3"], 33.0)                                                   # 33 from H8, same direction
M2 = [M["M2"][0], M["M2"][1] + 2.0]                                                              # 2 further from the board
# jig v4: the fan was slightly rotated. Rotate M2 and M3 about H9 (the fan's third ear) so that M3 has the same X as H8.
H9, H8 = b["holes"]["H9"], b["holes"]["H8"]
rad = math.hypot(M3[0] - H9[0], M3[1] - H9[1]); dx = H8[0] - H9[0]
ang = math.atan2(math.sqrt(rad * rad - dx * dx), dx) - math.atan2(M3[1] - H9[1], M3[0] - H9[0])
def rot(p):
    x, y = p[0] - H9[0], p[1] - H9[1]
    return [H9[0] + x * math.cos(ang) - y * math.sin(ang), H9[1] + x * math.sin(ang) + y * math.cos(ang)]
M3, M2 = rot(M3), rot(M2)
f["mounts"] = {"M1": M["M1"], "M2": r(M2), "M3": r(M3)}
f["fan_rotation_deg"] = round(math.degrees(ang), 2)
f["wifi_nub"] = r([M3[0] + 24.1, M3[1]])      # WiFi card locating post: in line with M3, 24.1 toward the audio end (chassis photo img1108)
E = f.get("envelope_photo", f["envelope"]); f["envelope_photo"] = E
f["envelope"] = dict(E, Y_max=round(E["Y_max"] + 2.0, 1))
C = f.get("impeller_center_photo", f["impeller_center"]); f["impeller_center_photo"] = C
f["impeller_center"] = r(rot([C[0], C[1] + 1.0]))
# jig v6 ruler check of the fan hub centre: 47 from the inside of the DC-end wall (matches) and 44.5 from the inside of the far wall
# (photo had 41.7). The far wall inner face is envelope Y_max + 2.0 (fan_clear in cad/base.py).
f["impeller_center"] = r([f["impeller_center"][0], f["envelope"]["Y_max"] + 2.0 - 44.5])
f["boss_h"] = {"M2": 8.4, "M3": 4.5}
json.dump(f, open("measurements/fan_mm.json", "w"), indent=1)

# ODD board flipped over the main board, BOT side up as in img1111/img1114, O6 on H8. ODD X runs along -X, ODD Y along +Y.
o = json.load(open("measurements/odd_mm.json"))["holes_mm"]
H8 = b["holes"]["H8"]
def odd_to_board(p): return r([H8[0] + (o["O6"][0] - p[0]), H8[1] + (p[1] - o["O6"][1])])
odd = {k: odd_to_board(v) for k, v in o.items()}
odd["O7"][0] = b["holes"]["H10"][0]          # O7 (inner pointy-end hole) lands on H10's X line (user, jig v4)
json.dump({"note": "ODD board holes in the main board frame, O6 on H8", "holes": odd,
           "mounts": {"O1": odd["O1"], "O7": odd["O7"]}, "boss_h": 14.0}, open("measurements/odd_mounts_mm.json", "w"), indent=1)
# port edge: the wall post between VGA (port 3) and HDMI (port 4) touched the VGA shell: 0.75 toward HDMI (+X)
p = json.load(open("measurements/ports_mm.json"))
P = p.get("port_edge_X_photo", p["port_edge_X"]); p["port_edge_X_photo"] = P
Q = [list(e) for e in P]
Q[3] = [P[3][0] + 0.75, P[3][1] + 0.75]; Q[4] = [P[4][0] + 0.75, P[4][1]]
# jig v5 (viewed from outside, DC on the left): DC and USB-C 1 toward the DC corner, VGA 0.5 toward HDMI
port_dx = {"dc": -1.0, "usbc": -1.0, "vga": 0.5}
port_dz = {"dc": 1.5, "usbc": 2.5, "rj45": 1.0, "vga": 0.5, "hdmi": 0.5, "usb3": 0.5, "usb2": 0.5, "audio": 1.0}   # all lifted
for k, (dx, dz) in {"usbc": (0.5, -0.5), "vga": (0.0, 0.5)}.items():          # jig v6: USB-C 0.5 right and 0.5 down, VGA 0.5 up
    port_dx[k] = port_dx.get(k, 0.0) + dx; port_dz[k] += dz
port_shape = {"usbc": "rrect"}                                                 # jig v6: USB-C window a rounded rectangle, not a pill
for i, k in enumerate(["dc", "usbc", "rj45", "vga", "hdmi", "usb3", "usb2", "audio"]):
    Q[i] = [Q[i][0] + port_dx.get(k, 0.0), Q[i][1] + port_dx.get(k, 0.0)]
p["port_edge_X"] = Q
json.dump(p, open("measurements/ports_mm.json", "w"), indent=1)
pp = json.load(open("measurements/port_profiles_mm.json"))
R = pp.get("ports_photo", pp["ports"]); pp["ports_photo"] = R
pp["ports"] = {k: dict(v, x=[v["x"][0] + port_dx.get(k, 0.0), v["x"][1] + port_dx.get(k, 0.0)],
                       z_top=round(v["z_top"] + port_dz[k], 2), z_bottom=round(v["z_bottom"] + port_dz[k], 2), shape=port_shape.get(k, v["shape"])) for k, v in R.items()}
json.dump(pp, open("measurements/port_profiles_mm.json", "w"), indent=1)
# SSD measured on the jig v5 (ruler, holes on the SFF-8201 pattern, drive square to the case): the hole nearest the audio-end wall is 15.5 from
# that wall (model 18.6) and the hole nearest the audio port is 20.5 from the port-edge wall (model 23.0)
sd = json.load(open("measurements/ssd_mm.json"))
S = sd.get("photo", {k: sd[k] for k in ["x_from", "x_to", "y_connector_end", "y_far_end", "bottom_holes"]}); sd["photo"] = S
ssd_dx, ssd_dy = 3.1, -2.5
sd.update(x_from=round(S["x_from"] + ssd_dx, 1), x_to=round(S["x_to"] + ssd_dx, 1), y_connector_end=round(S["y_connector_end"] + ssd_dy, 1),
          y_far_end=round(S["y_far_end"] + ssd_dy, 1), bottom_holes=[r([h[0] + ssd_dx, h[1] + ssd_dy]) for h in S["bottom_holes"]])
json.dump(sd, open("measurements/ssd_mm.json", "w"), indent=1)
print("ssd", sd["x_from"], sd["x_to"], sd["y_far_end"], sd["y_connector_end"], sd["bottom_holes"])
print("ports", Q)
for k, v in pp["ports"].items(): print(k, v["x"], v["z_top"], v["z_bottom"])
for k, v in b["holes"].items(): print(k, H.get(k), "->", v)
print("fan", f["mounts"], f["envelope"]); print("odd", odd)
