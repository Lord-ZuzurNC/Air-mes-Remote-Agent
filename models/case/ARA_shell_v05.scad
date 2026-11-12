/*
 ARA / Air-mes Remote Agent — shell study v0.5 (concept, not production-ready)
 Author: OpenAI / 2026-11-11
 Units: millimetres. License: CC-BY-SA-4.0 (design proposal).

 CHANGES FROM v0.4
 - Two rounded shells remain circular, with the joint at z=16.
 - Screen inserted from INSIDE front shell; independent, removable retainer.
 - Speaker opens toward a rear grille (no imaginary acoustic path to front).
 - Four solid bosses survive the cavity boolean; screws enter from front.
 - Custom approximately circular PCB reference, with keep-outs at bosses.
 - Four side-button holes line up with PCB-rim button locations.
 - USB-C outlet at 6 o'clock aligns with the edge of the custom PCB.
 - Two optional accessory screw bosses access the rear face.
 - Battery, PCB and MCU are shown without Z-overlap in the assembly view.

 IMPORTANT: MCU antenna keep-out, real PCB layout/trace routing, the precise
 USB-C connector and switch actuator designs, screen FPC routing/bend radius,
 charging IC thermal and safety requirements, and acoustic validation remain
 to be engineered before a functional build.

 OpenSCAD CLI:
   openscad -o back.stl -D 'part="back"' ARA_shell_v05.scad
   openscad -o front.stl -D 'part="front"' ARA_shell_v05.scad
   openscad -o retainer.stl -D 'part="retainer"' ARA_shell_v05.scad
   openscad -o plunger.stl -D 'part="button"' ARA_shell_v05.scad
*/

/* [Output] */
part = "exploded"; // [exploded,assembled,print,front,back,retainer,button,pcb]
show_components = true;
show_annotations = true;

/* [Envelope] */
outer_d = 60;
back_h = 16;
front_h = 6;
wall = 2;
back_round = 6;
front_round = 2.2;
body_r = outer_d / 2;
inner_r = body_r - wall;

/* [Exact component nominal outlines from DESIGN.md / the initial CAD] */
battery_x = 32.0;
battery_y = 20.5;
battery_z = 7.3;
battery_y0 = 6.5;
battery_clearance = 0.40;
battery_fence_gap = 0.9;
battery_fence_clear = 0.55; // intentional gap around pouch; never clamp a LiPo cell
battery_fence_h = 2.3;

speaker_w = 20;
speaker_l = 14;
speaker_t = 3.2;
speaker_y0 = -12.5;

mcu_x = 25.5; // long axis X
mcu_y = 18;
mcu_z = 3.1;
mcu_y0 = battery_y0;

pcb_t = 1.2;
pcb_r = 26;
pcb_z0 = wall + battery_z + battery_clearance;
pcb_post_r = 2.3;
pcb_post_d_hole = 1.7;

/* [Closure screws] */
closure_angles = [70, 110, 225, 315];
closure_r = 24;
closure_boss_d = 8.4;
closure_pilot_d = 1.7;   // example for M2 self-tapping: validate against screw
closure_clear_d = 2.45;
head_counterbore_d = 4.3;
head_counterbore_depth = 1.5;

/* [Buttons] */
button_angles = [-26, 26, 154, 206];
button_z0 = 12.1;
button_hole_d = 3.5;
button_pin_d = 3.0;
button_lip_d = 5.1;

/* [USB-C]
   Final pick (Lord, 2026-11-11): SHOU HAN "TYPE-C 6P CB1.6(073)",
   LCSC C2858274. 6-pin (VBUS x2, GND x2, CC1, CC2) — deliberately NOT
   a full data connector: firmware OTA goes over BLE (DESIGN.md), so
   USB-C only ever needs to charge, and skipping D+/D- keeps the part
   simpler/cheaper. Real body: 8.94mm wide x 3.16mm tall, ~6.8mm deep
   (from its datasheet drawing, not estimated). Rated 5V/3A — plenty
   for charging this battery. */
