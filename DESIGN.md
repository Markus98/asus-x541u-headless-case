# ASUS X541UVK headless case

Working spec for a 3D printed case around a scavenged laptop motherboard.
Updated as measurements and decisions come in.

## Hardware

- Main board: ASUS X541UVK MAIN BOARD rev 2.0, PN 60NB0CF0-MB1400
- Daughterboard: X541UVK_ODD rev 2.0, connected by ribbon cable (needed? see open questions)
- Cooling: original fan + heatpipe assembly, keep as is
- WiFi: M.2 2230 card on main board
- RAM: soldered chips on board (SO-DIMM slot on other side unknown)
- Storage: 2.5 inch SATA SSD on the ODD daughterboard's SATA connector
- SD card reader on the back side at the audio-jack end edge (slot opens at that edge)
- Fan is chassis-mounted beside the board, not on the board. WiFi card hangs about 25 mm past the board edge.
- Photos in `photos/` (HEIC originals plus JPEG conversions, `*-full.jpg` is full resolution)
  - `board-in-chassis.jpg`: fan side, original layout
  - `img1104.jpg`: fan side, ODD board flipped over the main board with SSD, the intended layout
  - `img1106.jpg`: port edge side profile
  - `img1107.jpg`: back side, SD reader corner
  - `img1108.jpg`: chassis with main board removed, ODD board and SSD in place
  - `img1109.jpg`: bare main board, back side, used for the computational measurements

## Decisions

- Mounting: reuse the laptop's M2.5 screws
- Screws thread directly into printed holes, no inserts
  - Pilot hole 1.9 mm, the M2.5 minor diameter (2.1 printed loose at 0.2 mm layers)
  - Boss outer diameter 6 mm minimum, thread depth at least screw length + 1 mm
