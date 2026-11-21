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
C = 43.4                                      # cav_l / 2
PCB_X0, PCB_X1, PCB_HW = -C + 0.25, 36.8, 14.65  # outline, half width
FPC_Y = 0.2                                   # display tail centre (panel drawing: 8.15 + 6.25 from the pin-1 edge)
PANEL_X0 = -C + 6.0                           # display bottom end (fpc_fold)
SLOT = (PANEL_X0 - 2.2, FPC_Y - 7.0, PANEL_X0 + 0.5, FPC_Y + 7.0)  # tail drops through here to J3
J3_MOUTH = PANEL_X0 + 5.7                     # fpc_run
TAIL = (SLOT[2], FPC_Y - 6.25, J3_MOUTH - 0.5, FPC_Y + 6.25)  # tail runs 1.0-1.3 mm under the board, slot to J3 courtyard
POSTS, POST_R = [(-C + 3.5, 11.5), (-C + 3.5, -11.5)], 2.2  # bezel screw posts pass through
LEDGE_Y = 13.7                                # |y| beyond this rests on the shell ledge
BATT = (-13.2, -10.0, 16.8, 10.0)             # 0.3 mm under the board: no parts
BATT_PCM = 2.0                                # kept clear below z 5.6 past the cell's -X end (protection board, leads)
SPK = (-C + 5.8, -10.0, -C + 19.8, 10.0)      # on the case floor, 4.1 mm under the board
DISP = (PANEL_X0, -14.6, PANEL_X0 + 59.2, 14.6)  # other side of the board
ANT_X0, ANT_KEEPOUT = PCB_X1, 15.0            # antenna base line = board edge
MOD_HW = 9.75                                 # module courtyard half width
PLUG = (-23.1, 0.3, -15.2, 3.5)               # mated JST-PH plug and lead bend, from J2's courtyard (mouth at y 4.2) down

# ref, library, footprint, CAD x, CAD y, rotation (deg, KiCad CCW), value
SW = ("Button_Switch_SMD", "SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010")
CAP, RES = ("Capacitor_SMD", "C_0603_1608Metric"), ("Resistor_SMD", "R_0603_1608Metric")
DIO, TP = ("Diode_SMD", "D_SOD-123"), ("TestPoint", "TestPoint_Pad_1.5x1.5mm")
PARTS = [
    ("U1", "RF_Module", "ESP32-S3-WROOM-1", PCB_X1 - 6.75, 0.0, 270, "ESP32-S3-WROOM-1-N16R8"),
    ("MK1", "Sensor_Audio", "InvenSense_ICS-43434-6_3.5x2.65mm", -C + 2.025, -0.71, 0, "ICS-43434"),
    ("J1", "Connector_USB", "USB_C_Receptacle_GCT_USB4125-xx-x_6P_TopMnt_Horizontal", -18.75, -12.5, 180,
     "SHOU HAN TYPE-C 6P(073) on the GCT USB4125 land pattern"),
    ("J2", "Connector_JST", "JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal", -19.15, 8.6, 180, "S2B-PH-SM4-TB"),
    ("J3", "Connector_FFC-FPC", "Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal", J3_MOUTH + 4.4, FPC_Y, 270,
     "FH12A-24S-0.5SH(55) or FH12-24S-0.5SH(55)"),
    ("U2", "Package_SO", "SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm", -20.5, -5.4, 0, "TP4056"),
    ("U3", "Package_DFN_QFN", "TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm", -15.0, -4.0, 0, "MAX17048G+T10"),
    ("U4", "Package_DFN_QFN", "TQFN-16-1EP_3x3mm_P0.5mm_EP1.23x1.23mm", -30.1, -11.0, 0, "MAX98357AETE+T"),
    ("U5", "Package_TO_SOT_SMD", "SOT-23-5", 0.0, 11.85, 0, "AP2112K-3.3TRG1"),
    ("TP1", *TP, -C + 2.025, 6.5, 0, "SPK+ wire pad"),
    ("TP2", *TP, -C + 2.025, -6.5, 0, "SPK- wire pad"),
    ("SW1", *SW, 8.0, 12.55, 0, "SKRTLAE010"),
    ("SW2", *SW, -8.0, 12.55, 0, "SKRTLAE010"),
    ("SW3", *SW, 8.0, -12.55, 180, "SKRTLAE010"),
    ("SW4", *SW, -8.0, -12.55, 180, "SKRTLAE010"),
    # display boost circuit, designators as in the GDEY0213B74 specification, section 12
    ("L1", "Inductor_SMD", "L_Cenker_CKCS4030", -34.55, 11.1, 90, "47uH CKCS4030-47uH/M"),
    ("Q1", "Package_TO_SOT_SMD", "SOT-323_SC-70", -27.7, 10.4, 0, "Si1308EDL"),
    ("R1", *RES, -30.7, 9.99, 0, "1M"),
    ("R2", *RES, -30.7, 11.47, 0, "2R2"),
    ("C4", *CAP, -34.55, 7.72, 0, "4u7 25V"),
    ("D1", *DIO, -35.75, -11.35, 90, "MBR0530T1G"),
    ("D2", *DIO, -33.4, -11.35, 90, "MBR0530T1G"),
    ("D3", *DIO, -34.55, -7.85, 0, "MBR0530T1G"),
    ("C3", *CAP, -27.27, -11.3, 90, "4u7 25V"),
    ("C2", *CAP, -25.2, -11.3, 90, "1u 25V"),
    ("C12", *CAP, -23.5, -1.2, 90, "1u 25V"),
    ("C11", *CAP, -22.0, -1.2, 90, "1u 25V"),
    ("C10", *CAP, -20.5, -1.2, 90, "1u 25V"),
    ("C5", *CAP, -19.0, -1.2, 90, "1u 25V"),
    ("C9", *CAP, -17.5, -1.2, 90, "1u 25V"),
    ("C7", *CAP, -16.0, -1.2, 90, "1u 25V"),
    ("C6", *CAP, -14.5, -1.2, 90, "1u 25V"),
]

