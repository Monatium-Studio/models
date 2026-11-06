"""모나티엄 진압반 MRV-1 '요람' 진압 장갑차 (4x4).

[원작] 모나티엄에는 경찰차량과 장갑차가 있다(엘레나 작중 행적: 슈팡의 경찰차량 파손, "장갑차에 묶어 총알받이로").
       교주 차원 진압반의 장비는 고무탄과 고전압 전기충격기뿐이다(엘리아스 침공전). 칸나: "최루 가스는 정말 완벽한 제압용 무기죠!"
       모나티엄 시장 엘레나가 만든 기계(전술 드론 MK-2, D-CAT, 마에스트로 2호, 거대 로봇 M.E.O.W.)는 모두 고양이 모양이다.
[오리지널] 진압반 분대(엘프 7명)를 태우는 4륜 진압 장갑차. 둥근 '식빵' 차체, 고양이 머리 원격 포탑(귀 = 확성기),
           고무 발바닥 패드가 달린 밀대, 졸린 눈 전조등. 포탑에 자동 충격탄 발사기(MR-37A)와 물대포(MR-W1)를 단다.

규약: docs/art/VEHICLES.md, 설정: docs/art/vehicles-elf.md
npm run model -- art/blender/vehicles/monatium/monatium_riot_apc.py
npm run shot -- vehicles/monatium/monatium_riot_apc.glb --views front,34,side,top
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import vehicles_elf as ve  # noqa: E402

cb.reset()
V = ve.Veh("monatium_riot_apc", "monatium")
M = V.M

# ------------------------------------------------------------------ 치수 (엘프 체격: 같은 급 인간 차량의 약 2/3)
R_W, W_W = 0.44, 0.30          # 바퀴 반지름·폭
Y_F, Y_R = -1.30, 1.30          # 앞·뒤 차축 (축거 2.6)
X_W = 0.88                      # 바퀴 중심 x (윤거 1.76)
Z_BELLY = 0.40
Z_ROOF = 1.70
HX = 1.00                       # 차체 반폭 (아래 수직면)
HX_TOP = 0.84                   # 지붕 반폭
Z_SH = 1.25                     # 수직면 → 기운 면


def tilt_x(z):
    """기운 옆면(z > Z_SH)의 반폭."""
    return HX + (HX_TOP - HX) * max(0.0, (z - Z_SH) / (Z_ROOF + 0.03 - Z_SH))


# ------------------------------------------------------------------ 차체 (식빵): 옆모습 ∩ 단면
SIDE = [(-1.95, Z_BELLY), (-2.22, 0.58), (-2.32, 1.04), (-2.02, 1.20), (-1.80, 1.24), (-1.30, 1.66),
        (0.0, Z_ROOF + 0.02), (1.70, Z_ROOF), (2.22, 1.56), (2.28, 0.62), (2.00, Z_BELLY)]
side_r = [0.0, 0.10, 0.10, 0.12, 0.06, 0.22, 0.0, 0.26, 0.10, 0.10, 0.0]
SEC = [(-0.94, Z_BELLY), (0.94, Z_BELLY), (HX, 0.55), (HX, Z_SH), (HX_TOP, Z_ROOF + 0.03),
       (-HX_TOP, Z_ROOF + 0.03), (-HX, Z_SH), (-HX, 0.55)]
sec_r = [0.0, 0.0, 0.08, 0.10, 0.22, 0.22, 0.10, 0.08]
hull = ve.sculpt("hull", ve.round_poly(SIDE, side_r, 3), ve.round_poly(SEC, sec_r, 3), bevel=0.02, seg=2,
                 mat=M["hull"])
for y in (Y_F, Y_R):            # 바퀴집: 바깥쪽만 둥글게 파낸다
    for sx in (1, -1):
        ve.cut(hull, cb.cylinder("well", radius=0.55, depth=0.50, loc=(sx * 1.0, y, R_W), rot=(0, 90, 0), verts=24))
TWO_TONE = (M["hull_d"], lambda c, n: c.z < 0.86, [("z", 0.86)])
BAND = (M["teal"], lambda c, n: 1.06 < c.z < 1.16 and abs(n.z) < 0.6, [("z", 1.06), ("z", 1.16)])
ve.paint(hull, [TWO_TONE, BAND, (M["hull_l"], lambda c, n: c.z > 1.62 and n.z > 0.80, [])],
         slots=[M["hull"], M["hull_d"], M["teal"], M["hull_l"]])
ve.shell(hull, 0.04, M["cabin"])          # 속이 빈 껍데기: 좌석 카메라가 창 구멍으로 밖을 본다
V.body(hull)

# 펜더 플레어 + 진흙받이
for y in (Y_F, Y_R):
    for sx in (1, -1):
        path = [(sx * 0.95, y + math.cos(math.radians(a)) * 0.575, R_W + math.sin(math.radians(a)) * 0.575)
                for a in range(-8, 189, 20)]
        sec = [(0.10, -0.02), (0.08, 0.03), (-0.08, 0.03), (-0.10, -0.02)]
        V.body(hw.sweep("fender", path, sec, side_vec=(1, 0, 0), cap=True, mat=M["hull_d"], smooth=50))
        x0, x1 = sorted((sx * 0.80, sx * 1.02))
        V.body(ve.rbox("flap", x0, x1, y + 0.50, y + 0.55, 0.16, 0.44, mat=M["rubber"]))

# ------------------------------------------------------------------ 앞 유리 ('고양이 눈' 두 장) + 접이식 격자
SL0, SL1 = (-1.80, 1.24), (-1.30, 1.66)
L_s = math.hypot(SL1[0] - SL0[0], SL1[1] - SL0[1])
U_SL = (1, 0, 0)
V_SL = (0, (SL1[0] - SL0[0]) / L_s, (SL1[1] - SL0[1]) / L_s)
N_SL = (0, -V_SL[2], V_SL[1])
O_SL = (0, (SL0[0] + SL1[0]) / 2, (SL0[1] + SL1[1]) / 2)


def on_sl(u, v, n=0.0):
    return tuple(O_SL[i] + U_SL[i] * u + V_SL[i] * v + N_SL[i] * n for i in range(3))


for sx in (1, -1):
    eye = [(0.07, -0.19), (0.68, -0.19), (0.75, -0.11), (0.73, 0.17), (0.64, 0.23), (0.10, 0.16), (0.06, 0.11)]
    eye = ve.round_poly([(sx * u, v) for u, v in eye], 0.05, 2)
    ve.cut_through(hull, eye, O_SL, U_SL, V_SL)
    V.body(ve.slab("windshield", eye, O_SL, U_SL, V_SL, 0.008, mat=M["glass"], lift=-0.024))
    V.body(ve.loop_frame("ws_frame", eye, O_SL, U_SL, V_SL, r=0.022, lift=0.004, mat=M["gear"], verts=4))
V.body(ve.slab("ws_pillar", ve.round_poly([(-0.05, -0.25), (0.05, -0.25), (0.05, 0.28), (-0.05, 0.28)], 0.02, 2),
               O_SL, U_SL, V_SL, 0.03, mat=M["hull_d"]))
for v in (-0.24, 0.26):         # 격자 테 + 세로 봉 (유리 위 7 cm)
    V.body(ve.bar("grille_h", on_sl(-0.82, v, 0.07), on_sl(0.82, v, 0.07), 0.016, verts=8, mat=M["gear"]))
for u in (-0.82, 0.82):
    V.body(ve.bar("grille_s", on_sl(u, -0.24, 0.07), on_sl(u, 0.26, 0.07), 0.016, verts=8, mat=M["gear"]))
    V.body(ve.bar("grille_arm", on_sl(u, 0.26, 0.07), on_sl(u, 0.30, 0.0), 0.014, verts=6, mat=M["gear"]))
    V.body(ve.bar("grille_foot", on_sl(u, -0.24, 0.07), on_sl(u, -0.26, 0.0), 0.012, verts=6, mat=M["gear"]))
# 세로 봉: 운전석·지휘석 눈(u ±0.44) 앞을 비우고 '고양이 눈' 안쪽·바깥쪽 가장자리에만 가늘게 (좌석 시점에서 길이 보이게)
for u in (-0.70, -0.20, 0.20, 0.70):
    V.body(ve.bar("grille_v", on_sl(u, -0.24, 0.07), on_sl(u, 0.26, 0.07), 0.006, verts=6, mat=M["steel"]))

# ------------------------------------------------------------------ 옆 창 (스타디움 창 + 막대 격자)
for sx in (1, -1):
    tz = Z_ROOF + 0.03 - Z_SH
    tlen = math.hypot(HX_TOP - HX, tz)
    up = (sx * (HX_TOP - HX) / tlen, 0, tz / tlen)
    nrm = (sx * tz / tlen, 0, -(HX_TOP - HX) / tlen)
    fwd = (0, 1 if sx > 0 else -1, 0)            # fwd x up = 바깥
    for i, (yc, ln, zc) in enumerate(((-1.20, 0.30, 1.40), (-0.36, 0.44, 1.44), (0.40, 0.44, 1.44), (1.16, 0.44, 1.44))):
        org = (sx * tilt_x(zc), yc, zc)
        if i == 0:      # 운전석·지휘석 옆 창은 실제 구멍 (좌석 시점)
            win = hw.stadium(ln, 0.19, 5)
            ve.cut_through(hull, win, org, fwd, up)
            V.body(ve.slab("swin", win, org, fwd, up, 0.008, mat=M["glass"], lift=-0.024))
            V.body(ve.loop_frame("swin_rim", win, org, fwd, up, r=0.02, lift=0.004, mat=M["gear"], verts=4))
        else:
            V.body(ve.slab("swin", hw.stadium(ln, 0.19, 4), org, fwd, up, 0.010, mat=M["lens"], lift=0.002))
            V.body(ve.slab("swin_rim", hw.stadium(ln + 0.06, 0.25, 4), org, fwd, up, 0.007, mat=M["gear"], lift=-0.003))
        for k in (-0.5, 0.5):
            a = tuple(org[j] + nrm[j] * 0.03 + up[j] * k * 0.07 for j in range(3))
            V.body(ve.bar("swin_bar", (a[0], yc - ln / 2 + 0.03, a[2]), (a[0], yc + ln / 2 - 0.03, a[2]), 0.008,
                          verts=6, mat=M["steel"]))

# ------------------------------------------------------------------ 지붕: 경광등 + 탐조등, 해치, 안테나, 손잡이
LB_Y, LB_Z = -1.10, 1.675
V.body(ve.bar("lightbar_base", (-0.62, LB_Y, LB_Z + 0.04), (0.62, LB_Y, LB_Z + 0.04), 0.045, verts=12, mat=M["gear"]))
for sx in (1, -1):
    V.body(ve.rbox("lb_foot", sx * 0.52 - 0.05, sx * 0.52 + 0.05, LB_Y - 0.05, LB_Y + 0.05, LB_Z - 0.03, LB_Z + 0.03,
                   mat=M["gear"]))
    V.body(hw.ycyl("flood", 0.075, LB_Y - 0.12, LB_Y + 0.06, x=sx * 0.70, z=LB_Z + 0.10, verts=14, bevel=0.01, seg=1,
                   mat=M["gear"]))
    V.body(hw.ycyl("flood_lens", 0.060, LB_Y - 0.128, LB_Y - 0.118, x=sx * 0.70, z=LB_Z + 0.10, verts=16,
                   mat=M["lamp"]))
    V.body(ve.bar("flood_yoke", (sx * 0.66, LB_Y, LB_Z + 0.04), (sx * 0.70, LB_Y, LB_Z + 0.06), 0.02, mat=M["steel"]))
V.part("light_beacon", (0, LB_Y, LB_Z + 0.10), props={"light": "beacon", "color": "#7ff0ea"})
for i in range(6):
    x0 = -0.48 + i * 0.16
    V.to("light_beacon", ve.rbox("beacon_cell", x0 + 0.01, x0 + 0.15, LB_Y - 0.05, LB_Y + 0.05, LB_Z + 0.07,
                                 LB_Z + 0.14, r=0.02, mat=M["glow"] if i % 2 == 0 else M["lens"]))
V.body(ve.rbox("beacon_cap", -0.50, 0.50, LB_Y - 0.06, LB_Y + 0.06, LB_Z + 0.14, LB_Z + 0.16, r=0.012, mat=M["gear"]))

HY = 1.32                        # 뒤 지붕 둥근 해치
V.part("hatch_roof", (0, HY - 0.30, Z_ROOF + 0.03), props={"rotAxis": "x", "rotDeg": 110})
V.to("hatch_roof", hw.zcyl("hatch_lid", 0.30, Z_ROOF + 0.03, Z_ROOF + 0.08, y=HY, verts=20, bevel=0.015, seg=1, mat=M["hull_l"]),
     hw.zcyl("hatch_boss", 0.12, Z_ROOF + 0.08, Z_ROOF + 0.10, y=HY, verts=12, bevel=0.008, seg=1, mat=M["hull_d"]),
     ve.bar("hatch_handle", (-0.10, HY + 0.13, Z_ROOF + 0.105), (0.10, HY + 0.13, Z_ROOF + 0.105), 0.012, mat=M["steel"]))
# 해치 아래 실제 구멍 (AI 지휘관이 상반신을 내민다 = crew_commander): 테를 실내까지 내린 관(안 반지름 0.28)으로 만들어
# 구멍 벽이 어두운 우물이 된다. 지붕은 관 벽 속(반지름 0.31)에서 뚫어 단면이 보이지 않는다. 테 바깥 모양은 그대로다
HR_OPEN = 0.28
hatch_ring = hw.zcyl("hatch_ring", 0.34, Z_ROOF - 0.12, Z_ROOF + 0.035, y=HY, verts=20, bevel=0.01, seg=1, mat=M["gear"])
cb.apply_modifiers(hatch_ring)      # 바깥 모서리만 베벨 (안쪽 모서리는 뚜껑에 가려져 삼각형을 아낀다)
ve.cut(hatch_ring, hw.zcyl("hatch_hole", HR_OPEN, Z_ROOF - 0.20, Z_ROOF + 0.10, y=HY, verts=20))
V.body(hatch_ring)
ve.cut(hull, hw.zcyl("hatch_hole", 0.31, Z_ROOF - 0.20, Z_ROOF + 0.10, y=HY, verts=20))
for sx in (1, -1):
    V.body(hw.zcyl("ant_base", 0.035, 1.62, 1.70, x=sx * 0.62, y=1.85, verts=10, mat=M["gear"]))
    V.body(ve.bar("ant", (sx * 0.62, 1.85, 1.70), (sx * 0.66, 1.98, 2.70), 0.006, r1=0.004, verts=5, mat=M["gear"]))
    V.body(cb.sphere("ant_tip", radius=0.016, loc=(sx * 0.66, 1.98, 2.71), segments=8, rings=4, material=M["glow"]))
    V.body(ve.bar("roof_rail", (sx * 0.68, 0.40, Z_ROOF + 0.03), (sx * 0.68, 0.90, Z_ROOF + 0.03), 0.014, mat=M["steel"]))
    for y in (0.40, 0.90):
        V.body(ve.bar("roof_rail_post", (sx * 0.68, y, Z_ROOF - 0.01), (sx * 0.68, y, Z_ROOF + 0.03), 0.012,
                      mat=M["steel"]))
V.body(hw.zcyl("turret_ring", 0.64, Z_ROOF - 0.02, Z_ROOF + 0.05, y=-0.20, verts=24, bevel=0.015, seg=1, mat=M["gear"]))
V.body(ve.text("roof_no", "07", 0.40, (0, 0.62, Z_ROOF + 0.025), ve.FACE_T, mat=M["steel"], lift=0.004))

# ------------------------------------------------------------------ 앞: 졸린 눈 전조등, 글자, 밀대(고무 발바닥 패드)
for sx, nm in ((1, "light_head_L"), (-1, "light_head_R")):
    c = (sx * 0.64, -2.30, 0.93)
    V.body(hw.ycyl("hl_house", 0.13, c[1] - 0.02, c[1] + 0.14, x=c[0], z=c[2], verts=14, bevel=0.015, seg=1, mat=M["gear"]))
    V.part(nm, c)
    V.to(nm, hw.ycyl(nm + "_lens", 0.105, c[1] - 0.035, c[1] - 0.015, x=c[0], z=c[2], verts=20, mat=M["lamp"]))
    lid = [(math.cos(math.radians(a)) * 0.15, max(math.sin(math.radians(a)) * 0.15, 0.0)) for a in range(-6, 187, 16)]
    V.body(ve.slab("hl_lid", lid, (c[0], c[1] - 0.03, c[2] + 0.02), (1, 0, 0), (0, 0, 1), 0.06, mat=M["hull_d"],
                   bevel=0.01, seg=1))
    V.body(hw.ycyl("blinker", 0.032, -2.33, -2.27, x=sx * 0.90, z=0.92, verts=12, mat=M["hazard"]))
V.body(ve.text("hood_mk", "진압반", 0.12, (0, -2.17, 1.12), ve.frame((0, -0.47, 0.88)), mat=M["steel"], lift=0.012))

PY = -2.46                       # 밀대 앞면
for sx in (1, -1):
    V.body(ve.bar("plow_arm", (sx * 0.55, -2.18, 0.56), (sx * 0.55, PY + 0.06, 0.62), 0.04, verts=10, mat=M["gear"]))
V.body(ve.bar("plow_bar_lo", (-1.00, PY + 0.03, 0.47), (1.00, PY + 0.03, 0.47), 0.045, verts=12, mat=M["gear"]))
V.body(ve.bar("plow_bar_hi", (-0.95, PY + 0.05, 0.81), (0.95, PY + 0.05, 0.81), 0.035, verts=12, mat=M["gear"]))
for sx in (1, -1):
    V.body(ve.bar("plow_post", (sx * 0.95, PY + 0.04, 0.45), (sx * 0.95, PY + 0.05, 0.83), 0.04, verts=10, mat=M["gear"]))
    for k in range(3):
        V.body(ve.decal(f"plow_hz{sx}{k}", [(-0.03, -0.12), (0.03, -0.12), (0.09, 0.12), (0.03, 0.12)],
                        (sx * (0.83 - k * 0.10), PY - 0.04, 0.64), ve.FACE_F, lift=0.002, mat=M["hazard"]))
plate_pts = ve.round_poly([(-0.90, -0.15), (0.90, -0.15), (0.90, 0.15), (-0.90, 0.15)], 0.10, 3)
V.body(ve.slab("plow_plate", plate_pts, (0, PY + 0.02, 0.64), (1, 0, 0), (0, 0, 1), 0.06, mat=M["gear"], bevel=0.012))
pad = [(u * 0.78, v * 0.78) for u, v in ve.round_poly(
    [(-0.22, -0.13), (0.22, -0.13), (0.27, 0.02), (0.12, 0.13), (0.0, 0.10), (-0.12, 0.13), (-0.27, 0.02)],
    [0.08, 0.08, 0.08, 0.06, 0.04, 0.06, 0.08], 3)]
V.body(ve.slab("paw_main", pad, (0, PY - 0.04, 0.60), (1, 0, 0), (0, 0, 1), 0.05, mat=M["teal"], bevel=0.015))
for i, (u, z, s) in enumerate(((-0.27, 0.715, 0.62), (-0.095, 0.755, 0.70), (0.095, 0.755, 0.70), (0.27, 0.715, 0.62))):
    toe = [(math.cos(2 * math.pi * k / 14) * 0.075 * s, math.sin(2 * math.pi * k / 14) * 0.068 * s) for k in range(14)]
    V.body(ve.slab(f"paw_toe{i}", toe, (u, PY - 0.04, z), (1, 0, 0), (0, 0, 1), 0.045, mat=M["teal"], bevel=0.010))
V.body(ve.text("plow_no", "모-0731", 0.045, (0.58, PY - 0.04, 0.53), ve.FACE_F, mat=M["steel"], lift=0.002))
for sx in (1, -1):
    # 거울
    V.body(ve.bar("mirror_arm", (sx * 0.99, -1.66, 1.20), (sx * 1.16, -1.78, 1.38), 0.012, verts=6, mat=M["gear"]))
    V.body(cb.sphere("mirror", radius=0.07, loc=(sx * 1.18, -1.80, 1.42), scale=(0.55, 0.35, 1.0), segments=10, rings=5,
                     material=M["gear"]))
    V.body(ve.decal(f"mirror_glass{sx}", hw.circle(0.055, 14, rx=0.030), (sx * 1.18, -1.776, 1.42), ve.FACE_B,
                    lift=0.0, mat=M["lens"]))

# ------------------------------------------------------------------ 옆: 문(앞바퀴 뒤), 엠블럼, 띠 글자, 보관함, 발판
DY0, DY1, DZ0, DZ1 = -0.74, -0.04, 0.50, 1.23
for sx, nm in ((1, "door_driver"), (-1, "door_commander")):
    x = sx * HX
    fr = ve.SIDE_L if sx > 0 else ve.SIDE_R
    uax = (0, 1, 0) if sx > 0 else (0, -1, 0)
    sg = 1 if sx > 0 else -1
    V.part(nm, (x, DY0, (DZ0 + DZ1) / 2), props={"rotAxis": "y", "rotDeg": -80 * sg})
    pts = ve.round_poly([(0, DZ0), (DY1 - DY0, DZ0), (DY1 - DY0, DZ1), (0, DZ1)], 0.07, 3)
    door = ve.slab(nm + "_panel", [(sg * u, v - 0.86) for u, v in pts], (x, DY0, 0.86), uax, (0, 0, 1), 0.035,
                   mat=M["hull"], bevel=0.01, seg=1)
    ve.paint(door, [TWO_TONE, BAND], slots=[M["hull"], M["hull_d"], M["teal"]])
    V.to(nm, door)
    # 문 뒤 차체에 실제 출입구 (탑승 연출: 문을 열면 실내가 보이고 몸이 그리로 들어간다). 문판보다 3 cm 안쪽
    hole = [(0.03, DZ0 + 0.03), (DY1 - DY0 - 0.03, DZ0 + 0.03), (DY1 - DY0 - 0.03, DZ1 - 0.03), (0.03, DZ1 - 0.03)]
    ve.cut_through(hull, [(sg * u, v - 0.86) for u, v in hole], (x, DY0, 0.86), uax, (0, 0, 1))
    V.to(nm, ve.bar(nm + "_handle", (x + sx * 0.055, DY1 - 0.20, 1.00), (x + sx * 0.055, DY1 - 0.07, 1.00), 0.014,
                    mat=M["steel"]))
    for y in (DY1 - 0.20, DY1 - 0.07):
        V.to(nm, ve.bar(nm + "_hpost", (x + sx * 0.03, y, 1.00), (x + sx * 0.058, y, 1.00), 0.011, mat=M["steel"]))
    for z in (0.62, 1.12):
        V.to(nm, hw.zcyl(nm + "_hinge", 0.022, z - 0.05, z + 0.05, x=x + sx * 0.04, y=DY0 + 0.01, verts=10,
                         mat=M["gear"]))
    V.to(nm, ve.logo_disc(nm + "_", (x + sx * 0.035, (DY0 + DY1) / 2 - 0.02, 0.83), 0.23, fr, disc=M["hull_d"],
                          rim=M["gold"], mark=M["gold"], lift=0.002))
    V.to(nm, ve.text(nm + "_less", "비살상", 0.07, (x + sx * 0.035, (DY0 + DY1) / 2, 1.11), fr, mat=M["steel"],
                     lift=0.002))
    for y, s in ((-1.45, "비살상"), (0.75, "모나티엄 진압반"), (1.75, "비살상")):
        V.body(ve.text(f"band_{sx}{y}", s, 0.07, (sx * (HX + 0.002), y, 1.11), fr, mat=M["steel"], lift=0.002))
    V.body(ve.text(f"side_no{sx}", "MRV-1  07", 0.06, (sx * (HX + 0.002), 1.95, 0.98), fr, mat=M["steel"], lift=0.002))
    x0, x1 = sorted((sx * (HX - 0.02), sx * (HX + 0.10)))
    V.body(ve.rbox("stow", x0, x1, 0.06, 0.62, 0.60, 0.92, r=0.025, mat=M["gear"]))
    for y in (0.20, 0.48):
        V.body(ve.rbox("stow_latch", sx * (HX + 0.10) - 0.012, sx * (HX + 0.10) + 0.012, y - 0.03, y + 0.03, 0.80, 0.86,
                       mat=M["steel"]))
    x0, x1 = sorted((sx * (HX - 0.12), sx * (HX + 0.12)))
    V.body(ve.rbox("step", x0, x1, DY0 + 0.04, DY1 - 0.04, 0.34, 0.38, r=0.01, mat=M["gear"]))
    for i in range(4):
        V.body(ve.decal(f"step_tread{sx}{i}", [(-0.09, -0.02), (0.09, -0.02), (0.09, 0.02), (-0.09, 0.02)],
                        (sx * HX, DY0 + 0.15 + i * 0.14, 0.383), ve.FACE_T, lift=0.0, mat=M["rubber"]))

# ------------------------------------------------------------------ 뒤: 경사로 문, 후미등, 손잡이, 배기
RZ0, RZ1 = 0.64, 1.46
RV = (0, -0.064, 0.998)                     # 뒷면 기울기 (위쪽)
RN = (0, 0.998, 0.064)                      # 바깥 법선
R0 = (0, 2.272, RZ0)


def ramp_pt(h, u=0.0, n=0.0):
    return (R0[0] - u, R0[1] + RV[1] * h + RN[1] * n, R0[2] + RV[2] * h + RN[2] * n)


RFR = ve.frame(RN)
V.part("hatch_rear", (0, 2.29, RZ0), props={"rotAxis": "x", "rotDeg": -100})
# 경사로 뒤 실제 출입구 (경사로가 내려가면 병력칸이 열린다). 경사로보다 3~4 cm 안쪽
ve.cut_through(hull, [(-0.60, 0.04), (0.60, 0.04), (0.56, RZ1 - RZ0 - 0.04), (-0.56, RZ1 - RZ0 - 0.04)], R0, (-1, 0, 0), RV)
ramp = ve.slab("ramp", ve.round_poly([(-0.64, 0.0), (0.64, 0.0), (0.60, RZ1 - RZ0), (-0.60, RZ1 - RZ0)], 0.07, 3),
               R0, (-1, 0, 0), RV, 0.045, mat=M["hull"], bevel=0.012, seg=1)
ve.paint(ramp, [TWO_TONE, BAND], slots=[M["hull"], M["hull_d"], M["teal"]])
V.to("hatch_rear", ramp)
V.to("hatch_rear", ve.slab("ramp_win", hw.stadium(0.42, 0.13, 6), ramp_pt(0.66), (-1, 0, 0), RV, 0.055, mat=M["lens"]))
V.to("hatch_rear", ve.text("ramp_mk", "진압반", 0.12, ramp_pt(0.28, 0, 0.045), RFR, mat=M["steel"], lift=0.002))
V.to("hatch_rear", ve.text("ramp_less", "비살상", 0.06, ramp_pt(0.47, 0, 0.045), RFR, mat=M["steel"], lift=0.002))
for sx in (1, -1):
    V.to("hatch_rear", ve.bar("ramp_grab", ramp_pt(0.18, sx * 0.48, 0.10), ramp_pt(0.55, sx * 0.48, 0.10), 0.016,
                              mat=M["steel"]))
    for h in (0.18, 0.55):
        V.to("hatch_rear", ve.bar("ramp_grab_post", ramp_pt(h, sx * 0.48, 0.04), ramp_pt(h, sx * 0.48, 0.105), 0.012,
                                  mat=M["steel"]))
for sx, nm in ((1, "light_tail_L"), (-1, "light_tail_R")):
    c = (sx * 0.84, 2.235, 1.32)
    V.body(ve.rbox("tl_house", c[0] - 0.08, c[0] + 0.08, c[1] - 0.06, c[1] + 0.035, c[2] - 0.13, c[2] + 0.13, r=0.03,
                   mat=M["gear"]))
    V.part(nm, c)
    V.to(nm, ve.rbox(nm + "_lens", c[0] - 0.055, c[0] + 0.055, c[1] + 0.03, c[1] + 0.045, c[2] - 0.10, c[2] + 0.10,
                     r=0.015, mat=M["tail"]))
    V.body(ve.rbox("rear_step", sx * 0.42 - 0.22, sx * 0.42 + 0.22, 2.20, 2.42, 0.40, 0.44, r=0.01, mat=M["gear"]))
V.body(hw.torus("rear_tow", 0.05, 0.016, loc=(0, 2.33, 0.47), rot=(90, 0, 0), seg=10, rseg=5, mat=M["steel"]))
V.body(ve.bar("exhaust_pipe", (-0.70, 2.05, 0.50), (-0.70, 2.36, 0.46), 0.045, verts=12, mat=M["gear"]))
V.body(hw.ycyl("exhaust_tip", 0.05, 2.33, 2.38, x=-0.70, z=0.464, verts=12, mat=M["steel"]))
V.empty("exhaust_1", (-0.70, 2.39, 0.46))

# ------------------------------------------------------------------ 포탑: 고양이 머리 (귀 = 확성기)
TY, TZ = -0.20, Z_ROOF + 0.05
RX, RY, RZ = 0.60, 0.55, 0.44


def head_pt(x, z, side=-1):
    """머리 돔 표면 점과 바깥 법선 (side=-1: 앞쪽 면, +1: 뒤쪽)."""
    q = 1 - (x / RX) ** 2 - (z / RZ) ** 2
    y = side * RY * math.sqrt(max(q, 0.0))
    n = (x / RX ** 2, y / RY ** 2, z / RZ ** 2)
    ln = math.sqrt(sum(a * a for a in n))
    return (x, TY + y, TZ + z), tuple(a / ln for a in n)


def head_side(y, z, sx):
    q = 1 - (y / RY) ** 2 - (z / RZ) ** 2
    x = sx * RX * math.sqrt(max(q, 0.0))
    n = (x / RX ** 2, y / RY ** 2, z / RZ ** 2)
    ln = math.sqrt(sum(a * a for a in n))
    return (x, TY + y, TZ + z), tuple(a / ln for a in n)


V.group("turret", (0, TY, TZ), props={"yawMin": -180, "yawMax": 180, "yawSpeed": 70})
V.to("turret", ve.dome("head", (0, TY, TZ), RX, RY, RZ, seg=28, rings=8, mat=M["hull"]))
V.to("turret", hw.zcyl("neck", 0.61, TZ - 0.02, TZ + 0.05, y=TY, verts=24, bevel=0.02, seg=1, mat=M["hull_d"]))
# 이마 띠 (밝은 덮개판)
V.to("turret", ve.dome("crown", (0, TY + 0.02, TZ + 0.265), RX * 0.66, RY * 0.70, RZ * 0.40, seg=20, rings=4,
                       mat=M["hull_l"]))
# 얼굴: 쌍둥이 카메라 눈 (아몬드형 렌즈 + 시안 점 + 하이라이트)
for sx in (1, -1):
    c, n = head_pt(sx * 0.17, 0.17)
    fr = ve.frame(n)
    almond = ve.round_poly([(-0.10, -0.05), (0.09, -0.06), (0.11, 0.05), (-0.07, 0.07)], 0.04, 3)
    if sx < 0:
        almond = [(-u, v) for u, v in reversed(almond)]
    c_in = tuple(c[i] - n[i] * 0.012 for i in range(3))
    V.to("turret", ve.slab("cam_eye", almond, c_in, fr["right"], fr["up"], 0.03, mat=M["lens"], bevel=0.008, seg=1))
    tip = tuple(c_in[i] + n[i] * 0.031 for i in range(3))
    V.to("turret", ve.decal(f"cam_dot{sx}", hw.circle(0.024, 12, cx=0.01 * sx), tip, fr, lift=0.0, mat=M["glow"]))
    V.to("turret", ve.decal(f"cam_hl{sx}", hw.circle(0.010, 8, cx=-0.03 * sx, cy=0.025), tip, fr, lift=0.0006,
                            mat=M["steel"]))
# 코·입 자리: 작은 확성기 그릴 (진압 방송)
c, n = head_pt(0.0, 0.03)
V.to("turret", ve.slab("mouth_grille", ve.round_poly([(-0.07, -0.025), (0.07, -0.025), (0.07, 0.025), (-0.07, 0.025)],
                                                      0.02, 2), tuple(c[i] - n[i] * 0.01 for i in range(3)),
                       ve.frame(n)["right"], ve.frame(n)["up"], 0.02, mat=M["gear"]))
# 이마 조준경 (포수 카메라): 귀 사이 작은 상자 + 시안 렌즈
V.to("turret", ve.rbox("sight_box", -0.075, 0.075, TY - 0.36, TY - 0.20, TZ + 0.33, TZ + 0.43, r=0.02, seg=2,
                       mat=M["gear"]))
V.to("turret", hw.ycyl("sight_lens", 0.032, TY - 0.368, TY - 0.355, z=TZ + 0.38, verts=14, mat=M["glow"]))
V.to("turret", hw.ycyl("sight_hood", 0.045, TY - 0.40, TY - 0.355, z=TZ + 0.38, verts=14, mat=M["gear"]))
# 귀: 둥근 삼각판 (앞면 = 확성기 판 + 슬롯)
for sx in (1, -1):
    bp, _ = head_side(-0.06, 0.29, sx)
    base = (bp[0] - sx * 0.10, bp[1], bp[2] - 0.01)
    ear = ve.slab("ear", ve.round_poly([(-0.17, 0.0), (0.17, 0.0), (0.02, 0.33)], [0.03, 0.03, 0.05], 3), base,
                  (1, 0, 0), (0, 0, 1), 0.08, mat=M["hull_l"], bevel=0.02, seg=1)
    inner = ve.slab("ear_in", ve.round_poly([(-0.115, 0.035), (0.115, 0.035), (0.017, 0.25)], 0.03, 3),
                    (base[0], base[1] - 0.080, base[2]), (1, 0, 0), (0, 0, 1), 0.010, mat=M["gear"])
    slots = [ve.slab(f"ear_slot{k}", hw.stadium(0.11 - k * 0.032, 0.014, 4),
                     (base[0], base[1] - 0.090, base[2] + 0.07 + k * 0.04), (1, 0, 0), (0, 0, 1), 0.003,
                     mat=M["steel"]) for k in range(3)]
    grp = [ear, inner] + slots
    ve.rot_about(grp, base, "Y", sx * 14)
    ve.rot_about(grp, base, "X", -6)
    V.to("turret", grp)
# 뒤 짐칸 + 최루탄 발사관 (짐칸 양옆 3관, 청록 마개 + 노랑 띠) + 안테나
V.to("turret", ve.rbox("bustle", -0.36, 0.36, TY + 0.40, TY + 0.72, TZ + 0.02, TZ + 0.29, r=0.05, seg=3, mat=M["gear"]))
V.to("turret", ve.rbox("bustle_lid", -0.32, 0.32, TY + 0.46, TY + 0.69, TZ + 0.28, TZ + 0.305, r=0.01, mat=M["hull_d"]))
for sx in (1, -1):
    for k in range(3):
        a = (sx * 0.35, TY + 0.46 + k * 0.095, TZ + 0.13)
        d = (sx * 0.55, -0.35, 0.76)
        b = tuple(a[i] + d[i] * 0.17 for i in range(3))
        V.to("turret", ve.bar("gas_tube", a, b, 0.036, verts=8, mat=M["gear"]))
        V.to("turret", ve.bar("gas_cap", b, tuple(b[i] + d[i] * 0.02 for i in range(3)), 0.038, verts=8, mat=M["teal"]))
        m = tuple(a[i] + d[i] * 0.11 for i in range(3))
        V.to("turret", ve.bar("gas_band", m, tuple(m[i] + d[i] * 0.02 for i in range(3)), 0.038, verts=8,
                              mat=M["hazard"]))
    V.empty(f"gas_tube_{'L' if sx > 0 else 'R'}", (sx * 0.47, TY + 0.55, TZ + 0.29), "turret",
            props={"fx": "teargas", "count": 3})
V.to("turret", ve.bar("t_ant", (-0.22, TY + 0.66, TZ + 0.29), (-0.24, TY + 0.74, TZ + 0.88), 0.006, r1=0.004, verts=5,
                      mat=M["gear"]))
V.to("turret", cb.sphere("t_ant_tip", radius=0.014, loc=(-0.24, TY + 0.745, TZ + 0.89), segments=8, rings=4,
                         material=M["glow"]))
for sx in (1, -1):       # 포탑 옆 엠블럼
    c, n = head_side(0.06, 0.15, sx)
    V.to("turret", ve.logo_disc(f"t_logo{sx}_", c, 0.13, ve.frame(n), disc=M["hull_d"], rim=M["gold"], mark=M["gold"],
                                lift=0.006))

# 포 받침 (gun_pitch): 머리 앞 아래를 가로지르는 받침대 = 수염 + 양옆 무기 받침판
GY, GZ = TY - 0.40, TZ + 0.13
V.group("gun_pitch", (0, GY, GZ), "turret", props={"pitchMin": -8, "pitchMax": 35, "pitchSpeed": 40})
V.to("gun_pitch", ve.bar("cradle", (-0.72, GY, GZ), (0.72, GY, GZ), 0.055, verts=16, mat=M["gear"]))
for sx in (1, -1):
    x0, x1 = sorted((sx * 0.63, sx * 0.73))
    V.to("gun_pitch", ve.rbox("cradle_plate", x0, x1, GY - 0.14, GY + 0.12, GZ - 0.10, GZ + 0.05, r=0.02,
                              mat=M["hull_d"]))
    x0, x1 = sorted((sx * 0.72, sx * 0.76))
    V.to("gun_pitch", hw.xcyl("cradle_cap", 0.065, x0, x1, y=GY, z=GZ, verts=16, mat=M["steel"]))
MOUNT_Z = GZ + 0.05
MX = 0.68
V.empty("mount_mr37a", (MX, GY, MOUNT_Z), "gun_pitch", aim=True,
        props={"weapon": "mount_mr37a", "model": "weapons/monatium/mount_mr37a.glb", "yawMin": 0, "yawMax": 0,
               "pitchMin": 0, "pitchMax": 0, "seat": "gunner"})
V.empty("muzzle_mr37a", (MX, GY - 0.585, MOUNT_Z + 0.085), "mount_mr37a")
V.empty("mount_water", (-MX, GY, MOUNT_Z), "gun_pitch", aim=True,
        props={"weapon": "mount_water_cannon", "model": "weapons/monatium/mount_water_cannon.glb", "yawMin": 0,
               "yawMax": 0, "pitchMin": 0, "pitchMax": 0, "seat": "gunner"})
V.empty("muzzle_water", (-MX, GY - 0.53, MOUNT_Z + 0.075), "mount_water")

# ------------------------------------------------------------------ 바퀴 + 차축·완충기 (정지)
V.wheel("wheel_FL", (X_W, Y_F, R_W), R_W, W_W, steer=1)
V.wheel("wheel_FR", (-X_W, Y_F, R_W), R_W, W_W, steer=1)
V.wheel("wheel_RL", (X_W, Y_R, R_W), R_W, W_W)
V.wheel("wheel_RR", (-X_W, Y_R, R_W), R_W, W_W)
for y in (Y_F, Y_R):
    V.body(ve.bar("axle", (-0.70, y, R_W), (0.70, y, R_W), 0.07, verts=12, mat=M["gear"]))
    for sx in (1, -1):
        V.body(ve.bar("damper", (sx * 0.62, y + 0.10, R_W + 0.02), (sx * 0.66, y + 0.18, 0.74), 0.04, verts=10,
                      mat=M["steel"]))

# ------------------------------------------------------------------ 실내: 계기판 + 조향 고리 (좌석 시점에서 보임)
V.body(ve.rbox("dash", -0.86, 0.86, -1.72, -1.46, 1.02, 1.20, r=0.03, mat=M["cabin"]))
V.body(ve.rbox("dash_top", -0.86, 0.86, -1.70, -1.44, 1.19, 1.22, r=0.01, mat=M["gear"]))
for sx in (1, -1):
    V.body(ve.slab("dash_screen", ve.round_poly([(-0.12, -0.05), (0.12, -0.05), (0.12, 0.05), (-0.12, 0.05)], 0.02, 2),
                   (sx * 0.44, -1.462, 1.11), (1, 0, 0), (0, 0.45, 0.89), 0.006, mat=M["lens"]))
    for k in range(4):
        V.body(ve.decal(f"dash_bar{sx}{k}", [(-0.10 + k * 0.055, -0.03), (-0.07 + k * 0.055, -0.03),
                                             (-0.07 + k * 0.055, -0.03 + 0.02 * (k + 1)), (-0.10 + k * 0.055, -0.03 + 0.02 * (k + 1))],
                        (sx * 0.44, -1.4565, 1.113), dict(right=(1, 0, 0), up=(0, 0.45, 0.89)), lift=0.0,
                        mat=M["glow"]))
V.body(hw.torus("steer_ring", 0.10, 0.014, loc=(0.44, -1.43, 1.13), rot=(-55, 0, 0), seg=12, rseg=5, mat=M["rubber"]))
V.body(ve.bar("steer_col", (0.44, -1.43, 1.13), (0.44, -1.55, 1.04), 0.020, mat=M["gear"]))

# ------------------------------------------------------------------ 좌석·승하차 (엘프 눈높이 = 좌석면 + 0.60 m)
# 운전석·지휘석 눈: 앞 유리(경사면 z 1.33~1.60)가 눈보다 높으면 하늘만 보인다. 방석을 높여 눈을 유리 가운데 높이로,
# 유리 쪽으로 당겨 길이 3~4 m 앞부터 보이게 한다 (머리는 지붕에 닿지만 1인칭에서는 보이지 않는다)
V.empty("seat_driver", (0.44, -1.30, 1.48), props={"controls": "drive"})
V.empty("seat_commander", (-0.44, -1.30, 1.48))
V.empty("seat_gunner", (0.0, TY - 0.42, TZ + 0.38), "turret",
        props={"controls": "turret,gun_pitch,mount_mr37a,mount_water,gas_tube_L,gas_tube_R", "view": "turret_camera"})
for i, (x, y) in enumerate(((0.50, 0.25), (-0.50, 0.25), (0.50, 1.05), (-0.50, 1.05)), 1):
    V.empty(f"seat_passenger_{i}", (x, y, 1.40), props={"facing": "inward"})
# 해치에 선 지휘관 (AI): 뒤 지붕 해치 구멍 가운데, 테 윗면 높이. -Y가 정면 (seat_*와 같다)
V.empty("crew_commander", (0.0, HY, Z_ROOF + 0.035))
V.empty("enter_driver", (1.55, -0.40, 0.0))
V.empty("enter_commander", (-1.55, -0.40, 0.0))
V.empty("enter_gunner", (0.0, 3.30, 0.0))
for i, (x, y) in enumerate(((0.45, 3.30), (-0.45, 3.30), (0.45, 3.80), (-0.45, 3.80)), 1):
    V.empty(f"enter_passenger_{i}", (x, y, 0.0))

# ------------------------------------------------------------------ 충돌
pts = []
for (y, z) in SIDE:
    hx = HX if z <= Z_SH + 0.01 else HX_TOP
    pts += [(hx, y, z), (-hx, y, z)]
V.col_hull("COL_hull", pts)
V.col("COL_plow", -1.02, 1.02, PY - 0.10, -2.20, 0.42, 0.86)
V.col_hull("COL_turret", [(sx * RX, TY + dy, TZ - 0.02) for sx in (1, -1) for dy in (-RY, 0.72)]
           + [(sx * 0.42, TY + dy, TZ + RZ) for sx in (1, -1) for dy in (-0.38, 0.38)], parent="turret")

V.finish("vehicles/monatium/monatium_riot_apc.glb", budget=22000, outline=0.010, props={
    "vehicleClass": "wheeled", "mass": 7800, "maxSpeed": 25.0, "wheelbase": round(Y_R - Y_F, 3),
    "track": round(2 * X_W, 3), "armor": "medium", "faction": "monatium", "crew": 3, "passengers": 4,
    "displayName": "MRV-1 '요람' 진압 장갑차",
})
