"""모나티엄 진압반 MRV-3 '괭이잠' 정찰 사이드카 (3륜).

[원작] 진압반장 칸나는 바이크를 탄다(엘레나 작중 행적: 범인 때문에 '칸나의 바이크'가 고구마가 되고 포셔에게 저당잡힘).
       모나티엄은 '최신식 이륜구동 스피드 머신 썬더볼트 4.1 알파'(슈팡의 세그웨이)를 만들고, 경찰차량을 굴린다.
       엘프의 지상 탈것으로 호버 차량은 원작에 나오지 않는다 → 바퀴 달린 내연기관 오토바이 계열로 정했다.
[오리지널] 특수작전부·정찰조가 타는 사이드카. 오토바이(운전수 + 뒷자리)와 사이드카(사수)에 엘프 3명이 탄다.
           '괭이잠'(고양이처럼 얕게 자며 늘 깨어 있는 잠). 전조등 위의 고양이 귀(방향지시등), 둥근 연료통의 엘프 로고,
           사이드카 앞 회전대에 MR-12 '토닥토닥' 고무탄 경기관총.

배치: 오토바이는 차량 왼쪽(+X), 사이드카는 오른쪽(-X). 바퀴 셋: wheel_FL(앞, 조향), wheel_RL(뒤, 구동), wheel_RR(사이드카).
규약: docs/art/VEHICLES.md, 설정: docs/art/vehicles-elf.md
npm run model -- art/blender/vehicles/monatium/monatium_scout.py
npm run shot -- vehicles/monatium/monatium_scout.glb --views front,34,side,top
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import vehicles_elf as ve  # noqa: E402

cb.reset()
V = ve.Veh("monatium_scout", "monatium")
M = V.M

BX = 0.40                 # 오토바이 중심선 (원점 = 세 바퀴 발자국의 가운데)
SX = -0.32                # 사이드카 중심선
R_B, W_B = 0.27, 0.13     # 오토바이 바퀴
R_S, W_S = 0.25, 0.12     # 사이드카 바퀴
YF, YR = -0.74, 0.62      # 앞·뒤 바퀴 (축거 1.36)
YS, XS = 0.24, -0.66      # 사이드카 바퀴


def tube(name, pts, r, mat, verts=8):
    sec = [(math.cos(2 * math.pi * k / verts) * r, math.sin(2 * math.pi * k / verts) * r) for k in range(verts)]
    return hw.sweep(name, pts, sec, side_vec=(1, 0, 0), cap=True, mat=mat, smooth=60)


# ================================================================== 오토바이
# 차대 (어두운 관)
HEAD = (BX, -0.46, 0.80)              # 조향 머리
for nm, pts in (
    ("frame_top", [HEAD, (BX, -0.20, 0.70), (BX, 0.20, 0.60), (BX, 0.56, 0.62)]),
    ("frame_down", [HEAD, (BX, -0.40, 0.42), (BX, -0.24, 0.22), (BX, 0.30, 0.22), (BX, 0.62, R_B)]),
):
    V.body(tube(nm, pts, 0.022, M["gear"]))
for sx in (1, -1):
    V.body(ve.bar("swingarm", (BX + sx * 0.07, 0.20, 0.25), (BX + sx * 0.07, YR, R_B), 0.020, mat=M["gear"]))
    V.body(ve.bar("shock", (BX + sx * 0.07, 0.50, 0.34), (BX + sx * 0.07, 0.40, 0.60), 0.022, mat=M["steel"]))
V.body(hw.xcyl("axle_r", 0.028, BX - 0.09, BX + 0.09, y=YR, z=R_B, verts=10, mat=M["steel"]))

# 엔진: 박서 2기통 (양옆으로 튀어나온 실린더 + 냉각 핀)
V.body(ve.rbox("crankcase", BX - 0.10, BX + 0.10, -0.24, 0.18, 0.20, 0.44, r=0.05, seg=2, mat=M["gear"]))
for sx in (1, -1):
    x0 = BX + sx * 0.10
    x1 = BX + sx * 0.25
    V.body(hw.xcyl("cyl", 0.075, min(x0, x1), max(x0, x1), y=-0.12, z=0.36, verts=14, mat=M["gear"]))
    for k in range(4):
        xf = BX + sx * (0.12 + k * 0.032)
        V.body(hw.xcyl("fin", 0.090, xf - 0.007, xf + 0.007, y=-0.12, z=0.36, verts=14, mat=M["gear"]))
    xh0, xh1 = sorted((BX + sx * 0.25, BX + sx * 0.29))
    V.body(hw.xcyl("head", 0.072, xh0, xh1, y=-0.12, z=0.36, verts=14, bevel=0.01, seg=1, mat=M["steel"]))
    # 배기관 (실린더 앞 → 아래 → 뒤)
    ex = BX + sx * 0.20
    V.body(tube("exhaust", [(ex, -0.20, 0.33), (ex, -0.26, 0.22), (ex, 0.10, 0.17), (BX + sx * 0.14, 0.64, 0.29)],
                0.022, M["gear"]))
    V.body(hw.ycyl("muffler", 0.042, 0.62, 0.90, x=BX + sx * 0.14, z=0.30, verts=12, r2=0.036, mat=M["hull_d"]))
    V.body(hw.ycyl("muffler_tip", 0.030, 0.90, 0.93, x=BX + sx * 0.14, z=0.30, verts=12, mat=M["steel"]))
V.empty("exhaust_1", (BX + 0.14, 0.93, 0.30))
V.empty("exhaust_2", (BX - 0.14, 0.93, 0.30))

# 연료통: 둥근 남보라 덩어리 + 청록 줄 + 금색 엘프 로고
tank = ve.sculpt("tank", ve.round_poly([(-0.44, 0.70), (-0.06, 0.64), (-0.04, 0.80), (-0.36, 0.86), (-0.46, 0.80)],
                                       [0.04, 0.05, 0.06, 0.08, 0.05], 3),
                 hw.rrect(0.25, 0.30, 0.09, 3, cx=BX, cy=0.75), bevel=0.012, seg=2, mat=M["hull"])
ve.paint(tank, [(M["teal"], lambda c, n: 0.738 < c.z < 0.758 and abs(n.z) < 0.7, [("z", 0.738), ("z", 0.758)])],
         slots=[M["hull"], M["teal"]])
V.body(tank)
V.body(hw.zcyl("tank_cap", 0.03, 0.85, 0.875, x=BX, y=-0.30, verts=12, mat=M["steel"]))
V.body(ve.logo_disc("tank_", (BX + 0.125, -0.23, 0.79), 0.085, ve.SIDE_L, disc=M["hull_d"], rim=M["gold"],
                    mark=M["gold"], lift=0.002))
V.body(ve.logo_disc("tankR_", (BX - 0.125, -0.23, 0.79), 0.085, ve.SIDE_R, disc=M["hull_d"], rim=M["gold"],
                    mark=M["gold"], lift=0.002))

# 안장 + 뒷자리 + 짐받이(무전기·안테나)
saddle = ve.sculpt("saddle", ve.round_poly([(-0.10, 0.62), (0.40, 0.62), (0.42, 0.70), (0.18, 0.70), (0.08, 0.74),
                                            (-0.08, 0.70)], [0.02, 0.02, 0.03, 0.06, 0.06, 0.04], 3),
                   hw.rrect(0.22, 0.20, 0.07, 3, cx=BX, cy=0.68), bevel=0.01, seg=2, mat=M["rubber"])
V.body(saddle)
V.body(ve.rbox("rack", BX - 0.10, BX + 0.10, 0.44, 0.78, 0.70, 0.72, mat=M["gear"]))
V.body(ve.rbox("radio", BX - 0.08, BX + 0.08, 0.58, 0.76, 0.72, 0.86, r=0.02, seg=2, mat=M["hull_d"]))
V.body(ve.rbox("radio_face", BX - 0.06, BX + 0.06, 0.759, 0.764, 0.75, 0.83, mat=M["lens"]))
for k in range(3):
    V.body(ve.rbox("radio_led", BX - 0.04 + k * 0.03, BX - 0.03 + k * 0.03, 0.764, 0.766, 0.81, 0.82, mat=M["glow"]))
V.body(ve.bar("radio_ant", (BX + 0.05, 0.70, 0.86), (BX + 0.07, 0.86, 1.80), 0.005, r1=0.003, verts=5, mat=M["gear"]))
V.body(cb.sphere("radio_ant_tip", radius=0.014, loc=(BX + 0.07, 0.862, 1.81), segments=8, rings=4, material=M["glow"]))
# 바깥쪽 가방 (짐가방)
V.body(ve.rbox("pannier", BX + 0.13, BX + 0.25, 0.40, 0.80, 0.36, 0.62, r=0.04, seg=2, mat=M["gear"]))
V.body(ve.rbox("pannier_lid", BX + 0.125, BX + 0.255, 0.42, 0.78, 0.56, 0.64, r=0.03, seg=2, mat=M["hull_d"]))
V.body(ve.text("pannier_mk", "정찰", 0.045, (BX + 0.256, 0.60, 0.46), ve.SIDE_L, mat=M["steel"], lift=0.002))
# 발판
for sx in (1, -1):
    V.body(ve.rbox("footboard", BX + sx * 0.10 - 0.05, BX + sx * 0.10 + 0.05, -0.02, 0.24, 0.26, 0.28, mat=M["gear"]))

# 앞 포크 + 펜더
for sx in (1, -1):
    V.body(ve.bar("fork", (BX + sx * 0.06, -0.48, 0.82), (BX + sx * 0.08, YF, R_B), 0.019, mat=M["steel"]))
V.body(hw.xcyl("axle_f", 0.022, BX - 0.10, BX + 0.10, y=YF, z=R_B, verts=10, mat=M["steel"]))
fpath = [(BX, YF + math.cos(math.radians(a)) * 0.315, R_B + math.sin(math.radians(a)) * 0.315) for a in range(10, 171, 16)]
V.body(hw.sweep("fender_f", fpath, [(0.085, -0.012), (0.075, 0.018), (-0.075, 0.018), (-0.085, -0.012)],
                side_vec=(1, 0, 0), cap=True, mat=M["hull"], smooth=50))
rpath = [(BX, YR + math.cos(math.radians(a)) * 0.31, R_B + math.sin(math.radians(a)) * 0.31) for a in range(20, 141, 15)]
V.body(hw.sweep("fender_r", rpath, [(0.09, -0.012), (0.08, 0.018), (-0.08, 0.018), (-0.09, -0.012)],
                side_vec=(1, 0, 0), cap=True, mat=M["hull"], smooth=50))

# 전조등 머리 (고양이 머리: 둥근 덮개 + 귀 모양 방향지시등) + 작은 바람막이
NC = (BX, -0.60, 0.88)
V.body(cb.sphere("nacelle", radius=0.12, loc=NC, scale=(1.05, 1.0, 0.92), segments=18, rings=10, material=M["hull"]))
V.body(hw.ycyl("hl_rim", 0.085, NC[1] - 0.115, NC[1] - 0.08, x=BX, z=NC[2] - 0.01, verts=16, mat=M["gear"]))
V.part("light_head_L", (BX, NC[1] - 0.12, NC[2] - 0.01))
V.to("light_head_L", hw.ycyl("hl_lens", 0.070, NC[1] - 0.125, NC[1] - 0.112, x=BX, z=NC[2] - 0.01, verts=16,
                             mat=M["lamp"]))
for sx in (1, -1):
    base = (BX + sx * 0.075, NC[1] - 0.02, NC[2] + 0.08)
    ear = ve.slab("nc_ear", ve.round_poly([(-0.045, 0.0), (0.045, 0.0), (0.005, 0.085)], [0.01, 0.01, 0.015], 2),
                  base, (1, 0, 0), (0, 0, 1), 0.035, mat=M["hull"], bevel=0.006, seg=1)
    inner = ve.slab("nc_ear_in", ve.round_poly([(-0.028, 0.012), (0.028, 0.012), (0.004, 0.064)], 0.008, 2),
                    (base[0], base[1] - 0.036, base[2]), (1, 0, 0), (0, 0, 1), 0.004, mat=M["hazard"])
    grp = [ear, inner]
    ve.rot_about(grp, base, "Y", sx * 18)
    V.body(grp)
V.body(ve.slab("screen", ve.round_poly([(-0.13, 0.0), (0.13, 0.0), (0.11, 0.17), (-0.11, 0.17)], 0.04, 2),
               (BX, NC[1] + 0.02, NC[2] + 0.08), (1, 0, 0), (0, -0.30, 0.95), 0.006, mat=M["glass"]))
# 핸들 + 손잡이 + 거울
HB = [(BX + 0.27, -0.30, 0.96), (BX + 0.16, -0.40, 0.94), (BX, -0.44, 0.92), (BX - 0.16, -0.40, 0.94),
      (BX - 0.27, -0.30, 0.96)]
V.body(tube("handlebar", HB, 0.014, M["steel"]))
V.body(ve.bar("riser", (BX, -0.46, 0.82), (BX, -0.44, 0.92), 0.02, mat=M["gear"]))
for sx in (1, -1):
    V.body(ve.bar("grip", (BX + sx * 0.20, -0.36, 0.95), (BX + sx * 0.28, -0.295, 0.962), 0.019, mat=M["rubber"]))
    V.body(ve.bar("mirror_stem", (BX + sx * 0.18, -0.38, 0.95), (BX + sx * 0.28, -0.40, 1.03), 0.007, verts=6,
                  mat=M["gear"]))
    V.body(cb.sphere("mirror", radius=0.040, loc=(BX + sx * 0.29, -0.40, 1.045), scale=(1.0, 0.35, 0.8), segments=10,
                     rings=5, material=M["gear"]))
# 계기판 (운전수 시점)
V.body(hw.zcyl("gauge", 0.045, 0.94, 0.965, x=BX, y=-0.48, verts=14, mat=M["gear"]))
V.body(ve.decal("gauge_face", hw.circle(0.036, 14), (BX, -0.48, 0.966), ve.FACE_T, lift=0.0, mat=M["lens"]))
V.body(ve.decal("gauge_arc", [(-0.025, 0.004), (-0.004, 0.022), (0.002, 0.016), (-0.019, 0.0)], (BX, -0.48, 0.967),
                ve.FACE_T, lift=0.0, mat=M["glow"]))
# 후미등
V.part("light_tail_L", (BX, YR + 0.33, 0.62))
V.to("light_tail_L", ve.rbox("tail_lens", BX - 0.04, BX + 0.04, YR + 0.315, YR + 0.335, 0.60, 0.645, r=0.008,
                             mat=M["tail"]))
V.body(ve.text("plate", "모-0912", 0.04, (BX, YR + 0.30, 0.52), ve.FACE_B, mat=M["steel"], lift=0.003))
V.body(ve.rbox("plate_bg", BX - 0.09, BX + 0.09, YR + 0.27, YR + 0.30, 0.49, 0.55, mat=M["hull_d"]))

# ================================================================== 사이드카
TUB_SIDE = [(-0.72, 0.45), (-0.52, 0.26), (0.42, 0.24), (0.62, 0.34), (0.61, 0.60), (0.42, 0.69), (-0.22, 0.69),
            (-0.56, 0.60)]
tub_r = [0.12, 0.14, 0.10, 0.10, 0.10, 0.12, 0.16, 0.14]
TUB_SEC = [(-0.19, 0.24), (0.19, 0.24), (0.31, 0.37), (0.30, 0.56), (0.19, 0.69), (-0.19, 0.69), (-0.30, 0.56),
           (-0.31, 0.37)]
tub = ve.sculpt("tub", ve.round_poly(TUB_SIDE, tub_r, 3), ve.round_poly(TUB_SEC, 0.07, 3),
                x_center=SX, bevel=0.015, seg=2, mat=M["hull"])
ve.paint(tub, [(M["hull_d"], lambda c, n: c.z < 0.40, [("z", 0.40)]),
               (M["teal"], lambda c, n: 0.50 < c.z < 0.555 and abs(n.z) < 0.6, [("z", 0.50), ("z", 0.555)])],
         slots=[M["hull"], M["hull_d"], M["teal"]])
ve.shell(tub, 0.025, M["cabin"])
COCK = hw.stadium(0.62, 0.40, 5, cx=0.12)          # (y, x) 순서가 아니라 (u=Y, v=X)를 아래에서 바꾼다
cock_pts = [(SX + v, u) for u, v in COCK]
ve.cut(tub, ve.plate("cock_cut", cock_pts, 0.6, (0, 0, 0.66), axis="Z"))
V.body(tub)
V.body(ve.loop_frame("cock_rim", [(x - SX, y) for x, y in cock_pts], (SX, 0, 0.665), (1, 0, 0), (0, 1, 0), r=0.016,
                     lift=0.0, mat=M["rubber"], verts=6))
V.body(ve.rbox("tub_floor", SX - 0.24, SX + 0.24, -0.20, 0.50, 0.26, 0.30, mat=M["cabin"]))
V.body(ve.rbox("tub_seat", SX - 0.18, SX + 0.18, 0.12, 0.38, 0.30, 0.40, r=0.03, seg=2, mat=M["rubber"]))
V.body(ve.rbox("tub_back", SX - 0.18, SX + 0.18, 0.38, 0.45, 0.36, 0.62, r=0.03, seg=2, mat=M["rubber"]))
# 바깥 옆면: 엘프 로고(금) + 띠 글자 + 번호
frR = ve.SIDE_R
V.body(ve.logo_disc("tub_", (SX - 0.307, 0.06, 0.45), 0.14, frR, disc=M["hull_d"], rim=M["gold"], mark=M["gold"],
                    lift=0.003))
V.body(ve.text("tub_less", "비살상", 0.040, (SX - 0.301, -0.30, 0.527), frR, mat=M["steel"], lift=0.003))
V.body(ve.text("tub_unit", "진압반 특수작전부", 0.034, (SX - 0.301, 0.36, 0.527), frR, mat=M["steel"], lift=0.003))
V.body(ve.text("tub_no", "MRV-3", 0.05, (SX - 0.307, -0.38, 0.44), frR, mat=M["steel"], lift=0.003))
# 앞 코: 회전대 기둥 + 작은 등
V.body(hw.zcyl("pintle_post", 0.032, 0.62, 0.80, x=SX, y=-0.32, verts=12, mat=M["gear"]))
V.body(hw.zcyl("pintle_collar", 0.045, 0.79, 0.81, x=SX, y=-0.32, verts=14, mat=M["steel"]))
V.body(ve.bar("pintle_brace", (SX, -0.40, 0.60), (SX, -0.32, 0.74), 0.018, mat=M["gear"]))
V.body(hw.ycyl("nose_light_house", 0.05, -0.68, -0.60, x=SX, z=0.47, verts=12, mat=M["gear"]))
V.part("light_head_R", (SX, -0.685, 0.47))
V.to("light_head_R", hw.ycyl("nose_lens", 0.038, -0.69, -0.678, x=SX, z=0.47, verts=12, mat=M["lamp"]))
# 뒤: 예비 바퀴 + 후미등 + 손잡이
SP = (SX, 0.66, 0.50)
V.body(ve.lathe("spare", ve.tire_profile(0.20, 0.10), SP, axis="Y", seg=16, mat=M["rubber"], smooth=50))
V.body(hw.ycyl("spare_hub", 0.12, SP[1] - 0.04, SP[1] + 0.045, x=SX, z=SP[2], verts=14, mat=M["hull_d"]))
V.body(hw.ycyl("spare_cap", 0.045, SP[1] + 0.04, SP[1] + 0.06, x=SX, z=SP[2], verts=10, mat=M["steel"]))
V.body(ve.bar("spare_arm", (SX, 0.58, 0.50), (SX, 0.62, 0.50), 0.03, mat=M["gear"]))
V.part("light_tail_R", (SX - 0.22, 0.60, 0.55))
V.to("light_tail_R", ve.rbox("tub_tail", SX - 0.25, SX - 0.19, 0.585, 0.615, 0.53, 0.57, r=0.006, mat=M["tail"]))
V.body(ve.bar("grab", (SX + 0.20, 0.30, 0.72), (SX + 0.20, -0.06, 0.72), 0.012, mat=M["steel"]))
for y in (0.30, -0.06):
    V.body(ve.bar("grab_post", (SX + 0.20, y, 0.67), (SX + 0.20, y, 0.72), 0.010, mat=M["steel"]))
# 사이드카 연결대 (차대 ↔ 통)
for y in (-0.30, 0.38):
    V.body(ve.bar("strut", (BX - 0.02, y, 0.24), (SX + 0.22, y, 0.30), 0.022, mat=M["gear"]))
V.body(ve.bar("strut_diag", (BX - 0.02, -0.40, 0.42), (SX + 0.25, -0.20, 0.36), 0.018, mat=M["gear"]))
# 사이드카 바퀴 팔 + 펜더
V.body(ve.bar("s_arm", (SX - 0.20, -0.05, 0.30), (XS + 0.06, YS, R_S), 0.022, mat=M["gear"]))
V.body(hw.xcyl("s_axle", 0.022, XS, XS + 0.10, y=YS, z=R_S, verts=10, mat=M["steel"]))
spath = [(XS, YS + math.cos(math.radians(a)) * 0.29, R_S + math.sin(math.radians(a)) * 0.29) for a in range(15, 166, 15)]
V.body(hw.sweep("fender_s", spath, [(0.085, -0.012), (0.075, 0.016), (-0.075, 0.016), (-0.085, -0.012)],
                side_vec=(1, 0, 0), cap=True, mat=M["hull"], smooth=50))
V.body(ve.bar("fender_s_stay", (XS + 0.06, YS - 0.20, 0.40), (SX - 0.24, YS - 0.20, 0.45), 0.012, mat=M["gear"]))

# 거치 무기: MR-12 '토닥토닥' (사이드카 사수)
MZ = 0.81 + 0.09                 # 트러니언 높이 (핀 받침 0.81 + 무기 pivotDrop 0.09)
V.empty("mount_mr12", (SX, -0.32, MZ), aim=True,
        props={"weapon": "mount_mr12", "model": "weapons/monatium/mount_mr12.glb", "yawMin": -100, "yawMax": 30,
               "pitchMin": -10, "pitchMax": 45, "seat": "gunner"})
V.empty("muzzle_mr12", (SX, -0.32 - 0.515, MZ + 0.025), "mount_mr12")

# ================================================================== 바퀴
V.wheel("wheel_FL", (BX, YF, R_B), R_B, W_B, steer=1, side=1, props={"drive": 0})
V.wheel("wheel_RL", (BX, YR, R_B), R_B, W_B, side=1, props={"drive": 1})
V.wheel("wheel_RR", (XS, YS, R_S), R_S, W_S, side=-1, props={"drive": 0})

# ================================================================== 좌석·승하차 (엘프 눈높이 = 좌석면 + 0.60 m)
V.empty("seat_driver", (BX, -0.02, 1.30), props={"controls": "drive", "pose": "ride"})
V.empty("seat_passenger_1", (BX, 0.30, 1.30), props={"pose": "ride"})
V.empty("seat_gunner", (SX, 0.06, 1.01), props={"controls": "mount_mr12", "pose": "sit"})
V.empty("enter_driver", (BX + 0.75, 0.00, 0.0))
V.empty("enter_passenger_1", (BX + 0.75, 0.45, 0.0))
V.empty("enter_gunner", (SX - 0.80, 0.05, 0.0))

# ================================================================== 충돌
V.col("COL_bike", BX - 0.20, BX + 0.20, YF - 0.30, YR + 0.32, 0.02, 0.96)
V.col_hull("COL_tub", [(SX + sx * 0.30, y, z) for sx in (1, -1) for (y, z) in TUB_SIDE])
V.col("COL_link", SX + 0.25, BX - 0.18, -0.40, 0.45, 0.20, 0.36)

V.finish("vehicles/monatium/monatium_scout.glb", budget=15000, outline=0.008, props={
    "vehicleClass": "wheeled", "mass": 380, "maxSpeed": 30.0, "wheelbase": round(YR - YF, 3),
    "track": round(BX - XS, 3), "armor": "light", "faction": "monatium", "crew": 2, "passengers": 1,
    "wheelLayout": "sidecar", "displayName": "MRV-3 '괭이잠' 정찰 사이드카",
})
