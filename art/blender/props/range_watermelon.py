"""사격장 근접 훈련용 수박 (프롤로그 함내 사격장, 칼 베기 튜토리얼).

npm run model -- art/blender/props/range_watermelon.py
npm run shot -- props/range_watermelon.glb --views front,34,side,top
PREVIEW=1 npm run model -- art/blender/props/range_watermelon.py
  → public/models/_tmp/range_watermelon_preview.glb (반쪽을 벌려 단면을 앞으로 돌린 확인용, 커밋 안 함)

원점 = 수박 바닥(z=0). 0.26 x 0.26 x 0.235 m (엘프에게 큰, 약간 납작한 공). 정면(-Y) 아래쪽에 노란 바닥 자국.
노드 (루트 range_watermelon 아래, 원점 = 구 중심 (0, 0, 0.1175)):
  fruit_whole        온전한 수박 (꼭지 포함)
  fruit_half_neg     x<0 반쪽. 자른 면은 x=0 평면에서 +X를 향한다
  fruit_half_pos     x>0 반쪽. 꼭지가 이쪽에 붙어 있고 자른 면은 -X를 향한다
    └ fruit_half_*_seeds  씨앗 (noOutline, 과육 면 위로 0.9 mm)
  fruit_chunk_01..04 튀는 과육 조각 (원점 = 조각 중심). 쉴 때는 수박 속에 숨어 있다
런타임이 노드를 켜고 끈다: 처음엔 fruit_whole만, 베면 반쪽 둘 + 조각 (반쪽·조각에 extras hidden=1 표시).
반쪽의 겉면은 온전한 구를 한 번 만들고 색을 칠한 뒤 x=0으로 잘라 복사한 것이라 줄무늬가 정확히 같다.
색은 정점색 머티리얼 하나(lk_vc)에 모은다.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import level_kit as lk  # noqa: E402

cb.reset()
PREVIEW = os.environ.get("PREVIEW", "") not in ("", "0")

A = 0.130     # 가로 반지름 (x, y)
C = 0.1175    # 세로 반지름 (z) → 높이 0.235
STRIPES = 10  # 짙은 줄무늬 수 (줄 하나 = 경선 칸 3개: 짙은 1 + 밝은 2)
BANDS = 14    # 위도 띠 수
T_SKIN = 0.005    # 단면 바깥 초록 겉껍질 띠
T_CREAM = 0.011   # 그 안쪽 흰 껍질 띠
SEED_H = 0.0009   # 씨앗이 과육 면 위로 솟은 높이

COL = {
    "rind": "#7bcb4e",    # 밝은 초록 껍질
    "stripe": "#2e7031",  # 짙은 초록 줄무늬
    "spot": "#e8e2a4",    # 바닥 자국 (연노랑)
    "stem": "#6f6a2e",    # 마른 꼭지
    "skin": "#3f8d3a",    # 단면의 겉껍질 띠
    "cream": "#f4f1d6",   # 흰 껍질
    "flesh": "#ff5d6c",   # 과육
    "seed": "#2b1b18",    # 씨앗
}
KEYS = list(COL)
KI = {k: i for i, k in enumerate(KEYS)}
SURF = {KI["rind"], KI["stripe"], KI["spot"]}     # 타원체 겉면: 해석적 노멀
CUT = {KI["skin"], KI["cream"], KI["flesh"]}       # 자른 면: 평평한 노멀


def _srgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def ell_normal(p, a=A, c=C):
    return Vector((p.x / (a * a), p.y / (a * a), p.z / (c * c))).normalized()


# ------------------------------------------------------------------ 겉면 (줄무늬 타원체)

def dome(a=A, c=C, stripes=STRIPES, bands=BANDS, seed=7):
    """경선이 물결치는 UV 타원체. 짙은 줄무늬 = 경선 칸, 면 material_index에 색 키."""
    rng = random.Random(seed)
    P = 2 * math.pi / stripes
    ph = [rng.uniform(0, 2 * math.pi) for _ in range(stripes)]
    dph = [rng.uniform(0.6, 1.4) for _ in range(stripes)]
    tw = rng.uniform(0, 2 * math.pi)

    def edge(s, th, j, right):
        """줄무늬 s의 왼쪽(0)/오른쪽(1) 경계 방위각. 느린 물결 + 위도마다 엇갈리는 톱니."""
        p = ph[s] + (dph[s] if right else 0.0)
        w = 0.10 * P * math.sin(3.0 * th + p) + 0.05 * P * math.sin(1.5 * th + tw)
        zig = 0.07 * P * (1 if (j + s + right) % 2 else -1) * math.sin(th)
        return s * P + (0.40 * P if right else 0.0) + w + zig

    bm = bmesh.new()
    top = bm.verts.new((0, 0, c))
    bot = bm.verts.new((0, 0, -c))
    rings = []
    for j in range(1, bands):
        th = math.pi * j / bands
        az = []
        for s in range(stripes):
            e0 = edge(s, th, j, 0)
            e1 = edge(s, th, j, 1)
            n0 = edge((s + 1) % stripes, th, j, 0) + (2 * math.pi if s + 1 == stripes else 0.0)
            az += [e0, e1, (e1 + n0) / 2]
        for k in range(len(az) - 1):
            assert az[k] < az[k + 1], ("경선 순서가 꼬임", j, k)
        rings.append([bm.verts.new((a * math.sin(th) * math.cos(f), a * math.sin(th) * math.sin(f),
                                    c * math.cos(th))) for f in az])
    n = stripes * 3
    for i in range(n):
        i2 = (i + 1) % n
        key = KI["stripe"] if i % 3 == 0 else KI["rind"]
        faces = [bm.faces.new((top, rings[0][i], rings[0][i2]))]
        for j in range(len(rings) - 1):
            faces.append(bm.faces.new((rings[j][i], rings[j + 1][i], rings[j + 1][i2], rings[j][i2])))
        faces.append(bm.faces.new((rings[-1][i], bot, rings[-1][i2])))
        for f in faces:
            f.material_index = key
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def spot(bm, caps, a=A, c=C):
    """바닥 자국: 정규화 공간에서 구 캡 여러 개(합집합)로 자르고 칠한다. caps = [(방위각, 극각, 반각) 도]."""
    S = Matrix.Diagonal((1 / a, 1 / a, 1 / c, 1.0))
    bmesh.ops.transform(bm, matrix=S, verts=bm.verts[:])
    us = []
    for az, pol, ang in caps:
        az, pol, ang = (math.radians(x) for x in (az, pol, ang))
        u = Vector((math.sin(pol) * math.cos(az), math.sin(pol) * math.sin(az), math.cos(pol)))
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-7,
                               plane_co=u * math.cos(ang), plane_no=u)
        us.append((u, math.cos(ang)))
    for f in bm.faces:
        m = f.calc_center_median()
        if any(m.dot(u) > ca + 1e-7 for u, ca in us):
            f.material_index = KI["spot"]
    bmesh.ops.transform(bm, matrix=S.inverted(), verts=bm.verts[:])


def stem(bm, base):
    """마른 꼭지: 굽은 육각 원뿔대. base = 겉면 위 뿌리 (조금 파묻힘)."""
    bx, by, bz = base
    path = [(bx, by, bz - 0.004), (bx + 0.001, by, bz + 0.007), (bx + 0.005, by + 0.001, bz + 0.0145),
            (bx + 0.011, by + 0.002, bz + 0.0185)]
    radii = [0.0072, 0.0058, 0.0050, 0.0046]
    rows = []
    for k, (p, r) in enumerate(zip(path, radii)):
        p = Vector(p)
        d = (Vector(path[min(k + 1, 3)]) - Vector(path[max(k - 1, 0)])).normalized()
        q = d.to_track_quat("Z", "Y")
        rows.append([bm.verts.new(p + q @ Vector((r * math.cos(2 * math.pi * i / 6), r * math.sin(2 * math.pi * i / 6), 0)))
                     for i in range(6)])
    faces = []
    for k in range(3):
        for i in range(6):
            i2 = (i + 1) % 6
            faces.append(bm.faces.new((rows[k][i], rows[k][i2], rows[k + 1][i2], rows[k + 1][i])))
    faces.append(bm.faces.new(rows[-1]))
    for f in faces:
        f.material_index = KI["stem"]
    bmesh.ops.recalc_face_normals(bm, faces=faces)


# ------------------------------------------------------------------ 자른 면

def halve(src, side):
    """src(닫힌 겉면)를 x=0으로 잘라 side(+1/-1) 쪽만 남기고 단면을 닫는다."""
    bm = src.copy()
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6,
                           plane_co=(0, 0, 0), plane_no=(side, 0, 0), clear_inner=True)
    loop = sorted({v for e in bm.edges if e.is_boundary for v in e.verts},
                  key=lambda v: math.atan2(v.co.z, v.co.y))
    for v in loop:
        v.co.x = 0.0

    def inset(p, d):
        q = Vector((0.0, p.y, p.z))
        return q * ((q.length - d) / q.length)

    L1 = [bm.verts.new(inset(v.co, T_SKIN)) for v in loop]
    L2 = [bm.verts.new(inset(v.co, T_SKIN + T_CREAM)) for v in loop]
    ctr = bm.verts.new((0.0, 0.0, 0.0))
    n = len(loop)
    for i in range(n):
        k = (i + 1) % n
        bm.faces.new((loop[i], loop[k], L1[k], L1[i])).material_index = KI["skin"]
        bm.faces.new((L1[i], L1[k], L2[k], L2[i])).material_index = KI["cream"]
        bm.faces.new((L2[i], L2[k], ctr)).material_index = KI["flesh"]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    assert not any(e.is_boundary for e in bm.edges), "반쪽 메시에 구멍"
    return bm, loop


def seeds(side, flesh_ry, flesh_rz, count=12, seed=3):
    """단면 씨앗: 느슨한 고리, 뾰족한 끝이 가운데를 향하는 물방울 (8각, 윗면 + 옆면)."""
    rng = random.Random(seed)
    bm = bmesh.new()
    nx = -side  # 단면이 바라보는 방향 (x)
    for k in range(count):
        t = 2 * math.pi * (k + rng.uniform(-0.22, 0.22)) / count + 0.2
        fr = rng.uniform(0.50, 0.68) * (1.0 if k % 2 else 0.9)
        cy, cz = math.cos(t) * flesh_ry * fr, math.sin(t) * flesh_rz * fr
        ru = Vector((0, math.cos(t), math.sin(t)))             # 바깥 (둥근 끝)
        rv = Vector((0, -math.sin(t), math.cos(t)))
        rot = rng.uniform(-0.35, 0.35)
        ru, rv = ru * math.cos(rot) + rv * math.sin(rot), rv * math.cos(rot) - ru * math.sin(rot)
        L, W = rng.uniform(0.0150, 0.0170), rng.uniform(0.0092, 0.0104)
        c = Vector((0, cy, cz))
        pts = []
        for i in range(8):
            s = 2 * math.pi * i / 8
            u = L / 2 * math.cos(s)
            v = W / 2 * math.sin(s) * (0.30 + 0.70 * (1 + math.cos(s)) / 2)
            pts.append(c + ru * u + rv * v)
        lo = [bm.verts.new(p + Vector((-nx * 0.0004, 0, 0))) for p in pts]
        hi = [bm.verts.new(p * 1.0 + Vector((nx * SEED_H, 0, 0))) for p in pts]
        faces = [bm.faces.new(hi)]
        for i in range(8):
            i2 = (i + 1) % 8
            faces.append(bm.faces.new((lo[i], lo[i2], hi[i2], hi[i])))
        for f in faces:
            f.material_index = KI["seed"]
            f.normal_update()
        # 윗면이 단면 바깥(nx)을 향하게
        if faces[0].normal.x * nx < 0:
            for f in faces:
                f.normal_flip()
    return bm


# ------------------------------------------------------------------ 튀는 조각

def chunk(seed, size):
    """불규칙한 쐐기 조각: 분홍 과육 + 바깥쪽 흰 껍질 띠 + 초록 겉면."""
    rng = random.Random(seed)
    w, h, d = size * rng.uniform(0.85, 1.0), size, size * rng.uniform(0.55, 0.7)
    # 단면 삼각형 (u, v): 꼭짓점 A가 안쪽, B-C가 겉껍질
    A2 = (rng.uniform(-0.1, 0.1) * w, -0.55 * h)
    B2 = (-0.5 * w, 0.45 * h)
    C2 = (0.5 * w, 0.40 * h)
    f = 0.24  # 흰 껍질 두께 비율

    def lerp(p, q, t):
        return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    B1, C1 = lerp(B2, A2, f), lerp(C2, A2, f)
    bm = bmesh.new()
    prof = [A2, B1, B2, C2, C1]           # 반시계: A, B1, B2, C2, C1
    lay = []
    for z in (-d / 2, d / 2):
        lay.append([bm.verts.new((u + rng.uniform(-0.08, 0.08) * size, v + rng.uniform(-0.06, 0.06) * size,
                                  z + rng.uniform(-0.08, 0.08) * size)) for (u, v) in prof])
    a0, b10, b20, c20, c10 = lay[0]
    a1, b11, b21, c21, c11 = lay[1]
    F = []
    F.append((bm.faces.new((a0, c10, b10)), "flesh"))
    F.append((bm.faces.new((b10, c10, c20, b20)), "cream"))
    F.append((bm.faces.new((a1, b11, c11)), "flesh"))
    F.append((bm.faces.new((b11, b21, c21, c11)), "cream"))
    F.append((bm.faces.new((b20, c20, c21, b21)), "rind"))      # 겉면
    F.append((bm.faces.new((a0, b10, b11, a1)), "flesh"))
    F.append((bm.faces.new((b10, b20, b21, b11)), "cream"))
    F.append((bm.faces.new((c10, a0, a1, c11)), "flesh"))
    F.append((bm.faces.new((c20, c10, c11, c21)), "cream"))
    for fc, k in F:
        fc.material_index = KI[k]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # 원점 = 조각 중심
    cen = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
    bmesh.ops.translate(bm, vec=-cen, verts=bm.verts[:])
    e = Vector((rng.uniform(0, 360), rng.uniform(0, 360), rng.uniform(0, 360)))
    R = (Matrix.Rotation(math.radians(e.z), 4, "Z") @ Matrix.Rotation(math.radians(e.y), 4, "Y")
         @ Matrix.Rotation(math.radians(e.x), 4, "X"))
    bmesh.ops.transform(bm, matrix=R, verts=bm.verts[:])
    return bm


# ------------------------------------------------------------------ 메시 오브젝트

VC = lk.vc_material()


def to_obj(name, bm, *, parent, loc=(0, 0, 0), flat=False, **props):
    """bmesh → 정점색 메시. 겉면 = 타원체 해석적 노멀, 단면 = 평면 노멀, 나머지 = 매끈/평평."""
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    keys = [p.material_index for p in me.polygons]
    for p in me.polygons:
        p.material_index = 0
        p.use_smooth = not flat
    ca = me.color_attributes.new(name="Col", type="BYTE_COLOR", domain="CORNER")
    cols = {k: (*_srgb(COL[KEYS[k]]), 1.0) for k in set(keys)}
    for p in me.polygons:
        for li in p.loop_indices:
            ca.data[li].color_srgb = cols[keys[p.index]]
    me.update()
    if not flat:
        base = [Vector(n.vector) for n in me.corner_normals]
        nl = []
        for p in me.polygons:
            k = keys[p.index]
            for li in p.loop_indices:
                if k in SURF:
                    nl.append(ell_normal(me.vertices[me.loops[li].vertex_index].co))
                elif k in CUT or k == KI["seed"]:
                    nl.append(Vector(p.normal))
                else:
                    nl.append(base[li])
        me.normals_split_custom_set([tuple(n) for n in nl])
    o = bpy.data.objects.new(name, me)
    cb.link(o, parent)
    cb.assign(o, VC)
    o.location = loc
    for k, v in props.items():
        o[k] = v
    return o


def tris(o):
    o.data.calc_loop_triangles()
    return len(o.data.loop_triangles)


# ------------------------------------------------------------------ 조립

root = cb.empty("range_watermelon", size=0.3)
CEN = (0.0, 0.0, C)

surf = dome()
# 정면(-Y)에서 +X로 35° 돌아간 아래쪽: 두 캡을 겹친 타원형 자국
spot(surf, [(-55, 124, 13), (-47, 128, 10), (-63, 128, 9.5)])

STEM_X = 0.011   # 꼭지는 x>0 반쪽에 온전히 들어가게 축에서 비켜 둔다
stem_base = (STEM_X, 0.0, C * math.sqrt(max(0.0, 1 - (STEM_X / A) ** 2)))

whole_bm = surf.copy()
stem(whole_bm, stem_base)
whole = to_obj("fruit_whole", whole_bm, parent=root, loc=CEN)

neg_bm, neg_loop = halve(surf, -1)
pos_bm, pos_loop = halve(surf, +1)
stem(pos_bm, stem_base)
ry = max(abs(v.co.y) for v in pos_loop) - T_SKIN - T_CREAM
rz = max(abs(v.co.z) for v in pos_loop) - T_SKIN - T_CREAM
# hidden=1: 처음엔 숨긴다는 표시 (레벨 로더 규약과 같은 이름. 소품 인스턴스에는 로더가 적용하지 않으니 칼 베기 연출이 끈다)
half_neg = to_obj("fruit_half_neg", neg_bm, parent=root, loc=CEN, hidden=1)
half_pos = to_obj("fruit_half_pos", pos_bm, parent=root, loc=CEN, hidden=1)
surf.free()
seed_neg = to_obj("fruit_half_neg_seeds", seeds(-1, ry, rz), parent=half_neg, noOutline=1)
seed_pos = to_obj("fruit_half_pos_seeds", seeds(+1, ry, rz), parent=half_pos, noOutline=1)

CHUNKS = [(-0.012, -0.035, 0.030, 0.052), (0.012, 0.040, 0.020, 0.046),
          (-0.010, 0.020, -0.040, 0.056), (0.014, -0.030, -0.030, 0.044)]
chunks = []
for i, (x, y, z, s) in enumerate(CHUNKS, start=1):
    chunks.append(to_obj(f"fruit_chunk_{i:02d}", chunk(40 + i, s), parent=root, flat=True,
                         loc=(x, y, C + z), outline=0.003, hidden=1))

print(f"[melon] tris whole={tris(whole)} half_neg={tris(half_neg)}+{tris(seed_neg)} "
      f"half_pos={tris(half_pos)}+{tris(seed_pos)} chunks={[tris(c) for c in chunks]}")
print(f"[melon] flesh radii y={ry:.4f} z={rz:.4f}, cut loop pts={len(pos_loop)}/{len(neg_loop)}")

if PREVIEW:
    # 확인용 배치: 반쪽 단면을 앞(-Y)으로 돌려 좌우에 벌리고, 온전한 수박은 뒤, 조각은 앞에 늘어놓는다
    half_neg.location = (-0.17, 0.0, C)
    half_neg.rotation_euler = (0, 0, math.radians(-90))
    half_pos.location = (0.17, 0.0, C)
    half_pos.rotation_euler = (0, 0, math.radians(90))
    whole.location = (0.0, 0.30, C)
    for i, ch in enumerate(chunks):
        ch.location = (-0.15 + 0.10 * i, -0.24, 0.035)
    cb.export("_tmp/range_watermelon_preview.glb", props={"outline": 0.004}, root=root)
else:
    cb.export("props/range_watermelon.glb", props={"outline": 0.004}, root=root)
