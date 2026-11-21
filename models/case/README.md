# ARA — case (bottom shell + screen bezel) — v0

**Status: geometry built and overlap-checked, not printed, not fit-tested.**
Rectangular, 93.8 × 33.8 × 12.5 mm assembled. Two printable bodies and 21
component ghosts in one SolidCraft design; `inspect.clearance` over all 23
bodies reports no overlap. Five items are blocking before a print is worth
doing — see **Blocking**.

![iso view](ara_case_iso.png)

Back face (antenna end to the right, speaker grille and the two screws at
the bottom end):

![back view](ara_case_back.png)

## Files

| File | Content |
|---|---|
| `ara_case.sc` | SolidCraft source: parameters, both printable bodies, all ghosts (`G_*`) |
| `ara_bottom_shell.stl` | Bottom shell, as modelled (Z up, back face on the bed) |
| `ara_bezel.stl` | Screen bezel with its posts, hooks and panel stops, as modelled (flip to print front-face down) |
| `ara_case_assembly.step` | All 23 bodies, for import into other CAD |
| `ara_case_iso.png`, `ara_case_back.png` | Renders of the current model |

## Axes and orientation words

Model axes: X along the length, Y across the width, Z from the back face
(z = 0) to the front (display side). Origin at the centre of the outline.

How the everyday words are mapped onto those axes — **this is an
interpretation, correct it here if it is wrong**:

| Word | Meaning in the model | Why |
|---|---|---|
| **top** (end) | **+X**, the antenna end | Requested: with the display read right-side-up, the antenna end is up. Nothing mechanical fixes "up" (no carry mode), so it is fixed by this convention and by the firmware drawing the panel in portrait with +X up. |
| **bottom** (end), "bottom face" | **−X** end, the end wall at x = −46.9 | Opposite the antenna. Carries the USB-C, the speaker, the mic port, the display FPC fold and the two screws. |
| **back face** | z = 0 | Speaker grille, screw heads. |
| **top plate** | the bezel, +Z | Screen side. |
| left / right | +Y / −Y, looking at the display with +X up | |
| horizontal / vertical | along Y / along X | Device held in portrait. |

The antenna was already alone at the +X end; no geometry was flipped to
make it the top. With +X up the panel's FPC tail is at the bottom.

The speaker's previous position was described as "back face, top-left,
vertical". That matches the previous iso render — where the −X end is
drawn toward the top of the picture and the −Y side toward the left — and
a 20 mm side lying along X. In that picture "top" is the −X end, the
opposite of the convention above. The target "bottom-center, horizontal"
was applied in the convention above: −X end, centred on y = 0, 20 mm side
along Y. Read the other way (bottom = +X) it would put the speaker under
the antenna, inside the keep-out; that was not done.

## Stack (Z)

| z (mm) | Layer |
|---|---|
| 0 → 1.6 | back wall (`floor_t`), speaker grille; locally 0 → 3.0 under the two screws |
| 1.6 → 8.6 | battery (7.0); speaker (1.6 → 4.8) at the bottom end |
| 8.6 → 8.9 | gap battery → PCB (`batt_gap` 0.3) |
| 8.9 → 9.9 | PCB (`pcb_t` 1.0), every component on its back-facing side |
| 9.9 → 10.3 | foam pad, compressed (`disp_gap` 0.4) |
| 10.3 → 11.3 | display panel (1.0) |
| 11.3 → 12.5 | bezel (`bezel_t` 1.2), flush with the shell rim; its underside bears on the panel border (`top_gap` 0) |

The PCB rests on a 1.2 mm ledge (`ledge`) running along both long walls at
z = 8.9. The bezel drops into a rabbet in the rim: 1.0 mm outer lip (`lip`),
0.15 mm fit per side (`bez_fit`).

## Layout (XY)

Length is set by one sum, all named parameters:

