#!/usr/bin/env python3
"""Writes ara_floorplan.kicad_pcb directly (no pcbnew / IPC API needed).

Board coordinates = case CAD coordinates (models/case/ara_case.sc) + (OX, OY).
F.Cu is the component side, which faces the BACK of the device, so the board
is drawn as seen from the back: CAD +X is right, CAD +Y is down.

Run:  python3 gen_floorplan.py && kicad-cli pcb drc ara_floorplan.kicad_pcb
"""
import math
import re
import uuid
from pathlib import Path

LIB = Path("/usr/share/kicad/footprints")
OUT = Path(__file__).with_name("ara_floorplan.kicad_pcb")
OX, OY = 100.0, 100.0  # CAD origin (case centre) on the sheet

# --- geometry shared with the case model (same numbers as its parameters) ---
PCB_X0, PCB_X1, PCB_HW = -44.65, 38.3, 14.65  # outline, half width
SLOT = (-37.9, -7.0, -35.4, 7.0)              # display FPC drops through here to J3
POSTS, POST_R = [(-41.4, 11.5), (-41.4, -11.5)], 2.2  # bezel screw posts pass through
LEDGE_Y = 13.7                                # |y| beyond this rests on the shell ledge
BATT = (-12.2, -10.0, 17.8, 10.0)             # 0.3 mm under the board: no parts
SPK = (-39.1, -10.0, -25.1, 10.0)             # on the case floor, 4.1 mm under the board
DISP = (-35.9, -14.6, 23.3, 14.6)             # other side of the board
ANT_X0, ANT_KEEPOUT = 38.3, 15.0              # antenna base line = board edge
MOD_HW = 9.75                                 # module courtyard half width

# ref, library, footprint, CAD x, CAD y, rotation (deg, KiCad CCW), value
SW = ("Button_Switch_SMD", "SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010")
PARTS = [
    ("U1", "RF_Module", "ESP32-S3-WROOM-1", 31.55, 0.0, 270, "ESP32-S3-WROOM-1-N16R8"),
    ("MK1", "Sensor_Audio", "InvenSense_ICS-43434-6_3.5x2.65mm", -40.4, 7.4, 270, "ICS-43434"),
    ("J1", "Connector_USB", "USB_C_Receptacle_GCT_USB4125-xx-x_6P_TopMnt_Horizontal", -42.5, 0.0, 270,
     "APPROXIMATION of SHOU HAN TYPE-C 6P CB1.6(073)"),
    ("J2", "Connector_JST", "JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal", -21.0, 8.0, 90, "LP702030 JST-PH"),
    ("J3", "Connector_FFC-FPC", "Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal", -29.5, 0.0, 270,
     "GDEY0213B74 24P FPC (connector not in BOM)"),
    ("U2", "Package_SO", "SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm", -21.9, -3.6, 0, "TP4056"),
    ("U3", "Package_DFN_QFN", "TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm", -14.6, -3.6, 0, "MAX17048G+T10"),
    ("U4", "Package_DFN_QFN", "TQFN-16-1EP_3x3mm_P0.5mm_EP1.23x1.23mm", -23.9, -10.0, 0, "MAX98357A"),
    ("U5", "Package_TO_SOT_SMD", "SOT-23-5", -17.5, -10.0, 0, "AP2112K-3.3"),
    ("TP1", "TestPoint", "TestPoint_Pad_2.0x2.0mm", -32.2, -11.4, 0, "SPK+ wire pad"),
    ("TP2", "TestPoint", "TestPoint_Pad_2.0x2.0mm", -28.8, -11.4, 0, "SPK- wire pad"),
    ("SW1", *SW, 8.0, 12.55, 0, "SKRTLAE010"),
    ("SW2", *SW, -8.0, 12.55, 0, "SKRTLAE010"),
    ("SW3", *SW, 8.0, -12.55, 180, "SKRTLAE010"),
    ("SW4", *SW, -8.0, -12.55, 180, "SKRTLAE010"),
]

