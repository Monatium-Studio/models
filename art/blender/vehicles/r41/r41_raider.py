"""R41 V-7 '나나니' 고속 습격차 (4x4).

[원작] 엘리아스 침공전에서 R41은 드론 물량전을 벌인다(유령 늪). 리뉴아(R41)의 별칭 "시공의 검은 말벌".
[오리지널] 드론 조작병과 사수를 태우고 전선 사이를 달리는 경량 습격차. 나나니벌처럼 실처럼 가는 허리(구동축 관)로
           앞 조종칸(머리·가슴)과 뒤 엔진 꼬투리(배)가 이어진다. 배 위에는 D-1 '모기' 군집 드론 7기를 담은
           벌집 발사함, 롤케이지 위 회전대에 M-4 '호박벌' 경기관총. 긴 행정의 다리 같은 서스펜션.

좌석: 운전수(왼쪽), 드론 조작병(오른쪽, 오각 화면), 사수(허리 위 발판에 서서 쏨).
규약: docs/art/VEHICLES.md, 설정: docs/art/vehicles-elf.md
npm run model -- art/blender/vehicles/r41/r41_raider.py
npm run shot -- vehicles/r41/r41_raider.glb --views front,34,side,top
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import r41  # noqa: E402
import vehicles_elf as ve  # noqa: E402

cb.reset()
V = ve.Veh("r41_raider", "r41")
M = V.M

R_W, W_W = 0.36, 0.26
YF, YR = -1.10, 0.98
X_W = 0.80

# ------------------------------------------------------------------ 조종칸 (머리·가슴): 모따기 통, 위가 열림
TUB_SIDE = [(-1.30, 0.36), (-1.66, 0.56), (-1.60, 0.78), (-1.05, 0.90), (0.16, 0.92), (0.16, 0.40)]
TUB_SEC = [(-0.48, 0.36), (0.48, 0.36), (0.62, 0.55), (0.62, 0.80), (0.54, 0.92), (-0.54, 0.92), (-0.62, 0.80),
           (-0.62, 0.55)]
tub = ve.facet("tub", TUB_SIDE, TUB_SEC, ch=0.02, mat=M["light"])
ve.paint(tub, [(M["shell"], lambda c, n: c.z < 0.55, [("z", 0.55)]),
               (M["amber"], lambda c, n: 0.70 < c.z < 0.725 and abs(n.z) < 0.5, [("z", 0.70), ("z", 0.725)])],
         slots=[M["light"], M["shell"], M["amber"]])
ve.shell(tub, 0.03, M["cabin"])
COCK = [(-0.52, -0.90), (0.52, -0.90), (0.54, 0.12), (-0.54, 0.12)]
ve.cut(tub, ve.plate("cock_cut", ve.round_poly(COCK, 0.05, 1), 0.6, (0, 0, 0.95), axis="Z"))
V.body(tub)
V.body(ve.rbox("floor", -0.50, 0.50, -0.95, 0.10, 0.38, 0.42, mat=M["cabin"]))
for sx in (1, -1):
    V.body(ve.rbox("seat", sx * 0.28 - 0.17, sx * 0.28 + 0.17, -0.30, 0.02, 0.42, 0.56, r=0.02, mat=M["polymer"]))
    V.body(ve.rbox("seat_back", sx * 0.28 - 0.17, sx * 0.28 + 0.17, 0.02, 0.08, 0.50, 0.86, r=0.02, mat=M["polymer"]))
# 계기판 + 운전 막대 + 조작병의 오각 화면
V.body(ve.rbox("dash", -0.52, 0.52, -0.95, -0.78, 0.62, 0.86, r=0.02, mat=M["cabin"]))
V.body(ve.bar("wheel_col", (0.28, -0.80, 0.80), (0.28, -0.62, 0.92), 0.02, verts=6, mat=M["shell"]))
V.body(r41.tube("steer", 0.11, 0.09, 0.025, (0.28, -0.60, 0.93), axis="Y", verts=6, mat=M["shell"]))
V.body(ve.bar("tablet_arm", (-0.28, -0.82, 0.86), (-0.28, -0.66, 1.00), 0.015, verts=6, mat=M["shell"]))
V.body(r41.ngon_prism("tablet", 5, 0.12, 0.025, (-0.28, -0.64, 1.02), axis="Y", rot_deg=90, mat=M["shell"]))
V.body(r41.ngon_prism("tablet_screen", 5, 0.10, 0.006, (-0.28, -0.624, 1.02), axis="Y", rot_deg=90, mat=M["glow_dim"]))
# 낮은 앞 유리 (각진 창틀 + 연기색 유리)
WS = [(-0.50, 0.0), (0.50, 0.0), (0.46, 0.20), (-0.46, 0.20)]
ws_o = (0, -0.96, 0.92)
V.body(ve.slab("windscreen", WS, ws_o, (1, 0, 0), (0, 0.45, 0.89), 0.008, mat=M["glass"]))
V.body(ve.loop_frame("ws_frame", WS, ws_o, (1, 0, 0), (0, 0.45, 0.89), r=0.018, lift=0.004, mat=M["shell"], verts=6))
# 옆: 엘프 로고 + 막대 부호 + 번호
for sx in (1, -1):
    V.body(r41.elf_logo(f"side{sx}_", (sx * 0.621, -0.55, 0.66), 0.20, axis="X", sign=sx, mat=M["shell"]))
    V.body(r41.stencil_bars(f"side{sx}_", (sx * 0.621, -1.05, 0.80), axis="X", sign=sx, h=0.04, unit=0.02,
                            mat=M["shell"]))
    V.body(ve.text(f"no{sx}", "V-7", 0.07, (sx * 0.621, -0.10, 0.80), ve.frame((sx, 0, 0)), mat=M["shell"], lift=0.001))

# 머리: 육각 전조등 + 큰턱 범퍼
for sx, nm in ((1, "light_head_L"), (-1, "light_head_R")):
    c = (sx * 0.40, -1.62, 0.68)
    V.body(r41.ngon_prism("hl_house", 6, 0.085, 0.10, (c[0], c[1] + 0.05, c[2]), axis="Y", rot_deg=0, mat=M["shell"],
                          ch=0.006))
    V.part(nm, c)
    V.to(nm, r41.ngon_prism(nm + "_lens", 6, 0.065, 0.015, (c[0], c[1] - 0.005, c[2]), axis="Y", rot_deg=0,
                            mat=M["glow_amber"]))
    V.body(ve.bar("mandible", (sx * 0.30, -1.55, 0.40), (sx * 0.26, -1.86, 0.44), 0.04, verts=6, mat=M["shell"]))
    V.body(ve.bar("mandible_tip", (sx * 0.26, -1.86, 0.44), (sx * 0.12, -1.98, 0.52), 0.032, r1=0.012, verts=6,
                  mat=M["shell"]))
    V.body(ve.bar("mandible_band", (sx * 0.28, -1.74, 0.425), (sx * 0.27, -1.80, 0.43), 0.045, verts=6, mat=M["amber"]))
V.body(ve.bar("bumper", (-0.32, -1.62, 0.44), (0.32, -1.62, 0.44), 0.035, verts=6, mat=M["shell"]))

# ------------------------------------------------------------------ 실 허리 (가는 구동축 관) + 사수 발판
WAIST = [(0.10, 0.36, 0.22, 0.64), (0.22, 0.16, 0.12, 0.62), (0.52, 0.16, 0.12, 0.62), (0.64, 0.36, 0.22, 0.66)]
V.body(r41.loft("waist", WAIST, mat=M["shell"]))
for y in (0.30, 0.44):
    V.body(r41.band(f"waist_ring{y}", WAIST, y - 0.012, y + 0.012, inflate=0.012, steps=1, mat=M["amber"]))
V.body(ve.rbox("deck", -0.36, 0.36, 0.20, 0.58, 0.88, 0.91, mat=M["shell"]))
for k in range(5):
    V.body(ve.rbox("deck_grate", -0.34, 0.34, 0.23 + k * 0.07, 0.25 + k * 0.07, 0.909, 0.915, mat=M["metal"]))
for sx in (1, -1):
    V.body(ve.bar("deck_strut", (sx * 0.30, 0.25, 0.88), (sx * 0.12, 0.30, 0.66), 0.022, verts=6, mat=M["shell"]))
    V.body(ve.bar("deck_strut2", (sx * 0.30, 0.55, 0.88), (sx * 0.12, 0.50, 0.66), 0.022, verts=6, mat=M["shell"]))

# ------------------------------------------------------------------ 배 (엔진 꼬투리): 줄무늬 + 벌집 드론 발사함 + 꼬리 침
POD = [(0.56, 0.48, 0.30, 0.70), (0.80, 0.62, 0.36, 0.72), (1.30, 0.60, 0.35, 0.72), (1.70, 0.46, 0.28, 0.70),
       (1.86, 0.30, 0.18, 0.68)]
pod = r41.loft("pod", POD, mat=M["light"])
ve.paint(pod, [(M["shell"], lambda c, n: c.z < 0.52, [("z", 0.52)])], slots=[M["light"], M["shell"]])
V.body(pod)
for i, (y0, y1) in enumerate(((0.98, 1.14), (1.40, 1.54))):
    V.body(r41.band(f"pod_stripe{i}", POD, y0, y1, inflate=0.007, steps=1, mat=M["shell"]))
# 벌집 발사함 (4 + 3 육각 칸): 제국 흑 칸 + 본 화이트 뚜껑 + 마젠타 상태등
HIVE_Z = 1.02
cells = [(-0.315 + 0.21 * i, 0.86) for i in range(4)] + [(-0.21 + 0.21 * i, 1.04) for i in range(3)]
V.body(ve.facet("hive_base", [(0.74, 0.96), (1.16, 0.96), (1.16, 1.02), (0.74, 1.02)],
                [(-0.46, 0.96), (0.46, 0.96), (0.46, 1.02), (-0.46, 1.02)], ch=0.01, mat=M["shell"]))
for k, (x, y) in enumerate(cells):
    V.body(r41.ngon_prism("hive_cell", 6, 0.118, 0.14, (x, y, HIVE_Z + 0.07), axis="Z", rot_deg=30, mat=M["shell"],
                          ch=0.006))
    V.body(r41.ngon_prism("hive_lid", 6, 0.098, 0.012, (x, y, HIVE_Z + 0.146), axis="Z", rot_deg=30, mat=M["ceramic"]))
    V.body(cb.sphere("hive_led", radius=0.014, loc=(x + 0.05, y - 0.03, HIVE_Z + 0.155), segments=6, rings=3,
                     material=M["glow"]))
    V.empty(f"drone_tube_{k + 1}", (x, y, HIVE_Z + 0.16), props={"drone": "drones/drone_swarm.glb", "launch": "up"})
V.body(r41.elf_logo("hive_", (0.0, 0.70, 0.95), 0.12, axis="Y", sign=-1, mat=M["amber"]))
V.body(ve.rbox("hive_front", -0.40, 0.40, 0.735, 0.745, 0.86, 1.02, mat=M["shell"]))
# 배기 (양옆, 앰버 끝) + 꼬리 침 + 후미등
for sx in (1, -1):
    V.body(ve.bar("exhaust", (sx * 0.40, 1.40, 0.62), (sx * 0.36, 1.84, 0.70), 0.035, verts=6, mat=M["metal"]))
    V.body(ve.bar("exhaust_tip", (sx * 0.36, 1.84, 0.70), (sx * 0.355, 1.88, 0.705), 0.04, verts=6, mat=M["amber"]))
V.empty("exhaust_1", (0.355, 1.90, 0.705))
V.empty("exhaust_2", (-0.355, 1.90, 0.705))
V.body(ve.bar("stinger", (0, 1.80, 0.62), (0, 2.08, 0.56), 0.05, r1=0.010, verts=6, mat=M["shell"]))
V.body(ve.bar("stinger_tip", (0, 2.04, 0.565), (0, 2.12, 0.55), 0.014, r1=0.003, verts=6, mat=M["amber"]))
for sx, nm in ((1, "light_tail_L"), (-1, "light_tail_R")):
    c = (sx * 0.30, 1.80, 0.76)
    V.part(nm, c)
    V.to(nm, r41.slits(nm + "_s", (c[0], c[1], c[2] - 0.04), (0, 0, 0.04), 3, (0.08, 0.02, 0.018), M["glow"]))

# ------------------------------------------------------------------ 롤케이지 (육각 관) + 회전대 + 더듬이
def hexbar(name, a, b, r=0.028):
    return ve.bar(name, a, b, r, verts=6, mat=M["shell"])


FH = [(0.56, -0.88, 0.92), (0.50, -0.80, 1.38), (-0.50, -0.80, 1.38), (-0.56, -0.88, 0.92)]
RH = [(0.56, 0.08, 0.92), (0.46, 0.06, 1.50), (-0.46, 0.06, 1.50), (-0.56, 0.08, 0.92)]
for hoop, nm in ((FH, "hoop_f"), (RH, "hoop_r")):
    for a, b in zip(hoop, hoop[1:]):
        V.body(hexbar(nm, a, b))
for sx in (1, -1):
    V.body(hexbar("rail", (sx * 0.50, -0.80, 1.38), (sx * 0.46, 0.06, 1.50)))
    V.body(hexbar("rear_brace", (sx * 0.46, 0.06, 1.50), (sx * 0.30, 0.70, 0.98), 0.024))
    V.body(hexbar("diag", (sx * 0.56, 0.08, 0.92), (sx * 0.50, -0.80, 1.38), 0.020))
    # 더듬이 (앞 고리 모서리)
    V.body(ve.bar("feeler", (sx * 0.50, -0.80, 1.38), (sx * 0.70, -1.40, 1.90), 0.007, r1=0.004, verts=5,
                  mat=M["shell"]))
    V.body(cb.sphere("feeler_tip", radius=0.016, loc=(sx * 0.70, -1.40, 1.91), segments=6, rings=4, material=M["glow"]))
V.body(ve.rbox("cage_top_line", -0.46, 0.46, 0.035, 0.085, 1.515, 1.525, mat=M["amber"]))
V.body(r41.cyl_z("pintle_post", 0.03, 0.08, (0, 0.06, 1.54), verts=6, mat=M["shell"]))
V.body(r41.cyl_z("pintle_ring", 0.045, 0.02, (0, 0.06, 1.585), verts=6, mat=M["amber"]))
# 드론 중계 안테나 (본 화이트 원판): 오른쪽 뒤 버팀대에서 선다. 사수 눈(회전대 0.55 m 뒤·0.27 m 위)보다 낮고 옆이라
# 정면을 겨눌 때 시야에 들지 않는다 (예전 자리는 회전대 바로 옆, 눈높이였다)
V.body(ve.bar("relay_mast", (-0.34, 0.54, 1.11), (-0.37, 0.60, 1.80), 0.012, verts=6, mat=M["shell"]))
V.body(r41.ngon_prism("relay_disc", 6, 0.08, 0.02, (-0.37, 0.60, 1.81), axis="Z", rot_deg=0, mat=M["ceramic"]))
V.body(cb.sphere("relay_led", radius=0.016, loc=(-0.37, 0.60, 1.835), segments=6, rings=3, material=M["glow"]))

V.empty("mount_lmg", (0, 0.06, 1.595 + 0.09), aim=True,
        props={"weapon": "mount_r41_lmg", "model": "weapons/r41/mount_r41_lmg.glb", "yawMin": -180, "yawMax": 180,
               "pitchMin": -15, "pitchMax": 50, "seat": "gunner"})
V.empty("muzzle_lmg", (0, 0.06 - 0.56, 1.595 + 0.12), "mount_lmg")   # 무기 muzzle (0, 0.56, 0.03)

# ------------------------------------------------------------------ 바퀴 + 다리 (긴 행정 A암, 앰버 완충 스프링)
for nm, x, y, st in (("wheel_FL", X_W, YF, 1), ("wheel_FR", -X_W, YF, 1), ("wheel_RL", X_W, YR, 0),
                     ("wheel_RR", -X_W, YR, 0)):
    V.wheel(nm, (x, y, R_W), R_W, W_W, steer=st, seg=20, lugs=12)
    sx = 1 if x > 0 else -1
    inner = 0.42 if y < 0 else 0.30
    for dz, dy in ((0.10, -0.12), (0.10, 0.12), (-0.08, -0.10), (-0.08, 0.10)):
        V.body(ve.bar("arm", (sx * inner, y + dy, R_W + dz + 0.04), (sx * (X_W - W_W / 2 - 0.04), y, R_W + dz * 0.4),
                      0.022, verts=6, mat=M["shell"] if dz > 0 else M["metal"]))
    V.body(ve.bar("coil", (sx * (inner + 0.02), y + 0.05, 0.86), (sx * (X_W - W_W / 2 - 0.06), y, R_W + 0.10), 0.045,
                  verts=6, mat=M["amber"]))
    V.body(ve.bar("coil_rod", (sx * (inner + 0.02), y + 0.05, 0.92), (sx * (X_W - W_W / 2 - 0.06), y, R_W + 0.06), 0.018,
                  verts=6, mat=M["steel"]))
    V.body(r41.cyl_x("hub_knuckle", 0.07, 0.06, (sx * (X_W - W_W / 2 - 0.04), y, R_W), verts=6, mat=M["metal"]))
    # 펜더 (각진 판)
    V.body(ve.facet("fender", [(y - 0.40, R_W + 0.34), (y + 0.40, R_W + 0.34), (y + 0.30, R_W + 0.42),
                               (y - 0.30, R_W + 0.42)],
                    [(sx * (X_W - 0.17), R_W + 0.34), (sx * (X_W + 0.17), R_W + 0.34), (sx * (X_W + 0.15), R_W + 0.42),
                     (sx * (X_W - 0.15), R_W + 0.42)] if sx > 0 else
                    [(-(X_W + 0.17), R_W + 0.34), (-(X_W - 0.17), R_W + 0.34), (-(X_W - 0.15), R_W + 0.42),
                     (-(X_W + 0.15), R_W + 0.42)], ch=0.008, mat=M["light"]))
    V.body(ve.bar("fender_stay", (sx * (X_W - 0.10), y, R_W + 0.36), (sx * 0.56, y, 0.80), 0.016, verts=6,
                  mat=M["shell"]))

# ------------------------------------------------------------------ 좌석·승하차
V.empty("seat_driver", (0.28, -0.20, 1.12), props={"controls": "drive"})
# 조작병 눈: 오각 화면(높이 1.02)이 시야 가운데를 막지 않게 조금 높고 뒤로 (화면은 아래쪽에, 길은 그 위로 보인다)
V.empty("seat_operator", (-0.28, -0.12, 1.24), props={"controls": "drone_tube", "view": "tablet"})
V.empty("seat_gunner", (0, 0.42, 1.80), props={"controls": "mount_lmg", "pose": "stand"})
V.empty("enter_driver", (1.30, -0.30, 0.0))
V.empty("enter_operator", (-1.30, -0.30, 0.0))
V.empty("enter_gunner", (0.0, 2.50, 0.0))

# ------------------------------------------------------------------ 충돌
V.col_hull("COL_tub", [(sx * 0.62, y, z) for sx in (1, -1) for (y, z) in TUB_SIDE])
V.col("COL_waist", -0.36, 0.36, 0.12, 0.62, 0.42, 0.91)
V.col_hull("COL_pod", [(sx * hw_, y, zc + sz * hh) for (y, hw_, hh, zc) in POD for sx in (1, -1) for sz in (1, -1)]
           + [(sx * 0.46, y, 1.17) for sx in (1, -1) for y in (0.75, 1.15)])
V.col("COL_cage", -0.56, 0.56, -0.90, 0.10, 0.92, 1.52)

V.finish("vehicles/r41/r41_raider.glb", budget=15000, outline=0.008, props={
    "vehicleClass": "wheeled", "mass": 1400, "maxSpeed": 33.0, "wheelbase": round(YR - YF, 3),
    "track": round(2 * X_W, 3), "armor": "light", "faction": "r41", "crew": 3, "passengers": 0,
    "drones": 7, "displayName": "V-7 '나나니' 고속 습격차",
})
