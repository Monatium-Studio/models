"""R41 V-21 '쌍살벌' 보병전투차 (6x6).

[원작] R41 병사들은 전원 실전 경험이 있는 군인 출신이고 효율적 전투용 장비를 갖췄다. 현장 지휘관 재량으로 움직인다
       (엘리아스 침공전). 리뉴아(R41)의 별칭은 "시공의 검은 말벌". R41 병기 도장은 PV 소총(회백 + 앰버 띠·줄).
[오리지널] 분대(엘프 6명)를 태우고 기관포로 엄호하는 6륜 보병전투차. 말벌의 몸: 머리(운전석·겹눈 시야창) +
           가슴(바퀴 여섯 = 다리 여섯, 포탑) + 잘록한 허리 + 줄무늬 배(병력칸, 뒤 경사로) + 꼬리 침(견인 고리).
           포탑: 25 mm 기관포(실탄, 차량 메시) + 공축 M-4 '호박벌' + 벌집 연막탄 발사기.

규약: docs/art/VEHICLES.md, 설정: docs/art/vehicles-elf.md
npm run model -- art/blender/vehicles/r41/r41_ifv.py
npm run shot -- vehicles/r41/r41_ifv.glb --views front,34,side,top
"""
import math

import bmesh
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import r41  # noqa: E402
import vehicles_elf as ve  # noqa: E402

cb.reset()
V = ve.Veh("r41_ifv", "r41")
M = V.M

R_W, W_W = 0.43, 0.32
X_W = 0.98
AXLES = (-1.70, -0.45, 1.62)
HX = 1.08                      # 가슴 옆 돌출부 반폭

# ------------------------------------------------------------------ 가슴 차체 (머리 쐐기 포함): 모따기 덩어리, 껍데기
SIDE = [(-2.50, 0.46), (-2.86, 0.92), (-2.30, 1.40), (-1.95, 1.56), (0.80, 1.58), (0.98, 1.46), (0.98, 0.46)]
SEC = [(-0.72, 0.44), (0.72, 0.44), (0.80, 0.88), (HX, 0.94), (HX, 1.30), (0.86, 1.58), (-0.86, 1.58), (-HX, 1.30),
       (-HX, 0.94), (-0.80, 0.88)]
hull = ve.facet("hull", SIDE, SEC, ch=0.025, mat=M["light"])
ve.paint(hull, [
    (M["shell"], lambda c, n: c.z < 0.915, [("z", 0.915)]),
    (M["amber"], lambda c, n: 1.00 < c.z < 1.035 and abs(n.z) < 0.5 and abs(c.x) > 0.9, [("z", 1.00), ("z", 1.035)]),
], slots=[M["light"], M["shell"], M["amber"]])
ve.shell(hull, 0.04, M["cabin"])

# 운전석 겹눈 시야창: 앞 경사판(glacis)에 육각 구멍 3개 + 유리 + 테
G0, G1 = (-2.86, 0.92), (-2.30, 1.40)
gl = math.hypot(G1[0] - G0[0], G1[1] - G0[1])
GV = (0, (G1[0] - G0[0]) / gl, (G1[1] - G0[1]) / gl)
GU = (1, 0, 0)
GN = (0, -GV[2], GV[1])
for i, (u, v) in enumerate(((0.29, 0.12), (0.53, 0.12), (0.41, -0.035))):
    o = (u, G0[0] + GV[1] * (gl * 0.5 + v), G0[1] + GV[2] * (gl * 0.5 + v))
    hexp = [(math.cos(math.radians(60 * k)) * 0.105, math.sin(math.radians(60 * k)) * 0.091) for k in range(6)]
    ve.cut_through(hull, hexp, (u, o[1], o[2]), GU, GV)
    V.body(ve.slab("eye_glass", hexp, (u, o[1], o[2]), GU, GV, 0.008, mat=M["glass"], lift=-0.025))
    V.body(ve.loop_frame("eye_rim", hexp, (u, o[1], o[2]), GU, GV, r=0.016, lift=0.006, mat=M["shell"], verts=4))
V.body(hull)