`cav_l = fpc_fold 9.0 + disp_l 59.2 + ant_keepout 15.0 + ant_l 6.0 + ant_gap 0.6 = 89.8`,
`L = cav_l + 2·wall = 93.8`. Width: `W = disp_w 29.2 + 2·fit 0.3 + 2·wall 2.0 = 33.8`.

`fpc_fold = usb_recess 1.0 + usb_d 6.8 + 1.2 + fpc_slot 2.5 − 0.5 − wall 2.0 = 9.0`:
at the bottom end the USB-C receptacle and the FPC fold sit one behind the
other along X. That is 6.0 mm more than the 3.0 mm the fold alone needed —
the cost of a centred USB-C on that end (see **USB-C**).

| Item | X range | Y range | Note |
|---|---|---|---|
| PCB | −44.65 → 38.3 | ±14.65 | one slot and two post holes, below |
| Display outline | −35.9 → 23.3 | ±14.6 | FPC end at −X (bottom) |
| Bezel window | −31.075 → 18.475 | ±12.35 | active area + 0.5 margin, **centred on the outline — placeholder, see Blocking 1** |
| ESP32 module body | 18.8 → 38.3 | ±9.0 | on the PCB back side |
| Antenna | 38.3 → 44.3 | ±9.0 | overhangs the PCB edge (PCB ends at 38.3) |
| Battery | −12.2 → 17.8 | ±10.0 | on the floor; nothing can sit on the PCB above it |
| Speaker | −39.1 → −25.1 | ±10.0 | on the floor, 20 mm side along Y; grille 3 × 5 holes Ø1.5, pitch 3.0, centred under it |
| USB-C | −45.9 → −39.1 | ±4.47 | under the PCB, z 5.74 → 8.9; mouth 1.0 mm behind the end wall's outer face (`usb_recess`) |
| FPC slot in the PCB | −37.9 → −35.4 | ±7.0 | `fpc_slot` × `fpc_slot_w` |
| FPC connector | −33.9 → −28.3 | ±7.55 | PCB back side, mouth toward the slot |
| Bezel posts / screws | x = −41.4 | y = ±11.5 | Ø4.0 posts through Ø4.4 PCB holes |
| Bezel hooks | at the +X end wall | 6 → 12 on each side | plastic only |
| Buttons | centred at x = ±8 | both long walls | openings 5.2 × 2.1 mm, z 6.9 → 9.0 |
| Mic port | x = −41.11 | y = 7.4 | Ø1.0 through the bezel, in the strip below the display |

**Battery access:** by full split — two screws out, shell off, unplug the
JST-PH from the PCB's back side.

## USB-C

On the bottom end wall, centred (y = 0). The opening is a stadium (two
half-circles joined by straight sides), 9.64 × 3.86 mm, end radius 1.93 —
the receptacle shell outline 8.94 × 3.16 mm from `docs/DESIGN.md` plus
`usb_clr` 0.35 all round. The ghost is the same stadium, 6.8 mm deep. The
previous opening was a square-cornered 9.64 × 3.86 rectangle, which read
as USB-A.

