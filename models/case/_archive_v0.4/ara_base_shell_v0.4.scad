/* Air-mes Remote Agent (ARA) — base round shell, v0.4

   Parametric model. Change the numbers in the sections below and
   re-render — nothing here needs a mouse.

   This is the FIXED MECHANICAL ENVELOPE other shells (carabiner loop,
   two-loop cord mount, the premium metal variants) are meant to attach
   to — see docs/DESIGN.md, "Enclosure".

   v0.4 changelog (Lord's review of v0.3):
     - Exterior profile changed from a flat-ended cylinder (circular on
       X, rectangular on Z) to a rounded/lens profile — circular on X,
       smoothly curved on Z, no right angle anywhere on the outside.
       Built with a 2D hull(sliver, sliver, circle) profile fed through
       rotate_extrude(), not minkowski() on the final solid — minkowski
       would round BOTH ends symmetrically, but the mating face between
       front_shell and back_shell has to stay flat for the screws/seam
       to work. Each piece only rounds its own OUTWARD-facing edge; the
       seam in the middle stays a plain cylindrical joint.
     - The back cavity gets a matching rounded profile too, offset
       inward by wall_thickness, instead of staying a flat-bottomed cut
       — otherwise the wall would thin out to near-zero right where the
       outer surface starts curving in (checked: at a naive constant-
       radius cavity cut, wall thickness at the rounded edge would drop
       from the nominal 2mm to ~0.5mm — caught by computing the profile
       radius at that height, not by eyeballing a render).
     - Screw bosses now start at z = back_fillet_r instead of z = 0: at
       z = 0 the main body's radius has shrunk to R - back_fillet_r for
       the rounded cap, which is narrower than the boss's own radius —
       a boss running all the way to z = 0 would float disconnected
       from the body for the first ~0.1mm. Starting it where the body
       is back to full radius avoids the problem instead of papering
       over it.
     - PCB rotated 90° ("laid down"): long axis (30mm) now along X
       instead of Y. Frees up room toward the mounting-tab side and
       improves screw-boss clearance (2.57mm vs 2.49mm) — modest, but
       free, and reduces how close the PCB's footprint reaches toward
       the now-rounded edge zones.

   v0.3 changelog (real component footprints replace every placeholder,
   verified by exhaustive overlap search in Python before being typed
   in here — not eyeballed):
     - Envelope grown 50->60mm diameter, 15->21mm thickness. Forced by
       real part sizes: the battery (EEMB LP702030, 20.5x32x7.3mm) and
       the MCU module (18x25.5x3.1mm) cannot both sit on one floor at
       50mm diameter (needs >=58mm just for those two) — confirmed by a
       500k-sample random-placement search finding zero valid layouts.
       Locked stack order (Lord, 2026-11-11): battery on the floor,
       PCB+MCU on standoffs above it, display on the front piece.
     - Speaker (Same Sky CDS-20144, oval 20x14x3.2mm) relocated off the
       front face entirely (v0.2's round pocket there overflowed the
       wall — see front_shell comments) to the back cavity, next to the
       battery on the same floor.
     - usbc_z keyed to the PCB's actual height, since the connector is
       soldered to it (not a fraction of back_depth, a leftover from
       the thinner v0.2 back piece).
     - Display switched to the square ET013TT1 (round panel went EOL —
       see docs/DESIGN.md). */

/* [Overall envelope] */
shell_diameter = 60; // mm, outer diameter
shell_thickness = 21; // mm, outer thickness
wall_thickness = 2; // mm, PLA/PETG wall
front_depth = 6; // mm, front piece (display + speaker port)
back_depth = shell_thickness - front_depth; // back piece (battery + PCB)

/* [Exterior rounding — "no right angles", Lord 2026-11-11]
   Each piece rounds only its own outward-facing edge; the mating seam
   stays flat. back_fillet_r is generous (the back piece is 15mm deep,
   plenty of room); front_fillet_r is kept small on purpose — the
   front piece is only 6mm deep and the screw clearance holes sit at
   r=27.5mm, close to the outer edge, so a bigger fillet there would
   push the flat zone below that radius (checked: front_fillet_r=2 ->
   flat zone down to r=28, still 0.5mm outside the screw holes). */