# ref -> {pad: net}. Pin numbers are from KiCad's symbol library (Audio:MAX98357A,
# Regulator_Linear:AP2112K-3.3, Battery_Management:TP4056-42-ESOP8, Sensor_Audio:ICS-43434,
# RF_Module:ESP32-S3-WROOM-1); MAX17048 and the JST polarity are from memory. The four I2S GPIOs
# are a provisional pick, not a pin plan. Everything else is left without a net.
G, VBUS, VBAT, V33 = "GND", "VBUS", "VBAT", "+3V3"
BCLK, WS, DOUT, DIN = "I2S_BCLK", "I2S_WS", "I2S_DOUT", "I2S_DIN"
NETS = {
    "U1": {"1": G, "40": G, "41": G, "2": V33, "4": BCLK, "5": WS, "6": DOUT, "7": DIN},
    "MK1": {"1": WS, "2": G, "3": G, "4": BCLK, "5": V33, "6": DIN},
    "U4": {"1": DOUT, "14": WS, "16": BCLK, "7": VBAT, "8": VBAT, "9": "SPK_P", "10": "SPK_N",
           "3": G, "11": G, "15": G, "17": G},
    "TP1": {"1": "SPK_P"}, "TP2": {"1": "SPK_N"},
    "U5": {"1": VBAT, "2": G, "3": VBAT, "5": V33},          # EN tied to VIN: assumption
    "U2": {"4": VBUS, "8": VBUS, "5": VBAT, "3": G, "9": G},
    "U3": {"2": VBAT, "3": VBAT, "1": G, "4": G, "9": G},
    "J1": {"A9": VBUS, "B9": VBUS, "A12": G, "B12": G, "SH": G},
    "J2": {"1": VBAT, "2": G},
}


def uid(tag):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "ara-floorplan/" + tag))


def rot(x, y, deg):
    """KiCad footprint rotation: positive = counter-clockwise on screen (Y down)."""
    a = math.radians(deg)
    return x * math.cos(a) + y * math.sin(a), -x * math.sin(a) + y * math.cos(a)


def courtyard_bbox(text, x, y, deg):
    """Board-space bbox of the footprint's F.CrtYd, in CAD coordinates."""
    pts = []
    for m in re.finditer(r'\((?:fp_line|fp_rect|fp_poly)\b(.*?)\(layer "F\.CrtYd"\)', text, re.S):
        chunk = m.group(1).rsplit("(fp_", 1)[-1]
        pts += [(float(a), float(b)) for a, b in re.findall(r"\((?:start|end|xy) (-?[\d.]+) (-?[\d.]+)\)", chunk)]
    rp = [rot(px, py, deg) for px, py in pts]
    return (x + min(p[0] for p in rp), y + min(p[1] for p in rp),
            x + max(p[0] for p in rp), y + max(p[1] for p in rp))


def embed(ref, lib, name, x, y, deg, value):
    """Library footprint -> board footprint block. Pad/text angles are absolute in a board."""
    src = (LIB / f"{lib}.pretty" / f"{name}.kicad_mod").read_text()
    # library item uuids repeat in every copy of a footprint: make them unique per instance
    src = re.sub(r'\(uuid "([^"]+)"\)', lambda m: f'(uuid "{uid(ref + m.group(1))}")', src)
    out, bump, net = [], False, None
    for line in src.splitlines():
        s = line.strip()
        if s.startswith(("(version", "(generator")):
            continue
        if s.startswith("(footprint "):
            line = f'(footprint "{lib}:{name}"'
        elif s == '(layer "F.Cu")' and line.startswith("\t(layer"):
            line += f'\n\t(uuid "{uid(ref)}")\n\t(at {OX + x:.4f} {OY + y:.4f} {deg})'
        elif s.startswith('(property "Reference"'):
            line, bump = line.replace("REF**", ref), True
        elif s.startswith('(property "Value"'):
            line, bump = f'\t(property "Value" "{value}"', True
        elif s.startswith(("(pad ", "(property ", "(fp_text ")):
            bump = True
            net = NETS.get(ref, {}).get(s.split('"')[1]) if s.startswith("(pad ") else None
        elif bump and s.startswith("(at "):
            v = s[4:-1].split()
            ang = (float(v[2]) if len(v) > 2 else 0.0) + deg
            line = f"\t\t(at {v[0]} {v[1]} {ang % 360:g})"
            if net:
                line += f'\n\t\t(net "{net}")'
            bump = False
        out.append(line)
    return "\n".join(out), courtyard_bbox(src, x, y, deg)


