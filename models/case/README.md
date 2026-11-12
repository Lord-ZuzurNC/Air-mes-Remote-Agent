# ARA — case proposal v0.5

**Status: parametric mechanical study, not a manufacturing validation.**

The model was rebuilt from the `DESIGN.md` spec and the original v0.4
`ara_base_shell.scad` model. It doesn't change the electronic component
choices; it changes how they're arranged.

## Composition

- `ARA_shell_v05.scad`: full OpenSCAD source. `part` parameter:
  `assembled`, `exploded`, `print`, `front`, `back`, `retainer`, `button`,
  `pcb`, `rear_view`. `show_components` displays the electronic mockups
  without baking them into the STLs.
- `ara_v05_front.stl`: front half-shell (screen and microphone, screw heads).
  Printed flipped (outward face down) so the display ledge doesn't need
  support material.
- `ara_v05_back.stl`: rear half-shell (battery, speaker, PCB posts, USB-C,
  buttons, accessory points).
- `ara_v05_retainer.stl`: screen retaining frame, screwed from the inside.
- `ara_v05_button.stl`: **study plunger** — 4 copies, laid out in a 2x2
  square, each standing upright (no support needed); to be resized once the
  real switches are chosen.
- `ara_v05_pcb.stl`: **clearance volume**, not an electronic circuit or
  Gerber files.
- PNG images: illustrative OpenSCAD renders.

## Geometry

- Shell footprint **Ø60mm × 22mm**, excluding buttons. The original was
  21mm thick.
- Rear half-shell: 16mm, front half-shell: 6mm.
- Flat mid-seam + three centering pins, four closure screws from the front.
- `ET013TT1` screen (27.1 × 28.4 × 0.4mm) inserted from the inside and held
  by a separate part, no permanent gluing.
- `LP702030` battery (study envelope 32 × 20.5 × 7.3mm) at the bottom: short
  guides with 0.55mm nominal clearance on the sides, cable exit upward.
- PCB **circular, notched at the fixings**, Ø52mm, mounted on 4 standoffs
  outside the battery volume. The ESP32 is represented as 25.5 × 18 × 3.1mm
  on its top face.
- USB-C planned at 6 o'clock, connected to the lower edge of the free-form
  PCB — **not** the small rectangular PCB from v0.4.
- 20 × 14 × 3.2mm speaker at the rear, grille straight into the back,
  with a spot for an acoustic gasket.
- Four radial plungers spread over two sides; still **indicative** volumes.
- Two rear mounting points 6mm apart for an optional external accessory
  (lanyard, cord, etc.).

## Planned assembly order

1. Install the speaker, gasket on the grille side, into the rear floor.
2. Place the battery, route the wires to the JST-PH; avoid any pressure on
   its pouch.
3. Mount the four plungers from the inside before the PCB.
4. Fix the PCB on the four standoffs; check the USB-C reaches the cutout
   and the buttons reach the contacts.
5. Install the E-Ink screen from the inside of the front face, connect the
   FPC ribbon carefully, position the retaining frame with light pressure
   on the **inactive border**.
6. Present the front face on the three pins and screw the four closure
   points.

## To validate before a working electronic prototype

**Blocking**

- **Real PCB layout**: the holes, edge-mounted buttons, USB-C, power
  components and the FPC connector need to be designed in electronic CAD
  and carried over to the mechanical model. A v0.1 floorplan now exists in
  `models/pcb/` (placement only, no schematic/routing yet) — see
  `models/pcb/README.md`, including an open conflict between the
  closure-screw clearance holes and the PCB outline that isn't resolved yet.
- **ESP32-S3 antenna**: its RF clearance zone and the placement of the
  speaker/battery metal are mandatory checks; the PCB disc shown doesn't
  include the copper keep-out yet and the module hasn't been repositioned
  to optimize it. Confirmed by calculation: best case ~13.8mm clearance
  against a 15mm target — see `models/pcb/README.md`.
- **LiPo**: confirm the real size and cable/JST-PH slack; the guide
  clearance must be confirmed against worst-case tolerances, with no
  constraint or compression on the battery.
- **E-Ink screen**: full FPC ribbon drawings, active face, allowed bend
  radius, optional protective glass clearance, and a non-damaging
  retention method. The current proposal isn't sealed against water/dust.
- **Screws**: choose the screws and check real pilot bores for the
  material; the M2 nominal values used are illustrative.

**Recommended tests**

- Print first in low-cost PLA to check component fit; choose PETG or
  another suitable material afterward.
- Test speaker intelligibility when the case is set down or worn: a rear
  grille can be partially blocked.
- Check how the Ø1.45mm grille holes come out depending on nozzle/layer
  height.
- Check actuation of the four plungers, switch forces, and the absence of
  accidental activation.
- Check thermal output and dissipation of the battery charger and
  amplifier.

## Validation done so far

OpenSCAD computed a **closed (watertight)** STL mesh for each separate part
(`front`, `back`, `retainer`, `button`, `pcb`); this proves topological
consistency of the exported surfaces, **not** the absence of interference
in a real physical assembly.

**Intellectual property**: this model proposal is distributed under
CC BY-SA 4.0 so it can be modified and shared in the spirit of the project.
This document isn't a check of the software-component obligations
mentioned in `DESIGN.md`.