- Stack, bottom up: printed base with 10 mm standoffs, the 10 mm air layer holds the fan, the CPU heatsink and the
  ports (all on the board's underside), then the main board, later the ODD board and SSD on top of the board, then a printed lid.
- Case frame = board frame: x = X (DC end at x=0), y = Y (port edge at y=0), z up. Plan view is `photos/board-in-chassis.jpg`
  rotated 90 degrees counter-clockwise. `photos/img1109.jpg` shows the underside.
- Case footprint is a rectangle: board plus the fan area, inner 217 x 238.7 mm, outer about 222 x 243.5 mm.
- Fan sits on the floor, flat face (big opening) up at PCB-underside level. Ear M1 is clamped under the board by the H9 screw
  (H9 boss 9 mm), M2 on an 8.4 mm boss, M3 (the ear next to the board) on a 4.5 mm boss. After the v4 jig M2 and M3 were rotated 1.2 degrees about H9
  so that M3 sits on H8's X line (M3 now 34.4 from H8). WiFi card: screwed at M3 on top of the fan ear, located by a nub post 24.1 toward the
  audio end of M3 (chassis photo), boss 2 mm above M3 (1 after jig v6), 2.0 mm pin, no screw.
- Wind channel: two 1.2 mm walls, 10 mm tall, along X=25.5 and X=88 (25.5 from the DC-end board edge, 62.5 apart, measured on the
  white lines under the board) from the port-edge wall to Y=138, 7 mm short of the far board edge (v3 print: the fan reaches under the board and needs 7 mm). Fan blows through it over the heatsink, out through slots in the port-edge wall.
- H2 and H7 get no bosses (no chassis post in the laptop). H11 (between H10 and H6) and H12 (edge half hole next to the battery connector) added after the v3 print.
- Battery connector overhangs the DC-end edge about 6 mm at Y 79 to 108: the whole DC-end wall sits 7 mm from the PCB edge (case stays a plain rectangle).
- ODD board flipped over the main board, BOT side up. In the laptop its hole O6 sits on H8; here the ODD board and the SSD plugged into it are
  moved 9.6 mm toward the port edge (`ssd_wall_gap` in `cad/base.py`: the SSD's far end 0.5 from the inner wall face), because with the cable
  clip the ribbon no longer reaches the laptop position. Its own 14 mm bosses at O1 (193.9, 105.5, the corner hole of the three) and
  O7 (140.5, 197.4, on H10's X line, the pointy-end hole). O6 (91.9, 121.9) is now over the main board with no hole under it: a loose
  2 mm spacer disc sits there under the ODD board with a nub up through the hole to the lid (see the ODD spacer below).
- Port openings follow each connector face (shape, height and vertical position from the profile photo `img1106`, `tools/port_profiles.py`),
  1 mm margin all round, never below the floor top. DC jack: 9 mm round hole centred on the jack face (plug boot; adjust `d` if the plug is fatter). RJ45 does not hang below the standoff plane (mid-mount), no floor pocket.
  After the v5 jig every window moved: all lifted (DC 1.5, USB-C 2.5, RJ45 and audio 1, the rest 0.5), DC and USB-C 1 toward the DC corner, VGA 0.5 toward HDMI
  (`tools/apply_print_feedback.py`, directions as seen from outside with the DC jack on the left). Jig v6: USB-C 0.5 right and 0.5 down as a
  rounded rectangle (1.5 mm corners), VGA 0.5 up. The port-edge wall sits 0.5 from the board edge (was 1).
  SD slot: window in the audio-end wall at Y 32.5 to 62.5, z 9.4 to 13.4 (v3 print: shifted 3.5 toward the port-edge corner; jig v5: 1 mm smaller all round).
  Because that wall is 6.5 from the board edge, the wall steps in there as a rectangular funnel (`sd_funnel` in `cad/base.py`): a flat plate
  0.5 mm from the board edge carries the slot (30 x 4, 1.5 corner radius) with 6 mm (Y) and 1.5 mm (Z) of flat area around it for fingers beside
  the card (plate opening 42 x 7), and from the plate's outer face the funnel flares at 45 degrees per side in Y and up and down in Z out to the
  outer wall face, 6 mm over the 6 mm run (54 x 18 there, Z 2.9 to 20.9). For printing (base stands on its floor) the ceiling is the steepest
  overhang at 45 degrees, there is no flat ceiling (the earlier flat one was a 6 mm bridge that sagged), and the funnel is a solid block from
  the floor to 0.2 under the lid lip so nothing floats. The downward flare stops 0.5 above the floor top (a short flat floor at the outer face
  is upward facing, so it prints fine). The 1.5 mm Z flat is all the 45 degree ceiling leaves: it reaches 20.9 at the outer face under the
  2.4 mm wall top. Same funnel in the jig with its thinner wall, on a floor bar.
- Vents, for bookshelf use (only the port edge and the lid open): exhaust slots in the port-edge wall between the channel walls, the full under-board
  layer (4 slots 14 mm wide, 1.5 mm ribs, z 3.4 to 11.4, about 450 mm2 of the 613 mm2 channel section); intake slots in the same wall above the
  ports (z 17.2 to 20.4), none above the exhaust to limit recirculation and none above the RJ45 window (its lifted top reaches 17.6). With the SSD
  standing 0.5 mm from that wall from X 128.2 on, only the three slots at X 112 to 128.5 remain (about 43 mm2, was 216 with the row to X 200.5);
  the audio-end wall carries no vents because the case will stand on it (user, 2026-11-03). The PCB separates the two layers. The blower draws
  through both faces: a 48-hole grille (4.5 mm holes, 6.5 pitch, about 760 mm2) in the floor under the fan and the same grille in the lid above
  it; with the case on its audio end both grilles are open and they are the real intake, right at the impeller. The small slots and the gaps
  round the port connectors (about 40 mm2 above the PCB, 280 mm2 below) only add a little crossflow over the board top.
- Base walls go the full height, 23.3 mm inside (SSD top 23 + 0.3, as thin as possible). The lid (`cad/out/lid.stl`, printed lip up) is a flat 2.4 mm
  plate with a 1.6 mm lip, 2.5 mm tall, that slots inside the walls with 0.2 mm clearance and goes round the posts (there is room above the DC jack
  and the battery connector, lip bottom is 7.4 above the PCB top). The lip is left out along the port-edge wall over the SSD's X range (127 to 199),
  where the SSD stands against that wall up to 0.3 under the plate. Four 10 mm screw posts in the corners, concentric with the
  5.1 mm corner fillet (0.1 inside the outer face), floor to wall top, in the four corners only (user: no posts bulging into the case elsewhere).
  They were 8 mm on a 4.1 fillet; the extra 1 mm keeps a wall round the lid's corner screw recesses in the first layers (see the chamfer below).
  A full 10 mm post reaches past the board edge at the two port-edge corners (base v8: the board sat on the posts), so every post is
  flattened at 0.5 from the board's X extent (`edge_clear`), like the port-edge gap. The post centres are 4.3 from the board edge at both
  ends (audio gap 7.0 like the DC end, was 6.5), which leaves 1.8 mm round the insert hole and 0.8 mm round the lead-in counterbore
  on the flat side. The lid is unchanged: its corner ring depends on the fillet centre, not the post diameter.
  Each has a 6 mm counterbore 2.5 deep (insert lead-in) above the 4.0 mm hole for an M3 x 5.7 heat-set insert. The lid has 5.6 mm bosses that plug
  into those counterbores, 3.4 mm holes with a 6.2 mm head recess 1.4 deep (1 mm floor over the boss), M3 x 10 button head screws sit
  about 0.3 above the plate. End gaps 7 mm at both ends (DC: battery connector; audio: post beside H5, 6.5 until base v8),
  port-edge gap 0.5, inner 217.5 x 238.7, outer about 222.3 x 243.5 mm, total height 25.7 mm.
  Port openings are closed windows shaped like the connectors, so the board goes in with a 3 mm slide toward the port edge.
  SSD screwed from outside: four 3.6 mm holes on the SFF-8201 bottom pattern, same 6.2 mm x 1.4 head recess (1 mm floor, SSD 0.3 below it).
  No bosses, the SSD screws straight to the plate. Lid grille over the fan. 1 mm chamfer on the case bottom edge and the lid top edge. The lid
  prints plate down, so the chamfer is at the bed and insets the first layer by 1 mm: with the 8 mm posts the 6.2 mm corner screw recess was
  1 mm from the outer face and the first layers had no wall round it (lid v3 corners failed). With the 10 mm posts the recess is 2 mm from the
  face, 1 mm at the first layer.
  Peek slit in the lid for the POWER and CHARGER LEDs (side-firing on the audio-end board edge beside H5, Y about 19 and 29 from the
  board-in-chassis photo): a 1 mm wide slit (as thin as prints, so nothing falls in) directly above the LED packages at X 202.5, Y 17 to 31, round ends, flared
  at 45 degrees on the inside (1.6 mm deep, 4.2 mm wide at the underside, 0.8 mm of straight 1 mm slot at the outer face) for a wider viewing angle. The CHARGER LED
  faces the SD funnel plate 0.5 mm away, so its side light is mostly blocked; the packages are still visible from above.
- SSD: bottom (hole side) up, plugged into the ODD board, position measured from the chassis photo (`tools/measure_ssd.py`, `measurements/ssd_mm.json`):
  then corrected on the v5 jig with a ruler (hole nearest the audio-end wall 15.5 from it, hole nearest the audio port 20.5 from the port-edge wall;
  the photo was 3.1 off in X and 2.5 in Y), then on lid v2 (16 from the audio-end wall, 19.5 from the port-edge wall, which is now 0.5 from the board):
  X 128.2 to 198.0, connector end at Y 109.6, far end Y 9.6, top at 23 mm in the laptop layout. Moved 9.6 toward the port edge with the ODD board
  (far end at Y 0.0, holes at Y 9.4 and 86.0): the ribbon with the cable clip does not reach otherwise. Lid holes 3.6 mm for the remaining slack.
- ODD spacer (`cad/out/odd_spacer.stl`): a loose 6 mm disc, 2 mm tall (the ODD board sits 2 mm above the main board top, measured on jig v6),
  placed on the main board top under ODD hole O6, with a 2.3 mm nub 7.8 mm long up through the 2.6 mm hole to 0.1 under the lid, so the spacer
  can move neither up nor down once the lid is on. Replaces the drilled H8 spacer: O6 is no longer over a board hole. Prints nub up.
- ODD cable clip (`cad/out/odd_clip_2.stl`, `cad/out/odd_clip_1.5.stl`): keeps the folded ODD ribbon cable from creasing. A 26.5 x 5.7 mm
  ring that slips onto the ODD board's pointy end: slot 22.5 wide and 1.2 tall (PCB plus ribbon, tight; 1.5 was loose), 2 mm side walls, a
  1.5 mm rectangular bar on one side of the slot and on the other a 3 mm bar between the side walls that is straight for 2 mm (or 1.5 mm,
  the second version) along the board and then ends in a full half round of 1.5 mm radius, round face outward, for the cable to fold round.
  Total depth 3.5 (3.0) mm, the side walls flush with the half round's apex. Prints flat on the inner face (the half round is a dome on top,
  no overhang). ODD PCB thickness assumed 1.0 like the main board.
- Stand (`cad/out/stand.stl`): the case stands vertically on either end wall with the ports to the back, in a slot along its length.
  A flat 243.5 x 56 x 2 mm plate (the case length, corners on the 5.1 fillet, 1 mm chamfer on the top edge) so books and the like can lie
  on it beside the case, with two 4 mm rails 14 mm tall forming a 26.3 mm slot (case 25.7 plus 0.3 a side). The rail ends and the LED
  step risers are chamfered 3 mm (the side profile; the 7.9 mm rail piece between the end gap and the step limits it), every other rail
  edge above the plate 1 mm (lead-in on the slot side, outer top edge, vertical corners); the concave step corners stay sharp.
  Flipping the case from one end to the other turns the lid to the other side of the slot, so both rails are notched the same: they stop
  10 mm short of both ends because the lid's corner screw heads (5.1 from the end faces) stick out of the lid, and drop to 8 mm over the
  LED slit (10.4 up from the audio-end face, Y 17 to 31 plus 2) so the LEDs show when the case stands on the audio end. The 14 mm rails
  stay under the SSD screw heads (15.8 above the audio-end face). The slot is open at both ends: nothing in front of the ports or the far
  wall. About 51 cm3 (a solid 18 mm bar was 144). Prints slot up.
- WiFi nub pin 2.0 mm for slack.
- WiFi antennas: the original lid flaps are the antennas (MAIN also carries Bluetooth); they go on the floor beside the SSD board. The cable
  slack coils round two C-shaped ends of a pill on the floor beside the WiFi card, in the free strip between the fan and the ODD board leg:
  centres (104, 190) and (104, 226), 16 mm outside diameter (coax bend radius), 1.6 mm walls, 12 mm tall with a 1.5 mm outward 45 degree lip
  at the top so the cable cannot slip off. One turn is about 120 mm, about 9 turns fit side by side. Parameters `coil_*` in `cad/base.py`.
- Material PETG, printer Bambu P1S. The 13 mm screws from the frame can be used for the lid.
- No power button, the board powers on when DC is applied. All ports reachable.
- Case modeled in build123d via build123d-mcp, source `cad/base.py`; numbers stamped in by `tools/gen_params.py` from `measurements/*.json`.
  The same source builds the fit jig (`cad/out/jig.stl`): 1.2 mm walls 19 mm high (all port openings complete), full-thickness wall strips at the corners
  so the full-height posts are embedded, the floor replaced by 1.6 mm bars through every boss, no grille. Lid jig (`cad/out/lid_jig.stl`):
  full lip and corner bosses, the plate reduced to a 6 mm edge band plus 8 mm bars through the SSD holes, no chamfer.
  IO jig (`cad/out/io_jig.stl`, exported outer face down): the port-edge wall alone as a 1.2 mm flat plate with its windows and vent slots (no standoffs).
- Measurements are computed from photos with the scripts in `tools/`, results in `measurements/`.

## Measurements

### Board coordinate frame

X runs along the port edge from the DC-jack end (X=0) to the audio-jack end (X=203.5).
Y runs from the port edge inward (Y=0 at the port edge). Z is up on the fan side.
Hole labels refer to `measurements/hole_map.jpg` (all current names on the photos and the CAD plan, made by `tools/hole_map.py`).

### Main board

Computed from `photos/img1109-full.jpg` with `tools/measure_board.py` and `tools/to_mm.py`.
Scale: 203.5 mm port edge (X) and 145 mm width (Y). Check: H4-H5 computed 63.3 vs measured 63.0, H5-H6 computed 49.2 vs measured 48.0.
Accuracy estimate about 0.5 mm, worse near the SD reader corner.

| Item | Value | Source |
|------|-------|--------|
| Port edge length | 203.5 mm | caliper |
| Width, perpendicular to port edge | 143.7 mm (from pixels, right side 143.7, left side 144.4) | photo, to be confirmed |
| Upper part (wide part) X extent | 0 to 142.1 mm | photo |
| Lower part (port strip) Y extent | 0 to 70.2 mm | photo |
| Inner L corner | X=142.2, Y=70.7 | photo |
| PCB thickness | 1 mm (user estimate) | |
| M2.5 screw thread length | 6 mm (plus some 13 mm from the frame) | user |
| Hole diameter | about 2.7 mm (from pixels) | photo |
| Tallest component, fan side | fan 10 mm | user |
| Tallest component, back side | ethernet port 13 mm | user |

Outline, as an L: (0,0) (203.5,0) (203.5,70.9) (142.2,70.9) (142.2,145) (0,145)

Mounting holes (mm):

Corrected after the v3 test print with H1 and H5 as references (`tools/apply_print_feedback.py`, raw photo values kept as `holes_photo` in the JSON):

| Hole | X | Y | note |
|------|---|---|------|
| H1 | 2.9 | 19.4 | reference |
| H2 | 34.9 | 10.3 | no boss |
| H3 | 90.9 | 22.3 | +0.8 toward H5 |
| H4 | 132.0 | 19.4 | +0.8 toward H5 |
| H5 | 194.5 | 19.4 | reference |
| H6 | 194.5 | 67.6 | on H5's line, 1.5 closer, then 0.5 back (jig v4) |
| H7 | 67.0 | 48.3 | no boss |
| H8 | 91.9 | 131.5 | as H3, 0.5 further from H3 |
| H9 | 20.4 | 141.8 | away from H2, on H10's line (net 0.9) |
| H10 | 140.5 | 141.8 | 1.5 toward H4, 1 away from H9, then 0.5 toward the DC end (jig v5) |
| H11 | 140.5 | 96.8 | new, 45 from H10, same X as H10 |
| H12 | 1.0 | 71.0 | new, edge half hole by the battery connector (from img1109) |

Not mounting holes: four heatsink spring screws around the CPU, edge notches (half holes) on the far edge at the DC end and on the step edge.

### Chassis cross-check of the main board holes

`photos/img1108.jpg` (chassis without the board) with `tools/find_posts.py`, `tools/match_posts.py`:
the hole pattern fits the chassis screw posts with a mirrored similarity transform (board seen from the
fan side). Affine residuals per hole: H3 1.5, H4 1.6, H5 0.2, H6 0.3, H8 1.0, H9 2.0, H10 0.8 mm.
Photo perspective limits this check to about 1 to 2 mm. H1 is hidden under the speaker bracket.
H2 and H7 have no chassis post at all, so the laptop did not use them for mounting. They are kept as bosses anyway.

### ODD daughterboard

From `photos/img1111-full.jpg` with `tools/measure_part.py`, scale from the user's 109 mm width
(14.61 px/mm; the caliper ticks in the same photo give 14.7, consistent).
Frame: aligned to the board's own edges (`tools/odd_align.py`, the board was rotated 2 degrees in the photo), origin at the
top-left of the aligned outline, BOT side up, X along the SATA edge, Y toward the pointy end. Y calibrated on two ruler references: O7 is 96.0 and the O1..O4 row is 4.0 from the SATA-edge PCB edge (photo was 2 percent short in Y,
edge detected 0.7 outside the real one). Height about 102.8 mm. Overlay: `measurements/odd_overlay.jpg`. Data: `measurements/odd_mm.json`.

| Item | Value |
|------|-------|
| Width along SATA edge | 109.0 mm (user) |
| Height perpendicular | about 102.8 mm (photo, Y calibrated on O7 and the O1..O4 row) |
| SATA connector | X 16.2 to 56.9 mm along the top edge, protrudes 6.6 mm past the edge, 4.3 mm tall on the TOP side (user) |
| Components on BOT side | about 1 mm (user) |

Outline (mm): top part is the full 109 mm width, about 25 mm deep at the left, stepping to 37 mm deep on the
right half; the leg is X 54 to 79, down to Y 102; see the JSON for the traced polygon.

Holes (mm, X, Y, diameter from photo):

| Hole | X | Y | dia |
|------|---|---|-----|
| O1 | 3.9 | 4.1 | 3.4 |
| O2 | 11.1 | 4.2 | 3.4 |
| O3 | 67.1 | 3.8 | 1.2 |
| O4 | 76.2 | 3.9 | 2.9 |
| O5 | 3.8 | 14.5 | 3.3 |
| O6 | 105.9 | 20.5 | 1.3 |
| O7 | 57.2 | 96.0 | 1.9 |
| O8 | 60.7 | 99.5 | 1.9 |

### Ports (from img1109, `tools/ports.py`, `measurements/ports_mm.json`)

Connector X extents along the port edge: 3 to 11 (DC jack, edge-mount, mostly above the PCB), 16.2 to 24 (USB-C, upper side), then:
91 to 109.5 (RJ45), 116.25 to 132.75 (VGA, protrudes 3 mm; v3 print: window and the post after it moved 0.75 toward HDMI), 137.75 to 153 (HDMI), 156.5 to 169.5 (USB 3),
(photo values; the jig v5 shifts below are applied on top by `tools/apply_print_feedback.py`)
174.5 to 188 (USB-A), 194.5 to 198.5 (audio jack). SD reader body at X 173 to 199.5, Y 37 to 65, slot opens at the audio-end edge.

### Port profiles (from `photos/img1106`, `tools/port_profiles.py`, `measurements/port_profiles_mm.json`)

Vertical extent of each connector face relative to the PCB underside (positive up, PCB top = +1.0). Each one scaled by its own
nominal width because the photo has strong perspective; about 0.5 mm good. Overlay: `measurements/port_profiles_overlay.jpg`.
Values as used in the CAD, i.e. after the jig v5 corrections (the raw photo values are kept as `ports_photo` in the JSON; the photo put every port 0.5 to 2.5 mm too low).

| Port | X | top | bottom | opening shape | jig v5 + v6 shift (X, Z) |
|------|---|-----|--------|---------------|--------------------------|
| dc | 2.0 to 10.0 | +4.4 | -0.5 | circle | -1, +1.5 |
| usbc | 15.7 to 23.5 | +4.7 | +0.7 | rrect | -0.5, +2 |
| rj45 | 91.0 to 109.5 | +4.2 | -9.8 | rect | 0, +1 |
| vga | 116.75 to 133.25 | +1.4 | -6.2 | dsub | +0.5, +1 |
| hdmi | 137.75 to 153.0 | +2.3 | -2.6 | hdmi | 0, +0.5 |
| usb3 | 156.5 to 169.5 | +3.1 | -3.6 | rect | 0, +0.5 |
| usb2 | 174.5 to 188.0 | +3.1 | -3.8 | rect | 0, +0.5 |
| audio | 194.5 to 198.5 | +2.9 | -2.5 | circle | 0, +1 |

### Fan

Mounting points from `photos/img1108.jpg` (chassis posts, mapped to the board frame with the affine fit of 7 board holes).
Cross-checked against the screw positions in `photos/board-in-chassis.jpg`: agree within 3 to 5 mm, the chassis photo is better conditioned.
`photos/img1112.jpg` turned out to have strong perspective (the fan is much closer to the camera than the caliper), so it is not used for sizes.
Data: `measurements/fan_mm.json`.

| Item | Board frame (X, Y) mm |
|------|------|
| Mount M1 (outlet-end corner) | 17.6, 163.2 |
| Mount M2 (far side) | 64.6, 234.2 (print feedback: 2 further from the board, then rotated about H9) |
| Mount M3 (next to the board) | 91.9, 165.9 (print feedback: 33 from H8, then rotated about H9 onto H8's X line) |
| WiFi nub post | 116.0, 165.9 (in line with M3, chassis photo) |
| Envelope | X 12.3 to 87.2, Y 146.5 to 236.2 (housing about 75 x 88 mm, 10 mm thick); far wall gap 2 mm (1 more than v3) |
| Impeller center, dia | 39.9, 193.7, about 55 mm (jig v6 ruler: hub centre 47 from the DC-end inside wall, 44.5 from the far inside wall; the photo had it 2.8 too far from the port edge) |
| Outlet | edge at Y 146.5, blows toward -Y, i.e. under the board toward the port edge |

All screws are M2.5 (2.1 mm pilots). Outlet spans about X 20 to 80 of the edge facing the board (from img1112). Ear plane assumed at the fan face that is visible in the chassis photo, which faces the floor.

## Open questions

Fill in after the colon on each line.

- Jig v7 / IO jig printed (USB-C rounded rectangle, VGA up, wall 0.5 from the board, WiFi nub +1): what still does not fit (hole, direction, mm):
- LED slit: are the LEDs visible enough through it, and is the Y position right (model: 19 and 29 from the port edge)?:
- Base v7 printed (1.9 pilots, 45 degree SD funnel): do the M2.5 screws grip without splitting the bosses, does the funnel ceiling print clean,
  is the SD card easy to pinch:
- Base v8 / lid v4 printed (SSD and ODD 9.6 toward the port edge, intake row cut to 3 slots, lip cut over the SSD, 10 mm corner posts):
  the board sat on the port-edge corner posts (fixed in v9: posts flattened at the board edge). Still to check: does the ribbon reach with
  the clip, do the ODD bosses and lid SSD holes line up, is the lid corner print clean, does the nub spacer hold:
- Base v9 (flattened posts, audio gap 7.0): does the board drop in:
- Anything on the main board top under the SSD's new position (X 128 to 198, Y 0 to 10) taller than the 2.6 mm gap, or at (91.9, 121.9) where the
  ODD spacer disc sits:
- Board-top airflow with only 3 intake slots left: does the board top (memory, VRM) run warm standing on the audio end:
- ODD cable clips printed (2 and 1.5 mm straight, 1.2 slot): which depth, does the slot take the board plus the ribbon, does it stay put:
- Stand v1 printed (2 mm plate, 4 mm rails 14 tall, 26.3 slot, notches at the ends and over the LED slit): does the case slide in, is it
  stable on either end, does the plate stay flat, do the screw heads clear, are the LEDs visible:
- Lid grille over the fan: enough on a shelf, or does the board top run warm (then offset it toward the board)?:

Answered:

- Lid v2 (2026-11-03): SSD holes measured on the lid, hole nearest the audio-end wall 16 from the inside wall, hole nearest the port edge 19.5
  from the port-edge inside wall (model had 15.5 and 20.0).

- Jig v6 (2026-11-02): USB-C 0.5 down and 0.5 right, as a rounded rectangle rather than a pill; VGA 0.5 up; port-edge wall and SD funnel plate
  0.5 from the board instead of 1 (wasted space). Fan hub centre on the jig: 47 from the DC-end inside wall, 44.5 from the far inside wall
  (the ears cannot check it, the mount photo had M3 14 mm off).
- Jig v5 (2026-11-02), directions as seen from outside with the DC jack on the left: audio up 1, USB and HDMI up 0.5, VGA right 0.5 and up 0.5,
  DC and USB-C 1 toward the corner, RJ45 up 1, USB-C up 2.5, DC up 1.5. H11, H10 and O7 row 0.5 toward the DC end. SD slot 1 smaller all round,
  with a gradual finger dimple in the wall around it. SSD on the jig: hole nearest the audio-end wall 15.5 from the inside wall, hole nearest the
  audio port 20.5 from the port-edge inside wall (holes standard, drive square to the case).
- Lid: M3 inserts, SSD bottom face up (bottom holes), WiFi nub needs slack. Screw posts inside the case in the corners. Walls on the base, lid flat
  with a lip, no SSD bosses (as thin as possible). Ample space above the DC jack.
  O7 is 96 mm from the SATA-edge PCB edge; O1..O4 are on one line 4 mm from it (ruler). Screw posts in the corners, fillet concentric.
- Jig v4 (2026-11-02): fan pattern fits, rotate M2/M3 about H9 so M3 is on H8's line; WiFi nub post 1 mm above M3; H6 0.5 further from H5.
  Lid: SSD top at 23 mm from the plate, SSD screwed from outside through the lid, lid bolted with inserts.
- Base v3 print feedback (2026-11-02): battery connector needs 7 mm past the DC-end edge, channel walls at 25.5 and 88, hole shifts as in the holes table,
  H11 and H12 added, M3 33 mm from H8 at 4.5 mm, M2 2 mm further out plus 1 mm fan clearance, ODD board on O6=H8 with 14 mm bosses at O1 and O7.

- All screws M2.5. RJ45 does not hang below the 10 mm layer. Lid heights later.
- Standoffs 10 mm. Fan on the floor, flat face up at PCB level, ears at H9 (under the board), 10 mm and 4.5 mm. Heatsink on the underside, lower than 10 mm. Chassis walls form a wind channel, 10 mm tall.
- Jig fits well enough for a first draft. Case is rectangular. Use chassis photo for positions.

- Port edge 203.5 mm. Screws M2.5, mostly 6 mm thread, some 13 mm from the frame.
- ODD board kept, flipped over the main board. Fan and WiFi stay in place. SSD kept.
- No power button. All ports reachable. PETG on a Bambu P1S. Fan 10 mm, PCB 1 mm, ethernet 13 mm.

## Log

- 2026-11-04: stand slimmed to a 2 mm plate with 4 mm rails (books can lie on the plate; a third of the filament); rail edges chamfered, 3 mm on the ends
- 2026-11-03: stand for standing the case on either end wall, ports to the back (`cad/out/stand.stl`): slotted bar, walls notched at the ends
  for the lid screw heads and over the LED slit
- 2026-11-03: base v8: the board collides with the 10 mm port-edge corner posts. Posts flattened at 0.5 from the board's X extent, audio-end
  gap 7.0 (was 6.5) so both port-edge posts keep a wall round the insert hole; case 0.5 longer. Base v9 exported.
- 2026-11-03: SSD and ODD board 9.6 toward the port edge (ribbon reach with the clip): ODD bosses, lid SSD holes and lip follow, intake row cut
  to the 3 slots the SSD does not cover (the audio-end wall faces the ground), ODD spacer with a nub to the lid replaces the H8 spacer, corner posts 10 mm on a 5.1 fillet so the lid chamfer
  leaves a wall round the corner screw recesses in the first layers
- 2026-11-03: ODD cable clip, two depths (`cad/out/odd_clip_2.stl`, `cad/out/odd_clip_1.5.stl`), slot 1.2, fold radius 1.5
- 2026-11-03: SD funnel symmetric at 45 degrees up and down, solid block to under the lid lip, opening 54 x 18 (base v6 printed with a flat ceiling that sagged and too small a hole)
- 2026-11-03: M2.5 pilot holes 1.9 (2.1 printed loose)
- 2026-11-03: SSD 0.5 toward the DC end and 0.5 toward the port edge (ruler on lid v2), lid v3 exported
- 2026-11-02: antenna cable coil ends beside the WiFi card
- 2026-11-02: SD funnel printable without supports: solid down to the floor, flat ceiling, flare downward only
- 2026-11-02: LED peek slit in the lid (1 mm, flared inside), WiFi nub boss 1 mm higher, H8 spacer 2 mm
- 2026-11-02: jig v7: USB-C rounded rectangle 0.5 right and down, VGA 0.5 up, port-edge wall and SD plate 0.5 from the board
- 2026-11-02: impeller centre from the ruler (Y 193.7), both grilles follow
- 2026-11-02: lid grille over the fan, exhaust row widened to 4 slots; vent area table in the decisions
- 2026-11-02: IO jig (port wall only, face down) added
- 2026-11-02: SD slot as a stepped-in rectangular funnel at the board edge (replaces the dimple), flat plate around the slot before the flare
- 2026-11-02: SSD moved 3.1 toward the audio end and 2.5 toward the port edge (ruler on the v5 jig), lid v2 exported
- 2026-11-02: jig v6 / base v5 from the v5 jig: port windows lifted and shifted, H10 row 0.5 toward the DC end, SD slot smaller with a finger scoop, intake row starts after RJ45
- 2026-11-02: port openings shaped per connector from the profile photo; DC jack and USB-C are both on the upper side
- 2026-11-02: lid v1: full-height base walls, flat lid, inside screw posts, SSD screws, H8 spacer, SSD measured from the chassis photo, ODD Y calibrated on O7
- 2026-11-02: jig v5: fan mounts rotated about H9, WiFi nub post, H6 +0.5
- 2026-11-02: ODD frame aligned to the board edges (2 degree photo rotation removed), hole map image
- 2026-11-02: base v4 from the v3 print feedback, bar-floor fit jig (`cad/out/jig.stl`)
- 2026-11-01: base v3d: separate USB-C and DC jack notches
- 2026-11-01: base v3c: floor grille back under the fan, intake slits in the audio-end wall
- 2026-11-01: base v3b: intake moved to floor slots beside the fan, channel walls extended to the exhaust wall
- 2026-11-01: base v3: frame corrected (underside down), 10 mm standoffs, fan at floor level, wind channel, port windows, SD notch
- 2026-11-01: rectangular base v2 with fan mounts, floor grille and wall slots; fan mounts from chassis posts
- 2026-11-01: ODD board and fan measured from img1111/img1112, main board holes cross-checked against chassis posts
- 2026-11-01: base plate and test jig modeled, exports in `cad/out/`
- 2026-11-01: main board outline and 10 mounting holes measured from img1109
- 2026-11-01: build123d-mcp installed, project config in `.mcp.json`, modeling skill in `.claude/skills/`