back_fillet_r = 6;
front_fillet_r = 2;

/* [Display — E Ink ET013TT1, fixed per docs/DESIGN.md]
   Square panel, not round (the round 1.1" panel named in earlier specs
   turned out EOL with no sourceable round replacement — see DESIGN.md). */
display_active_w = 23.30; // mm, active square area (the viewing window)
display_outer_w = 27.1; // mm, outer panel footprint — rests on the ledge
display_outer_l = 28.4;
display_pocket_depth = 1.2; // mm, recess depth from the OUTER face

/* [Speaker port — front face, "12 o'clock". The real driver (below)
   lives in the back cavity; this is just the acoustic opening. */
speaker_port_d = 5;
speaker_hole_d = 0.8;
speaker_hole_ring = 1.5;
speaker_wall_h = 2;
speaker_r = 20; // mm, radial placement from centre

/* [Mic — front face, "6 o'clock", opposite the speaker port] */
mic_hole_d = 1.5;

/* [Buttons — 2 left + 2 right, side by side along the curve] */
button_hole_d = 4;
button_z = back_depth * 0.5; /* > back_fillet_r, stays in
                                                the straight cylindrical
                                                band, unaffected by the
                                                rounded bottom */
button_angular_offset = 26;

/* [Battery — EEMB LP702030, 3.7V 350mAh, JST-PH, fixed per docs/DESIGN.md]
   Real dimensions from EEMB's own listing (20.5 x 32.0 x 7.3mm), laid
   on its SHORT axis (Lord, 2026-11-11): matches the PCB's own
   orientation (also laid down, see below) instead of being rotated
   90° from it. Fixes two problems at once — checked by computing both,
   not assumed: (1) the battery no longer sticks ~7.5mm past the PCB's
   footprint on each end (it did, when the two were cross-wise); the
   PCB now fully covers the battery with ~1mm margin all round. (2) the
   speaker gets real margin to the cavity wall (was 1.07mm, now 4.74mm)
   because the battery's footprint no longer reaches as far down. */
battery_w = 32.0; // mm, now the WIDE axis (X) — was the long axis
battery_l = 20.5; // mm, now the SHORT axis (Y)
battery_t = 7.3; // mm, thick
battery_center_x = 0;
battery_center_y = 6;
battery_fence_pad = 1; /* mm, locating-lip padding around the battery
                             footprint — kept to 1mm (not wall_thickness,
                             2mm) specifically because the battery is
                             now wider: at 2mm padding the fence clips
                             the screw bosses (-0.6mm clearance, checked
                             by computing it, not caught by eye); 1mm
                             keeps 0.79mm clearance instead. */
battery_fence_h = 2; /* mm, short locating lip — NOT a full
                            enclosure; the PCB above and the standoffs
                            around it are what actually hold it in. */

/* [PCB + MCU — sized to the MCU, not the battery; laid down 90°
   (Lord, 2026-11-11) so the long axis runs along X, not Y.
   ESP32-S3-WROOM-1-N16R8: 18 x 25.5 x 3.1mm, soldered on the PCB's
   top face (the face toward the front/display). */
mcu_w = 25.5; // mm, long axis now along X (was 18 along X in v0.3)
mcu_l = 18;
mcu_t = 3.1;
pcb_w = 30; // mm, long axis along X, matching the MCU's rotation
pcb_l = 22;
pcb_t = 1.2;
standoff_d = 4;
standoff_inset = 2.5; /* mm, standoffs sit inset from the PCB corners,
                        like a real board's mounting holes. */
standoff_clearance = 0.4; // mm, tolerance over the battery's real thickness
standoff_h = battery_t + standoff_clearance;

/* [USB-C — back piece only] */
usbc_width = 9.5;
usbc_height = 3.6;
// Keyed to the PCB's real height — the connector is soldered to it.
usbc_z = wall_thickness + standoff_h + pcb_t / 2;

/* [Loop/accessory mounting interface — fixed] */
mount_hole_d = 2.2;
mount_hole_spacing = 6;
mount_tab_depth = 3;