# 머리: 육각 전조등(앰버) + 큰턱 견인 고리 + 더듬이 안테나 + 운전수 해치
for sx, nm in ((1, "light_head_L"), (-1, "light_head_R")):
    c = (sx * 0.78, -2.70, 1.00)
    V.body(r41.ngon_prism("hl_house", 6, 0.12, 0.10, (c[0], c[1] + 0.02, c[2]), axis="Y", rot_deg=0, mat=M["shell"],
                          ch=0.008))
    V.part(nm, c)
    V.to(nm, r41.ngon_prism(nm + "_lens", 6, 0.09, 0.02, (c[0], c[1] - 0.04, c[2]), axis="Y", rot_deg=0,
                            mat=M["glow_amber"]))
    # 큰턱: 앞으로 굽은 두 갈래 고리
    j0 = (sx * 0.34, -2.56, 0.52)
    V.body(ve.bar("mandible_a", j0, (sx * 0.30, -2.86, 0.56), 0.035, verts=6, mat=M["shell"]))
    V.body(ve.bar("mandible_b", (sx * 0.30, -2.86, 0.56), (sx * 0.20, -2.98, 0.66), 0.03, r1=0.018, verts=6,
                  mat=M["shell"]))
    V.body(ve.bar("mandible_band", (sx * 0.31, -2.80, 0.55), (sx * 0.30, -2.86, 0.56), 0.04, verts=6, mat=M["amber"]))
    # 더듬이 (철조망 절단 겸 안테나)
    a0 = (sx * 0.62, -2.28, 1.42)
    V.body(ve.bar("feeler_base", a0, (a0[0], a0[1] + 0.02, a0[2] + 0.06), 0.03, verts=6, mat=M["shell"]))
    V.body(ve.bar("feeler", (a0[0], a0[1] + 0.02, a0[2] + 0.06), (sx * 0.78, -2.80, 2.05), 0.008, r1=0.005, verts=5,
                  mat=M["shell"]))
    V.body(cb.sphere("feeler_tip", radius=0.018, loc=(sx * 0.78, -2.80, 2.06), segments=6, rings=4, material=M["glow"]))


def ngon_hole(obj, n, r, c, z0, z1, rot=0.0):
    """obj를 Z축 정n각 기둥(외접 r, 중심 c=(x, y), z0..z1)으로 뚫는다 (해치 구멍)."""
    return ve.cut(obj, r41.ngon_prism("hole_cut", n, r, z1 - z0, (c[0], c[1], (z0 + z1) / 2), axis="Z", rot_deg=rot))


# 운전수 해치: 실제 구멍이 있다 (탑승 연출로 조종수가 내려가고, AI 운전수는 머리와 어깨를 내민다 = crew_driver).
# 구멍 < 뚜껑 < 테 (육각 외접 반지름, 내접 = x0.866: 구멍 내접 0.24 m). 경첩(hatch_driver 원점)은 그대로다
# 테 아래 받침 관이 지붕과 경사판을 뚫고 실내로 내려가 구멍 벽(제국 흑)이 되고, 경사판 위에 뜨던 테를 받친다
DH = (0.42, -1.97)
DH_OPEN, DH_LID, DH_RING = 0.28, 0.30, 0.33
V.part("hatch_driver", (0.42, -1.70, 1.585), props={"rotAxis": "x", "rotDeg": -100})
V.to("hatch_driver", r41.ngon_prism("hatch_d", 6, DH_LID, 0.05, (DH[0], DH[1], 1.60), axis="Z", rot_deg=0, mat=M["light"],
                                    ch=0.01),
     ve.rbox("hatch_d_grip", 0.36, 0.48, -2.06, -2.02, 1.625, 1.645, mat=M["shell"]))
hd_ring = r41.ngon_prism("hatch_d_ring", 6, DH_RING, 0.03, (DH[0], DH[1], 1.585), axis="Z", rot_deg=0, mat=M["shell"])
hd_well = r41.ngon_prism("hatch_d_well", 6, DH_LID, 0.20, (DH[0], DH[1], 1.47), axis="Z", rot_deg=0, mat=M["shell"])
for o in (hd_ring, hd_well):
    ngon_hole(o, 6, DH_OPEN, DH, 1.30, 1.70)
V.body(hd_ring, hd_well)
# 지붕·경사판 구멍은 받침 관 벽 속(구멍과 받침 바깥 사이)에서 뚫어 단면이 보이지 않는다
ngon_hole(hull, 6, (DH_OPEN + DH_LID) / 2, DH, 1.30, 1.70)