usbc_w = 9.7;  // mm, cutout — already had margin over the real 8.94mm body
usbc_h = 3.8;  // mm, cutout — already had margin over the real 3.16mm body
// z position: the connector is a TOP-mount SMD part, sitting ON the
// PCB's top surface, not straddling its mid-thickness — its own
// centreline is pcb top + half its own body height, not pcb_z0+pcb_t/2
// (bug fixed 2026-11-11: that formula put the port ~2.2mm too low,
// found when the real connector height (3.16mm) was looked up instead
// of assumed).
usbc_body_h = 3.16;
usbc_z = pcb_z0 + pcb_t + usbc_body_h / 2;

/* [Display: Unisystem ET013TT1] */
display_x = 27.1;
display_y = 28.4;
display_t = 0.4;
display_tolerance = 0.8;
window_size = 23.1; // nominal active = 23.3; allow 0.1 mm lip per side
display_lip = 1.2;
display_seat_z = front_h - display_lip;

$fn = 40;
eps = 0.03;

assert(outer_d >= 58, "Check component layout for a smaller enclosure");
assert(pcb_z0 + pcb_t + mcu_z < back_h, "MCU breaches the rear-shell split plane");
assert(battery_fence_gap >= 0.5, "Battery locating lip too close to cell");

auto_bevel = 0.7;

module round_rect(w, h, r) {
    offset(r=r) square([w-2*r, h-2*r], center=true);
}

// Rounded on bottom and sharp on top, for seam alignment.
module profile_2d(R, H, round_r) {
    hull() {
        translate([0, H-0.002]) square([R, 0.002]);
        translate([0, 0]) square([R-round_r, 0.002]);
        translate([R-round_r, round_r]) circle(r=round_r, $fn=48);
    }
}

module exterior_back() {
    rotate_extrude($fn=96) profile_2d(body_r, back_h, back_round);
}
module back_void() {
    translate([0,0,wall])
        rotate_extrude($fn=96)
            profile_2d(inner_r, back_h, max(0.5, back_round-wall));
}
module exterior_front() {
    translate([0,0,front_h]) mirror([0,0,1])
        rotate_extrude($fn=96) profile_2d(body_r, front_h, front_round);
}

module at_polar(r, deg, z=0) {
    translate([r*cos(deg), r*sin(deg), z]) children();
}

module PCB_posts() {
    for (x=[-19,19], y=[-1,13])
        translate([x, y, wall])
            difference() {
                cylinder(d=2*pcb_post_r, h=pcb_z0-wall);
                translate([0,0,pcb_z0-wall-4.8])
                    cylinder(d=pcb_post_d_hole, h=5.0);
            }
}

module battery_fence() {
    // Four independent guide rails, no pressure applied to the pouch.
    // Leave the +Y end open to route the battery wires / JST-PH harness.
    for (sx=[-1,1])
        translate([sx*(battery_x/2+battery_fence_clear+battery_fence_gap/2),battery_y0,wall+battery_fence_h/2])
            cube([battery_fence_gap,battery_y+2*(battery_fence_clear+battery_fence_gap),battery_fence_h],center=true);
    translate([0,battery_y0-battery_y/2-battery_fence_clear-battery_fence_gap/2,wall+battery_fence_h/2])
        cube([battery_x+2*(battery_fence_clear+battery_fence_gap),battery_fence_gap,battery_fence_h],center=true);
    for (sx=[-1,1])
        translate([sx*(battery_x/4+2.6),battery_y0+battery_y/2+battery_fence_clear+battery_fence_gap/2,wall+battery_fence_h/2])
            cube([battery_x/4-3.5,battery_fence_gap,battery_fence_h],center=true);
}

module speaker_fence() {
    // Low locating rim; actual speaker must have a gasket against the grille.
    translate([0,speaker_y0,wall])
        linear_extrude(height=1.35)
            difference() {
                round_rect(speaker_w+1.3,speaker_l+1.3,2.6);
                round_rect(speaker_w+0.3,speaker_l+0.3,2.2);
            }
}

module accessory_bosses() {
    // Rear blind holes. Two small screws accept optional strap adapters.
    for (x=[-3,3])
        translate([x,21.5,wall]) cylinder(d=5.3,h=5.0);
}