/* [Front/back assembly screws — diagonal, clear of everything else] */
screw_count = 4; // positioned at 45/135/225/315°
screw_hole_d = 2.2;
screw_pilot_d = 1.6;
screw_boss_d = 5;
screw_r = shell_diameter / 2 - screw_boss_d / 2; // boss placement radius

/* [Speaker driver — Same Sky CDS-20144, oval 20x14x3.2mm, back cavity] */
speaker_drv_w = 20;
speaker_drv_l = 14;
speaker_drv_t = 3.2;
speaker_drv_x = 0;
speaker_drv_y = -14; /* mm, moved up from -18 — the battery's rotation
                        freed this room (see battery comment above) */

$fn = 48;

/* 2D profile (radius, height) for a solid-of-revolution body that is
   FLAT/SHARP at z=H and ROUNDED (quarter-circle, radius fillet_r) at
   z=0. rotate_extrude() turns this into the lens/egg-style exterior. */
module rounded_profile(R, H, fillet_r) {
  hull() {
    translate([0, H - 0.001]) square([R, 0.001]);
    translate([0, 0]) square([max(R - fillet_r, 0.001), 0.001]);
    translate([R - fillet_r, fillet_r]) circle(r=fillet_r, $fn=64);
  }
}

module back_shell() {
  difference() {
    union() {
      /* outer body: flat/sharp at the TOP (mating face, z=back_depth),
               rounded at the BOTTOM (outward face, z=0) */
      rotate_extrude($fn=96)
        rounded_profile(shell_diameter / 2, back_depth, back_fillet_r);

      /* screw bosses — start at z=back_fillet_r, not z=0: below
               that height the main body has already narrowed for the
               rounded cap, so a boss reaching all the way to the floor
               would hang disconnected from the body for a sliver near
               the bottom (checked: the body doesn't reach the boss's
               own radius until ~0.08mm above z=0 — not worth the risk) */
      for (a = [45, 135, 225, 315])
        rotate([0, 0, a])
          translate([screw_r, 0, back_fillet_r])
            cylinder(d=screw_boss_d, h=back_depth - back_fillet_r);
    }

    /* inner cavity — same rounded-profile family, offset inward by
           wall_thickness (same fillet center, radius reduced by the
           wall thickness) so the wall stays a constant ~2mm all the
           way around the rounded bottom instead of thinning out there */
    translate([0, 0, wall_thickness])
      rotate_extrude($fn=96)
        rounded_profile(
          shell_diameter / 2 - wall_thickness,
          back_depth, // tall enough to stay open at the top
          max(back_fillet_r - wall_thickness, 0.1)
        );

    for (a = [45, 135, 225, 315])
      rotate([0, 0, a])
        translate([screw_r, 0, -1])
          cylinder(d=screw_pilot_d, h=back_depth + 2);

    translate([-usbc_width / 2, -shell_diameter / 2 - 1, usbc_z - usbc_height / 2])
      cube([usbc_width, wall_thickness + 2, usbc_height]);

    for (side = [0, 180])
      for (off = [-button_angular_offset, button_angular_offset])
        rotate([0, 0, side + off])
          translate([shell_diameter / 2 - wall_thickness - 1, 0, button_z])
            rotate([0, 90, 0])
              cylinder(d=button_hole_d, h=wall_thickness + 2);

    for (x = [-mount_hole_spacing / 2, mount_hole_spacing / 2])
      translate([x, shell_diameter / 2 - mount_tab_depth, back_depth - 2])
        rotate([90, 0, 0])
          cylinder(d=mount_hole_d, h=mount_tab_depth + 2);
  }

  /* battery locating lip — short fence, real footprint (32x20.5,
       laid on its short axis). Padding is 1mm, not wall_thickness,
       specifically because 2mm padding here clips the screw bosses. */
  translate([battery_center_x, battery_center_y, wall_thickness])
    difference() {
      cube([battery_w + 2 * battery_fence_pad, battery_l + 2 * battery_fence_pad, battery_fence_h], center=true);
      cube([battery_w, battery_l, battery_fence_h + 2], center=true);
    }