def P(x, y):
    return f"(xy {OX + x:.4f} {OY + y:.4f})"


def edge(tag, pts):
    return "\n".join(
        f'\t(gr_line (start {OX + a[0]:.4f} {OY + a[1]:.4f}) (end {OX + b[0]:.4f} {OY + b[1]:.4f})'
        f' (stroke (width 0.1) (type default)) (layer "Edge.Cuts") (uuid "{uid(f"{tag}{i}")}"))'
        for i, (a, b) in enumerate(zip(pts, pts[1:] + pts[:1])))


def rect_pts(r):
    return [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]


def hole(i, x, y, r):
    return (f'\t(gr_circle (center {OX + x:.4f} {OY + y:.4f}) (end {OX + x + r:.4f} {OY + y:.4f})'
            f' (stroke (width 0.1) (type default)) (fill no) (layer "Edge.Cuts") (uuid "{uid(f"post{i}")}"))')


def note_rect(tag, r, label):
    x0, y0, x1, y1 = r
    return (f'\t(gr_rect (start {OX + x0:.4f} {OY + y0:.4f}) (end {OX + x1:.4f} {OY + y1:.4f})'
            f' (stroke (width 0.1) (type dash)) (fill no) (layer "Dwgs.User") (uuid "{uid(tag)}"))\n'
            f'\t(gr_text "{label}" (at {OX + (x0 + x1) / 2:.4f} {OY + (y0 + y1) / 2:.4f} 0) (layer "Dwgs.User")'
            f' (uuid "{uid(tag + "t")}") (effects (font (size 1 1) (thickness 0.12))))')


def keepout(tag, r, footprints_only):
    x0, y0, x1, y1 = r
    rule = "allowed" if footprints_only else "not_allowed"
    return f'''\t(zone (net 0) (net_name "") (layers "F.Cu" "B.Cu") (uuid "{uid(tag)}") (name "{tag}")
\t\t(hatch edge 0.5) (connect_pads (clearance 0)) (min_thickness 0.25) (filled_areas_thickness no)
\t\t(keepout (tracks {rule}) (vias {rule}) (pads {rule}) (copperpour {rule}) (footprints not_allowed))
\t\t(fill (thermal_gap 0.5) (thermal_bridge_width 0.5))
\t\t(polygon (pts {P(x0, y0)} {P(x1, y0)} {P(x1, y1)} {P(x0, y1)}))
\t)'''


HEADER = '''(kicad_pcb
\t(version 20260206)
\t(generator "ara_gen_floorplan")
\t(generator_version "10.0")
\t(general (thickness 1.0) (legacy_teardrops no))
\t(paper "A4")
\t(title_block (title "ARA floorplan v0 - rectangular") (comment 1 "Component side (F.Cu) faces the back of the device"))
\t(layers
\t\t(0 "F.Cu" signal) (2 "B.Cu" signal)
\t\t(9 "F.Adhes" user "F.Adhesive") (11 "B.Adhes" user "B.Adhesive")
\t\t(13 "F.Paste" user) (15 "B.Paste" user)
\t\t(5 "F.SilkS" user "F.Silkscreen") (7 "B.SilkS" user "B.Silkscreen")
\t\t(1 "F.Mask" user) (3 "B.Mask" user)
\t\t(17 "Dwgs.User" user "User.Drawings") (19 "Cmts.User" user "User.Comments")
\t\t(21 "Eco1.User" user "User.Eco1") (23 "Eco2.User" user "User.Eco2")
\t\t(25 "Edge.Cuts" user) (27 "Margin" user)
\t\t(31 "F.CrtYd" user "F.Courtyard") (29 "B.CrtYd" user "B.Courtyard")
\t\t(35 "F.Fab" user) (33 "B.Fab" user)
\t)
\t(setup (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no))
\t(net 0 "")'''


