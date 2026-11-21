# ARA — PCB — v0

**Status: floorplan only — outline, real library footprints placed,
keep-out rule areas, ten nets assigned to pads. No schematic, no
routing.** DRC runs and reports 33 violations (28 errors, 5 warnings) and
41 unconnected items: none is a courtyard overlap, a keep-out breach or a
board-edge clearance; all 28 errors are inside two library footprints
measured against KiCad's default constraints, and the 41 unconnected items
are the nets, none of which is routed. One footprint is an approximation
and one has no BOM part — see **Blocking**.

## Files (`kicad/`)

| File | Content |
|---|---|
| `gen_floorplan.py` | Writes the board file as text from the KiCad library footprints; holds every placement number and the pad-to-net table. Also asserts no courtyard bounding boxes overlap each other, the slot or the post holes, and prints the free area. |
| `ara_floorplan.kicad_pcb` | Generated board (KiCad 10.0.6 format) |
| `ara_floorplan.svg` | `kicad-cli pcb export svg` of Edge.Cuts, F.Cu, F.Fab, F.CrtYd, Dwgs.User, Cmts.User |
| `drc_report.txt` | Full `kicad-cli pcb drc --severity-all` output |

Regenerate and check:

```
python3 gen_floorplan.py
kicad-cli pcb drc --severity-all --output drc_report.txt ara_floorplan.kicad_pcb
```

## Conventions

- Board coordinates = case coordinates (`models/case/README.md`) + (100, 100) mm.
- Every component is on F.Cu, and F.Cu faces the **back** of the device
  (the display lies on the other side, which carries no parts). The board
  is therefore drawn as seen from the back, landscape: case +X to the
  right, case +Y down.
- In the device's own words (`models/case/README.md`, *Axes and
  orientation words*): the antenna end, **right** in the drawing, is the
  **top** of the device; the USB-C end, **left** in the drawing, is the
  **bottom**.
- Thickness 1.0 mm, 2 layers.

## Outline

Rectangle 82.95 × 29.3 mm (case x −44.65 → 38.3, y ±14.65) with three
internal cut-outs:

| Cut-out | Region (case mm) | Purpose |
|---|---|---|
| Slot | x −37.9 → −35.4, y ±7.0 (2.5 × 14) | the display FPC drops through it to J3 |
| Holes ×2 | Ø4.4 at (−41.4, ±11.5) | the bezel's screw posts pass through and locate the board |

Area 2 365.0 mm². The +X edge is the antenna base line: the module's
antenna (6 mm) overhangs the board entirely. The slot leaves a 7.65 mm
rail on each side; the holes leave 1.05 mm to the −X edge and 0.95 mm to
the long edges.

The outer 0.95 mm along both long edges (|y| > 13.7) rests on the shell
ledge; the ledge is cut away only at the four switches.

## Placement

Case coordinates, mm. Rotation is KiCad's (counter-clockwise).

| Ref | Part | Library footprint | x | y | Rot |
|---|---|---|---|---|---|
| U1 | ESP32-S3-WROOM-1-N16R8 | `RF_Module:ESP32-S3-WROOM-1` | 31.55 | 0 | 270 |
| MK1 | ICS-43434 | `Sensor_Audio:InvenSense_ICS-43434-6_3.5x2.65mm` | −40.4 | 7.4 | 270 |
| J1 | USB-C, charge-only | `Connector_USB:USB_C_Receptacle_GCT_USB4125-xx-x_6P_TopMnt_Horizontal` — **approximation** | −42.5 | 0 | 270 |
| J2 | Battery JST-PH | `Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal` | −21.0 | 8.0 | 90 |
| J3 | Display FPC, 24 × 0.5 mm | `Connector_FFC-FPC:Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal` — part not in BOM | −29.5 | 0 | 270 |
| U2 | TP4056 | `Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm` | −21.9 | −3.6 | 0 |
| U3 | MAX17048G+T10 | `Package_DFN_QFN:TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm` | −14.6 | −3.6 | 0 |
| U4 | MAX98357A | `Package_DFN_QFN:TQFN-16-1EP_3x3mm_P0.5mm_EP1.23x1.23mm` | −23.9 | −10.0 | 0 |
| U5 | AP2112K-3.3 | `Package_TO_SOT_SMD:SOT-23-5` | −17.5 | −10.0 | 0 |
| TP1, TP2 | speaker wire pads | `TestPoint:TestPoint_Pad_2.0x2.0mm` | −32.2, −28.8 | −11.4 | 0 |
| SW1–SW4 | Alps SKRTLAE010 | `Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010` | ±8.0 | ±12.55 | 0 / 180 |

U4 and U5 use the footprints KiCad's own symbols for those parts point to
(`Audio:MAX98357A`, `Regulator_Linear:AP2112K-3.3`).

J1 sits at the bottom edge, centred, mouth toward −X. Its body is the
8.94 × 6.8 mm of `docs/DESIGN.md`; it overhangs the board edge by 1.25 mm
to reach 1.0 mm behind the case's outer face.

