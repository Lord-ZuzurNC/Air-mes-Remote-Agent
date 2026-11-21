# ARA — PCB — v0

**Status: floorplan only — outline, real library footprints placed
(32, display boost circuit included), keep-out rule areas, 27 nets
assigned to pads. No schematic, no routing.** DRC runs and reports 33
violations (28 errors, 5 warnings) and 84 unconnected items: none is a
courtyard overlap, a keep-out breach or a board-edge clearance; all 28
errors are inside two library footprints measured against KiCad's default
constraints, and the 84 unconnected items are the nets, none of which is
routed. The bottom 30 mm of the board is packed courtyard to courtyard and
the support passives are not placed — see **Blocking**.

## Files

| File                            | Content                                                                                                                                                                                                                                        |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `kicad/gen_floorplan.py`        | Writes the board file as text from the KiCad library footprints; holds every placement number and the pad-to-net table. Also asserts no courtyard bounding boxes overlap each other, the cut-outs or the rule areas, and prints the free area. |
| `kicad/ara_floorplan.kicad_pcb` | Generated board (KiCad 10.0.6 format)                                                                                                                                                                                                          |
| `kicad/ara_floorplan.svg`       | `kicad-cli pcb export svg` of Edge.Cuts, F.Cu, F.Fab, F.CrtYd, Dwgs.User, Cmts.User                                                                                                                                                            |
| `kicad/drc_report.txt`          | Full `kicad-cli pcb drc --severity-all` output                                                                                                                                                                                                 |
| `BOM_to_buy.md`                 | The shopping list: every part, order code, quantity for one unit                                                                                                                                                                               |

Regenerate and check, from `kicad/`:

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
  orientation words*): the antenna and hook end, **right** in the drawing,
  is the **top** of the device; the screw end, **left** in the drawing, is
  the **bottom**. The device's right wall (USB-C) is the **upper** edge of
  the drawing.
- Thickness 1.0 mm, 2 layers.
- Reference designators are on F.Fab, not on the silkscreen: this is a
  floorplan, and at this density they would overlap pads.

## Outline

Rectangle 79.95 × 29.3 mm (case x −43.15 → 36.8, y ±14.65) with three
internal cut-outs:

| Cut-out  | Region (case mm)                         | Purpose                                                                                  |
| -------- | ---------------------------------------- | ---------------------------------------------------------------------------------------- |
| Slot     | x −39.6 → −36.9, y −6.8 → 7.2 (2.7 × 14) | the display FPC drops through it to J3; centred on the tail, 0.2 mm off the board centre |
| Holes ×2 | Ø4.4 at (−39.9, ±11.5)                   | the bezel's screw posts pass through and locate the board                                |

Area 2 274.3 mm². The +X edge is the antenna base line: the module's
antenna (6 mm) overhangs the board entirely. Between the −X edge and the
slot a 3.55 mm rail carries the microphone and the two speaker pads; the
slot leaves 7.85 mm and 7.45 mm of board at its ends; the holes leave
1.05 mm to the −X edge, 0.95 mm to the long edges and 2.1 / 2.5 mm to the slot.

The outer 0.95 mm along both long edges (|y| > 13.7) rests on the shell
ledge; the ledge is cut away at the four switches and at the USB-C.

## Placement

Case coordinates, mm. Rotation is KiCad's (counter-clockwise).