module back_shell() {
    difference() {
        union() {
            difference() { exterior_back(); back_void(); }
            for (a=closure_angles)
                at_polar(closure_r,a,wall)
                    cylinder(d=closure_boss_d,h=back_h-wall);
            PCB_posts();
            battery_fence();
            speaker_fence();
            accessory_bosses();
            // Three small seam-registration pegs (not structural fasteners).
            for (a=[0,90,180])
                at_polar(27.5,a,back_h-2.0)
                    cylinder(d=2.5,h=3.2);
        }
        // Blind main pilots: leave bottom intact.
        for (a=closure_angles)
            at_polar(closure_r,a,back_h-7.5)
                cylinder(d=closure_pilot_d,h=8);
        // Side exits for plunger shafts; switches live on the PCB perimeter.
        for (a=button_angles)
            rotate([0,0,a])
                translate([25.8,0,button_z0])
                    rotate([0,90,0]) cylinder(d=button_hole_d,h=5.5);
        // USB-C is on the PCB's lower edge, at the SAME y-axis as the outlet.
        // Clearance is provisional until the exact connector footprint is chosen.
        translate([-usbc_w/2,-body_r-0.5,usbc_z-usbc_h/2])
            cube([usbc_w,8,usbc_h]);
        // Grille is DIRECTLY behind the driver, not across the enclosure.
        for (x=[-7.5:3:7.5], y=[-4.5:3:4.5])
            translate([x,speaker_y0+y,-0.5])
                cylinder(d=1.45,h=wall+1.0);
        // Rear mounting screws accessible from the outside, blind in bosses.
        for (x=[-3,3])
            translate([x,21.5,-0.5]) cylinder(d=1.65,h=7.0);
    }
}

module display_recess() {
    translate([0,0,-eps])
        linear_extrude(height=display_seat_z+eps)
            round_rect(display_x+display_tolerance,
                       display_y+display_tolerance,0.8);
}

module retainer_outline_2d() {
    union() {
        round_rect(30.0,31.4,1.2);
        for (x=[-17.3,17.3]) translate([x,0]) circle(d=7.0);
    }
}

module front_shell() {
    difference() {
        exterior_front();
        // Screen service access from the inside. No adhesive required to lock it.
        display_recess();
        // Shallow counter-pocket prevents the retainer's mounting ears from
        // colliding with the otherwise solid front lid.
        translate([0,0,-eps])
            linear_extrude(height=1.8+eps) retainer_outline_2d();
        // Viewing aperture opens into the ledge. E-ink sits BELOW front face.
        translate([0,0,-eps])
            linear_extrude(height=front_h+2*eps)
                round_rect(window_size,window_size,0.8);
        // Mic: dedicated front-facing bore, opposite the rear speaker cavity.
        translate([0,20,-eps]) cylinder(d=1.5,h=front_h+2*eps);
        // Main closure: clearance shaft and recess for a low-profile head.
        for (a=closure_angles) {
            at_polar(closure_r,a,-eps)
                cylinder(d=closure_clear_d,h=front_h+2*eps);
            at_polar(closure_r,a,front_h-head_counterbore_depth)
                cylinder(d=head_counterbore_d,h=head_counterbore_depth+eps);
        }
        // Three female locating holes for the rear-shell pegs.
        for (a=[0,90,180])
            at_polar(27.5,a,-eps)
                cylinder(d=3.0,h=1.6);
        // Pilot for the internal SCREEN retainer, from inner side only.
        for (x=[-17.3,17.3])
            translate([x,0,-eps]) cylinder(d=1.6,h=4.0);
    }
}

module retainer() {
    // Fits inside the square inner screen recess, supported by two ears.
    // 4 tall corner pads touch only the panel's inactive border.
    difference() {
        union() {
            linear_extrude(height=1.4)
                difference() {
                    retainer_outline_2d();
                    round_rect(24.1,24.1,0.8);
                }
            for (x=[-12.7,12.7],y=[-13.2,13.2])
                translate([x,y,1.4]) cylinder(d=2.0,h=2.7);
        }
        // Two screw passages.
        for (x=[-17.3,17.3])
            translate([x,0,-eps]) cylinder(d=2.2,h=1.5+2*eps);
        // Flex tail can run out through the top (+Y) of the retaining rim.
        translate([-3.4,12.0,-eps]) cube([6.8,7.5,2]);
    }
}

