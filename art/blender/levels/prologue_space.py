"""프롤로그 우주 장면 (오프닝 1·2 + 엔딩 피격 외부 컷).

docs/scenario.md 4장 '프롤로그'
  오프닝 1 우주: 엘피니아 함대(기함·수송함·호위함)가 지구로 향한다           → CAM_fleet_*
  오프닝 2 탐사선 관측: 탐사선이 망원 카메라로 지구(북미)를 관측한다            → CAM_probe_*
  엔딩 END_ATTACK 외부 컷: 지구의 ICBM이 솟아올라 단 분리 → 탄두 버스가 운동에너지 탄두를 풀고
                            탄두가 기함 함교를 직격한다 (근접 통과·빗나감 탄두 포함) → CAM_attack_*
규칙: docs/LEVELS.md (CAM_/LOOK_), docs/art/space.md (WP_icbm_, WP_warhead_, FX_, hidden, 루트 속성)

에셋은 public/models/space/*.glb를 불러와 놓는다 (다시 만들지 않음). 먼저 그 스크립트들을 실행해 둔다.
  기함·탐사선: 노드 구조 유지 (ship_flagship > bridge / bridge_damaged(hidden=1), ship_probe)
  호위함 8척·수송함 2척: 머티리얼별로 합쳐 그리기 호출을 줄인다 (fleet_escorts_*, fleet_transports_*)
  지구: 북미가 함대 쪽을 보게 돌린다. 지구 텍스처에 구운 태양 방향(sunLocal)을 같이 돌려 장면 태양을 정한다
  달: 장면 태양으로 다시 굽는다. 별하늘: 함대와 지구 사이를 중심으로 반지름 420 m

좌표: Blender Z-up, 함대 진행 방향 = -Y (지구 쪽). 모든 노드 collider=0 (충돌 없는 컷신 장면).

npm run model -- art/blender/levels/prologue_space.py
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "space"))
import bpy  # noqa: E402
import cb  # noqa: E402
import space_kit as sk  # noqa: E402
import moon as moon_mod  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

cb.reset()
ROOT = cb.empty("prologue_space", size=5.0)
D = math.radians


# ================================================================== 도우미

def fix_mats(objs):
    """같은 이름 머티리얼을 여러 번 불러와 생긴 '.001' 복제를 원본으로 되돌린다 (이름에 점 금지)."""
    for o in objs:
        if o.type != "MESH":
            continue
        for i, m in enumerate(o.data.materials):
            if m and re.match(r".*\.\d{3}$", m.name):
                base = bpy.data.materials.get(m.name[:-4])
                if base:
                    o.data.materials[i] = base
    for m in list(bpy.data.materials):
        if m.users == 0:
            bpy.data.materials.remove(m)


def import_glb(rel):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(cb.MODELS_DIR, rel))
    new = [o for o in bpy.data.objects if o not in before]
    fix_mats(new)
    top = [o for o in new if o.parent is None]
    assert len(top) == 1, (rel, [o.name for o in top])
    return top[0]


def rot(yaw=0.0, pitch=0.0, roll=0.0):
    """함선 방향: yaw(Z, +면 함수가 +X 쪽으로), pitch(+면 함수가 아래로), roll(Y)."""
    return (Matrix.Rotation(D(yaw), 4, "Z") @ Matrix.Rotation(D(pitch), 4, "X")
            @ Matrix.Rotation(D(roll), 4, "Y"))


def set_xform(obj, loc, R4, scale=1.0):
    obj.rotation_mode = "QUATERNION"
    obj.location = Vector(loc)
    obj.rotation_quaternion = R4.to_quaternion()
    obj.scale = (scale, scale, scale)


def world_of(obj):
    bpy.context.view_layer.update()
    return obj.matrix_world.translation.copy()


def instances(rel, name, placements, outline):
    """같은 함선 여러 척을 그룹(body/fine/glow/plume)별로 한 메시로 합친다."""
    top = import_glb(rel)
    src = [o for o in top.children_recursive if o.type == "MESH"]
    bpy.context.view_layer.update()
    groups = {}
    for (loc, R4) in placements:
        T = Matrix.Translation(Vector(loc)) @ R4
        for o in src:
            c = o.copy()
            c.data = o.data.copy()
            cb.link(c)
            c.parent = None
            c.matrix_world = T @ o.matrix_world
            g = o.name.rsplit("_", 1)[-1]
            groups.setdefault(g, []).append(c)
    for o in [top] + list(top.children_recursive):
        bpy.data.objects.remove(o, do_unlink=True)
    out = []
    for g, objs in groups.items():
        j = cb.join(objs, f"{name}_{g}")
        j["collider"] = 0
        if g == "body":
            j["outline"] = outline
        else:
            j["noOutline"] = 1
        sk._parent_keep(j, ROOT)
        out.append(j)
    return out


def marker(name, loc, parent=ROOT, **props):
    e = cb.empty(name, loc=tuple(loc), size=1.0)
    for k, v in props.items():
        e[k] = v
    sk._parent_keep(e, parent)
    return e


def look_quat(src, dst):
    """빈 오브젝트의 -Y가 dst를 보게 (LEVELS.md: CAM_의 -Y가 시선)."""
    return (Vector(dst) - Vector(src)).to_track_quat("-Y", "Z")


def rail(shot, points):
    """points: [(t, cam, look, fov), ...] → CAM_<shot>_<nn> + LOOK_<shot>_<nn>."""
    for i, (t, cam, look, fov) in enumerate(points):
        c = marker(f"CAM_{shot}_{i:02d}", cam, t=float(t), fov=float(fov))
        c.rotation_mode = "QUATERNION"
        c.rotation_quaternion = look_quat(cam, look)
        marker(f"LOOK_{shot}_{i:02d}", look)


def three(v):
    """Blender 벡터 → three.js 문자열 (x, z, -y)."""
    return f"{v.x:.4f},{v.z:.4f},{-v.y:.4f}"


def unit_ll(lat, lon):
    la, lo = D(lat), D(lon)
    return Vector((math.cos(la) * math.sin(lo), -math.cos(la) * math.cos(lo), math.sin(la)))


def lerp(a, b, t):
    return a + (b - a) * t


# ================================================================== 지구 (북미가 함대를 보게)
E = Vector((0.0, -360.0, -125.0))
R_E = 100.0
earth = import_glb("space/earth.glb")
sun_local = Vector(tuple(float(x) for x in earth["sunLocal"].split(",")))
NA = (40.0, -98.0)                       # 북미 중부 (목표 '50개 별의 가호를 받는 왕국')
f = (-E).normalized()                    # 지구 → 함대
a1 = unit_ll(*NA)
a2 = (Vector((0, 0, 1)) - a1 * a1.z).normalized()
b1 = f
b2 = (Vector((0, 0, 1)) - f * f.z).normalized()
roll = D(-10.0)                          # 북쪽을 살짝 기울여 화면에 힘을 준다
b2 = (Matrix.Rotation(roll, 3, b1) @ b2).normalized()
A = Matrix((a1, a2, a1.cross(a2))).transposed()
B = Matrix((b1, b2, b1.cross(b2))).transposed()
R_earth = (B @ A.transposed()).to_4x4()
set_xform(earth, E, R_earth)
sk._parent_keep(earth, ROOT)
SUN = (R_earth.to_3x3() @ sun_local).normalized()      # 지구에 구운 실제 태양 방향 (Blender)
# 함선 조명: 같은 방위에서 위로 들어 올린 태양 (지구 텍스처의 태양은 북미 남서쪽이라 그대로면 아래에서 비춘다)
h = Vector((SUN.x, SUN.y, 0.0)).normalized()
SHIP_SUN = (h * math.cos(D(38)) + Vector((0, 0, 1)) * math.sin(D(38))).normalized()


def on_earth(lat, lon, alt=0.0):
    n = (R_earth.to_3x3() @ unit_ll(lat, lon)).normalized()
    return E + n * (R_E + alt), n


# ================================================================== 별하늘 + 달
SKY_C = Vector((0.0, -120.0, -40.0))
SKY_R = 420.0
sky = import_glb("space/starfield.glb")
set_xform(sky, SKY_C, Matrix.Identity(4), SKY_R / 540.0)
sk._parent_keep(sky, ROOT)
moon_dir = (Vector((-0.5, -0.55, 0.66))).normalized()     # 함대 전경 컷의 오른쪽 위
moon = moon_mod.build(tuple(SUN), radius=15.0)
set_xform(moon, SKY_C + moon_dir * 360.0, Matrix.Identity(4))
sk._parent_keep(moon, ROOT)

# ================================================================== 함대 (지구로 향하는 쐐기 진형)
FLAG_LOC, FLAG_ROT = Vector((0.0, 0.0, 0.0)), rot(0, 6, 0)
flag = import_glb("space/elfinia_flagship.glb")
flag.name = "ship_flagship"
set_xform(flag, FLAG_LOC, FLAG_ROT)
sk._parent_keep(flag, ROOT)
# 대본(docs/script/prologue.md 5.1): 기함 「큰망치」가 앞에, 강습 수송함들이 뒤에 선다. 호위함은 양옆을 감싼다.
# 모두 함대 전경 컷의 끝 카메라(y≈118)보다 앞에 둔다.
ESCORTS = [
    ((-56.0, -26.0, 6.0), rot(4, 6, -6)),       # 기함 우현 앞 (C1, -X = 우현)
    ((60.0, -20.0, -8.0), rot(-3, 6, 5)),       # 기함 좌현 앞 (C2)
    ((-104.0, 18.0, 14.0), rot(2, 5, -4)),      # 우현 날개
    ((108.0, 26.0, -12.0), rot(-2, 7, 4)),      # 좌현 날개
    ((-128.0, 74.0, 2.0), rot(3, 5, -3)),       # 우현 끝
    ((122.0, 84.0, 8.0), rot(-4, 6, 3)),        # 좌현 끝
    ((-30.0, 100.0, 34.0), rot(1, 6, 0)),       # 맨 뒤
]
TRANSPORTS = [
    ((-46.0, 50.0, -16.0), rot(2, 6, -2)),      # 강습 수송함 1 (T1)
    ((-16.0, 70.0, 18.0), rot(-1, 6, 2)),       # 강습 수송함 2
    ((18.0, 78.0, -14.0), rot(0, 6, 0)),        # 강습 수송함 3
]
instances("space/elfinia_cruiser.glb", "fleet_escorts", [(Vector(l), r) for l, r in ESCORTS], 0.07)
instances("space/elfinia_transport.glb", "fleet_transports", [(Vector(l), r) for l, r in TRANSPORTS], 0.09)
# 합친 함선마다 위치 표시 (ship_<n>: 미션 시스템이 함선 위치를 찾을 때 쓴다. 메시 없음)
for i, (l, r) in enumerate(ESCORTS + TRANSPORTS, start=1):
    e = marker(f"ship_{i}", l, shipClass="cruiser" if i <= len(ESCORTS) else "transport")
    e.rotation_mode = "QUATERNION"
    e.rotation_quaternion = r.to_quaternion()

# ================================================================== 탐사선 (지구 가까이, 망원경을 북미에)
S_NA, n_na = on_earth(*NA)
P_PROBE = E + (n_na + Vector((0.3, 0.0, 0.1))).normalized() * (R_E + 58.0)
T_PROBE, _ = on_earth(41.6, -87.6)         # 미시간호 남쪽 끝 (망원 화면에서 호숫가가 보이게)
probe = import_glb("space/elfinia_probe.glb")
probe.name = "ship_probe"
probe.rotation_mode = "QUATERNION"
probe.location = P_PROBE
probe.rotation_quaternion = look_quat(P_PROBE, T_PROBE)
sk._parent_keep(probe, ROOT)
marker("MARK_target", T_PROBE)              # 관측 목표 (브리핑 화면의 목표 표시가 가리킴)

bpy.context.view_layer.update()
HIT = flag.matrix_world @ bpy.data.objects["anchor_bridge_hit"].matrix_parent_inverse.inverted() \
    @ bpy.data.objects["anchor_bridge_hit"].location if False else \
    bpy.data.objects["anchor_bridge_hit"].matrix_world.translation.copy()
BRIDGE = bpy.data.objects["anchor_bridge"].matrix_world.translation.copy()

# ================================================================== 오프닝 1: 함대 플라이바이 (10 s)
rail("fleet", [
    (0.0, (30.0, 64.0, 10.0), (-2.0, -40.0, -12.0), 42),      # 기함 좌현 뒤: 추진기 불빛 너머 지구
    (3.0, (58.0, 24.0, 12.0), (2.0, -70.0, -26.0), 44),       # 좌현 귀 지느러미 끝 바깥을 지나며
    (5.5, (56.0, -14.0, 40.0), (-6.0, -130.0, -50.0), 46),    # 위로 올라서며 함교·엠블럼, 앞 호위함
    (8.0, (26.0, 46.0, 64.0), (-6.0, -170.0, -72.0), 50),     # 뒤·위로 빠지며 진형과 지구를 한 화면에
    (10.0, (14.0, 118.0, 82.0), (-6.0, -210.0, -92.0), 50),   # 함대 전경 + 지구 (+ 오른쪽 위 달)
])

# ================================================================== 오프닝 2: 탐사선 관측 (7 s)
d = (T_PROBE - P_PROBE).normalized()
up = (Vector((0, 0, 1)) - d * d.z).normalized()
side = d.cross(up).normalized()
# 망원 카메라 시점: 경통 앞에서 목표를 좁은 화각으로 당겨 본다 (위성 영상풍 화면 오버레이용)
lens = bpy.data.objects["anchor_lens"].matrix_world.translation.copy()
rail("scope", [
    (0.0, lens + d * 0.6, T_PROBE, 24),
    (9.0, lens + d * 1.2, T_PROBE, 9),
])
rail("probe", [
    (0.0, P_PROBE - d * 5.0 + side * 15.0 + up * 4.0, P_PROBE + d * 7.0, 40),    # 옆에서: 경통이 지구를 겨눔
    (3.5, P_PROBE - d * 9.0 + side * 10.0 + up * 3.2, P_PROBE + d * 22.0, 37),
    (7.0, P_PROBE - d * 10.0 + side * 3.6 + up * 3.0, T_PROBE, 32),              # 어깨 너머 경통과 같은 시선
])

# ================================================================== 엔딩: ICBM → 탄두 → 함교 직격 (11 s)
LAUNCH, n_l = on_earth(41.0, -100.5)                    # 미국 중부 평원
to_fleet = (FLAG_LOC - LAUNCH).normalized()
lat_v = n_l.cross(to_fleet).normalized()
# 시각은 미션 시스템의 ATTACK_TIMES(stage1 1.9, stage2 2.9, mirv 4.2, impact 9.0)와 맞춘다
ICBM = [
    # (t, 위치, scale, event)  scale: 작은 지구(반지름 100 m)에서 함대(실척)로 오며 커지는 원근 속임
    (0.0, LAUNCH, 0.25, "launch"),
    (1.0, LAUNCH + n_l * 7.0, 0.25, ""),
    (1.9, LAUNCH + n_l * 20.0 + to_fleet * 6.0, 0.3, "sep_stage_1"),
    (2.9, lerp(LAUNCH, FLAG_LOC, 0.22) + n_l * 26.0, 0.38, "sep_stage_2"),
    (4.2, lerp(LAUNCH, FLAG_LOC, 0.5) + n_l * 18.0 + lat_v * 6.0, 0.55, "release"),
    (5.4, lerp(LAUNCH, FLAG_LOC, 0.56) + n_l * 16.0 + lat_v * 10.0, 0.55, "bus_drift"),
]
for k, (t, p, s, ev) in enumerate(ICBM):
    props = {"t": t, "scale": s}
    if ev:
        props["event"] = ev
    marker(f"WP_icbm_{k}", p, **props)
REL = ICBM[4][1]
bpy.context.view_layer.update()
C1 = Vector(ESCORTS[0][0])
T1 = Vector(TRANSPORTS[0][0])
WARHEADS = [
    # (이름, [(t, 위치)], scale)  0 = 함교 직격, 1 = 호위함 C1 선체 스침, 2 = 수송함 옆 빗나감, 3 = 기함·C2 사이 통과
    (0, [(4.3, REL), (7.0, lerp(REL, HIT, 0.62) + Vector((5.0, 0, -4.0))), (9.0, HIT)], 2.4),
    (1, [(4.4, REL), (7.1, lerp(REL, C1, 0.65) + Vector((-6.0, 0, 4.0))), (8.8, C1 + Vector((2.5, -6.0, 3.6))),
         (9.6, C1 + Vector((-10.0, 60.0, 12.0)))], 2.4),
    (2, [(4.5, REL), (7.4, lerp(REL, T1, 0.6) + Vector((8.0, 0, -6.0))), (9.4, T1 + Vector((9.5, -2.0, 7.5))),
         (10.6, T1 + Vector((16.0, 90.0, 26.0)))], 2.4),
    (3, [(4.6, REL), (7.6, Vector((26.0, -50.0, -6.0))), (9.2, Vector((32.0, 6.0, 2.0))),
         (10.4, Vector((38.0, 110.0, 16.0)))], 2.4),
]
for n, pts, s in WARHEADS:
    for k, (t, p) in enumerate(pts):
        marker(f"WP_warhead_{n}_{k}", p, t=t, scale=s)
# 피탄·연기·파편 (FX_<종류>_<id>: t = 시작 시각, size = 지름 m)
HIT_OUT = (HIT - BRIDGE).normalized()
marker("FX_hit_bridge", HIT, t=9.0, size=16.0, target="ship_flagship", show="bridge_damaged", hide="bridge")
marker("FX_hit_1", C1 + Vector((2.5, -6.0, 3.6)), t=8.8, size=5.0, kind="graze")
marker("FX_smoke_bridge", HIT + HIT_OUT * 3.0, t=9.2, size=12.0, dur=6.0)
marker("FX_debris_bridge", HIT + HIT_OUT * 2.0, t=9.05, size=10.0, count=14)
marker("FX_smoke_1", C1 + Vector((2.5, -6.0, 3.6)), t=9.0, size=5.0, dur=4.0)
# 미션 시스템의 임시 연출(src/game/cinematic/attack.ts)이 찾는 표시: 직격점, 발사 지점들 (주 ICBM + 함께 솟는 몇 발)
marker("MARK_hit_bridge", HIT)
for i, (la, lo) in enumerate(((41.0, -100.5), (47.5, -106.0), (38.5, -112.0), (34.0, -97.0))):
    marker(f"MARK_launch_{i}", on_earth(la, lo)[0])

# 카메라: 지구 표면에서 올려다본 발사 → 상승을 따라감 → 함대 쪽에서 들어오는 탄두 → 함교 직격
up_l = n_l
rail("attack", [
    # 카메라는 대기 껍질(반지름 1.065 R) 밖에 둔다 (안쪽에서는 껍질이 화면을 덮음)
    (0.0, LAUNCH + up_l * 16.0 + lat_v * 20.0 - to_fleet * 14.0, LAUNCH + up_l * 4.0, 48),  # 발사장을 비스듬히 내려다봄
    (1.0, LAUNCH + up_l * 19.0 + lat_v * 18.0 - to_fleet * 9.0, ICBM[1][1] + up_l * 6.0, 50),
    (1.9, ICBM[2][1] + lat_v * 16.0 - to_fleet * 5.0 + up_l * 2.0, ICBM[2][1] + to_fleet * 5.0, 48),  # 1단 분리
    (2.9, ICBM[3][1] + lat_v * 18.0 - to_fleet * 10.0, ICBM[3][1] + to_fleet * 14.0, 46),            # 2단 분리
    (4.2, REL - to_fleet * 18.0 + up_l * 4.0 + lat_v * 6.0, FLAG_LOC, 46),   # 버스 뒤: 탄두가 함대로 갈라짐
    (6.2, Vector((-34.0, -78.0, 24.0)), lerp(REL, FLAG_LOC, 0.45), 50),       # 함대 앞에서: 다가오는 탄두들
    (7.8, HIT + Vector((34.0, -30.0, 8.0)), lerp(REL, HIT, 0.75), 44),
    (9.0, HIT + Vector((26.0, -20.0, 7.0)), HIT, 40),                         # 함교 직격
    (11.0, HIT + Vector((36.0, -26.0, 10.0)), HIT + Vector((0, 4.0, -2.0)), 42),
])

# ================================================================== 루트 속성
for o in ROOT.children_recursive:
    if o.type == "MESH" and "collider" not in o.keys():
        o["collider"] = 0
props = {
    "sky": "#05081a",
    "sun": three(SHIP_SUN),
    "ambient": 0.45,
    "music": "prologue_space",
    "collider": 0,
    "camNear": 0.5,
    "camFar": 2000.0,
    "skyNode": "starfield",
    "earthSun": three(SUN),
}
print("[space] sun(three)", props["sun"], " earthSun", props["earthSun"])
print("[space] HIT", tuple(round(v, 2) for v in HIT), " probe", tuple(round(v, 1) for v in P_PROBE))
sk.purge_materials()
sk.export_glb("levels/prologue_space.glb", props=props, root=ROOT)