| Ref                           | Part                                          | Library footprint                                                                       | x                        | y      | Rot     |
| ----------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------ | ------ | ------- |
| U1                            | ESP32-S3-WROOM-1-N16R8                        | `RF_Module:ESP32-S3-WROOM-1`                                                            | 30.05                    | 0      | 270     |
| MK1                           | ICS-43434                                     | `Sensor_Audio:InvenSense_ICS-43434-6_3.5x2.65mm`                                        | −41.375                  | −0.71  | 0       |
| J1                            | USB-C, charge-only, SHOU HAN TYPE-C 6P(073)   | `Connector_USB:USB_C_Receptacle_GCT_USB4125-xx-x_6P_TopMnt_Horizontal` — see Blocking 2 | −18.75                   | −12.5  | 180     |
| J2                            | Battery header, JST S2B-PH-SM4-TB             | `Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal`                        | −19.15                   | 8.6    | 180     |
| J3                            | Display FPC, 24 × 0.5 mm, Hirose FH12A / FH12 | `Connector_FFC-FPC:Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal`                   | −27.3                    | 0.2    | 270     |
| U2                            | TP4056                                        | `Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm`                                  | −20.5                    | −5.4   | 0       |
| U3                            | MAX17048G+T10                                 | `Package_DFN_QFN:TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm`                                   | −15.0                    | −4.0   | 0       |
| U4                            | MAX98357AETE+T                                | `Package_DFN_QFN:TQFN-16-1EP_3x3mm_P0.5mm_EP1.23x1.23mm`                                | −30.1                    | −11.0  | 0       |
| U5                            | AP2112K-3.3TRG1                               | `Package_TO_SOT_SMD:SOT-23-5`                                                           | 0                        | 11.85  | 0       |
| TP1, TP2                      | speaker wire pads                             | `TestPoint:TestPoint_Pad_1.5x1.5mm`                                                     | −41.375                  | ±6.5   | 0       |
| SW1–SW4                       | Alps SKRTLAE010                               | `Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010`                       | ±8.0                     | ±12.55 | 0 / 180 |
| L1                            | 47 µH, Cenker CKCS4030-47uH/M                 | `Inductor_SMD:L_Cenker_CKCS4030`                                                        | −34.55                   | 11.1   | 90      |
| Q1                            | Si1308EDL                                     | `Package_TO_SOT_SMD:SOT-323_SC-70`                                                      | −27.7                    | 10.4   | 0       |
| R1                            | 1 MΩ                                          | `Resistor_SMD:R_0603_1608Metric`                                                        | −30.7                    | 9.99   | 0       |
| R2                            | 2.2 Ω                                         | `Resistor_SMD:R_0603_1608Metric`                                                        | −30.7                    | 11.47  | 0       |
| C4                            | 4.7 µF / 25 V                                 | `Capacitor_SMD:C_0603_1608Metric`                                                       | −34.55                   | 7.72   | 0       |
| D1, D2                        | MBR0530T1G                                    | `Diode_SMD:D_SOD-123`                                                                   | −35.75, −33.4            | −11.35 | 90      |
| D3                            | MBR0530T1G                                    | `Diode_SMD:D_SOD-123`                                                                   | −34.55                   | −7.85  | 0       |
| C3                            | 4.7 µF / 25 V                                 | `Capacitor_SMD:C_0603_1608Metric`                                                       | −27.27                   | −11.3  | 90      |
| C2                            | 1 µF / 25 V                                   | `Capacitor_SMD:C_0603_1608Metric`                                                       | −25.2                    | −11.3  | 90      |
| C12, C11, C10, C5, C9, C7, C6 | 1 µF / 25 V                                   | `Capacitor_SMD:C_0603_1608Metric`                                                       | −23.5 → −14.5, pitch 1.5 | −1.2   | 90      |

U4 and U5 use the footprints KiCad's own symbols for those parts point to
(`Audio:MAX98357A`, `Regulator_Linear:AP2112K-3.3`). L1's footprint is the
library's own for the part on the shopping list.

J1 is on the device's right wall, mouth toward −Y, 1.0 mm behind the
case's outer face; its body overhangs the board edge by 1.25 mm.

J3 is 5.7 mm inboard of the panel's bottom end, mouth toward the slot. The
tail comes off the panel on the other side of the board, turns down
through the slot and folds back into J3. The FH12A (top contact) and FH12
(bottom contact) share this land pattern (Hirose catalogue, one table for
both); which one is fitted depends on the panel, see Blocking 3.

J2's mouth faces −Y. The 3.9 mm in front of it (down to y = 0.3) is kept
free for the mated plug and the lead bend.

The mic's sound port (NPTH Ø0.5 in the footprint) lands at case
(−41.375, 0), under the bezel's Ø1.0 port.

TP1/TP2 are on the rail at the bottom edge, 3.8 mm from the speaker's end.

Rule areas in the board file:

| Name                   | Region (case mm)                  | Forbids                                               |
| ---------------------- | --------------------------------- | ----------------------------------------------------- |
| `ANT_KEEPOUT_A` / `_B` | x 21.8 → 36.8, \|y\| 9.75 → 14.65 | tracks, vias, pads, copper pour, footprints           |
| `BATTERY_NO_PARTS`     | x −13.2 → 16.55, y ±10            | footprints (battery is 0.3 mm under the board)        |
| `FPC_TAIL_NO_PARTS`    | x −36.9 → −32.2, y −6.05 → 6.45   | footprints (the tail runs 1.0–1.3 mm under the board) |
| `JST_PLUG_NO_PARTS`    | x −23.1 → −15.2, y 0.3 → 3.5      | footprints (mated plug, lead bend)                    |

