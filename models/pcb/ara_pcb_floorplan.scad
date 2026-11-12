// ARA — PCB floor-plan prototype (not a schematic, not a routed board)
//
// This is a COMPONENT PLACEMENT STUDY matching the real case model in
// models/case/ARA_shell_v05.scad — same outline, same mounting hole
// positions, same component choices from docs/DESIGN.md. It exists to
// answer one question concretely: does everything fit, and how bad is
// the antenna keepout problem for a device this small? It is NOT a
// schematic, NOT routed copper, NOT DRC-checked. That needs a real EDA
// tool — see models/pcb/kicad/ for the actual KiCad file.
//
// Antenna keepout finding (2026-11-12): Espressif's own hardware
// design guidelines recommend >=15mm clearance in ALL directions
// around the ESP32-S3-WROOM-1's PCB antenna, measured inside the
// final housing — see
// https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html
// At this device's size (60mm shell), that's not achievable in every
// direction. The ~13.8mm figure quoted in earlier notes was computed
// at the OLD mcu_cy=10 — NOT re-verified since mcu_cy moved to 2.
// Treat that number as stale until recomputed.
//
// RECOVERY NOTE (2026-11-12): this file was found missing from disk
// (no trace, never committed to git) partway through this session.
// Rebuilt from the tracked edit history below — if anything here
// looks off versus what you remember, say so.

board_r   = 26;    // mm — matches case ARA_shell_v05.scad pcb_r
board_t   = 1.2;   // mm — matches case pcb_t
$fn = 96;
eps = 0.03;

// Mounting holes — EXACT match to case's PCB_posts() positions, so
// this board actually sits on those 4 standoffs, not a redrawn guess.
mount_holes = [[-19,-1], [19,-1], [-19,13], [19,13]];
mount_hole_d = 2.2;

// Closure-screw clearance notches — EXACT match to case's closure_angles/
// closure_r/closure_boss_d (ARA_shell_v05.scad). Found 2026-11-12: a plain
// circular outline let these clearance holes reach past this board's own
// radius. Fixed with edge notches. closure_r went 24 -> 18 -> back to 24
// (Lord, 2026-11-12): the case's real fix was clipping the boss to the
// curved exterior, not moving the screws — moving them broke alignment
// with other internal features and ate their space.
closure_angles = [70, 110, 225, 315];
closure_r = 24;
closure_notch_d = 10.1;  // closure_boss_d/2+0.85, radius form

/* [ESP32-S3-WROOM-1-N16R8] */
mcu_w = 25.5; // long axis, X — antenna end at +X
mcu_l = 18.0;
mcu_t = 3.1;
mcu_cx = 0;
mcu_cy = 2;   // moved from 10 (Lord, 2026-11-12): at cy=10 the module's
              // 25.5mm width overlapped the top closure notches — checked
              // with shapely, not eyeballed. cy=2 sits in the middle of
              // the valid band (-4.0 to 7.9) at closure_r=24, clear of
              // every notch, the mount holes, and the mic.
antenna_margin = 3; // mm, keepout strip at the module's antenna end —
                     // real width TBD from the module's own reference
                     // layout; this is a placeholder gap, not a
                     // validated copper keepout dimension.

/* [USB-C — SHOU HAN TYPE-C 6P CB1.6(073), LCSC C2858274, final pick] */
usbc_w = 8.94; usbc_t = 3.16; usbc_depth = 6.8;
usbc_cx = 0; usbc_cy = -board_r + 1; // edge-mount, aligned with the
                                      // case's 6-o'clock USB-C cutout

/* [Mic — ICS-43434] */
mic_w = 3.5; mic_l = 2.65;
mic_cx = 0; mic_cy = 21; // moved clear of the MCU footprint (was
                          // board_r-10=16, overlapped it — caught by
                          // computing the overlap, not by eye). Still
                          // only ~0.15mm clear of the top closure
                          // notches at r=24 — tight, flagged, not fixed
                          // yet (Lord hasn't decided if that's OK).

/* [Charge IC — TP4056, SOIC-8, sketch placement] */
charge_w = 5; charge_l = 4;
charge_cx = 0; charge_cy = -18;   // moved again (Lord, 2026-11-12): good
                                    // instinct — TP4056 close to the
                                    // USB-C input keeps the high-current
                                    // charge path short. Checked clear of
                                    // U1/U4/mic/notches/mount holes; only
                                    // 0.6mm from the USB-C footprint and
                                    // 7.5mm from U4.

/* [Fuel gauge — MAX17048G+T10, sketch placement] */
gauge_w = 3; gauge_l = 3;
gauge_cx = 10; gauge_cy = -10;   // moved from 14,-10 — same joint check
                                   // as the charge IC above.

module board_outline() {
    difference() {
        linear_extrude(height = board_t) circle(r = board_r);
        for (p = mount_holes)
            translate([p[0], p[1], -eps])
                cylinder(d = mount_hole_d, h = board_t + 2 * eps);
        for (a = closure_angles)
            translate([closure_r*cos(a), closure_r*sin(a), -eps])
                cylinder(d = closure_notch_d, h = board_t + 2 * eps);
    }
}

module mcu_footprint() {
    color([0.1, 0.1, 0.12])
        translate([mcu_cx, mcu_cy, board_t])
            cube([mcu_w, mcu_l, mcu_t], center = true);
    // antenna keepout strip at the +X end — drawn as a flat marker,
    // not a validated copper-clearance dimension (see header)
    color([0.9, 0.2, 0.2, 0.35])
        translate([mcu_cx + mcu_w/2, mcu_cy, board_t + eps])
            linear_extrude(height = 0.05)
                square([antenna_margin, mcu_l], center = true);
    // 15mm "ideal" clearance ring from the antenna tip, per Espressif —
    // drawn so the shortfall is visible, not hidden
    antenna_x = mcu_cx + mcu_w / 2;
    color([0.9, 0.2, 0.2, 0.12])
        translate([antenna_x, mcu_cy, board_t + eps])
            linear_extrude(height = 0.02)
                circle(r = 15);
}

module usbc_footprint() {
    color([0.2, 0.2, 0.22])
        translate([usbc_cx, usbc_cy, board_t + usbc_t/2])
            cube([usbc_w, usbc_depth, usbc_t], center = true);
}

module mic_footprint() {
    color([0.25, 0.45, 0.25])
        translate([mic_cx, mic_cy, board_t + 0.5])
            cube([mic_w, mic_l, 1], center = true);
}

module charge_ic_footprint() {
    color([0.3, 0.3, 0.33])
        translate([charge_cx, charge_cy, board_t + 0.75])
            cube([charge_w, charge_l, 1.5], center = true);
}

module fuel_gauge_footprint() {
    color([0.3, 0.3, 0.33])
        translate([gauge_cx, gauge_cy, board_t + 0.5])
            cube([gauge_w, gauge_l, 1], center = true);
}

module pcb_prototype() {
    board_outline();
    mcu_footprint();
    usbc_footprint();
    mic_footprint();
    charge_ic_footprint();
    fuel_gauge_footprint();
}

pcb_prototype();