J3 sits 1.5 mm inboard of the slot, mouth toward the slot. The tail comes
off the panel on the other side of the board, turns down through the slot
and folds back into J3 — the connector was already at that end, facing
that way; it moved with the panel, not relative to it.

The mic's sound port (NPTH Ø0.5 in the footprint) lands at case
(−41.11, 7.4), under the bezel's Ø1.0 port.

TP1/TP2 sit above the speaker (4.1 mm under the board there).

Rule areas in the board file:

| Name | Region (case mm) | Forbids |
|---|---|---|
| `ANT_KEEPOUT_A` / `_B` | x 23.3 → 38.3, \|y\| 9.75 → 14.65 | tracks, vias, pads, copper pour, footprints |
| `BATTERY_NO_PARTS` | x −12.2 → 17.8, y ±10 | footprints (battery is 0.3 mm under the board) |

The antenna strips are the part of the 15 mm keep-out that falls on the
board: the two bands beside the module body, back to 15 mm behind the
antenna base line. The module footprint's own T-shaped courtyard covers
15 mm to each side of and ahead of the antenna, which here lies entirely
beyond the board edge.

## Nets

Assigned to pads, not routed. Pin numbers come from KiCad's symbol library
except where noted.

| Net | Pads |
|---|---|
| `I2S_BCLK` | U1.4 (IO4), U4.16 (BCLK), MK1.4 (SCK) |
| `I2S_WS` | U1.5 (IO5), U4.14 (LRCLK), MK1.1 (WS) |
| `I2S_DOUT` | U1.6 (IO6) → U4.1 (DIN) |
| `I2S_DIN` | MK1.6 (SD) → U1.7 (IO7) |
| `SPK_P`, `SPK_N` | U4.9 (OUTP) → TP1, U4.10 (OUTN) → TP2 |
| `VBUS` | J1 A9/B9, U2.4 (VCC), U2.8 (CE) |
| `VBAT` | J2.1, U2.5 (BAT), U3.2 (CELL), U3.3 (VDD), U4.7/8 (VDD), U5.1 (VIN), U5.3 (EN) |
| `+3V3` | U5.5 (VOUT), U1.2, MK1.5 |
| `GND` | U1.1/40/41, MK1.2 (LR)/3, U2.3/9, U3.1/4/9, U4.3/11/15/17, U5.2, J1 A12/B12/shell, J2.2 |

Choices made here that a schematic has to confirm:

- The four I2S GPIOs are a provisional pick. Mic and amplifier share one
  clock pair.
- The amplifier runs from `VBAT`, as `docs/DESIGN.md` sizes it (0.93 W at
  3.7 V); the regulator sits between `VBAT` and `+3V3`, enable tied to its
  input (always on).
- U3's pin numbers and J2's polarity are from memory, not from a library
  symbol or the cell's datasheet.
- Left without a net: J3 (all 24), the switches, J1's CC pins, U1's other
  GPIOs, U2 PROG/TEMP/status, U3 I2C/alert, U4 gain and shutdown.

## DRC — actual output

`kicad-cli pcb drc --severity-all`, KiCad 10.0.6, default board constraints
(no project file), machine locale French. Header and footer verbatim:

```
** Found 33 DRC violations **
** Found 41 unconnected pads **
** Found 0 Footprint errors **
```

All 33, grouped by identical message (count on the left):

```
12 [drill_out_of_range]: Taille du trou en dehors de la plage (configuration des contraintes du PCB trou min 0,3000 mm ; réel 0,2000 mm)
     Rule: configuration des contraintes du PCB; error — Pad métallisé 41 [GND] de U1
 8 [hole_clearance]: Violation d'isolation des trous (configuration des contraintes des trous isolation 0,2500 mm; réel 0,0993 mm)
     Rule: configuration des contraintes des trous; error — Pad 1 de SW1, SW2, SW3, SW4 (2 each)
 8 [hole_clearance]: Violation d'isolation des trous (configuration des contraintes des trous isolation 0,2500 mm; réel 0,1500 mm)
     Rule: configuration des contraintes des trous; error — Pad MP de SW1, SW2, SW3, SW4 (2 each)
 4 [silk_edge_clearance]: Silkscreen clipped by board edge
     Rule: configuration des contraintes de la sérigraphie; warning — Segment de U1 sur F.Silkscreen (2), Champ référence de MK1 (1), Champ référence de J1 (1)
 1 [lib_footprint_mismatch]: L'empreinte 'ESP32-S3-WROOM-1' ne correspond pas à la copie en librairie 'RF_Module'
     Local override; warning — Empreinte U1
```

The 41 unconnected items, all one message, counted by net:

```
41 [unconnected_items]: Missing connection between items
     GND 21, VBAT 7, VBUS 3, +3V3 2, I2S_BCLK 2, I2S_WS 2, I2S_DOUT 1, I2S_DIN 1, SPK_P 1, SPK_N 1
```

Reading:

- **`drill_out_of_range` ×12** — the module footprint's thermal vias under
  its ground pad are 0.2 mm; KiCad's default minimum is 0.3 mm. Real for
  any fab with a 0.3 mm minimum drill; a fab-capability decision, not a
  placement fault.