def main():
    outline = rect_pts((PCB_X0, -PCB_HW, PCB_X1, PCB_HW))
    strip_x0 = ANT_X0 - ANT_KEEPOUT  # 15 mm behind the antenna base line
    ant_strips = [(strip_x0, MOD_HW, PCB_X1, PCB_HW), (strip_x0, -PCB_HW, PCB_X1, -MOD_HW)]

    blocks, boxes = [], {}
    for ref, lib, name, x, y, deg, value in PARTS:
        text, boxes[ref] = embed(ref, lib, name, x, y, deg, value)
        blocks.append(text)
    boxes["U1"] = (18.8 - 0.75, -MOD_HW, PCB_X1, MOD_HW)  # module body only; its T courtyard is the keep-out

    body = [HEADER, *blocks, edge("edge", outline), edge("slot", rect_pts(SLOT)),
            *(hole(i, x, y, POST_R) for i, (x, y) in enumerate(POSTS)),
            note_rect("batt", BATT, "BATTERY 30x20x7 (0.3 under board)"),
            note_rect("spk", SPK, "SPEAKER 14x20 (case floor)"),
            note_rect("disp", DISP, "DISPLAY outline (other side)"),
            keepout("ANT_KEEPOUT_A", ant_strips[0], False),
            keepout("ANT_KEEPOUT_B", ant_strips[1], False),
            keepout("BATTERY_NO_PARTS", BATT, True),
            ")"]
    OUT.write_text("\n".join(body) + "\n")

    # --- self-check + free placement area, on a 0.1 mm raster ---
    def inside(r, x, y):
        return r[0] <= x <= r[2] and r[1] <= y <= r[3]

    cutouts = [SLOT] + [(x - POST_R, y - POST_R, x + POST_R, y + POST_R) for x, y in POSTS]
    for i, c in enumerate(cutouts):
        boxes[f"cutout{i}"] = c  # courtyards must stay off the slot and the post holes too
    blocked = list(boxes.values()) + ant_strips + [BATT]
    refs = list(boxes)
    for i, a in enumerate(refs):
        for b in refs[i + 1:]:
            ra, rb = boxes[a], boxes[b]
            assert ra[2] <= rb[0] or rb[2] <= ra[0] or ra[3] <= rb[1] or rb[3] <= ra[1], f"courtyards overlap: {a} {b}"
    board = free = free_tall = 0
    for ix in range(round(PCB_X0 * 10 - 0.5), round(PCB_X1 * 10)):
        for iy in range(round(-PCB_HW * 10 - 0.5), round(PCB_HW * 10)):
            x, y = ix / 10 + 0.05, iy / 10 + 0.05
            if not (PCB_X0 < x < PCB_X1 and abs(y) < PCB_HW) or inside(SLOT, x, y) or any(
                    math.hypot(x - px, y - py) < POST_R for px, py in POSTS):
                continue
            board += 1
            if abs(y) > LEDGE_Y or any(inside(r, x, y) for r in blocked):
                continue
            free += 1
            free_tall += not inside(SPK, x, y)
    for ref, r in boxes.items():
        print(f"{ref:4s} courtyard CAD x {r[0]:7.2f}..{r[2]:7.2f}  y {r[1]:7.2f}..{r[3]:7.2f}")
    print(f"board area            {board / 100:8.1f} mm2")
    print(f"free for unplaced BOM {free / 100:8.1f} mm2 (of which {free_tall / 100:.1f} mm2 not over the speaker)")
    print("wrote", OUT.name)


if __name__ == "__main__":
    main()
