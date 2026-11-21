# ARA — case proposal v0.8

**Status: parametric mechanical study, not a manufacturing validation.**

Built in SolidCraft around the fixed BOM of `docs/DESIGN.md`. Goal of this
iteration: the shortest, smallest shell the fixed components allow, and an
MCU placement whose antenna is no longer over the battery. Earlier studies
(OpenSCAD v0.4/v0.5, SolidCraft back shells v01–v07) live in `.history/`,
which is not tracked.

## Composition

- `ARA_case_v08.sc`: SolidCraft source. Every size is a named parameter
  (`R`, `wall`, `floor_t`, `top_t`, `bat_h`, `seam`, `closure_r`, …) and
  every feature is named. Bodies prefixed `G_` are **component ghosts**
  (battery, PCB, MCU shield / antenna zone, speaker, USB-C, display,
  switches, inserts, mic, ZIF, JST, PCB screw heads) kept for clearance
  checks; they are not parts.
- `ARA_case_v08.step`: the three printable parts only.
- `ara_v08_front.stl`: front body — display face, side wall, buttons,
  USB-C opening, carries the PCB. Exported in assembly orientation; print
  it display face down (fence and posts then point up, no support).
- `ara_v08_back.stl`: back lid — floor, speaker grille, battery rails,
  screw heads. Prints as exported.
- `ara_v08_button.stl`: one plunger (print 4), exported along X; stand it
  upright to print.

There is no separate screen retainer anymore: the PCB holds the panel
through a foam frame (see below).

## Geometry

**Ø58 × 12.7 mm** (60.0 mm across the button caps). Previous study:
Ø60 × 22 mm.

Vertical stack, from the back face (z = 0) up — this is what sets the
height, each line is a parameter:

| z (mm)      | Layer                                                  |
| ----------- | ------------------------------------------------------ |
| 0 – 1.6     | back floor (`floor_t`)                                 |
| 1.6 – 8.9   | battery, worst-case 7.3 mm (`bat_h`)                   |
| 8.9 – 9.3   | air above the battery (`bat_gap`), never clamped        |
| 9.3 – 10.5  | PCB, 1.2 mm (`pcb_t`)                                  |
| 10.5 – 11.3 | foam frame on the panel's inactive border (`foam`)     |
| 11.3 – 11.7 | ET013TT1 panel, 0.4 mm (`panel_t`)                     |
| 11.7 – 12.7 | front lip around the window (`top_t`)                  |

Everything else fits **beside** the battery in the 7.7 mm under the PCB,
not stacked on it: MCU, USB-C, the four switches, mic and JST are on the
PCB's **back side**; the speaker lies on the floor under the MCU.

- **Split**: flat seam at z = 5.0 (`seam`). Back lid 0 – 5.0, front body
  5.0 – 12.7. Wall 1.6 mm, 2 mm rounds on both outer edges.
- **Closure**: 4× M2 button-head screws (M2×8) threaded from the back
  through Ø2.45 clearance holes, heads in Ø4.3 × 1.5 recesses, into M2
  heat-set inserts in Ø3.2 × 4.0 pilots at the bottom of the front's
  Ø5.6 bosses. Bosses at r = 24.8 mm, ±33° and 180 ± 33° — clear of the
  battery, the USB-C, the buttons and the antenna. No screw on the display
  face.
- **Display**: 23.5 mm square window (active area 23.30 + 0.1 mm per side)
  in a 1.0 mm lip. The panel drops into a 0.8 mm locating fence
  (27.5 × 28.8 mm inside, 0.2 mm per side) that also serves as the PCB's
  upper stop; 16 mm gap in the fence's lower side for the FPC.
- **MCU**: `ESP32-S3-WROOM-1` on the PCB back side, long axis along Y,
  **antenna toward 12 o'clock**, module spanning y = −0.15 … 25.35 mm.
  The PCB is cut away under the antenna zone (y > 18.85 mm, |x| < 10 mm).
- **Battery**: `LP702030` envelope 32 × 20.5 × 7.3 mm in the lower half of
  the lid (centre y = −11.15 mm), 0.8 mm rails at 0.25 mm per side, open at
  both short ends for the JST-PH lead.