# ref -> {pad: net}. Pin numbers are from KiCad's symbol library (Audio:MAX98357A,
# Regulator_Linear:AP2112K-3.3, Battery_Management:TP4056-42-ESOP8, Sensor_Audio:ICS-43434,
# RF_Module:ESP32-S3-WROOM-1); MAX17048 and the JST polarity are from memory. The module GPIOs are a
# provisional pick, not a pin plan.
G, VBUS, VBAT, V33 = "GND", "VBUS", "VBAT", "+3V3"
BCLK, WS, DOUT, DIN = "I2S_BCLK", "I2S_WS", "I2S_DOUT", "I2S_DIN"
SWN, CP, VGH, VGL = "EPD_SW", "EPD_CP", "EPD_PREVGH", "EPD_PREVGL"
# GDEY0213B74 FPC pin -> net (specification section 5 pin table and section 12 reference circuit).
# Pins 1, 4 (NC), 6, 7 (TSCL, TSDA) and 19 (VPP) stay open, as the reference circuit draws them.
EPD = {2: "EPD_GDR", 3: "EPD_RESE", 5: "EPD_VSH2", 8: G, 9: "EPD_BUSY", 10: "EPD_RST", 11: "EPD_DC",
       12: "EPD_CS", 13: "EPD_SCK", 14: "EPD_MOSI", 15: V33, 16: V33, 17: G, 18: "EPD_VDD", 20: "EPD_VSH1",
       21: VGH, 22: "EPD_VSL", 23: VGL, 24: "EPD_VCOM"}