- **`hole_clearance` ×16** — inside the library's SKRTLAE010 footprint:
  its two locating holes sit 0.10 / 0.15 mm from its own pads, under the
  default 0.25 mm. The switch is now the final part, so these stay until
  the board constraints are set or the footprint is adjusted.
- **`silk_edge_clearance` ×4** — the module's silkscreen outline follows
  the antenna past the board edge (2); the reference texts of MK1 and J1
  lie over the FPC slot (2). Cosmetic.
- **`lib_footprint_mismatch` ×1** — KiCad sees the embedded U1 as differing
  from its library copy. Cause not isolated; the other fourteen
  footprints, embedded by the same code, are not flagged.
- **`unconnected_items` ×41** — every net, because nothing is routed.
- Absent from the report: `courtyards_overlap`, `items_not_allowed`
  (rule areas), `copper_edge_clearance`.

## Margins

Courtyard-to-courtyard gaps, from the bounding boxes `gen_floorplan.py` prints:

| Pair | Gap (mm) |
|---|---|
| U1 courtyard ↔ battery zone | 0.25 |
| J1 courtyard ↔ FPC slot | 0.25 |
| MK1 ↔ post hole | 0.32 |
| J2 ↔ J3 | 0.40 |
| TP1 ↔ TP2 | 0.40 |
| MK1 ↔ J1 | 0.45 |
| MK1 ↔ FPC slot | 0.50 |
| U4 ↔ J3 | 0.50 |
| Switch courtyard ↔ battery zone | 0.50 |
| U3 ↔ battery zone | 0.77 |
| TP1 / TP2 ↔ J3 | 0.85 |
| U2 ↔ J3 | 0.90 |
| J3 ↔ FPC slot | 1.00 |
| U4 ↔ TP2 | 1.30 |
| U2 ↔ U4 | 1.60 |
| U2 ↔ U3 | 1.97 |
| U2 ↔ U5 | 2.00 |
| U4 ↔ U5 | 2.25 |

Area left for everything not yet placed, after removing courtyards, the
cut-outs, both rule areas, the module and the ledge strips: **593.5 mm²**,
of which 516.3 mm² is not above the speaker (component height limit over
the speaker: 4.1 mm; elsewhere 7.3 mm down to the case floor). That area
is fragmented — the strip below the display at the bottom end, strips
beside the battery (≈3.7 mm wide) and beside the module, and gaps between
parts — not one usable block.

## Blocking

1. **USB-C footprint is an approximation.** KiCad's library has no
   footprint for the SHOU HAN TYPE-C 6P CB1.6(073), and its mechanical
   drawing was not available. J1 is the library's GCT USB4125 — a real
   USB-C receptacle, also 6-pin power-only, same 8.94 × 6.8 mm body — the
   closest match found; its pads, shell-stake holes and board-edge
   position are GCT's, not SHOU HAN's. If "CB1.6" denotes a sunk-board
   mount, the real part also needs a board cut-out. Needs the manufacturer
   land pattern.
2. **Display FPC geometry unknown** (tail position, width, length, contact
   side): the slot size, J3's distance from it and J3's top/bottom-contact
   variant are guesses. J3's part is not in the BOM.
3. **Parts with no BOM entry are not placed:** battery protection if the
   cell has none, USB-C CC resistors, the amplifier's gain/shutdown
   resistors, decoupling for U1/U2/U4/U5, module strapping. Whether they
   fit in the fragmented 594 mm² is not shown.
4. **TP4056 footprint is a generic SOIC-8 with exposed pad** (2.41 × 3.3 mm
   pad); not checked against the TP4056 datasheet's land pattern.

## Unvalidated

- J3's pins 2 and 3 are left unconnected along with the rest. On Good
  Display's 24-pin pinout as recalled here they are GDR and RESE, which
  that vendor's reference circuit wires to an external FET and inductor.
  `docs/DESIGN.md` records that no boost circuit is needed; check those
  two pins against the datasheet before the schematic.
- Routability: 40 module pins to the bottom end must pass the battery
  zone, where the board is free of parts but only 2 layers, or the 3.7 mm
  side strips that also hold the switches. The I2S lines and both supply
  rails make that trip.
- No copper under the display has been considered for the panel or for
  the antenna (ground pour extent near x = 23 → 38).
- The slot is drawn with square corners; a routed slot has a radius.
- The amplifier is 5 mm from the speaker pads and at the far end of the
  board from the antenna (60.7 mm); its switching output has not been
  looked at beyond that.
- JST-PH mouth faces the battery with 4.4 mm for the lead bend.
- Switch pads on the long edges sit over the ledge cut-outs only;
  anything else placed at |y| > 13.7 lands on the ledge.

## Recommended tests

1. Get the SHOU HAN and GDEY0213B74 drawings, replace J1/J3, resize the
   slot, re-run DRC.
2. Draw the schematic before any routing, then run DRC with
   `--schematic-parity`; settle the I2S pins and the regulator's enable
   there.
3. Set the board constraints for the chosen fab (minimum drill, hole
   clearance) so the 28 footprint-internal errors are judged against real
   limits.
4. Print the SVG at 1:1 and lay the real parts on it.