  // PCB standoffs — sized/placed for the real MCU-sized, laid-down PCB
  for (x = [-pcb_w / 2 + standoff_inset, pcb_w / 2 - standoff_inset])
    for (y = [battery_center_y - pcb_l / 2 + standoff_inset, battery_center_y + pcb_l / 2 - standoff_inset])
      translate([x, y, wall_thickness])
        difference() {
          cylinder(d=standoff_d, h=standoff_h);
          translate([0, 0, -1])
            cylinder(d=screw_pilot_d, h=standoff_h + 2);
        }

  /* speaker driver bay floor marker — low lip just to locate the
       driver on the floor */
  translate([speaker_drv_x, speaker_drv_y, wall_thickness])
    difference() {
      cube([speaker_drv_w + 2 * wall_thickness, speaker_drv_l + 2 * wall_thickness, 1.5], center=true);
      cube([speaker_drv_w, speaker_drv_l, 3], center=true);
    }
}

/* Reference-only ghost volumes for the real components, so the fit can
   be checked by eye against the actual cavity. Call separately from
   the printable export — these are not part of the printed shell. */
module components_reference() {
  color("DarkGreen")
    translate([battery_center_x, battery_center_y, wall_thickness])
      cube([battery_w, battery_l, battery_t], center=true);

  color("SaddleBrown")
    translate([0, battery_center_y, wall_thickness + standoff_h])
      cube([pcb_w, pcb_l, pcb_t], center=true);

  color("DimGray")
    translate([0, battery_center_y, wall_thickness + standoff_h + pcb_t])
      cube([mcu_w, mcu_l, mcu_t], center=true);

  color("SteelBlue")
    translate([speaker_drv_x, speaker_drv_y, wall_thickness + speaker_drv_t / 2])
      cube([speaker_drv_w, speaker_drv_l, speaker_drv_t], center=true);
}

module front_shell() {
  difference() {
    /* outer body: flat/sharp at the BOTTOM (mating face, z=0),
           rounded at the TOP (outward/display face, z=front_depth) —
           same profile as back_shell, mirrored and shifted to flip
           which end is rounded */
    translate([0, 0, front_depth])
      mirror([0, 0, 1])
        rotate_extrude($fn=96)
          rounded_profile(shell_diameter / 2, front_depth, front_fillet_r);

    // display pocket — square, not round (ET013TT1)
    translate([-display_outer_w / 2, -display_outer_l / 2, front_depth - display_pocket_depth])
      cube([display_outer_w, display_outer_l, display_pocket_depth + 1]);

    /* display window — narrower, continues through to the inner
           face. What's left between this and the pocket IS the ledge. */
    translate([-display_active_w / 2, -display_active_w / 2, -1])
      cube([display_active_w, display_active_w, front_depth + 2]);

    // FPC channel, clear of the speaker (90°) and mic (270°)
    translate([display_active_w / 2 - 1, -3, -1])
      cube([(display_outer_w - display_active_w) / 2 + 2, 6, front_depth + 2]);

    // speaker acoustic port
    rotate([0, 0, 90])
      translate([speaker_r, 0, -1])
        cylinder(d=speaker_port_d, h=front_depth - speaker_wall_h + 1);

    rotate([0, 0, 90])
      translate([speaker_r, 0, front_depth - speaker_wall_h])for (a = [0:60:300])
        rotate([0, 0, a])
          translate([speaker_hole_ring, 0, 0])
            cylinder(d=speaker_hole_d, h=speaker_wall_h + 2);

    // mic acoustic port, "6 o'clock", opposite the speaker port
    rotate([0, 0, 270])
      translate([speaker_r, 0, -1])
        cylinder(d=mic_hole_d, h=front_depth + 2);

    /* assembly screw clearance holes, same diagonal angles/radius
           as the back shell's bosses */
    for (a = [45, 135, 225, 315])
      rotate([0, 0, a])
        translate([screw_r, 0, -1])
          cylinder(d=screw_hole_d, h=front_depth + 2);
  }
}

/* [Toggle] */
show_component_ghosts = false; /* true = overlay the reference boxes for
                                  a fit check; leave false for the
                                  actual printable export. */

// Laid out side by side for preview/printing — not assembled.
translate([-shell_diameter / 2 - 5, 0, 0]) front_shell();
translate([shell_diameter / 2 + 5, 0, 0]) {
  back_shell();
  if (show_component_ghosts) components_reference();
}
