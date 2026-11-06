"""지구에서 발사한 3단 ICBM (프롤로그 엔딩 '함대 피격').

[원작] 엘레나 테마극장: 엘프 함대는 "날아다니던 중 미사일을 맞았다". 이후 엘프들은 포로가 된다.
[오리지널] 지구가 쏘아 올린 3단 대륙간 탄도 미사일. 탄두 버스가 폭약 없는 운동에너지 탄두
          (kinetic_warhead.glb)를 풀어 기함 함교를 직격한다. 특정 실존 미사일을 본뜨지 않은 일반형이다.
  - 흰 원통 동체, 회색 단 사이 링, 검정 롤 띠·체커 띠, 옆면 배선 덮개(레이스웨이)
  - 단마다 노즐 하나. 엘피니아 함선과 반대로 각지고 흰·검정 배색, 주황 UNLIT 화염

노드 (단 분리를 위해 단마다 따로)
  earth_icbm                 루트. 원점 = 1단 노즐 끝, 진행 방향(탄두) = Blender -Y = three.js +Z (lookAt으로 겨눔)
    stage_1                  1단 + 1-2단 사이 링 (원점 = 1단 중심)
      stage_1_body / _fine
      exhaust_0              1단 화염 (UNLIT, 원점 = 노즐 끝, 화염은 three.js -Z로 뻗음) + exhaust_0_haze
    stage_2                  2단 + 2-3단 사이 링
      exhaust_1              2단 화염 (hidden=1: 1단 분리 뒤 켠다)
    stage_3                  3단 모터
      exhaust_2              3단 화염 (hidden=1)
    bus                      탄두 버스(후추진체) + 덮개
      shroud_L, shroud_R     탄두 덮개 반쪽 (분리 시 옆으로 벌어짐, 커스텀 속성 move = three.js 부모 공간 방향)
      warhead_slot_0..3      운동에너지 탄두를 붙이는 자리 (빈 오브젝트, three.js +Z = 탄두 진행 방향)
      exhaust_bus            버스 자세 제어 분사 (hidden=1)
hidden=1 노드는 엔진이 처음에 숨긴다. 길이 약 23 m, 1단 지름 1.9 m.

npm run model -- art/blender/space/earth_icbm.py
npm run shot -- space/earth_icbm.glb --views side,34,front,back
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import space_kit as sk  # noqa: E402
from space_kit import Hull, st  # noqa: E402
from mathutils import Matrix  # noqa: E402

cb.reset()
PI = math.pi
LINE = "#26242a"
M = sk.M


def cyl_hull(y0, y1, r, r1=None, ring=24):
    r1 = r if r1 is None else r1
    return Hull([st(y1, r1, r1, r1, n=2.0), st(y0, r, r, r, n=2.0)], ring=ring, sub=1)


def bands(h, name, ys, mat, width=0.35):
    return [h.patch(f"{name}{i}", y - width / 2, y + width / 2, 0, 2 * PI, mat, lift=0.01, ns=1, nt=24)
            for i, y in enumerate(ys)]


def checker(h, name, y, width, n=8, mat="m_black"):
    """롤 확인용 체커 띠 (반 칸씩 검정)."""
    out = []
    for k in range(n):
        if k % 2 == 0:
            t0 = 2 * PI * k / n
            out.append(h.patch(f"{name}{k}", y - width / 2, y + width / 2, t0, t0 + 2 * PI / n, mat, lift=0.012,
                               ns=1, nt=3))
    return out


def raceway(name, y0, y1, r, t=PI / 2 + 0.35):
    """옆면 배선 덮개 (가는 반원 막대)."""
    x, z = r * math.cos(t), r * math.sin(t)
    return hw.ycyl(name, 0.09, y0, y1, x=x, z=z, verts=8, mat=M("m_gray"))


def flame(name, y_exit, r, length, *, hidden=False, parent=None):
    """주황 UNLIT 화염 노드 (원점 = 노즐 끝) + 반투명 겉껍질 자식."""
    core = [hw.ycyl(f"{name}_core", r * 0.55, y_exit - 0.05, y_exit + length * 0.35, r2=0.0, verts=10,
                    mat=M("flame_core"), cap=False),
            hw.ycyl(f"{name}_mid", r * 0.78, y_exit - 0.02, y_exit + length * 0.75, r2=r * 0.05, verts=14,
                    mat=M("flame"), cap=False),
            sk.disc(f"{name}_disc", r * 0.75, (0, y_exit - 0.04, 0), (0, 1, 0), "flame_core", n=14)]
    o = sk.vc_join(core, name, "glow", line=LINE)
    sk.set_origin(o, (0, y_exit, 0))
    haze = sk.vc_join([hw.ycyl(f"{name}_h", r * 1.05, y_exit, y_exit + length, r2=r * 0.35, verts=16,
                               mat=M("flame_haze"), cap=False)], f"{name}_haze", "plume", line=LINE)
    sk.set_origin(haze, (0, y_exit, 0))
    sk._parent_keep(haze, o)
    if hidden:
        o["hidden"] = 1
    if parent is not None:
        sk._parent_keep(o, parent)
    return o


def stage_node(name, body, fine, center_y, parent):
    e = cb.empty(name, loc=(0, center_y, 0), size=1.0)
    sk._parent_keep(e, parent)
    sk.vc_join(body, f"{name}_body", "body", line=LINE, parent=e)
    sk.vc_join(fine, f"{name}_fine", "fine", line=LINE, parent=e)
    return e


root = cb.empty("earth_icbm", size=2.0)

# ================================================================== 1단 (y 0 → -9.0) + 1-2단 사이 링
R1 = 0.95
h1 = cyl_hull(-9.0, -0.4, R1)
body = [h1.mesh("s1", "m_white"),
        hw.ycyl("s1_skirt", R1 * 1.04, -0.9, 0.0, r2=R1 * 1.12, verts=24, mat=M("m_gray")),
        hw.tube("s1_nozzle", 0.62, 0.48, -0.1, 0.95, c=(0, 0), verts=20, r_out2=0.8, r_in2=0.7, mat=M("m_black")),
        hw.ycyl("s1_throat", 0.5, 0.25, 0.3, verts=16, mat=M("m_black")),
        hw.ycyl("i12", R1 * 1.0, -10.0, -9.0, r2=R1, verts=24, mat=M("m_gray")),
        raceway("s1_race", -8.6, -0.9, R1)]
fine = bands(h1, "s1_band", (-2.2, -7.6), "m_black", 0.4) + checker(h1, "s1_chk", -8.4, 0.7)
s1 = stage_node("stage_1", body, fine, -4.5, root)
flame("exhaust_0", 0.95, 1.0, 14.0, parent=s1)

# ================================================================== 2단 (y -10.0 → -15.0) + 2-3단 사이 링
R2 = 0.85
h2 = cyl_hull(-15.0, -10.0, R2)
body = [h2.mesh("s2", "m_white"),
        hw.tube("s2_nozzle", 0.45, 0.35, -10.0, -9.3, c=(0, 0), verts=16, r_out2=0.6, r_in2=0.52, mat=M("m_black")),
        hw.ycyl("i23", R2, -15.6, -15.0, r2=R2, verts=24, mat=M("m_gray")),
        raceway("s2_race", -14.6, -10.3, R2)]
fine = bands(h2, "s2_band", (-12.6,), "m_black", 0.35) + checker(h2, "s2_chk", -14.4, 0.5)
s2 = stage_node("stage_2", body, fine, -12.5, root)
flame("exhaust_1", -9.3, 0.75, 9.0, hidden=True, parent=s2)

# ================================================================== 3단 (y -15.6 → -18.2)
R3 = 0.75
h3 = cyl_hull(-18.2, -15.6, R3)
body = [h3.mesh("s3", "m_white"),
        hw.tube("s3_nozzle", 0.36, 0.28, -15.6, -15.1, c=(0, 0), verts=14, r_out2=0.46, r_in2=0.4, mat=M("m_black"))]
fine = bands(h3, "s3_band", (-17.6,), "m_black", 0.3)
s3 = stage_node("stage_3", body, fine, -16.9, root)
flame("exhaust_2", -15.1, 0.55, 6.0, hidden=True, parent=s3)

# ================================================================== 탄두 버스 + 덮개
bus = cb.empty("bus", loc=(0, -18.8, 0), size=1.0)
sk._parent_keep(bus, root)
bb = [hw.ycyl("bus_core", 0.62, -19.3, -18.2, verts=20, mat=M("m_gray")),
      hw.ycyl("bus_deck", 0.72, -19.45, -19.25, verts=20, mat=M("m_black"))]
for k in range(4):
    a = PI / 4 + k * PI / 2
    bb.append(cb.box(f"bus_rcs{k}", size=(0.16, 0.3, 0.16), loc=(0.66 * math.cos(a), -18.6, 0.66 * math.sin(a)),
                     material=M("m_black")))
sk.vc_join(bb, "bus_body", "body", line=LINE, parent=bus)
# 탄두 자리 4개 (덮개 안, 버스 앞판 위)
for k in range(4):
    a = PI / 4 + k * PI / 2
    e = cb.empty(f"warhead_slot_{k}", loc=(0.32 * math.cos(a), -19.5, 0.32 * math.sin(a)), size=0.3)
    # three.js +Z = 탄두 진행 방향: Blender에서 빈 오브젝트 회전 없음 → 로컬 -Y(Blender) = three +Z
    sk._parent_keep(e, bus)
# 덮개: 오자이브를 반으로 (X 기준 좌우)
ogive = [st(-23.0, 0.0, 0.0, 0.0, n=2.0)]
for i in range(1, 7):
    a = i / 6
    r = R3 * math.sqrt(1 - (1 - a) ** 2) ** 0.9
    ogive.append(st(-23.0 + 3.0 * a, r, r, r, n=2.0))
ogive.append(st(-18.2, R3, R3, R3, n=2.0))
hs = Hull(ogive, ring=24, sub=1)
for side, nm in ((1, "shroud_L"), (-1, "shroud_R")):
    t0, t1 = (-PI / 2, PI / 2) if side > 0 else (PI / 2, 3 * PI / 2)
    shell = hs.patch(f"{nm}_shell", -23.0, -18.2, t0, t1, "m_white", lift=0.0, nt=12)
    shell.name = shell.data.name = f"{nm}_mesh"
    cb.solidify(shell, 0.05, offset=-1.0)
    tip = hs.patch(f"{nm}_tip", -23.0, -21.6, t0, t1, "m_gray", lift=0.012, nt=12)
    o = sk.vc_join([shell], nm, "body", line=LINE)
    sk.set_origin(o, (0, -20.0, 0))
    sk.vc_join([tip], f"{nm}_fine", "fine", line=LINE, parent=o)
    o["move"] = f"{side * 2.5:g},0,1.5"      # three.js 부모 공간: 옆으로 벌어지며 앞으로
    o["rotAxis"] = "0,1,0"
    sk._parent_keep(o, bus)
flame("exhaust_bus", -18.6, 0.12, 1.2, hidden=True, parent=bus)

sk.purge_materials()
bpy = cb.bpy if hasattr(cb, "bpy") else __import__("bpy")
tris = cb.tri_count()
print(f"[sk] earth_icbm tris {tris} / 4000")
assert tris <= 4000, tris
cb.export("space/earth_icbm.glb", props={"outline": 0.03, "collider": 0, "lengthM": 23}, root=root)