The antenna strips are the part of the 15 mm keep-out that falls on the
board: the two bands beside the module body, back to 15 mm behind the
antenna base line. The module footprint's own T-shaped courtyard covers
15 mm to each side of and ahead of the antenna, which here lies entirely
beyond the board edge. The battery area stops 0.25 mm short of the
battery's top end (x = 16.8), where the module's library courtyard begins.

## Display boost circuit

From the GDEY0213B74 specification, section 12 *Reference Circuit*
(page 29, a drawing; read from a render of it). Designators are the
specification's own; it has no C1 and no C8. Ten capacitors, not seven:
C2, C4 and C11 are in the drawing as well.

| Ref | Value         | Between                                           |
| --- | ------------- | ------------------------------------------------- |
| C4  | 4.7 µF / 25 V | `+3V3` (L1's input side) and `GND`                |
| L1  | 47 µH, 500 mA | `+3V3` and `EPD_SW`                               |
| Q1  | Si1308EDL     | drain `EPD_SW`, gate `EPD_GDR`, source `EPD_RESE` |
| R1  | 1 MΩ          | `EPD_GDR` and `GND`                               |
| R2  | 2.2 Ω         | `EPD_RESE` and `GND`                              |
| D3  | MBR0530       | anode `EPD_SW`, cathode `EPD_PREVGH`              |
| C5  | 1 µF / 25 V   | `EPD_PREVGH` and `GND`                            |
| C3  | 4.7 µF / 25 V | `EPD_SW` and `EPD_CP`                             |
| D2  | MBR0530       | anode `EPD_CP`, cathode `GND`                     |
| D1  | MBR0530       | cathode `EPD_CP`, anode `EPD_PREVGL`              |
| C11 | 1 µF / 25 V   | `EPD_PREVGL` and `GND`                            |
| C2  | 1 µF / 25 V   | `EPD_VSH2` and `GND`                              |
| C9  | 1 µF / 25 V   | `EPD_VSH1` and `GND`                              |
| C10 | 1 µF / 25 V   | `EPD_VSL` and `GND`                               |
| C12 | 1 µF / 25 V   | `EPD_VCOM` and `GND`                              |
| C7  | 1 µF / 25 V   | `EPD_VDD` and `GND`                               |
| C6  | 1 µF / 25 V   | `+3V3` (VCI) and `GND`                            |

Panel pins, and the J3 pad each lands on. J3 is turned so that its pad 1
is at −Y; the panel's pin 1 is at +Y (left, seen from the front; the fold
does not change that). FPC pin n is therefore on J3 pad 25 − n:

| FPC pin | Name       | Net                               | J3 pad |
| ------- | ---------- | --------------------------------- | ------ |
| 1, 4    | NC         | —                                 | 24, 21 |
| 2       | GDR        | `EPD_GDR`                         | 23     |
| 3       | RESE       | `EPD_RESE`                        | 22     |
| 5       | VSH2       | `EPD_VSH2`                        | 20     |
| 6, 7    | TSCL, TSDA | — (open in the reference circuit) | 19, 18 |
| 8       | BS         | `GND` (4-wire SPI)                | 17     |
| 9       | BUSY       | `EPD_BUSY`                        | 16     |
| 10      | RES#       | `EPD_RST`                         | 15     |
| 11      | D/C#       | `EPD_DC`                          | 14     |
| 12      | CS#        | `EPD_CS`                          | 13     |
| 13      | SCL        | `EPD_SCK`                         | 12     |
| 14      | SDA        | `EPD_MOSI`                        | 11     |
| 15, 16  | VDDIO, VCI | `+3V3`                            | 10, 9  |
| 17      | VSS        | `GND`                             | 8      |
| 18      | VDD        | `EPD_VDD`                         | 7      |
| 19      | VPP        | — (open in the reference circuit) | 6      |
| 20      | VSH1       | `EPD_VSH1`                        | 5      |
| 21      | VGH        | `EPD_PREVGH`                      | 4      |
| 22      | VSL        | `EPD_VSL`                         | 3      |
| 23      | VGL        | `EPD_PREVGL`                      | 2      |
| 24      | VCOM       | `EPD_VCOM`                        | 1      |