module button_plunger() {
    // Example radial plunger, printed separately; dimension to a chosen SMT switch.
    // X-axis is insertion direction: inner flange catches inside the wall.
    translate([0,0,0]) rotate([0,90,0]) {
        cylinder(d=button_lip_d,h=1.0);
        translate([0,0,1.0]) cylinder(d=button_pin_d,h=4.1);
    }
}

module pcb_reference() {
    // Conceptual custom PCB disc. Missing: actual RF antenna keepout and traces.
    difference() {
        linear_extrude(height=pcb_t) circle(r=pcb_r,$fn=96);
        for (a=closure_angles)
            at_polar(closure_r,a,-eps)
                cylinder(r=closure_boss_d/2+0.85,h=pcb_t+2*eps);
        for (x=[-19,19],y=[-1,13])
            translate([x,y,-eps]) cylinder(d=2.2,h=pcb_t+2*eps);
    }
}

// REFERENCE geometry only. Never part of printable STL export.
module battery_ghost() {
    color([0.15,0.42,0.63,0.85])
        translate([0,battery_y0,wall+battery_z/2])
            cube([battery_x,battery_y,battery_z],center=true);
}
module speaker_ghost() {
    color([0.3,0.3,0.32,0.9])
        translate([0,speaker_y0,wall+speaker_t/2])
            linear_extrude(height=speaker_t,center=true) round_rect(speaker_w,speaker_l,3.2);
}
module pcb_ghost() {
    color([0.13,0.46,0.3,0.75])
        translate([0,0,pcb_z0]) pcb_reference();
    color([0.18,0.19,0.2,0.9])
        translate([-mcu_x/2,mcu_y0-mcu_y/2,pcb_z0+pcb_t])
            cube([mcu_x,mcu_y,mcu_z]);
}
module display_ghost() {
    color([0.13,0.14,0.15])
        translate([0,0,display_seat_z-display_t])
            linear_extrude(height=display_t)
                round_rect(display_x,display_y,0.8);
    color([0.89,0.88,0.80])
        translate([0,0,display_seat_z+0.01])
            linear_extrude(height=0.06)
                square([window_size-0.2,window_size-0.2],center=true);
    color([0.09,0.1,0.1]) {
        translate([0,6,display_seat_z+0.08])
            linear_extrude(height=0.08)
                text("ARA",size=3.4,halign="center",valign="center",font="DejaVu Sans:style=Bold");
        translate([-3.7,-0.4,display_seat_z+0.08]) cylinder(d=1.6,h=0.08);
        translate([3.7,-0.4,display_seat_z+0.08]) cylinder(d=1.6,h=0.08);
        translate([0,-5,display_seat_z+0.08])
            linear_extrude(height=0.08)
                text("12:45",size=3.3,halign="center",valign="center",font="DejaVu Sans:style=Bold");
    }
}
module front_assembly() {
    color([0.85,0.86,0.84,1]) front_shell();
    if(show_components) display_ghost();
    if(show_components) {
        color([0.65,0.67,0.7,1]) translate([0,0,0.25]) retainer();
    }
}
module back_assembly() {
    color([0.45,0.48,0.51,1]) back_shell();
    if(show_components) {
        battery_ghost(); speaker_ghost(); pcb_ghost();
        for(a=button_angles)
            color([0.17,0.17,0.18])
                rotate([0,0,a]) translate([26,0,button_z0]) button_plunger();
    }
}

if(part=="back") back_shell();
else if(part=="front") front_shell();
else if(part=="retainer") retainer();
else if(part=="button") for(i=[0:3]) translate([i*8,0,0]) button_plunger();
else if(part=="pcb") pcb_reference();
else if(part=="assembled") {
    back_assembly();
    translate([0,0,back_h]) front_assembly();
}
else if(part=="exploded") {
    back_assembly();
    translate([0,0,back_h+9]) front_assembly();
}
else if(part=="rear_view") rotate([180,0,0]) back_shell();
else if(part=="print") {
    translate([-34,0,0]) front_shell();
    translate([34,0,0]) back_shell();
    translate([0,-48,0]) retainer();
    // 4 plungers — one per real button, not one sample to duplicate by hand
    for(i=[0:3]) translate([-16+i*8,-69,0]) button_plunger();
}