NETS = {
    "U1": {"1": G, "40": G, "41": G, "2": V33, "4": BCLK, "5": WS, "6": DOUT, "7": DIN,
           "17": "EPD_BUSY", "18": "EPD_CS", "19": "EPD_MOSI", "20": "EPD_SCK", "21": "EPD_DC", "22": "EPD_RST"},
    "MK1": {"1": WS, "2": G, "3": G, "4": BCLK, "5": V33, "6": DIN},
    "U4": {"1": DOUT, "14": WS, "16": BCLK, "7": VBAT, "8": VBAT, "9": "SPK_P", "10": "SPK_N",
           "3": G, "11": G, "15": G, "17": G},
    "TP1": {"1": "SPK_P"}, "TP2": {"1": "SPK_N"},
    "U5": {"1": VBAT, "2": G, "3": VBAT, "5": V33},          # EN tied to VIN: assumption
    "U2": {"4": VBUS, "8": VBUS, "5": VBAT, "3": G, "9": G},
    "U3": {"2": VBAT, "3": VBAT, "1": G, "4": G, "9": G},
    "J1": {"A9": VBUS, "B9": VBUS, "A12": G, "B12": G, "SH": G},
    "J2": {"1": VBAT, "2": G},
    # J3 is turned so that its pad 1 lies at -Y; the panel's pin 1 lies at +Y: FPC pin n lands on pad 25 - n
    "J3": {str(25 - n): net for n, net in EPD.items()},
    "L1": {"1": V33, "2": SWN}, "C4": {"1": V33, "2": G},
    "Q1": {"1": "EPD_GDR", "2": "EPD_RESE", "3": SWN},       # SC-70-3: 1 gate, 2 source, 3 drain
    "R1": {"1": "EPD_GDR", "2": G}, "R2": {"1": "EPD_RESE", "2": G},
    "D3": {"2": SWN, "1": VGH}, "C5": {"1": VGH, "2": G},    # SOD-123: pad 1 cathode, pad 2 anode
    "C3": {"1": SWN, "2": CP}, "D2": {"2": CP, "1": G}, "D1": {"1": CP, "2": VGL}, "C11": {"1": VGL, "2": G},
    "C2": {"1": "EPD_VSH2", "2": G}, "C6": {"1": V33, "2": G}, "C7": {"1": "EPD_VDD", "2": G},
    "C9": {"1": "EPD_VSH1", "2": G}, "C10": {"1": "EPD_VSL", "2": G}, "C12": {"1": "EPD_VCOM", "2": G},
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
    out, bump, net, to_fab = [], False, None, False
    for line in src.splitlines():
        s = line.strip()
        if s.startswith(("(version", "(generator")):
            continue
        if s.startswith("(footprint "):
            line = f'(footprint "{lib}:{name}"'
        elif s == '(layer "F.Cu")' and line.startswith("\t(layer"):
            line += f'\n\t(uuid "{uid(ref)}")\n\t(at {OX + x:.4f} {OY + y:.4f} {deg})'
        elif s.startswith('(property "Reference"'):
            line, bump, to_fab = line.replace("REF**", ref), True, True
        elif to_fab and s == '(layer "F.SilkS")':
            line, to_fab = line.replace("F.SilkS", "F.Fab"), False  # a floorplan: designators on F.Fab, not on silkscreen
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
\t(title_block (title "ARA floorplan v0 - rectangular, 79.95 x 29.3") (comment 1 "Component side (F.Cu) faces the back of the device"))
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

    # the rule area stops where the module's own library courtyard (0.75 mm behind its body) begins
    batt_zone = (BATT[0], BATT[1], min(BATT[2], PCB_X1 - 19.5 - 0.75), BATT[3])

    blocks, boxes = [], {}
    for ref, lib, name, x, y, deg, value in PARTS:
        text, boxes[ref] = embed(ref, lib, name, x, y, deg, value)
        blocks.append(text)
    boxes["U1"] = (PCB_X1 - 19.5 - 0.25, -MOD_HW, PCB_X1, MOD_HW)  # module body + 0.25; its T courtyard is the keep-out

    body = [HEADER, *blocks, edge("edge", outline), edge("slot", rect_pts(SLOT)),
            *(hole(i, x, y, POST_R) for i, (x, y) in enumerate(POSTS)),
            note_rect("batt", BATT, "BATTERY 30x20x7 (0.3 under board)"),
            note_rect("tail", TAIL, "FPC TAIL (under board)"),
            note_rect("plug", PLUG, "JST PLUG"),
            note_rect("spk", SPK, "SPEAKER 14x20 (case floor)"),
            note_rect("disp", DISP, "DISPLAY outline (other side)"),
            keepout("ANT_KEEPOUT_A", ant_strips[0], False),
            keepout("ANT_KEEPOUT_B", ant_strips[1], False),
            keepout("BATTERY_NO_PARTS", batt_zone, True),
            keepout("FPC_TAIL_NO_PARTS", TAIL, True),
            keepout("JST_PLUG_NO_PARTS", PLUG, True),
            ")"]
    OUT.write_text("\n".join(body) + "\n")

    # --- self-check + free placement area, on a 0.1 mm raster ---
    def inside(r, x, y):
        return r[0] <= x <= r[2] and r[1] <= y <= r[3]

    cutouts = [SLOT] + [(x - POST_R, y - POST_R, x + POST_R, y + POST_R) for x, y in POSTS]
    for i, c in enumerate(cutouts):
        boxes[f"cutout{i}"] = c  # courtyards must stay off the slot and the post holes too
    for name, z in (("battery zone", batt_zone), ("tail zone", TAIL), ("plug zone", PLUG),
                    ("antenna strip A", ant_strips[0]), ("antenna strip B", ant_strips[1])):
        boxes[name] = z  # rule areas: courtyards must stay out of them as well
    blocked = list(boxes.values())
    refs = list(boxes)
    for i, a in enumerate(refs):
        for b in refs[i + 1:]:
            ra, rb = boxes[a], boxes[b]
            assert (ra[2] <= rb[0] + 1e-6 or rb[2] <= ra[0] + 1e-6 or ra[3] <= rb[1] + 1e-6
                    or rb[3] <= ra[1] + 1e-6), f"courtyards overlap: {a} {ra} {b} {rb}"
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