- **Speaker**: `CDS-20144` on the lid floor under the MCU's shielded half
  (centre y = 8 mm, 0.5 mm gasket below it), square locating fence
  20.6 × 14.6 mm so any 20 × 14 oval fits, grille of 15 × Ø1.4 mm holes
  through the 1.6 mm floor directly under the diaphragm.
- **USB-C** at **9 o'clock** (y = −4.5 mm), receptacle on the PCB back side,
  centred 1.58 mm below the board (z = 7.72), front 0.3 mm behind the outer
  surface. 9.4 × 3.6 mm stadium opening, extended by a notch down to the
  seam so the receptacle slides in with the board.
- **Buttons**: Talk 12.5°, Stop 0°, Menu −12.5° (right side), Power 167.5°
  (left, above the USB-C). Ø3.4 holes on the same axis height as the USB-C
  (z = 7.72). Plunger: Ø5.0 × 0.8 flange inside, Ø3.0 shaft, cap 1.2 mm
  proud; 0.2 mm to the switch actuator at rest.
- **Mic**: `ICS-43434` (bottom port) on the PCB back side at
  (−6, −23.6), sound through a Ø1.0 front hole and a short tube ending
  0.3 mm above the PCB for a foam ring.
- **PCB**: Ø52.4 disc with four Ø6.4 notches at the closure bosses and the
  antenna cut-out. Held in the front by 3 M2 thread-forming screws (from
  the board's back) into Ø4.5 posts at (±18, 4) and (0, −24.3).

## What changed from the previous iteration

Compared against `.history/ARA_shell_v05.scad` and the measured geometry
of `.history/ARA_back_USB_clean_editable_v07.sc`:

| | v0.5 / v07 | v0.8 |
| --- | --- | --- |
| Outer size | Ø60 × 22 mm (back 16 + front 6) | **Ø58 × 12.7 mm** |
| Envelope volume | 62.2 cm³ | **33.6 cm³ (−46 %)** |
| Side wall / floor / display lip | 2.0 / 2.0 / 1.2 mm | 1.6 / 1.6 / 1.0 mm |
| Parts | front, back, retainer, 4 plungers | front, back, 4 plungers |
| Battery ↔ MCU | MCU stacked on top of it | side by side |
| Antenna ↔ battery | 1.6 mm, directly above | **19.75 mm**, beside |
| USB-C | 6 o'clock | 9 o'clock |
| Closure bosses | Ø8.4 at r = 27 in the `.scad`, r = 24 in v07 | Ø5.6 at r = 24.8 |

Height went from 22 to 12.7 mm (−9.3 mm). The old stack was floor 2 +
battery 7.3 + 0.4 + PCB 1.2 + MCU 3.1 on top of the board + 2 mm free to the
seam, then a 6 mm front holding the panel and its retainer. Now the MCU sits
beside the battery under the board, the PCB itself holds the panel, and the
walls are 0.4 mm thinner.

## Antenna keep-out

Espressif asks for 15 mm of clearance around the PCB antenna inside the
finished enclosure. Measured distances from the antenna zone (the module's
last 6.5 mm, an assumption to check against the module drawing):

| To | v0.8 (measured) | v0.5 (calculated from the `.scad`) |
| --- | --- | --- |
| Battery | **19.75 mm** | 1.6 mm, overlapping in plan |
| Closure inserts (brass + screw) | 11.15 mm | ~8.4 mm |
| PCB hold screws | 15.5 mm | — |
| Switches | 17.5 mm | — |
| USB-C | 22.9 mm | — |
| Display panel | 5.06 mm | ~6.4 mm |
| Speaker | **3.95 mm** | ~6.4 mm |
| Plastic side wall | **0.5 mm** at the corner, 2.05 mm on axis | 7.9 mm at the corner, ~14.5 mm on axis |

The ~13.8 mm figure in earlier notes could not be reproduced from any of
the earlier geometries and is superseded by this table.

## Planned assembly order

1. Press the 4 M2 heat-set inserts into the front's bosses from the seam
   face (soldering iron, not cold).
2. Fit the 4 plungers from the inside, flange against the wall.
3. Lay the panel face down in the fence, FPC tail through the lower gap,
   then the foam frame on its inactive border.
4. Plug the FPC into the ZIF on the PCB, then lower the PCB in, back side
   facing out; the USB-C slides into its notch. Fix it with the 3 M2
   thread-forming screws.
5. In the back lid: speaker with its gasket into the fence, battery into
   its rails.
6. Plug the battery (JST-PH) and the speaker into the PCB, close the lid,
   4 M2×8 screws from the back.

**Battery replacement**: 4 screws, lift the lid (the battery comes with it),
unplug the JST-PH. The screen isn't touched.
**Screen replacement**: lid off, unplug battery and speaker, 3 PCB screws,
lift the board, open the ZIF; the panel lifts out of its fence. No glue
anywhere.

## To validate before a working electronic prototype

**Blocking**

- **PCB floorplan is now out of date**: `models/pcb/` still has the MCU on
  the top face, antenna toward +X, USB-C at 6 o'clock and notches at
  r = 27. This case needs a double-sided board: MCU, USB-C, switches, mic,
  JST, charger on the back side, the ZIF alone on the top side outside the
  display footprint, the copper-free cut-out under the antenna, and
  notches at r = 24.8 / ±33°.
- **Antenna**: the battery problem is fixed (19.75 mm). The antenna now
  sits 0.5 mm from the plastic wall and 3.95 mm from the speaker magnet.
  A Ø60 shell (`R = 30`) gives +1 mm to the wall without other changes. A
  range test on a real prototype remains mandatory.
- **USB-C at 9 o'clock** instead of 6, and a USB-C receptacle mounting
  assumption (top-mount, body on the board face, centred 1.58 mm off it)
  that the `CB1.6(073)` drawing has to confirm — a mid-mount version moves
  `usb_z` and the button axis with it.
- **Side switches** aren't chosen: the model reserves 3.5 × 4 × 3 mm per
  switch on the board's back side, actuator axis 1.58 mm below the board,
  at r = 26.2 mm. The plunger length follows the part picked.
- **E-Ink panel**: FPC exit assumed on the lower edge (16 mm gap), active
  area assumed centred on the outline, no cover glass; the foam frame
  pressure on the panel border is the retention method and is untested.
- **Screws/inserts**: M2 heat-set reference dimensions (Ø3.2 × 4.0 pilot),
  not a datasheet match yet. The PCB hold screws only bite 1.8 mm, enough
  to keep the board in place with the lid off, not more; their pilots
  leave 0.4 mm of material under the front face.

**Margins to watch**

- Battery: 0.4 mm above the worst-case 7.3 mm envelope (0.7 mm on the
  7.0 mm nominal), 0.25 mm to each rail. Little room for swelling.
- JST-PH zone (4.5 × 6 × 4.2 mm on the board's back side, right of the
  battery) sits 0.1 mm above the battery rail: placeholder until the real
  connector is picked.
- Screw head recesses end 0.05 mm inside the flat part of the back face.
- No registration lip between lid and front: alignment relies on the 4
  screws (±0.2 mm).

**Recommended tests**

- Print first in low-cost PLA to check fit, then PETG; check the 1.6 mm
  walls and the 1.0 mm lip come out clean.
- Speaker intelligibility with the device lying on its back (grille
  partly blocked) and with the open back volume under the MCU.
- Plunger travel, switch force and accidental presses, especially Talk vs
  Stop at 6 mm spacing.
- Thermal behaviour of the charger and amplifier.

## Validation done so far

Measured in SolidCraft on the v0.8 model, not assumed:

- Each build stage matched the hand-computed volume (front 4381.7 mm³,
  back 5493.2 mm³, within 0.01 %); all parts are closed solids.
- `inspect.clearance` over all 27 bodies (parts + component ghosts): **no
  overlap**, except the four heat-set inserts in their pilots (intended
  0.2 mm interference). This caught a real defect in the USB-C opening
  (0.2 mm wall sliver against the receptacle), fixed before export.
- Closure boss to display panel: **4.46 mm** in plan, at the same height
  (the old "~3.2 mm" comment only matches the ET013TT1 envelope at r = 27
  in the `.scad`; the r = 24 bosses really present in v07 give 0.2 mm).
- Boss outer edge at r = 27.6 merges into the side wall (inner r = 27.4,
  outer 29) — nothing is clipped by the outer surface any more.
- The antenna distances in the table above.

Not verified: anything electrical, acoustic, thermal, or printed.

**Intellectual property**: this model proposal is distributed under
CC BY-SA 4.0 so it can be modified and shared in the spirit of the project.
