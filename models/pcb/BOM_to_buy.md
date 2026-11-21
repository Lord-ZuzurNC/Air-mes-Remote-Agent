# ARA — shopping list for one prototype unit

**Status: every part in `docs/DESIGN.md` and in the floorplan has an order
line. Order codes were read from the distributors' own pages on
2026-11-21, except where a line says otherwise. Two lines need a
decision or a check before ordering — see **Blocking**.**

Quantities are what **one unit** uses. Where the distributor sells a
minimum lot, that is in the last column; nothing here is padded for
spares. Prices are the lowest break seen that day, in USD at LCSC and
DigiKey, and are only there to size the order.

Sourcing rule: LCSC first, DigiKey second, Amazon for the battery only.
Two lines fall outside it because neither distributor carries the part:
the display (Good Display's own shop) and the board itself (a PCB fab).

## A. LCSC — one order

| #   | Ref                               | Part                                  | Manufacturer part number                  | Package                                                   | Qty | LCSC     | Price, lot                             |
| --- | --------------------------------- | ------------------------------------- | ----------------------------------------- | --------------------------------------------------------- | --- | -------- | -------------------------------------- |
| A1  | U1                                | MCU module                            | `ESP32-S3-WROOM-1-N16R8` (Espressif)      | module 18 × 25.5 mm, PCB antenna                          | 1   | C2913202 | $5.31 — **0 in stock**, see Blocking 1 |
| A2  | U2                                | Li-ion charger                        | `TP4056` (TPOWER)                         | ESOP-8                                                    | 1   | C382139  | $0.12, lot of 5                        |
| A3  | U3                                | Fuel gauge                            | `MAX17048G+T10` (Analog Devices / Maxim)  | TDFN-8, 2 × 2 mm                                          | 1   | C2682616 | $1.96                                  |
| A4  | U4                                | I2S amplifier                         | `MAX98357AETE+T` (Analog Devices / Maxim) | TQFN-16, 3 × 3 mm                                         | 1   | C910544  | $1.26                                  |
| A5  | U5                                | 3.3 V regulator                       | `AP2112K-3.3TRG1` (Diodes Inc.)           | SOT-25 (SOT-23-5)                                         | 1   | C51118   | $0.17, lot of 5                        |
| A6  | J1                                | USB-C receptacle, 6-pin               | `TYPE-C 6P(073)` (SHOU HAN)               | SMT, on-board, 4 shell legs                               | 1   | C668623  | $0.04, lot of 10                       |
| A7  | J2                                | Battery header                        | `S2B-PH-SM4-TB(LF)(SN)` (JST)             | PH 2.0 mm, 2-pin, side entry, SMT                         | 1   | C295747  | $0.21, lot of 5                        |
| A8  | J3                                | Display FPC connector, top contact    | `FH12A-24S-0.5SH(55)` (Hirose)            | 24-pin, 0.5 mm, horizontal SMT, 2.0 mm high               | 1   | C506794  | $0.83                                  |
| A9  | J3                                | Display FPC connector, bottom contact | `FH12-24S-0.5SH(55)` (Hirose)             | same footprint as A8                                      | 1   | C202112  | $0.52                                  |
| A10 | SW1–SW4                           | Side-push tactile switch              | `SKRTLAE010` (Alps Alpine)                | 4.5 × 3.4 × 1.65 mm SMT                                   | 4   | C110293  | $0.15, lot of 5                        |
| A11 | L1                                | Boost inductor 47 µH                  | `CKCS4030-47uH/M` (CENKER)                | 4.0 × 4.0 × 3.0 mm; Isat 0.95 A, Irms 0.72 A, DCR 0.445 Ω | 1   | C354593  | $0.05, lot of 10                       |
| A12 | Q1                                | Boost MOSFET, N-channel               | `SI1308EDL-T1-GE3` (Vishay)               | SC-70-3 (SOT-323)                                         | 1   | C469327  | $0.26, lot of 5                        |
| A13 | D1–D3                             | Schottky 30 V / 0.5 A                 | `MBR0530T1G` (onsemi)                     | SOD-123                                                   | 3   | C82046   | $0.06, lot of 10                       |
| A14 | R1                                | Resistor 1 MΩ 1 %                     | `0603WAF1004T5E` (UNI-ROYAL)              | 0603                                                      | 1   | C22935   | lot of 100                             |
| A15 | R2                                | Resistor 2.2 Ω 1 %                    | `RC0603FR-072R2L` (Yageo)                 | 0603                                                      | 1   | C112307  | lot of 100                             |
| A16 | C3, C4                            | Capacitor 4.7 µF / 25 V X5R           | `CL10A475KA8NQNC` (Samsung)               | 0603                                                      | 2   | C69335   | $0.04, lot of 10                       |
| A17 | C2, C5, C6, C7, C9, C10, C11, C12 | Capacitor 1 µF / 25 V X5R             | `CL10A105KA8NNNC` (Samsung)               | 0603                                                      | 8   | C5673    | $0.03, lot of 50                       |

A8 and A9 are one position on the board: buy both, fit the one that
matches the panel (`models/pcb/README.md`, Blocking 3).

## B. DigiKey — one order

| #   | Ref | Part                                                              | Manufacturer part number                     | Package                                  | Qty | DigiKey        | Price, lot                                   |
| --- | --- | ----------------------------------------------------------------- | -------------------------------------------- | ---------------------------------------- | --- | -------------- | -------------------------------------------- |
| B1  | MK1 | I2S MEMS microphone                                               | `ICS-43434` (TDK InvenSense)                 | LGA-6, 3.5 × 2.65 × 0.98 mm, bottom port | 1   | 1428-1066-1-ND | $3.92 — marked **obsolete**, 52 007 in stock |
| B2  | —   | Speaker 20 × 14 mm, 4 Ω, 1 W                                      | `CDS-20144` (Same Sky, formerly CUI Devices) | oval frame, 3.2 mm, solder pads          | 1   | 102-3542-ND    | $4.88                                        |
| B3  | —   | Case screw, M2 × 0.4 × 8 mm, pan head Phillips, zinc-plated steel | `MPMS 002 0008 PH` (B&F Fastener Supply)     | head Ø3.85 × 1.52 mm                     | 2   | H739-ND        | lowest break seen is 100 pieces              |

## C. Support passives — LCSC, same order as A

Not in `docs/DESIGN.md` and not placed on the floorplan. These are what
the ICs' typical application circuits need; **values are provisional
until there is a schematic** (`models/pcb/README.md`, Blocking 1). All
0603, all with order codes read from LCSC.

| #   | For                                                                    | Part              | Manufacturer part number     | Qty | LCSC   | Lot                        |
| --- | ---------------------------------------------------------------------- | ----------------- | ---------------------------- | --- | ------ | -------------------------- |
| C1  | J1 CC1, CC2 pull-downs (without them a USB-C source supplies no power) | 5.1 kΩ 1 %        | `0603WAF5101T5E` (UNI-ROYAL) | 2   | C23186 | 100                        |
| C2  | U2 PROG: 1200 / 6800 ≈ 0.18 A, half the cell's capacity per hour       | 6.8 kΩ 1 %        | `0603WAF6801T5E` (UNI-ROYAL) | 1   | C23212 | 100                        |
| C3  | U1 EN pull-up                                                          | 10 kΩ 1 %         | `0603WAF1002T5E` (UNI-ROYAL) | 1   | C25804 | 100                        |
| C4  | U3 I2C pull-ups                                                        | 4.7 kΩ 1 %        | `0603WAF4701T5E` (UNI-ROYAL) | 2   | C23162 | 100                        |
| C5  | U4 SD_MODE pull-up (channel select)                                    | 100 kΩ 1 %        | `0603WAF1003T5E` (UNI-ROYAL) | 1   | C25803 | 100                        |
| C6  | U2 input and battery side, U1 supply, U4 supply                        | 10 µF / 10 V X5R  | `CL10A106KP8NNNC` (Samsung)  | 4   | C19702 | 20                         |
| C7  | U1, U3, U4, MK1 decoupling                                             | 100 nF / 50 V X7R | `CL10B104KB8NNNC` (Samsung)  | 4   | C1591  | 100                        |
| C8  | U5 input and output, U1 EN delay                                       | 1 µF / 25 V X5R   | `CL10A105KA8NNNC` (Samsung)  | 3   | C5673  | covered by A17's lot of 50 |

## D. Elsewhere

| #   | Part                                                                                                                        | Reference                                                                     | Qty             | Where                                                                                                                                                                    |
| --- | --------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| D1  | E-paper panel 2.13", 250 × 122, SSD1680, 24-pin FPC — the bare panel, not the `-FT11` touch/front-light HAT and not `-FL01` | `GDEY0213B74` (Good Display)                                                  | 1               | Good Display's shop, linked from its product page: buy-lcd.com. Not at LCSC; DigiKey not checked. Price not read (shop page not reachable); about $5 in a search result. |
| D2  | Li-Po cell 3.7 V 350 mAh, 7 × 20 × 30 mm nominal, with protection, JST-PH 2.0 mm plug                                       | `LP702030` (EEMB)                                                             | 1               | Amazon.fr, ASIN B095W1XHVY, about €10.99. Listing seen in a search result only; see Blocking 2.                                                                          |
| D3  | Bare PCB, 2 layers, 1.0 mm, 79.95 × 29.3 mm, one internal slot 2.7 × 14 mm, two Ø4.4 holes                                  | `models/pcb/kicad/ara_floorplan.kicad_pcb` — **not routed, do not order yet** | 1 (fabs sell 5) | any prototype fab                                                                                                                                                        |
| D4  | Bottom shell, PETG, 13.9 g                                                                                                  | `models/case/ara_bottom_shell.stl`                                            | 1               | printed                                                                                                                                                                  |
| D5  | Bezel, PETG, 2.7 g                                                                                                          | `models/case/ara_bezel.stl`                                                   | 1               | printed                                                                                                                                                                  |

## Not on the list because it is not specified yet

- **Foam pad** between PCB and panel: 0.4 mm compressed, about 59 × 29 mm;
  material and free thickness not chosen (`models/case/README.md`).
- **Speaker leads**: two wires about 15 mm, from the speaker's solder pads
  to TP1/TP2. Any 28–30 AWG wire.
- **Button caps**: not designed (`models/case/README.md`, Blocking 3).
- **Mic gasket**, **speaker gasket**: not designed.

## Blocking

1. **The module is out of stock at both distributors** (LCSC C2913202:
   0; DigiKey 5407-ESP32-S3-WROOM-1-N16R8CT-ND: 0, 650 on back order,
   8 weeks quoted, $6.76). Order it on back order from either, or from
   another distributor; the part number must stay exactly `-N16R8` (not
   `-1U`, not `N8R8`).
2. **Battery: measure before plugging.** The Amazon page itself could not
   be opened; its search result gives 7.3 × 20.5 × 32 mm, "with JST
   connector" and built-in protection, and EEMB's own page gives the same
   20.5 × 32.0 × 7.3 mm for the cell. No EEMB document giving the plug
   type or the wire order was found. Not confirmed: that the plug is
   JST-PH 2.0 mm, and which wire is positive — the listing itself warns
   the pinout is not universal. The board's J2 polarity is not confirmed
   either. Check both with a multimeter; swap the crimps in the plug if
   they disagree.

## Codes not to order

Three LCSC codes look right and are not; the tables above have the right
ones.

| Part            | Not this                         | This                      | Why                                                                                                                                      |
| --------------- | -------------------------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| AP2112K-3.3TRG1 | C23380830                        | C51118                    | the first is a TECH PUBLIC part sold under the same number; the second is Diodes Inc.                                                    |
| Si1308EDL       | C7603347                         | C469327                   | same: TECH PUBLIC versus Vishay                                                                                                          |
| USB-C           | C2858274, `TYPE-C 6P CB1.6(073)` | C668623, `TYPE-C 6P(073)` | different part on purpose: the `CB1.6` is sunk 1.6 mm into the board and does not fit under the panel (`models/case/README.md`, *USB-C*) |

The Sunlord SWPA4030S470MT, the obvious 47 µH / 4030 part, is not
orderable at LCSC; the Cenker part in A11 is, and KiCad's library has its
footprint. DigiKey equivalent if needed: Eaton `SDCL1V4030-470M-R`,
283-SDCL1V4030-470M-RCT-ND (4 × 4 × 3 mm, Isat 0.95 A).

DigiKey codes for the lines bought at LCSC, should a line be unavailable:
MAX17048G+T10 `MAX17048G+T10CT-ND`, MAX98357AETE+T `MAX98357AETE+TCT-ND`,
SKRTLAE010 `4809-SKRTLAE010CT-ND`, S2B-PH-SM4-TB `455-S2B-PH-SM4-TBCT-ND`,
FH12A-24S-0.5SH(55) `HFK124CT-ND`, FH12-24S-0.5SH(55) `HFJ124CT-ND`.

## How the codes were checked

- LCSC: the product-detail data behind each `lcsc.com/product-detail`
  page (code, manufacturer, part number, package, stock, minimum lot).
  C469327, C51118, C354593 and C112307 were read a second time the same
  day and matched. The UNI-ROYAL 2.2 Ω (C22939) is at zero stock at LCSC,
  hence the Yageo part for R2.
- DigiKey: the product pages, through a page-reading tool rather than as
  raw pages. H739-ND was matched to `MPMS 002 0008 PH` from DigiKey
  listings in a search result; its head size is the one DigiKey gives for
  the 5 mm screw of the same series (H738-ND).
- Not checked at all: prices and stock after 2026-11-21.