No mechanical drawing of the SHOU HAN TYPE-C 6P CB1.6(073) was available
(none in KiCad's library, no web access when this was built). Only the
three body dimensions come from the part; the end radius is the USB-C
shell's own geometry (half its height).

A centred USB-C and the display FPC both want the middle of the same end:
the receptacle is 8.94 mm wide, the FPC at least 12.5 mm (24 × 0.5 mm
contacts), the board 29.3 mm. They cannot sit side by side, so they sit in
series along X — receptacle at the board edge, then a slot through the
board for the FPC. Hence the extra 6.0 mm of length.

## Display FPC routing

Decided: the tail does not leave the panel sideways in its own plane. It
comes off the panel's bottom end, turns down through the PCB slot and
folds back under the board into the connector on the back side —
`G_FPCTail` models that path.

The connector's position is consistent with this: before and after this
change it sits on the PCB's back side at the panel's FPC end, mouth facing
the edge the tail comes over, 2.0 mm inboard of the panel end. What
changed is the edge: the tail used to wrap the board's outer edge and now
wraps the slot's, because the USB-C took the outer edge. That end is the
**bottom** in the convention above; "the connector is at the top" holds
only in the earlier render's reading, where the −X end is drawn up.

`G_FPCTail` is an idealisation: 12.5 mm wide, 0.3 mm thick, square
corners, 1.0 mm past the panel end. None of that is measured.

## Assembly and retention

The bezel carries everything; the bottom shell is the lid.

1. Bezel face down. The panel goes in **from behind**, face against the
   bezel underside. It cannot go through: the window (49.55 × 24.7) is
   smaller than the outline (59.2 × 29.2) — 2.25 mm of overlap on each long
   side, 4.825 mm on each short side while `act_off_x` = 0.
2. Three stops on the bezel underside locate the panel along X, 0.2 mm
   from each end: one at the top end (`PanelStopTop`), two at the bottom
   end either side of the FPC tail (`PanelStopBotA/B`). Along Y the panel
   is located by the shell walls (0.3 mm per side) once closed, and by
   nothing before that.
3. Foam pad, then the PCB over the two bezel posts, tail through the slot
   into the connector. The posts fix the PCB in X and Y.
4. Battery and speaker in the bottom shell, JST-PH plugged, speaker wires
   on their pads.
5. The two hook noses at the bezel's top end go into pockets in the
   shell's +X end wall; the shell swings closed and two screws go in from
   the back face, through the floor, into the posts.

The panel has no retention feature of its own. Closed, it is held between
the bezel underside (contact) and the foam on the PCB, the PCB on its
ledges; the hooks and screws are what keep that stack shut.

| Feature | Body | Geometry |
|---|---|---|
| Posts ×2 | bezel | Ø4.0, z 3.1 → 11.3, pilot Ø1.6 × 5.5 deep |
| Screw seats ×2 | shell | floor thickened to 3.0, Ø2.2 through, Ø4.2 × 1.8 counterbore from the back |
| Hooks ×2 | bezel | tongue 1.2 × 6 × 2.0 under the plate, nose 0.9 mm into the wall, z 9.5 → 10.5 |
| Hook pockets ×2 | shell | 1.0 deep × 6.6 × 1.35, z 9.3 → 10.65; 1.0 mm of wall left outside |
| Screws ×2 (`G_Screw1/2`) | ghost | thread-forming Ø2 × 6 pan head, placeholder; shank drawn at its 1.5 mm core |

No metal at the antenna end: the hooks are printed, the screws are 77.9 mm
from the antenna.

## Measured

Volumes (`measure`), against the values computed before building:

| Body | Bounding box (mm) | Volume measured | Volume computed | Faces |
|---|---|---|---|---|
| `BottomShell` | 93.8 × 33.8 × 12.5 | 11 323.60 mm³ | 11 323.60 mm³ | 89, closed |
| `Bezel` | 91.55 × 31.5 × 9.4 | 2 241.26 mm³ | 2 241.26 mm³ | 56, closed |

Solid-volume mass at 1.27 g/cm³ (PETG): 14.4 g shell, 2.8 g bezel.

Overlap check, all 23 bodies (`inspect.clearance {}`), verbatim:

```
{"bodies":23,"near":[],"nearest":{},"overlaps":[],"pairs_checked":61,
 "pairs_pruned":192,"pairs_reused":0,"truncated":false,"unchecked":[]}
```

Grille, from the shell's cylinder faces: 15 holes Ø1.5 through the 1.6 mm
floor at x = −35.1 / −32.1 / −29.1, y = 0, ±3, ±6 — a 7.5 × 13.5 mm field
centred in the 14 × 20 mm speaker footprint, 5.5 mm from the nearest screw
counterbore.

Parameter test (`check_parameters {ant_keepout: 10, batt_h: 8, usb_d: 7.5}`):
`errors: []`, shell rebuilds to 89.5 × 33.8 × 13.5 mm, design restored.
Ghosts placed with plain numbers (`G_JST`, `G_TP4056`, `G_MAX17048`,
`G_MAX98357A`, `G_AP2112K`, `G_FPC`'s and `G_FPCTail`'s Y, switch Y, hook
and stop Y) do not follow parameters; the others do.

## Antenna keep-out

Rule applied: no metal-bearing part of the device within 15 mm of the
antenna volume (18 × 6 × 3.1 mm box), measured in 3D, in every direction —
stricter than a sideways/forward-only reading. Distances from `G_Antenna`
(`inspect.clearance`, exact faces):

| To | Distance (mm) | |
|---|---|---|
| Display panel | **15.07** | governs `ant_keepout`; 0.07 mm of margin |
| Battery | 20.50 | |
| Switches SW1 / SW3 | 28.14 | |
| Switches SW2 / SW4 | 44.10 | |
| MAX17048 | 51.90 | |
| AP2112K | 54.30 | |
| JST-PH | 54.90 | |
| TP4056 | 57.20 | |
| MAX98357A | 60.70 | |
| Speaker | 63.41 | |
| FPC connector | 66.60 | |
| FPC tail | 72.20 | |
| Microphone | 76.95 | |
| USB-C | 77.40 | |
| Screws | 77.94 | |
| Module body, PCB edge | 0 | by construction; PCB stops at the antenna base line |
| Bezel hook tongue (plastic) | 0.40 | above the antenna |
| Shell end wall (plastic) | 0.60 | |

What this does **not** cover: the outside world. The outer wall is 7.9 mm
from the antenna's sides and 2.6 mm from its tip, so a hand or a metal
surface against the +X end is inside 15 mm regardless of the case.

The 15 mm between display and antenna is the largest single term in the
length. KiCad's library footprint for this module draws the keep-out as a
T (15 mm to each side and ahead of the antenna, nothing behind its base
line); under that reading `ant_keepout` could shrink toward 0 and the case
toward ~79 mm. Left at 15 here; it is one parameter if an RF test says
otherwise.

## Margins

Smallest gaps, measured with `inspect.clearance`:

| Pair | Gap (mm) | Comment |
|---|---|---|
| Bezel ↔ display top | 0 | contact by design; tolerance is taken by the foam, not by a gap |
| Screw core ↔ post pilot | 0.05 | radial; the thread is meant to cut into the post |
| Hook nose ↔ pocket | 0.10 end, 0.15 above | from the feature dimensions; lets the top end lift 0.15 |
| Bezel post ↔ PCB hole | 0.20 | radial |
| Display ↔ side walls | 0.30 | `fit` |
| PCB ↔ battery | 0.30 | **no swelling allowance** for the Li-Po |
| Switch body ↔ shell opening | 0.33 | |
| USB-C shell ↔ opening | 0.35 | `usb_clr` |
| PCB ↔ display | 0.40 | foam, compressed thickness, not chosen |
| Antenna ↔ end wall | 0.60 | |
| FPC tail ↔ slot edge | 0.64 | idealised tail |
| FPC tail ↔ bezel underside | 0.70 | idealised tail |
| Bezel post ↔ speaker | 0.75 | speaker drawn as a box; the real frame is oval |
| Bezel post ↔ microphone | 0.78 | |
| Screw head ↔ speaker | 0.85 | |
| Speaker ↔ JST-PH | 0.90 | |
| Speaker top ↔ USB-C underside | 0.94 | vertical |
| Battery ↔ module | 1.00 | `batt_mod_gap` |
| Battery ↔ switches | 1.20 | |
| Battery ↔ MAX17048 | 1.40 | |
| Microphone ↔ USB-C | 1.66 | |
| JST-PH ↔ ledge | 1.75 | |
| Speaker top ↔ FPC connector | 2.10 | vertical |
| USB-C ↔ FPC tail | 2.20 | |
| Speaker top ↔ PCB | 4.10 | vertical |
| Battery ↔ JST-PH mouth | 4.40 | room for the lead bend |
| Speaker ↔ battery | 12.90 | |

Walls: 2.0 mm sides, 1.6 mm back, 1.0 mm rim lip. At the four corners the
cavity is square inside a 4 mm outer radius, so the wall thins to 1.17 mm
and the bezel seat narrows to 0.17 mm there (computed, not measured).

## Blocking

1. **Display active-area position and FPC tail dimensions are unknown.**
   `docs/DESIGN.md` gives the panel outline and the active-area size but
   not where the active area sits inside the outline. The window is
   centred on the outline (`act_off_x = 0`), which is almost certainly
   wrong along X. The routing is decided; the tail's lateral position,
   width, thickness, length and bend radius are not measured, so the slot
   (2.5 × 14 mm) and the 2.0 mm from panel end to connector are
   assumptions. Needs the Good Display mechanical drawing or a calliper on
   the real panel.
2. **USB-C receptacle drawing missing.** Position, opening shape and body
   size are set; the mounting is not. The ghost is surface-mounted under
   the PCB and overhangs its edge by 1.25 mm. If "CB1.6" in the part name
   means a sunk-board (mid-mount) type, its height relative to the PCB and
   the opening's Z both change.
3. **No button caps.** The switch is final (Alps SKRTLAE010; the ghost,
   4.5 × 3.39 × 1.65 mm, matches the 4.5 × 3.4 × 1.65 in `docs/DESIGN.md`
   and the outline of KiCad's footprint for that part, so no geometry
   changed). Its actuator tip stops 0.3 mm short of the cavity wall; a
   cap/plunger has to bridge that and the 2.0 mm wall.
4. **Fasteners are not in the BOM.** The two screws are a placeholder
   size; pilot diameter and engagement (4.7 mm) are untested in PETG.
5. **The FPC connector has no BOM entry.** Its ghost is a Hirose FH12-24S
   outline, 2.0 mm high.

## Unvalidated

- Component heights for the JST-PH header (5.5), FPC connector (2.0),
  TP4056 (1.75), MAX17048 (0.75), AP2112K (1.45, the SOT-23-5 package
  maximum) and the switch (1.65) are recalled datasheet values; KiCad's 3D
  models are not installed on this machine to check them against.
  MAX98357A (0.75) is the figure in `docs/DESIGN.md`.
- Closing the case: the hook-and-swing motion with 8.2 mm posts has not
  been simulated; the posts clear the end wall by 1.5 mm.
- The bezel bears on the panel with no nominal gap. With the foam too
  thick or the print too tall the panel is squeezed; nothing here limits
  that force.
- Nothing fixes the speaker or the battery.
- Mic path: 1.4 mm of open air between the PCB top and the bezel underside
  at the port; needs a gasket or a printed chimney.
- Speaker has no gasket to the grille and no defined back volume.
- 1.0 mm USB-C recess vs. plug engagement.
- Printability: the USB opening is a 9.64 mm bridge with rounded ends, the
  button openings 5.2 mm, the hook pockets 6.6 mm; the rim lip is 1.0 mm
  (2 perimeters at 0.4 mm); the posts are 8.2 mm tall on a 1.2 mm plate.

## Recommended tests

1. Calliper the real GDEY0213B74 (active-area offset, FPC position, width
   and tail length), set `act_off_x`, `fpc_slot`, `fpc_slot_w`, re-run the
   clearance check.
2. Print both bodies in PETG; check bezel fit in the rabbet (0.15 mm/side),
   that the hooks engage and the case swings closed, and that the PCB
   ledge prints clean without support.
3. Drive the two screws into printed posts; check they hold and the posts
   do not split.
4. Dry-fit battery, speaker and a USB-C plug through the opening.
5. RF: RSSI at a fixed distance with the display in place, then with the
   module slid 5 and 10 mm toward the display, to decide whether
   `ant_keepout` can come down; repeat with the +X end held in a fist.

---

Licence: CC-BY-SA-4.0.