# 옆: 엘프 로고(제국 흑), 막대 부호, 번호, 보관함, 배기 그릴
for sx in (1, -1):
    V.body(r41.elf_logo(f"side{sx}_", (sx * (HX + 0.001), -1.05, 1.13), 0.30, axis="X", sign=sx, mat=M["shell"]))
    V.body(r41.stencil_bars(f"side{sx}_", (sx * (HX + 0.001), 0.30, 1.18), axis="X", sign=sx, h=0.06, unit=0.03,
                            mat=M["shell"], pattern=(1, 1, 0, 1, 0, 1, 1, 0, 1)))
    V.body(ve.text(f"side_no{sx}", "V-21", 0.09, (sx * (HX + 0.001), 0.30, 1.08), ve.frame((sx, 0, 0)), mat=M["shell"],
                   lift=0.001))
    x0, x1 = sorted((sx * (HX - 0.02), sx * (HX + 0.09)))
    V.body(ve.rbox("bin", x0, x1, -2.20, -1.30, 1.10, 1.28, r=0.02, mat=M["shell"]))
    V.body(ve.rbox("bin_line", x0 - 0.002, x1 + 0.002, -2.20, -1.30, 1.18, 1.20, mat=M["amber"]))
for k in range(3):     # 오른쪽 배기 그릴 (세로 슬릿, 장갑판 뒤)
    V.body(ve.rbox("louver", -HX - 0.012, -HX + 0.01, 0.62 + k * 0.09, 0.67 + k * 0.09, 1.00, 1.26, mat=M["shell"]))
V.empty("exhaust_1", (-HX - 0.05, 0.71, 1.13))

# 덧댄 장갑판 (가슴 마디판): 옆 돌출부에 모따기 판 3장 + 볼트, 지붕 등판
for sx in (1, -1):
    for i, (y0, y1) in enumerate(((-0.95, -0.25), (-0.15, 0.55))):
        pts = [(y0, 0.96), (y1, 0.96), (y1 + 0.04, 1.02), (y1 + 0.04, 1.26), (y1, 1.30), (y0, 1.30)]
        pl = ve.side(f"plate{sx}{i}", pts, 0.035, sx * (HX + 0.017), bevel=0.008, seg=1, mat=M["light"])
        V.body(pl)
        for (yy, zz) in ((y0 + 0.05, 1.00), (y1 - 0.02, 1.00), (y0 + 0.05, 1.26), (y1 - 0.02, 1.26)):
            V.body(r41.screw(f"pb{sx}{i}{yy}{zz}", (sx * (HX + 0.036), yy, zz), axis="X", r=0.014, h=0.008,
                             mat=M["steel"]))
    V.body(ve.rbox("plate_line", sx * (HX + 0.034) - 0.002, sx * (HX + 0.034) + 0.002, -0.95, 0.59, 1.12, 1.135,
                   mat=M["amber"]))
scutum = ve.facet("scutum", [(-1.85, 1.56), (0.70, 1.56), (0.75, 1.62), (-1.75, 1.63)],
                  [(-0.80, 1.56), (0.80, 1.56), (0.74, 1.63), (-0.74, 1.63)], ch=0.01, mat=M["light"])
ngon_hole(scutum, 6, DH_RING + 0.015, DH, 1.40, 1.80)     # 등판 앞 끝을 운전수 해치 테 둘레만큼 비운다
V.body(scutum)
for sx in (1, -1):
    V.body(ve.rbox("scutum_line", sx * 0.70 - 0.008, sx * 0.70 + 0.008, -1.70, 0.60, 1.625, 1.632, mat=M["amber"]))

# ------------------------------------------------------------------ 허리 (잘록한 제국 흑 이음매) + 배 (줄무늬 병력칸)
WAIST = [(0.90, 0.80, 0.42, 0.98), (1.04, 0.66, 0.36, 0.98), (1.18, 0.66, 0.36, 0.99), (1.30, 0.82, 0.44, 1.01)]
V.body(r41.loft("waist", WAIST, mat=M["shell"]))
for sx in (1, -1):
    V.body(ve.rbox("waist_line", sx * 0.66 - 0.006, sx * 0.66 + 0.006, 1.04, 1.18, 1.00, 1.03, mat=M["amber"]))
    V.body(ve.bar("waist_hose", (sx * 0.62, 0.95, 1.22), (sx * 0.60, 1.25, 1.24), 0.03, verts=6, mat=M["metal"]))
ABD = [(1.24, 0.82, 0.44, 1.02), (1.50, 1.02, 0.53, 1.04), (2.15, 1.00, 0.52, 1.03), (2.55, 0.90, 0.47, 1.00),
       (2.80, 0.80, 0.42, 0.99)]
