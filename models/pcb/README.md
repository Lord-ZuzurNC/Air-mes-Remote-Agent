# ARA — PCB status

**What this is: a component placement study, not a PCB.**
No schematic, no trace routing, no DRC-clean netlist yet. `ara_pcb_floorplan.scad`
only checks that the outline and the major components fit together without
overlapping — verified by overlap calculation, not by eye (two real errors were
caught this way: the USB-C cutout that looked like it "overflowed" the outline
— expected for an edge connector, not a bug; and the microphone that genuinely
overlapped the ESP32 — fixed).

## Current state: KiCad v0.1 floorplan

`kicad/kicad.kicad_pcb` carries the same layout into a real KiCad file you can
open — not a live API session. KiCad 10.0.x's IPC API is missing several
handlers needed for scripted/live editing (`GetOpenDocuments`, `GetItems`,
`RunAction` all return "no handler available"), confirmed on both the AppImage
and the native Debian package. The file was written directly and validated
with `kicad-cli pcb export svg` and `kicad-cli pcb drc`: 0 unconnected pads, 0
footprint errors; the only DRC flags are the expected edge-connector clearance
warnings for the USB-C connector.

No schematic, no netlist, no routing yet — footprints are self-contained
placeholders (silhouette + 2 dummy pads), not verified library parts.

**Open issue found while building this file — now resolved:** the case
model's closure-screw clearance holes (4×, Ø10.1mm at r=24mm) reached
~29mm from center — past both the 26mm PCB radius and the 28mm cavity
wall. Fixed by cutting 4 matching edge notches into the board outline
(computed with shapely: circle minus 4 clearance circles, re-exported as
an Edge.Cuts polygon) instead of leaving a plain circle. Decided by Lord,
2026-11-12.

## Contents

- `ara_pcb_floorplan.scad` / `.stl`: Ø52mm outline (matches
  `models/case/ARA_shell_v05.scad`), same 4 mounting holes, real footprints
  for the ESP32-S3-WROOM-1 and the chosen USB-C connector (`SHOU HAN TYPE-C
  6P CB1.6(073)`), and indicative (not schematic-driven) spots for the
  microphone, charge IC and battery gauge.
- `kicad/`: the same floorplan as an actual KiCad project (see above).

## Real problem found: antenna clearance

Espressif's hardware guidelines for the ESP32-S3-WROOM-1 recommend **at least
15mm clearance in every direction** around the PCB antenna, measured inside
the finished enclosure (not just on the board):
<https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html>

**On a 60mm device, that's not reachable in every direction — checked by
calculation, not assumed.** With the current placement (module oriented
antenna toward +X, chosen after comparing several options):
- Best direction (toward the shell, +X): **~13.8mm** — close to the target,
  not on it.
- Other directions (especially toward the battery): noticeably less.

The semi-transparent red circle in the render shows this 15mm clearance — it
visibly overshoots the board outline on the right side, an honest view of the
shortfall.

**This isn't something geometry alone fixes.** Espressif says so themselves:
even with careful placement, a PCB antenna needs validation on a real
prototype, not just by calculation. Expect reduced BLE range compared to a
larger device, and plan a real range test once the first electronic
prototype is assembled.