Where the parts are: the seven capacitors that hang on one panel pin each
(C12, C11, C10, C5, C9, C7, C6) are in a row behind J3's pads.
L1 and C4 are on the left side of J3 (case +Y), Q1, R1 and R2 beside its
GDR/RESE end; D1–D3, C3 and C2 are on the right side (−Y), next to U4.
`EPD_SW` has to cross from one side of J3 to the other (about 20 mm,
around J3's mouth or under it on the other layer), and the VGH/VGL pads
are 10–14 mm from their diodes.

## Nets

Assigned to pads, not routed. Pin numbers come from KiCad's symbol library
except where noted; the display's are in the section above.

| Net                                                                                                                             | Pads                                                                                                                                                     |
| ------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `I2S_BCLK`                                                                                                                      | U1.4 (IO4), U4.16 (BCLK), MK1.4 (SCK)                                                                                                                    |
| `I2S_WS`                                                                                                                        | U1.5 (IO5), U4.14 (LRCLK), MK1.1 (WS)                                                                                                                    |
| `I2S_DOUT`                                                                                                                      | U1.6 (IO6) → U4.1 (DIN)                                                                                                                                  |
| `I2S_DIN`                                                                                                                       | MK1.6 (SD) → U1.7 (IO7)                                                                                                                                  |
| `SPK_P`, `SPK_N`                                                                                                                | U4.9 (OUTP) → TP1, U4.10 (OUTN) → TP2                                                                                                                    |
| `EPD_BUSY`, `EPD_CS`, `EPD_MOSI`, `EPD_SCK`, `EPD_DC`, `EPD_RST`                                                                | U1.17 (IO9), U1.18 (IO10), U1.19 (IO11), U1.20 (IO12), U1.21 (IO13), U1.22 (IO14) → J3                                                                   |
| `EPD_GDR`, `EPD_RESE`, `EPD_SW`, `EPD_CP`, `EPD_PREVGH`, `EPD_PREVGL`, `EPD_VSH1`, `EPD_VSH2`, `EPD_VSL`, `EPD_VCOM`, `EPD_VDD` | see *Display boost circuit*                                                                                                                              |
| `VBUS`                                                                                                                          | J1 A9/B9, U2.4 (VCC), U2.8 (CE)                                                                                                                          |
| `VBAT`                                                                                                                          | J2.1, U2.5 (BAT), U3.2 (CELL), U3.3 (VDD), U4.7/8 (VDD), U5.1 (VIN), U5.3 (EN)                                                                           |
| `+3V3`                                                                                                                          | U5.5 (VOUT), U1.2, MK1.5, J3.9/10 (VCI, VDDIO), L1.1, C4.1, C6.1                                                                                         |
| `GND`                                                                                                                           | U1.1/40/41, MK1.2 (LR)/3, U2.3/9, U3.1/4/9, U4.3/11/15/17, U5.2, J1 A12/B12/shell, J2.2, J3.8/17, R1.2, R2.2, D2.1, one pad of each of C2, C4–C7, C9–C12 |

Choices made here that a schematic has to confirm:

- The ten module GPIOs (four I2S, six display) are a provisional pick. Mic
  and amplifier share one clock pair.
- The display's supply (VCI, VDDIO, L1) is on the always-on `+3V3`; no
  load switch.
- The amplifier runs from `VBAT`, as `docs/DESIGN.md` sizes it (0.93 W at
  3.7 V); the regulator sits between `VBAT` and `+3V3`, enable tied to its
  input (always on).
- Q1 is wired 1 = gate, 2 = source, 3 = drain, and the diodes pad 1 =
  cathode: the usual SC-70-3 MOSFET and SOD-123 assignments, not checked
  against the Vishay and onsemi datasheets.
- U3's pin numbers and J2's polarity are from memory, not from a library
  symbol or the cell's datasheet. The cell's lead polarity is not
  documented by its seller either.
- Left without a net: the switches, J1's CC pins, U1's other GPIOs, U2
  PROG/TEMP/status, U3 I2C/alert, U4 gain and shutdown, J3 pads 6, 18, 19,
  21, 24.

## DRC — actual output

`kicad-cli pcb drc --severity-all`, KiCad 10.0.6, default board constraints
(no project file), machine locale French. Header and footer verbatim:

```
** Found 33 DRC violations **
** Found 84 unconnected pads **
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
     Rule: configuration des contraintes de la sérigraphie; warning — Segment de U1 sur F.Silkscreen (2), Segment de D3 sur F.Silkscreen (2)
 1 [lib_footprint_mismatch]: L'empreinte 'ESP32-S3-WROOM-1' ne correspond pas à la copie en librairie 'RF_Module'
     Local override; warning — Empreinte U1
```

The 84 unconnected items, all one message, counted by net:

```
84 [unconnected_items]: Missing connection between items
     GND 35, +3V3 7, VBAT 7, VBUS 3, EPD_SW 3, I2S_BCLK 2, I2S_WS 2, EPD_GDR 2, EPD_RESE 2, EPD_CP 2,
     EPD_PREVGH 2, EPD_PREVGL 2, I2S_DOUT 1, I2S_DIN 1, SPK_P 1, SPK_N 1, EPD_BUSY 1, EPD_CS 1,
     EPD_MOSI 1, EPD_SCK 1, EPD_DC 1, EPD_RST 1, EPD_VCOM 1, EPD_VSL 1, EPD_VSH1 1, EPD_VSH2 1, EPD_VDD 1
```

Reading:

- **`drill_out_of_range` ×12** — the module footprint's thermal vias under
  its ground pad are 0.2 mm; KiCad's default minimum is 0.3 mm. Real for
  any fab with a 0.3 mm minimum drill; a fab-capability decision, not a
  placement fault.
- **`hole_clearance` ×16** — inside the library's SKRTLAE010 footprint:
  its two locating holes sit 0.10 / 0.15 mm from its own pads, under the
  default 0.25 mm. These stay until the board constraints are set or the
  footprint is adjusted.
- **`silk_edge_clearance` ×4** — the module's silkscreen outline follows
  the antenna past the board edge (2); the outline of D3 ends on the FPC
  slot's edge (2). Cosmetic.
- **`lib_footprint_mismatch` ×1** — KiCad sees the embedded U1 as differing
  from its library copy. Cause not isolated; the other 31 footprints,
  embedded by the same code, are not flagged.
- **`unconnected_items` ×84** — every net, because nothing is routed.
- Absent from the report: `courtyards_overlap`, `items_not_allowed`
  (rule areas), `copper_edge_clearance`, `silk_over_copper`,
  `silk_overlap`.

## Margins

Courtyard-to-courtyard gaps, from the bounding boxes `gen_floorplan.py`
prints. The placement is at its limit: in the list below 0.00 means the
two courtyards share an edge.

| Pair                                                           | Gap (mm) |
| -------------------------------------------------------------- | -------- |
| D3 ↔ D1, D2, U4, J3, FPC slot                                  | 0.00     |
| U4 ↔ C3                                                        | 0.00     |
| J2 ↔ plug area                                                 | 0.00     |
| J3 ↔ R1                                                        | 0.01     |
| R1 ↔ R2; C-row ↔ U2; C-row ↔ plug area                         | 0.02     |
| Within the C-row                                               | 0.04     |
| J1 ↔ U2; J3 ↔ Q1; J3 ↔ U4; D1 ↔ D2; U4 ↔ D2                    | 0.05     |
| J3 ↔ C12; Q1 ↔ R1, R2; U3 ↔ C6, C7                             | 0.07     |
| J3 ↔ L1; J3 ↔ U2; L1 ↔ C4                                      | 0.10     |
| L1 ↔ R1, R2                                                    | 0.12     |
| U5 ↔ battery area                                              | 0.15     |
| U2 ↔ U3; U3 ↔ battery area                                     | 0.17     |
| J1 ↔ J3; J1 ↔ battery area                                     | 0.18     |
| MK1 ↔ FPC slot; MK1 ↔ board edge                               | 0.20     |
| J1 ↔ C2                                                        | 0.35     |
| Switch courtyard ↔ battery area; U1 body + 0.25 ↔ battery area | 0.50     |
| TP1 / TP2 ↔ FPC slot                                           | 0.52     |
| J2 ↔ J3                                                        | 0.55     |
| D1 ↔ post hole                                                 | 0.80     |
| L1 ↔ post hole                                                 | 0.90     |

These are courtyards, not copper: none of the pairs produces a clearance
error in DRC.

Why it is this tight: under the board the length is used end to end
(`models/case/README.md`, *Layout*), and between the speaker and the
battery there are 9.9 mm for everything taller than 4.1 mm. J1 (10.74 mm
of courtyard along X), J2 (9.2 mm) and U2 share that zone; J1 fits between
J3's courtyard and the battery area with 0.18 mm on each side. The boost
circuit is in the two 4.5–4.9 mm bands beside J3 and the 4.7 mm blocks
between J3 and the slot.

Area left for everything not yet placed, after removing courtyards, the
cut-outs, the rule areas, the module and the ledge strips: **341.2 mm²**,
of which 316.1 mm² is not above the speaker (component height limit over
the speaker: 4.1 mm; elsewhere 7.3 mm down to the case floor). Almost all
of it is beside the battery (two strips 3.7 mm wide, between and beyond
the switches), beside the module, and on the bottom rail — not next to
the ICs that need the passives.

## Blocking

1. **Support passives are not placed, and the room for them is not next
   to their ICs.** USB-C CC resistors, the TP4056's programming resistor
   and capacitors, decoupling for U1/U2/U3/U4/U5/MK1, the module's EN
   network, the fuel gauge's pull-ups, the amplifier's mode resistor:
   about twenty 0603 parts, listed as section C of `BOM_to_buy.md`. The
   bottom 30 mm has no free courtyard left; the 341 mm² is elsewhere.
   Either they go in 0402, or the case gets longer (each millimetre of
   `fpc_fold` adds 27 mm² in the tall zone), or the battery header
   changes.
2. **USB-C footprint is GCT's, the part is SHOU HAN's.** KiCad's library
   has no footprint for the TYPE-C 6P(073). J1 is the library's GCT
   USB4125. Against the SHOU HAN drawing the pad columns (±0.5, ±1.52,
   ±2.75), the shell slot span (8.64), the slot row spacing (3.80) and the
   distance from the mouth to the front slots (2.60) are the same; pad and
   slot sizes were not compared. The drawing asks for a 1.6 mm board.
3. **J3's contact side is undecided.** The panel specification does not
   say which face of the tail carries the contacts. The footprint is the
   same; the part differs (FH12A top contact / FH12 bottom contact).
4. **TP4056 footprint is a generic SOIC-8 with exposed pad** (2.41 × 3.3 mm
   pad); not checked against the TP4056 datasheet's land pattern.
5. **Battery protection** is assumed to be in the cell (the seller says
   so; not verified). If it is not, a protection IC and FET have no place
   on this board.

## Unvalidated

- Routability: 40 module pins to the bottom end must pass the battery
  zone, where the board is free of parts but only 2 layers, or the 3.7 mm
  side strips that also hold the switches and U5. The I2S lines, the six
  display lines and both supply rails make that trip.
- `EPD_SW` is a switching node about 20 mm long as placed. The reference
  layout keeps it short; whether the panel's supplies are clean enough
  like this is not known.
- The 1 µF / 25 V capacitors on the ±15–20 V rails are 0603 X5R; their
  capacitance under that bias is well below 1 µF. The specification asks
  for the value and the rating, nothing more.
- U5 is 19 mm from J2 and 17 mm from U1, between two buttons.
- No copper under the display has been considered for the panel or for
  the antenna (ground pour extent near x = 22 → 37).
- The slot is drawn with square corners; a routed slot has a radius.
- The amplifier is 12 mm from the speaker pads, across the slot's end, and
  65.4 mm from the antenna; its switching output has not been looked at
  beyond that.
- The 3.9 mm in front of J2 for the plug and lead bend is an estimate, not
  taken from the JST drawing.
- Switch pads on the long edges sit over the ledge cut-outs only;
  anything else placed at |y| > 13.7 lands on the ledge.

## Recommended tests

1. Draw the schematic before any routing, with the support passives, then
   run DRC with `--schematic-parity`; settle the GPIOs, the display supply
   switch and the regulator's enable there.
2. Decide Blocking 1 with the schematic's real part count in hand.
3. Compare J1 against the SHOU HAN drawing pad by pad; check Q1's and the
   diodes' pinouts against their datasheets.
4. Set the board constraints for the chosen fab (minimum drill, hole
   clearance) so the 28 footprint-internal errors are judged against real
   limits.
5. Print the SVG at 1:1 and lay the real parts on it, the JST plug
   included.