abd = r41.loft("abdomen", ABD, mat=M["light"])
for sx in (1, -1):              # 뒤 바퀴집
    ve.cut(abd, cb.cylinder("abd_well", radius=0.53, depth=0.50, loc=(sx * 1.02, AXLES[2], R_W), rot=(0, 90, 0), verts=24))
ve.paint(abd, [(M["shell"], lambda c, n: c.z < 0.80, [("z", 0.80)])], slots=[M["light"], M["shell"]])
ve.shell(abd, 0.035, M["cabin"])
V.body(abd)


def open_band(o):
    """띠는 배를 감싸는 고리라 양 끝 마개(팔각면)가 필요 없다. 마개가 있으면 병력칸 안을 판처럼 가로막는다 (좌석 시점·탑승 연출)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if len(f.verts) > 4], context="FACES")
    bm.to_mesh(o.data)
    bm.free()
    return o


for i, (y0, y1) in enumerate(((1.58, 1.80), (2.10, 2.30))):
    V.body(open_band(r41.band(f"abd_stripe{i}", ABD, y0, y1, inflate=0.008, steps=2, mat=M["shell"])))
    V.body(open_band(r41.band(f"abd_edge{i}", ABD, y0 - 0.025, y0 - 0.005, inflate=0.006, steps=1, mat=M["amber"])))
# 배 지붕 병력 해치 (육각, 정지)
for sx in (1, -1):
    V.body(r41.ngon_prism("abd_hatch", 6, 0.20, 0.04, (sx * 0.38, 1.95, 1.50), axis="Z", rot_deg=0, mat=M["light"],
                          ch=0.008))
    V.body(r41.ngon_prism("abd_hatch_ring", 6, 0.22, 0.02, (sx * 0.38, 1.95, 1.475), axis="Z", rot_deg=0, mat=M["shell"]))
# 뒤 경사로 (병력 하차 해치)
RY = 2.785
ramp = [(-0.40, 0.0), (0.40, 0.0), (0.58, 0.18), (0.58, 0.48), (0.36, 0.70), (-0.36, 0.70), (-0.58, 0.48), (-0.58, 0.18)]
V.part("hatch_rear", (0, RY, 0.62), props={"rotAxis": "x", "rotDeg": -100})
# 경사로 뒤 병력칸 실제 출입구 (경사로가 내려가면 열린다). 경사로보다 3~4 cm 안쪽
ve.cut_through(abd, [(-0.37, 0.04), (0.37, 0.04), (0.54, 0.19), (0.54, 0.47), (0.34, 0.66), (-0.34, 0.66), (-0.54, 0.47),
                     (-0.54, 0.19)], (0, RY - 0.01, 0.62), (-1, 0, 0), (0, 0, 1))
V.to("hatch_rear", ve.slab("ramp", ramp, (0, RY - 0.01, 0.62), (-1, 0, 0), (0, 0, 1), 0.05, mat=M["light"], bevel=0.01,
                           seg=1))
V.to("hatch_rear", ve.slab("ramp_stripe", [(-0.58, 0.30), (0.58, 0.30), (0.58, 0.40), (-0.58, 0.40)],
                           (0, RY + 0.035, 0.62), (-1, 0, 0), (0, 0, 1), 0.008, mat=M["shell"]))
hexw = [(math.cos(math.radians(60 * k)) * 0.08, 0.56 + math.sin(math.radians(60 * k)) * 0.07) for k in range(6)]
V.to("hatch_rear", ve.slab("ramp_win", hexw, (0, RY + 0.035, 0.62), (-1, 0, 0), (0, 0, 1), 0.006, mat=M["visor"]))
V.to("hatch_rear", r41.elf_logo("ramp_", (0.30, RY + 0.044, 0.82), 0.14, axis="Y", sign=1, mat=M["shell"]))
for sx in (1, -1):
    V.to("hatch_rear", ve.bar("ramp_grip", (sx * 0.30, RY + 0.06, 0.70), (sx * 0.30, RY + 0.06, 0.88), 0.014, verts=6,
                              mat=M["shell"]))
# 꼬리 침 (견인 고리) + 후미등 (마젠타 슬릿)
V.body(ve.bar("stinger", (0, 2.70, 0.58), (0, 3.02, 0.52), 0.06, r1=0.012, verts=6, mat=M["shell"]))
V.body(ve.bar("stinger_tip", (0, 2.98, 0.525), (0, 3.06, 0.51), 0.016, r1=0.004, verts=6, mat=M["amber"]))
for sx, nm in ((1, "light_tail_L"), (-1, "light_tail_R")):
    c = (sx * 0.68, RY - 0.03, 1.02)
    V.part(nm, c)
    V.to(nm, r41.slits(nm + "_s", (c[0] - sx * 0.04, c[1] - 0.01, c[2] - 0.06), (0, 0, 0.06), 3, (0.10, 0.02, 0.025),
                       M["glow"]))

# ------------------------------------------------------------------ 바퀴 여섯 (다리) + 각진 다리 팔
names = (("wheel_FL", "wheel_FR", 1), ("wheel_ML", "wheel_MR", 0), ("wheel_RL", "wheel_RR", 0))
for (nl, nr, st), y in zip(names, AXLES):
    V.wheel(nl, (X_W, y, R_W), R_W, W_W, steer=st, seg=22, lugs=14)
    V.wheel(nr, (-X_W, y, R_W), R_W, W_W, steer=st, seg=22, lugs=14)
    for sx in (1, -1):
        V.body(ve.bar("leg_upper", (sx * 0.66, y - 0.10, 0.82), (sx * 0.80, y, R_W + 0.02), 0.05, verts=6,
                      mat=M["shell"]))
        V.body(ve.bar("leg_lower", (sx * 0.66, y + 0.18, 0.52), (sx * 0.80, y, R_W - 0.02), 0.04, verts=6,
                      mat=M["metal"]))
        V.body(ve.bar("leg_damper", (sx * 0.70, y + 0.16, 0.86), (sx * 0.79, y + 0.04, R_W + 0.06), 0.03, verts=6,
                      mat=M["amber"]))

# ------------------------------------------------------------------ 포탑 (낮은 모따기 포탑) + 기관포
TY, TZ = -0.55, 1.58
V.body(r41.ngon_prism("turret_ring", 8, 0.66, 0.05, (0, TY, TZ + 0.005), axis="Z", rot_deg=22.5, mat=M["shell"]))
V.group("turret", (0, TY, TZ), props={"yawMin": -180, "yawMax": 180, "yawSpeed": 60})
T_SIDE = [(-1.06, 1.62), (-1.14, 1.82), (-0.94, 2.02), (0.12, 2.04), (0.26, 1.92), (0.26, 1.62)]
T_SEC = [(-0.62, 1.60), (0.62, 1.60), (0.70, 1.80), (0.50, 2.04), (-0.50, 2.04), (-0.70, 1.80)]
tur = ve.facet("turret_shell", T_SIDE, T_SEC, ch=0.02, mat=M["light"])
ve.paint(tur, [(M["amber"], lambda c, n: 1.745 < c.z < 1.770 and abs(n.z) < 0.6, [("z", 1.745), ("z", 1.770)]),
               (M["shell"], lambda c, n: c.z < 1.66, [("z", 1.66)])], slots=[M["light"], M["amber"], M["shell"]])
V.to("turret", tur)
V.to("turret", r41.elf_logo("t_r_", (-0.846, TY + 0.20, 1.89), 0.13, axis="X", sign=-1, mat=M["shell"]))
for sx in (1, -1):
    V.to("turret", r41.stencil_bars(f"t{sx}_", (sx * 0.68, TY + 0.40, 1.70), axis="X", sign=sx, h=0.035, unit=0.018,
                                    mat=M["shell"]))
    # 벌집 연막탄 발사기 (육각 관 3개, 앰버 마개)
    for k, (dy, dz) in enumerate(((0.0, 0.0), (0.075, 0.0), (0.0375, 0.065))):
        a = (sx * 0.60, TY - 0.30 + dy, 1.86 + dz)
        d = (sx * 0.50, -0.55, 0.67)
        b = tuple(a[i] + d[i] * 0.16 for i in range(3))
        V.to("turret", ve.bar("smoke_tube", a, b, 0.040, verts=6, mat=M["shell"]))
        V.to("turret", ve.bar("smoke_cap", b, tuple(b[i] + d[i] * 0.015 for i in range(3)), 0.042, verts=6,
                              mat=M["amber"]))
    V.empty(f"smoke_{'L' if sx > 0 else 'R'}", (sx * 0.70, TY - 0.36, 1.98), "turret", props={"fx": "smoke", "count": 3})
# 포탑 옆 증가장갑 (오른쪽) + 드론 벌집 발사함 (왼쪽, D-1 '모기' 4기)
V.to("turret", ve.facet("t_armor", [(TY - 0.30, 1.66), (TY + 0.55, 1.66), (TY + 0.60, 1.74), (TY + 0.60, 1.92),
                                     (TY - 0.25, 1.98), (TY - 0.36, 1.86)],
                        [(-0.82, 1.66), (-0.66, 1.66), (-0.66, 1.98), (-0.78, 1.98), (-0.84, 1.92), (-0.84, 1.72)],
                        ch=0.01, mat=M["light"]))
V.to("turret", ve.rbox("t_armor_line", -0.846, -0.836, TY - 0.20, TY + 0.50, 1.80, 1.815, mat=M["amber"]))
HIVE_X, HIVE_Y, HIVE_Z = 0.86, TY + 0.15, 1.83
V.to("turret", ve.rbox("hive_bracket", 0.64, 0.74, HIVE_Y - 0.20, HIVE_Y + 0.20, 1.72, 1.90, mat=M["shell"]))
for k, (dy, dz) in enumerate(((-0.105, -0.06), (0.105, -0.06), (-0.105, 0.12), (0.105, 0.12))):
    c = (HIVE_X, HIVE_Y + dy, HIVE_Z + dz)
    V.to("turret", r41.ngon_prism("hive_cell", 6, 0.115, 0.26, c, axis="X", rot_deg=30, mat=M["shell"], ch=0.006))
    V.to("turret", r41.ngon_prism("hive_lid", 6, 0.095, 0.012, (c[0] + 0.132, c[1], c[2]), axis="X", rot_deg=30,
                                  mat=M["ceramic"]))
    V.to("turret", cb.sphere("hive_led", radius=0.012, loc=(c[0] + 0.14, c[1], c[2] + 0.05), segments=6, rings=3,
                             material=M["glow"]))
    V.empty(f"drone_tube_{k + 1}", (c[0] + 0.16, c[1], c[2]), "turret",
            props={"drone": "drones/drone_swarm.glb", "launch": "side"})
V.to("turret", r41.elf_logo("hive_", (HIVE_X + 0.145, HIVE_Y, HIVE_Z + 0.03), 0.07, axis="X", sign=1, mat=M["amber"]))

# 포수 조준경 (오른쪽 앞, 마젠타 고리-점 눈) / 지휘관 조준경 (왼쪽 뒤, 오각 머리)
V.to("turret", ve.rbox("gsight", -0.50, -0.26, TY - 0.30, TY - 0.06, 2.02, 2.16, r=0.015, mat=M["shell"]))
V.to("turret", r41.ring_eye("gsight_", (-0.38, TY - 0.302, 2.09), 0.045, axis="Y", sign=-1, mat_ring=M["glow"],
                            mat_dot=M["glow"], depth=0.004, verts=12))
V.to("turret", r41.cyl_z("csight_post", 0.05, 0.14, (0.36, TY + 0.02, 2.10), verts=6, mat=M["shell"]))
V.to("turret", r41.ngon_prism("csight_head", 5, 0.11, 0.10, (0.36, TY + 0.02, 2.22), axis="Z", rot_deg=90,
                              mat=M["light"], ch=0.008))
V.to("turret", r41.ngon_prism("csight_lens", 5, 0.06, 0.012, (0.36, TY - 0.065, 2.22), axis="Y", rot_deg=90,
                              mat=M["glow_dim"]))
# 뒤 짐칸 + 안테나 둘
V.to("turret", ve.rbox("t_bustle", -0.50, 0.50, TY + 0.80, TY + 1.02, 1.66, 1.94, r=0.02, mat=M["shell"]))
for sx in (1, -1):
    V.to("turret", ve.bar("t_ant", (sx * 0.40, TY + 0.95, 1.94), (sx * 0.44, TY + 1.10, 2.95), 0.007, r1=0.004, verts=5,
                          mat=M["shell"]))

# 포 (gun_pitch): 방패(망틀릿) + 25 mm 기관포 + 슬롯 포구 제퇴기 + 공축 기관총 구멍
GY, GZ = TY - 0.52, 1.84
V.group("gun_pitch", (0, GY, GZ), "turret", props={"pitchMin": -8, "pitchMax": 45, "pitchSpeed": 35,
                                                               "weapon": "r41_autocannon"})
V.to("gun_pitch", ve.facet("mantlet", [(GY - 0.12, GZ - 0.13), (GY + 0.10, GZ - 0.13), (GY + 0.10, GZ + 0.13),
                                       (GY - 0.06, GZ + 0.13), (GY - 0.12, GZ + 0.07)],
                           [(-0.24, GZ - 0.13), (0.24, GZ - 0.13), (0.24, GZ + 0.13), (-0.24, GZ + 0.13)], ch=0.015,
                           mat=M["shell"]))
V.to("gun_pitch", r41.ngon_prism("jacket", 8, 0.065, 0.40, (0, GY - 0.32, GZ), axis="Y", rot_deg=22.5, mat=M["light"],
                                 ch=0.006))
V.to("gun_pitch", r41.ngon_prism("jacket_band", 8, 0.068, 0.03, (0, GY - 0.20, GZ), axis="Y", rot_deg=22.5,
                                 mat=M["amber"]))
V.to("gun_pitch", r41.cyl_y("barrel", 0.034, 1.30, (0, GY - 1.17, GZ), verts=10, mat=M["metal"]))
V.to("gun_pitch", r41.ngon_prism("brake", 6, 0.06, 0.16, (0, GY - 1.88, GZ), axis="Y", rot_deg=0, mat=M["metal"],
                                 ch=0.006))
V.to("gun_pitch", r41.cyl_y("brake_ring", 0.064, 0.02, (0, GY - 1.80, GZ), verts=6, mat=M["amber"]))
for sx in (1, -1):
    V.to("gun_pitch", ve.rbox("brake_slot", sx * 0.058 - 0.004, sx * 0.058 + 0.004, GY - 1.93, GY - 1.85, GZ - 0.018,
                              GZ + 0.018, mat=M["shell"]))
V.to("gun_pitch", r41.cyl_y("coax_port", 0.022, 0.03, (-0.15, GY - 0.12, GZ - 0.02), verts=8, mat=M["metal"]))
V.empty("muzzle_main", (0, GY - 1.97, GZ), "gun_pitch")
V.empty("eject_main", (0.26, GY + 0.20, GZ), "turret")
V.empty("mount_coax", (-0.15, GY - 0.05, GZ - 0.02), "gun_pitch", aim=True,
        props={"weapon": "mount_r41_lmg", "model": "", "yawMin": 0, "yawMax": 0, "pitchMin": 0, "pitchMax": 0,
               "seat": "gunner"})
V.empty("muzzle_coax", (-0.15, GY - 0.14, GZ - 0.02), "mount_coax")

# 지휘관 해치 (포탑 지붕 왼쪽 뒤, 지휘관 조준경 뒤): 팔각 테 + 검은 우물 + 뒤 경첩 뚜껑. AI 지휘관이 상반신을 내민다
# (crew_commander). 구멍 < 뚜껑 < 테 (팔각 외접 반지름, 내접 = x0.924: 구멍 내접 0.27 m)
# 포탑 덩어리는 속이 차 있어 지붕을 우물 벽 속에서 파내고, 테를 컵(벽 + 바닥)으로 내려 구멍 아래를 검게 막는다
CH = (0.16, -0.14)
CH_OPEN, CH_LID, CH_RING = 0.293, 0.314, 0.343
CH_TOP, CH_FLOOR = 2.075, 1.70            # 테 윗면 (지붕 2.035 위 4 cm), 우물 바닥
CH_HINGE = (CH[0], CH[1] + CH_LID * 0.924 + 0.018, CH_TOP + 0.018)
hc_cup = r41.ngon_prism("hatch_c_ring", 8, CH_RING, CH_TOP - CH_FLOOR + 0.02, (CH[0], CH[1], (CH_TOP + CH_FLOOR - 0.02) / 2),
                        axis="Z", rot_deg=22.5, mat=M["shell"])
ngon_hole(hc_cup, 8, CH_OPEN, CH, CH_FLOOR, CH_TOP + 0.10, rot=22.5)
ngon_hole(tur, 8, (CH_OPEN + CH_RING) / 2, CH, CH_FLOOR - 0.01, 2.30, rot=22.5)
V.to("turret", hc_cup)
for sx in (1, -1):          # 테 위 경첩 마디 (뚜껑 마디와 같은 축)
    V.to("turret", ve.bar("hatch_c_knuckle", (CH[0] + sx * 0.085, CH_HINGE[1], CH_HINGE[2]),
                          (CH[0] + sx * 0.13, CH_HINGE[1], CH_HINGE[2]), 0.018, verts=6, mat=M["shell"]))
V.part("hatch_commander", CH_HINGE, "turret", props={"rotAxis": "x", "rotDeg": -105})
V.to("hatch_commander",
     r41.ngon_prism("hatch_c", 8, CH_LID, 0.045, (CH[0], CH[1], CH_TOP + 0.0025), axis="Z", rot_deg=22.5, mat=M["light"],
                    ch=0.008),
     ve.rbox("hatch_c_grip", CH[0] - 0.06, CH[0] + 0.06, CH[1] - 0.23, CH[1] - 0.19, CH_TOP + 0.025, CH_TOP + 0.045,
             mat=M["shell"]),
     ve.bar("hatch_c_knuckle", (CH[0] - 0.075, CH_HINGE[1], CH_HINGE[2]), (CH[0] + 0.075, CH_HINGE[1], CH_HINGE[2]), 0.018,
            verts=6, mat=M["shell"]))

# ------------------------------------------------------------------ 실내: 운전석 계기판 (시야창 너머로 보임)
V.body(ve.rbox("dash", 0.14, 0.70, -2.44, -2.34, 0.98, 1.08, r=0.02, mat=M["cabin"]))
V.body(ve.slab("dash_screen", [(-0.10, -0.03), (0.10, -0.03), (0.10, 0.03), (-0.10, 0.03)], (0.42, -2.338, 1.04),
               (1, 0, 0), (0, 0.5, 0.866), 0.005, mat=M["glow_dim"]))
for sx in (1, -1):
    V.body(ve.bar("stick", (0.42 + sx * 0.11, -2.26, 0.96), (0.42 + sx * 0.11, -2.32, 1.08), 0.015, verts=6,
                  mat=M["shell"]))

# ------------------------------------------------------------------ 좌석·승하차
V.empty("seat_driver", (0.41, -2.22, 1.24), props={"controls": "drive", "view": "vision_blocks"})
V.empty("seat_gunner", (-0.38, TY - 0.34, 2.09), "turret",
        props={"controls": "turret,gun_pitch,mount_coax", "view": "gunner_sight"})
V.empty("seat_commander", (0.36, TY - 0.11, 2.22), "turret",
        props={"controls": "drone_tube,smoke_L,smoke_R", "view": "commander_sight"})
for i, (x, y) in enumerate(((0.45, 1.45), (-0.45, 1.45), (0.45, 1.95), (-0.45, 1.95), (0.45, 2.40), (-0.45, 2.40)), 1):
    V.empty(f"seat_passenger_{i}", (x, y, 1.32), props={"facing": "inward"})
# 해치에 선 승무원 (AI): 해치 구멍 가운데, 테 윗면 높이. -Y가 정면 (seat_*와 같다)
V.empty("crew_commander", (CH[0], CH[1], CH_TOP), "turret")
V.empty("crew_driver", (DH[0], DH[1], 1.60))
V.empty("enter_driver", (1.55, -2.00, 0.0))
V.empty("enter_gunner", (0.0, 3.60, 0.0))
V.empty("enter_commander", (0.0, 3.60, 0.0))
for i, (x, y) in enumerate(((0.45, 3.60), (-0.45, 3.60), (0.45, 4.10), (-0.45, 4.10), (0.45, 4.60), (-0.45, 4.60)), 1):
    V.empty(f"enter_passenger_{i}", (x, y, 0.0))

# ------------------------------------------------------------------ 충돌
V.col_hull("COL_hull", [(sx * hx, y, z) for (y, z) in SIDE for sx in (1, -1) for hx in ((HX,) if z > 0.9 else (0.80,))])
V.col("COL_waist", -0.66, 0.66, 0.95, 1.28, 0.62, 1.34)
V.col_hull("COL_abdomen", [(sx * hw_ * 1.0, y, zc + sz * hh) for (y, hw_, hh, zc) in ABD for sx in (1, -1) for sz in (1, -1)])
V.col_hull("COL_turret", [(sx * 0.70, y, z) for sx in (1, -1) for (y, z) in T_SIDE], parent="turret")

V.finish("vehicles/r41/r41_ifv.glb", budget=22000, outline=0.010, props={
    "vehicleClass": "wheeled", "mass": 11500, "maxSpeed": 24.0, "wheelbase": round(AXLES[2] - AXLES[0], 3),
    "track": round(2 * X_W, 3), "armor": "medium", "faction": "r41", "crew": 3, "passengers": 6,
    "displayName": "V-21 '쌍살벌' 보병전투차",
})
