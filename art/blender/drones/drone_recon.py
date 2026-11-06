"""R41 D-4 '하루살이' 정찰 드론.

겹눈 하나와 꼬리 감지선 세 가닥으로 거리를 훑는 정찰기. 무장은 없고, 발견한 표적을 군집 드론에게 넘긴다.
2막(HUD 꺼짐)에서 은신 판정의 주인공. 동축 로터 두 장이 서로 반대로 돈다. 길이 0.55 m, 삼각형 3k 이하.

규약: 정면 -Y, 가장 낮은 점 z=0. rotor_upper / rotor_lower 는 Z축 회전(서로 반대 방향).
앵커: eye(겹눈 중심, 탐지 원뿔의 시작), scan(배 아래 스캐너), center.

npm run model -- art/blender/drones/drone_recon.py
npm run shot -- drones/drone_recon.glb
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import r41  # noqa: E402

cb.reset()
M = r41.mats()

# ---------------------------------------------------------------- 동체: 큰 머리 + 가는 꼬리 붐
BODY = [
    (-0.105, 0.050, 0.046, 0.200),
    (-0.085, 0.064, 0.058, 0.202),
    (-0.030, 0.066, 0.060, 0.206),
    (0.020, 0.050, 0.048, 0.210),
    (0.050, 0.030, 0.030, 0.212),
    (0.080, 0.024, 0.024, 0.214),
    (0.170, 0.012, 0.012, 0.220),
]
r41.loft("body", BODY, mat=M["shell"])
r41.band("crown", BODY, -0.080, 0.010, base=r41.clip_unit(r41.OCT_UNIT, 0.25), inflate=0.004, steps=3, mat=M["ceramic"])
r41.band("boom_band0", BODY, 0.090, 0.100, inflate=0.003, steps=1, mat=M["ceramic"])
r41.band("boom_band1", BODY, 0.120, 0.130, inflate=0.003, steps=1, mat=M["ceramic"])
for sx in (1, -1):
    r41.slits(f"side_slit{sx}", (sx * 0.0665, -0.050, 0.190), (0, 0.016, 0), 3, (0.002, 0.010, 0.005), M["glow"])

# ---------------------------------------------------------------- 겹눈 (육각 판 + 일곱 겹)
r41.ngon_prism("eye_frame", 6, 0.058, 0.014, (0, -0.110, 0.200), mat=M["metal"], ch=0.003)
r41.tube("eye_rim", 0.060, 0.050, 0.005, (0, -0.1185, 0.200), axis="Y", verts=6, mat=M["ceramic"])
r41.ngon_prism("eye_base", 6, 0.050, 0.003, (0, -0.1185, 0.200), mat=M["shell"])
for k in range(6):
    a = math.radians(60 * k + 30)
    r41.ngon_prism(f"facet{k}", 6, 0.0135, 0.003, (0.026 * math.cos(a), -0.1205, 0.200 + 0.026 * math.sin(a)),
                   mat=M["glow"] if k % 2 else M["glow_dim"])
r41.ngon_prism("facet_c", 6, 0.0150, 0.004, (0, -0.1210, 0.200), mat=M["glow"])

# ---------------------------------------------------------------- 배 아래 스캐너 (고리-점, 아래를 봄) + 다리 셋
r41.cyl_z("scanner", 0.024, 0.016, (0, -0.030, 0.140), verts=12, mat=M["metal"], ch=0.002)
r41.ring_eye("scan_", (0, -0.030, 0.1315), 0.018, axis="Z", sign=-1, mat_ring=M["glow"], mat_dot=M["glow_dim"], verts=12)
for k, ang in enumerate((90, 210, 330)):
    a = math.radians(ang)
    top = (0.040 * math.cos(a), -0.020 + 0.040 * math.sin(a), 0.155)
    foot = (0.085 * math.cos(a), -0.020 + 0.085 * math.sin(a), 0.004)
    mid = tuple((p + q) / 2 for p, q in zip(top, foot))
    L = math.dist(top, foot)
    leg = r41.cyl_z(f"leg{k}", 0.0040, L, mid, verts=6, mat=M["metal"])
    # 다리 방향 정렬: Z축을 (top - foot)로
    leg.rotation_euler = Vector((0, 0, 1)).rotation_difference(Vector(top) - Vector(foot)).to_euler()
    r41.cyl_z(f"foot{k}", 0.0085, 0.006, (foot[0], foot[1], 0.003), r_top=0.006, verts=6, mat=M["amber"])

# ---------------------------------------------------------------- 하루살이 꼬리 감지선 셋
TAIL0 = (0, 0.168, 0.220)
for k, (dx, dz) in enumerate(((0.0, 0.020), (0.045, -0.006), (-0.045, -0.006))):
    end = (TAIL0[0] + dx, 0.420, TAIL0[2] + 0.040 + dz)
    mid = tuple((p + q) / 2 for p, q in zip(TAIL0, end))
    L = math.dist(TAIL0, end)
    t = r41.cyl_z(f"cercus{k}", 0.0022, L, mid, r_top=0.0012, verts=6, mat=M["metal"])
    t.rotation_euler = Vector((0, 0, 1)).rotation_difference(Vector(end) - Vector(TAIL0)).to_euler()
    r41.cyl_z(f"cercus_tip{k}", 0.0042, 0.010, end, verts=6, mat=M["glow"]).rotation_euler = t.rotation_euler
    # 감지선 마디 (세라믹 고리 둘)
    for j, f in enumerate((0.40, 0.72)):
        p = tuple(a + (b - a) * f for a, b in zip(TAIL0, end))
        r41.cyl_z(f"cercus_node{k}{j}", 0.0042, 0.006, p, verts=6, mat=M["ceramic"]).rotation_euler = t.rotation_euler
r41.cyl_y("tail_cap", 0.016, 0.014, (0, 0.170, 0.220), r_front=0.010, verts=8, mat=M["metal"])

# ---------------------------------------------------------------- 날개판 한 쌍 (하루살이 날개, 세로로 섬) + 엠블럼
wing_pts = [(-0.010, 0.255), (0.060, 0.255), (0.095, 0.330), (0.070, 0.345), (0.010, 0.300)]
for sx in (1, -1):
    parts = [r41.prof(f"wing{sx}", wing_pts, 0.006, loc=(sx * 0.030, 0, 0), ch=0.0015, mat=M["ceramic"])]
    parts.append(r41.prof(f"wing_edge{sx}", [(-0.012, 0.250), (0.062, 0.250), (0.062, 0.258), (-0.012, 0.258)], 0.008,
                          loc=(sx * 0.030, 0, 0), ch=0.001, mat=M["shell"]))
    parts += r41.emblem(f"wing{sx}_", (sx * 0.0332, 0.040, 0.292), 0.030, axis="X", sign=sx, mat=M["shell"])
    r41.pivot_rotate(parts, (sx * 0.030, 0, 0.255), "Y", sx * 14)

# ---------------------------------------------------------------- 동축 로터 (움직이는 파츠)
MAST = (0, -0.020)
r41.cyl_z("mast", 0.010, 0.060, (MAST[0], MAST[1], 0.282), verts=8, mat=M["metal"])
r41.ngon_prism("mast_collar", 6, 0.020, 0.012, (MAST[0], MAST[1], 0.262), axis="Z", rot_deg=30, mat=M["shell"], ch=0.002)
rotors = {}
for nm, z, sign in (("rotor_lower", 0.290, 1), ("rotor_upper", 0.310, -1)):
    parts = [r41.ngon_prism(f"{nm}_hub", 6, 0.016, 0.008, (MAST[0], MAST[1], z), axis="Z", mat=M["metal"])]
    for b in (0, 180):
        ang = (20 if sign > 0 else 110) + b
        a = math.radians(ang)
        L = 0.150
        parts.append(cb.box(f"{nm}_blade{b}", size=(L, 0.020, 0.003),
                            loc=(MAST[0] + math.cos(a) * (L / 2 + 0.012), MAST[1] + math.sin(a) * (L / 2 + 0.012), z),
                            rot=(sign * (10 if b == 0 else -10), 0, ang), bevel=0.001, bevel_segments=1,
                            material=M["ceramic"]))
        parts.append(cb.box(f"{nm}_tip{b}", size=(0.012, 0.0205, 0.0035),
                            loc=(MAST[0] + math.cos(a) * (L + 0.006), MAST[1] + math.sin(a) * (L + 0.006), z),
                            rot=(0, 0, ang), material=M["amber"]))
    rotors[nm] = (parts, (MAST[0], MAST[1], z))
r41.ngon_prism("mast_cap", 6, 0.010, 0.010, (MAST[0], MAST[1], 0.320), axis="Z", r2=0.004, mat=M["shell"])
r41.cyl_z("beacon", 0.0035, 0.004, (MAST[0], MAST[1], 0.327), verts=6, mat=M["glow"])

r41.finish(
    "drone_recon", "drones/drone_recon.glb",
    moving=rotors,
    anchors={
        "eye": (0, -0.123, 0.200),
        "scan": (0, -0.030, 0.130),
        "center": (0, 0.0, 0.205),
    },
    props={"outline": 0.0035},
    node_props={"rotor_upper": {"outline": 0.0018}, "rotor_lower": {"outline": 0.0018}},
    ground=True,
)
