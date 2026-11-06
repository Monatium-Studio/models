"""엘피니아 3식 대검 '끌' (엘피니아 원정군 제식 대검·전투 나이프).

[오리지널] 지구 침공 당시 엘피니아 원정군 병사 전원에게 지급된 대검. 7식 소총 총구에 꽂는 착검용이지만
           평소에는 왼손에 쥐고 빠르게 베는 근접 무기로 쓴다(CoD식 빠른 근접 공격).
7식 소총·5식 권총과 같은 형태 문법: 둥근 베벨, 금색 고리(날밑의 착검 고리), 남색 원판 + 금색 엘프 로고,
회녹 폴리머 손잡이(고리 홈 4줄), 자줏빛 건메탈 날밑·손잡이 머리(착검 홈), 은색 칼날(어두운 피홈, 밝은 날 띠, `3식` 각인).
실존 나이프를 그대로 옮기지 않았다: 둥근 사각 손잡이, 요람형 날밑, 클립 포인트 날은 이 작품용 조합이다.

npm run model -- art/blender/weapons/elfinia/elfinia_bayonet.py
npm run shot -- weapons/elfinia/elfinia_bayonet.glb --views side,34,front,top --focus elfinia_bayonet

원점·축 (왼손 소켓 socket_hand_L에 루트를 그대로 붙인다. three.js에서 -Z = 손가락 방향, +Y = 엄지 쪽)
  - 원점 = 주먹이 감싸는 손잡이 가운데(파지점)
  - Blender +Z = 칼끝 (손잡이 축은 세로, 손잡이 머리는 -Z), +Y = 날(앞), -Y = 등(착검 고리 쪽), ±X = 날 옆면
  - three.js에서는 칼끝 +Y, 날 -Z(손가락 방향). 1인칭에서 보이는 면은 -X(로고·각인 면)
  - 앵커: `tip`(칼끝, 근접 판정 앞 끝), `grip`(원점)

만드는 법: 총기 헬퍼(home_weapons)를 그대로 쓰려고 칼을 총처럼 눕혀(칼끝 +Y, 날 -Z, 고리 +Z) 만든 뒤,
마지막에 X축 +90°를 메시에 구워 세운다. 눕힌 좌표 (x, y, z)는 내보낸 three.js 좌표와 같다.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402

cb.reset()
g = hw.Gun("elfinia_bayonet")
# 칼날 색 (이 스크립트 전용 키, 머티리얼 8개 안). 툰 렌더에서 steel(#cfcac4)은 거의 흰색으로 떠서 그보다 밝은 날 띠가
# 보이지 않고, 날 경사면(옆면과 17°)은 빛 방향에 따라 한 단(×0.78) 어둡게 칠해진다. 어느 단이든 띠가 밝게 읽히도록
# 옆면은 한 단 어두운 은색, 날 띠는 거의 흰 은색으로 둔다. 핀·단추도 같은 밝은 은색(edge)을 써서 steel 슬롯을 비운다.
hw.PAL["blade"] = "#a6a29e"
hw.PAL["edge"] = "#f7f5f1"

# ------------------------------------------------------------------ 치수 (눕힌 좌표: y = 칼 길이, z = 등 쪽 위)
HDL0, HDL1 = -0.0440, 0.0370     # 손잡이 폴리머 (양 끝은 머리·목 고리 안에 숨음)
COL0, COL1 = 0.0355, 0.0425      # 목 고리(건메탈)
G0, G1 = 0.0420, 0.0540          # 날밑 판 (두께 0.012)
POM0, POM1 = -0.0585, -0.0400    # 손잡이 머리
BL0 = 0.0500                     # 칼날 시작 (날밑 안)
TIP_Y = 0.1940                   # 칼끝 (날밑 윗면에서 0.14)
SPINE_Z, EDGE_Z = 0.0100, -0.0140  # 칼날 밑동 폭 0.024
CLIP_Y, BELLY_Y = 0.1460, 0.1400
T_HALF = 0.00225                 # 칼날 반두께 (두께 0.0045)
ZR, RO, RI = 0.0302, 0.0142, 0.0092   # 착검 고리 중심 z, 바깥·안 반지름
GHW = 0.0130                     # 날밑 판 반폭 (X)
QB = -0.0240                     # 날밑 아래(날 쪽) 끝

# ================================================================== 칼날 (단면 로프트)


def spine_z(y):
    if y <= CLIP_Y:
        return SPINE_Z
    u = min((y - CLIP_Y) / (TIP_Y - CLIP_Y), 1.0)
    return SPINE_Z * (1 - u) ** 1.4          # 오목한 클립


def edge_z(y):
    if y <= BELLY_Y:
        return EDGE_Z
    u = min((y - BELLY_Y) / (TIP_Y - BELLY_Y), 1.0)
    return EDGE_Z * (1 - u ** 1.8)           # 둥근 배


def half_t(y):
    if y <= 0.128:
        return T_HALF
    u = (y - 0.128) / (TIP_Y - 0.128)
    return T_HALF + (0.0006 - T_HALF) * u    # 끝으로 갈수록 얇아짐


def lerp(a, b, k):
    return a + (b - a) * max(0.0, min(1.0, k))


def blade_section(y):
    """(x, z) 8점: 옆면 +X, 날 경사 +X, 날 끝, 날 경사 -X, 옆면 -X, 등 모따기 -X, 등, 등 모따기 +X."""
    t, zs, ze = half_t(y), spine_z(y), edge_z(y)
    H = zs - ze
    if y < 0.061:                    # 리카소 (날 없는 밑동)
        bw, te = 0.0008, 0.8 * t
    elif y < 0.070:                  # 플런지 라인 (둥글게 시작하는 날 경사)
        k = (y - 0.061) / 0.009
        bw = 0.0008 + (0.0062 - 0.0008) * math.sqrt(1 - (1 - k) ** 2)
        te = lerp(0.8 * t, 0.0003, k * 1.4)
    else:
        bw, te = 0.0062, 0.0003
    bw = min(bw, 0.5 * H)
    sc = min(lerp(0.0008, 0.0034, (y - 0.150) / 0.016), 0.3 * H)   # 클립 쪽 등날(스웨지)
    tw = lerp(0.55, 0.2, (y - 0.150) / 0.03) * t
    zb = ze + bw
    return [(t, zs - sc), (t, zb), (te, ze), (-te, ze), (-t, zb), (-t, zs - sc), (-tw, zs), (tw, zs)]


def blade_mesh():
    ys = [BL0, 0.056, 0.061, 0.0625, 0.064, 0.066, 0.068, 0.070, 0.085, 0.100, 0.115, 0.128, 0.136, 0.140,
          0.146, 0.150, 0.154, 0.158, 0.162, 0.166, 0.170, 0.174, 0.178, 0.182, 0.186, 0.189, 0.1915]
    bm = bmesh.new()
    rings = [[bm.verts.new((x, y, z)) for (x, z) in blade_section(y)] for y in ys]
    tip = bm.verts.new((0.0, TIP_Y, 0.0))
    k = 8

    def mat_of(j, ym):
        if j in (1, 2, 3):           # 날 경사 띠 (밝게). 리카소의 작은 모따기는 칼날색
            return 1 if ym > 0.0615 else 0
        if j in (5, 7):              # 등 모따기: 클립 구간에서 등날이 되면 밝게
            return 1 if ym > 0.153 else 0
        return 0

    mats = []                        # 면 생성 순서대로 (cb.assign이 material_index를 지우므로 나중에 넣는다)
    for i in range(len(rings) - 1):
        ym = (ys[i] + ys[i + 1]) / 2
        for j in range(k):
            j2 = (j + 1) % k
            bm.faces.new((rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j]))
            mats.append(mat_of(j, ym))
    for j in range(k):
        bm.faces.new((rings[-1][j], rings[-1][(j + 1) % k], tip))
        mats.append(mat_of(j, TIP_Y))
    bm.faces.new(list(reversed(rings[0])))
    mats.append(0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = cb._new_mesh_obj("blade", bm)
    cb.assign(o, hw.M("blade"), hw.M("edge"))
    for poly, mi in zip(o.data.polygons, mats):
        poly.material_index = mi
    cb.smooth(o, angle=12)           # 옆면·날 경사·등 사이는 각지게
    return o


g.s(blade_mesh())
# 피홈 (어두운 긴 원형, 양쪽) + 각인
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    g.f(hw.decal(f"fuller{sx}", hw.stadium(0.050, 0.0046, 6), (sx * T_HALF, 0.097, 0.0035), mat="metal", **fr))
g.f(hw.text("mk_type", "3식", 0.0062, (-T_HALF, 0.084, -0.0034), mat="metal", **hw.LEFT))
g.f(hw.text("mk_serial", "No.0412", 0.0036, (T_HALF, 0.090, -0.0036), mat="metal", **hw.RIGHT))

# ================================================================== 날밑 (요람형 판 + 금색 착검 고리)
RA = RO - 0.0005                     # 판 윗면 = 고리 바깥면 바로 안쪽 (고리 벽 속에 숨음)
a0 = -math.degrees(math.acos(GHW / RA))
cradle = [(RA * math.cos(math.radians(a)), ZR + RA * math.sin(math.radians(a)))
          for a in [a0 + (-180 - 2 * a0) * i / 10 for i in range(11)]]
guard_pts = [(GHW, QB + GHW)] + cradle + [(-GHW, QB + GHW)] + hw.arc_pts(0, QB + GHW, GHW, 180, 360, 8)[1:-1]
g.s(hw.section("guard", guard_pts, G0, G1, bevel=0.0022, seg=2, mat="metal"))


def lathe_ring(name, r_in, r_out, y0, y1, c, *, rr=0.0016, n=2, seg=30, mat="gold"):
    """Y축 고리 (단면 = 둥근 사각형). c = (x, z) 중심."""
    prof = hw.rrect(r_out - r_in, y1 - y0, rr, n=n, cx=(r_in + r_out) / 2, cy=(y0 + y1) / 2)
    bm = bmesh.new()
    rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ca, sa = math.cos(a), math.sin(a)
        rings.append([bm.verts.new((c[0] + r * ca, y, c[1] + r * sa)) for r, y in prof])
    k = len(prof)
    for i in range(seg):
        i2 = (i + 1) % seg
        for j in range(k):
            j2 = (j + 1) % k
            bm.faces.new((rings[i][j], rings[i][j2], rings[i2][j2], rings[i2][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = cb._new_mesh_obj(name, bm)
    cb.smooth(o, angle=50)
    cb.assign(o, hw.M(mat))
    return o


g.s(lathe_ring("muzzle_ring", RI, RO, G0 - 0.0015, G1 + 0.0015, (0, ZR)))
# 날밑 고정 핀 (양쪽). 옆면이 평평한 구간(z ≥ QB + GHW, 아래는 반원으로 말림)에만 붙인다
for sx, fr in ((-1, hw.LEFT), (1, hw.RIGHT)):
    g.f(hw.decal(f"guard_pin{sx}", hw.circle(0.0017, 10), (sx * GHW, (G0 + G1) / 2, -0.0065), mat="edge", **fr))
    g.f(hw.decal(f"guard_pin2{sx}", hw.circle(0.0013, 10), (sx * GHW, (G0 + G1) / 2, 0.0145), mat="edge", **fr))

# 목 고리 (손잡이와 날밑 사이, 건메탈)
g.s(hw.section("collar", hw.rrect(0.0255, 0.0315, 0.0078, n=3), COL0, COL1, bevel=0.0012, seg=2, mat="metal"))

# ================================================================== 손잡이 (회녹 폴리머, 고리 홈 4줄)
GROOVES = (0.0275, 0.0160, 0.0045, -0.0070)
ring_st = [(HDL1, 0.97), (0.0340, 0.98)]
for gy in GROOVES:
    ring_st += [(gy + 0.0024, 1.0), (gy + 0.0012, 0.895), (gy - 0.0012, 0.895), (gy - 0.0024, 1.0)]
ring_st += [(-0.0160, 1.0), (-0.0360, 1.0), (-0.0400, 1.02), (-0.0405, 1.02),
            (-0.0418, 0.70), (HDL0, 0.70)]   # 머리 안에 들어가면 바로 가늘게 (머리 벽과 몇 mm 겹침 방지)
ring_st.sort(key=lambda p: -p[0])
handle = hw.sweep("handle", [(0, y, 0) for y, _ in ring_st], hw.rrect(0.024, 0.030, 0.0075, n=3),
                  side_vec=(1, 0, 0), scales=[(s, s) for _, s in ring_st], smooth=40)
cb.smooth(handle, angle=40)          # 홈 벽은 각지게, 둥근 모서리는 부드럽게
cb.assign(handle, hw.M("olive"), hw.M("olive_d"))
for p in handle.data.polygons:
    cy = p.center.y
    p.material_index = 1 if any(abs(cy - gy) < 0.0023 for gy in GROOVES) else 0
g.s(handle)

# 손잡이 원판 (엘피니아 남색 + 금테 + 엘프 로고): 양쪽. 칼끝이 위로 보이게 세워 붙인다
LOGO_Y = -0.0260
for sx in (-1, 1):
    c = (sx * 0.0120, LOGO_Y, 0.0)
    fr = dict(right=(0, 0, -sx), up=(0, 1, 0))      # 법선 = right x up = sx·X
    g.f(hw.decal(f"medal{sx}", hw.circle(0.0064, 20), c, mat="navy", **fr))   # 금테 안쪽까지만 (겹침 최소)
    g.f(hw.ring_decal(f"medal_rim{sx}", c, 0.0072, 0.0063, mat="gold", lift=0.0008, **fr))
    g.logo(c, 0.0088, mat="gold", name=f"elf_logo{sx}", **fr)

# ================================================================== 손잡이 머리 (건메탈, 착검 홈 + 멈치 단추)
pom_side = [(POM1, -0.0165), (POM1, 0.0185)] + hw.arc_pts(-0.0525, 0.0125, 0.0060, 90, 180, 3) + \
    hw.arc_pts(-0.0525, -0.0105, 0.0060, 180, 270, 3)
pommel = hw.sculpt("pommel", pom_side, hw.rrect(0.027, 0.035, 0.0085, n=3, cy=0.001), bevel=0.0015, seg=2,
                   mat="metal")
# 착검 홈: 등 쪽(+z)에서 손잡이 머리 끝으로 열린 홈 (7식 소총의 착검 돌기가 들어감). 잘린 면은 어두운 색
slot = hw.boxr("lug_slot_cut", -0.0036, 0.0036, -0.0700, -0.0470, 0.0115, 0.0300, mat="dark")
bm_ = pommel.modifiers.new("Slot", "BOOLEAN")
bm_.object = slot
bm_.operation = "DIFFERENCE"
bm_.solver = "EXACT"
bm_.material_mode = "TRANSFER"
for nm in [m.name for m in pommel.modifiers if m.type == "BEVEL"]:
    pommel.modifiers.move(pommel.modifiers.find(nm), len(pommel.modifiers) - 1)
slot.hide_render = True
cb.apply_modifiers(pommel)
bpy.data.objects.remove(slot, do_unlink=True)
g.s(pommel)
# 착검 멈치 단추 (-X, 1인칭 쪽) + 반대쪽 스프링 핀
g.s(hw.xcyl("release", 0.0034, -0.0146, -0.0105, y=-0.0500, z=0.0040, verts=16, bevel=0.0008, seg=2,
            mat="edge"))
g.f(hw.decal("release_pin", hw.circle(0.0016, 10), (0.0135, -0.0500, 0.0040), mat="edge", **hw.RIGHT))

# ================================================================== 세우기 (X축 +90°: 칼끝 +Y → +Z, 날 -Z → +Y)
RX = Matrix.Rotation(math.radians(90), 4, "X")
for o in g.static + g.fine:
    cb.apply_modifiers(o)
    o.data.transform(RX @ o.matrix_world)
    o.matrix_world = Matrix.Identity(4)

# ================================================================== 앵커 (세운 Blender 좌표)
g.anchor("tip", (0, 0, TIP_Y))
g.anchor("grip", (0, 0, 0))

g.finish("weapons/elfinia/elfinia_bayonet.glb", outline=0.0015, fp="0.12,-0.16,-0.25", fprot="0,0,0")
