"""엘프 차량 공용 헬퍼 (vehicles_elf).

교주 차원 모나티엄 진압반(아군)과 R41 모나티엄 제국군(적)의 차량, 차량 전용 거치 무기를 만든다.
차량 규약: docs/art/VEHICLES.md, 목록과 설정: docs/art/vehicles-elf.md

사용:
    import os, sys
    sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
    import cb, vehicles_elf as ve
    cb.reset()
    V = ve.Veh("monatium_riot_apc", "monatium")
    V.body(ve.sculpt("hull", side_pts, sec_pts, bevel=0.03, mat=V.M["hull"]))
    V.group("turret", (0, -0.3, 1.7))                    # 포탑 (차량 좌표계)
    V.to("turret", obj, ...)
    V.wheel("wheel_FL", (0.86, -1.35, 0.44), 0.44, 0.32, steer=1)
    V.empty("seat_driver", (0.45, -1.2, 1.38))
    V.finish("vehicles/monatium/monatium_riot_apc.glb", props={...}, budget=22000)

노드 계층 (finish가 만든다)
    <루트: 차량 id>                 루트 커스텀 속성 (vehicleClass, mass, maxSpeed, wheelbase, track, armor, outline ...)
      body                         빈 오브젝트. 자식 body_<머티리얼> 메시 + body_decals(noOutline)
      wheel_FL ...                 메시. 원점 = 바퀴 중심. radius, steer
      turret                       빈 오브젝트. 자식 turret_<머티리얼>
        gun_pitch                  빈 오브젝트. 자식 gun_<머티리얼>, muzzle_main ...
      mount_<id>                   빈 오브젝트(Z 180°). weapon, model, yawMin/yawMax, pitchMin/pitchMax, restYawDeg
        muzzle_<id>
      hatch_*, door_*              메시. 원점 = 경첩. rotAxis, rotDeg (three.js 부모 공간)
      light_head_L ...             메시 (UNLIT)
      seat_*, enter_*, exhaust_*   빈 오브젝트
      COL_*                        충돌 전용 메시 (투명 UNLIT_collider, noOutline)

조준 노드 (노획 미군 세트 vehicles_us와 같은 규칙)
    turret, gun_pitch: 차량 좌표계 그대로 (회전 없음, three.js 정면 +Z). turret은 three Y축(+ = 차량 왼쪽),
                       gun_pitch는 three X축으로 돈다(포구가 위로 = -X 회전).
    mount_*:           Blender Z축 180° 돌려 두고 restYawDeg=180을 단다. 로컬 +Y(Blender) = 로컬 -Z(three)가 총구 쪽이라
                       무기 glb(총구 +Y)를 변환 없이 자식으로 붙이면 차량 정면을 본다. 런타임은 rest 회전 위에
                       로컬 yaw(Y)와 pitch(X, + = 위)를 곱한다. yaw·pitch 범위가 0이면 고정 거치(부모가 조준).

좌표: 1 BU = 1 m, Z-up, 차량 정면 -Y, 차량 왼쪽 = +X (_L), 원점 = 차체 중심 아래 지면.
"""
from __future__ import annotations

import math

import bmesh
import bpy
from mathutils import Matrix, Vector

import cb
import home_weapons as hw   # 수정하지 않고 2D 외곽선·데칼·글자·엘프 로고·스윕만 빌려 쓴다
import r41                  # 수정하지 않고 모따기 덩어리·n각 기둥·팔레트만 빌려 쓴다

# ================================================================== palette
# 모나티엄 진압반: weapons-home.md 3장(home_weapons.PAL)과 monatium_sop.PAL에서 가져온 값
MON = {
    "hull": "#706478",      # 진압반 남보라 (지휘색): 차체 외장
    "hull_l": "#857a8d",    # 밝은 남보라: 지붕판, 포탑 덮개, 귀 지느러미 (큰 면이 너무 어둡지 않게)
    "hull_d": "#56445b",    # 남보라 그림자: 아래 차체, 펜더, 로고 원판
    "gear": "#433c44",      # 진압 장비 회색 (monatium_sop gear): 범퍼, 격자, 차대, 손잡이
    "rubber": "#2a252b",    # 타이어, 고무 패드 테두리
    "steel": "#cfcac4",     # 은색 금속 (진압반 일반 금속): 휠 캡, 격자 봉, 손잡이, 글자
    "gold": "#d6b25e",      # 금색: 엘프 로고와 로고 원판 테에만 (금색 줄은 쓰지 않음)
    "teal": "#3f9a94",      # 비살상 표식: 차체 띠, 범퍼 고무 패드
    "hazard": "#e8c34a",    # 경고 노랑: 범퍼 끝, 물대포 경고
    "lens": "#26303a",      # 창, 꺼진 렌즈
    "glow": "#7ff0ea",      # UNLIT 시안: 경광등, 센서
    "lamp": "#ffe7a6",      # UNLIT 전조등
    "tail": "#ff7a6b",      # UNLIT 후미등
    "cabin": "#6b6370",     # 실내 (껍데기 안쪽 면, 계기판)
    "glass": "#26303a",     # 창유리 (반투명 0.35)
}
MON_GLOW = ("glow", "lamp", "tail")
MON_DARK = {"gear", "rubber", "lens", "hull_d"}
MON_LINE = hw.LINE           # 붉은 갈색 먹선 #4a2229
MON_LINE_DARK = hw.LINE_DARK

# R41 제국: r41-style.md 3장 (r41.PAL)과 같은 값
R41 = {
    "light": r41.PAL["light"],      # PV 소총 회백: 차체 외장
    "shell": r41.PAL["shell"],      # 제국 흑: 아래 차체, 말벌 띠, 롤케이지, 바퀴 휠
    "metal": r41.PAL["metal"],      # 건메탈: 포신, 서스펜션, 기계부
    "amber": r41.PAL["amber"],      # 앰버: 띠, 가는 줄, 엘프 로고 (어두운 면)
    "ceramic": r41.PAL["ceramic"],  # 본 화이트: 드론 벌집 띠, 노획 태그
    "steel": r41.PAL["steel"],      # 핀, 볼트, 렌즈 테
    "polymer": r41.PAL["polymer"],  # 슬레이트 라벤더: 좌석, 보조 판
    "rubber": r41.PAL["rubber"],    # 타이어
    "visor": r41.PAL["visor"],      # 연기색 창, 잠망경
    "glow": r41.PAL["glow"],        # UNLIT 마젠타: 센서 눈, 후미등, 드론 상태등
    "glow_dim": r41.PAL["glow_dim"],  # UNLIT 바이올렛: 화면
    "glow_amber": r41.PAL["glow_amber"],  # UNLIT 앰버: 전조등
    "cabin": "#47434f",     # 실내 (껍데기 안쪽 면, 계기판)
    "glass": r41.PAL["visor"],  # 창유리·잠망경 (반투명 0.4)
}
R41_GLOW = ("glow", "glow_dim", "glow_amber")
R41_LINE = dict(r41.LINE, visor="#1d1a24")


def mats(faction: str) -> dict:
    """진영 팔레트 머티리얼 + 투명 충돌 머티리얼. 이름: mv_<키> (모나티엄), rv_<키> (R41)."""
    M = {}
    if faction == "monatium":
        for k, c in MON.items():
            if k in MON_GLOW:
                M[k] = cb.mat(f"mv_{k}", c, emission=c, unlit=True)
            elif k == "glass":
                M[k] = cb.mat(f"mv_{k}", c, alpha=0.35, line=MON_LINE_DARK)
            else:
                M[k] = cb.mat(f"mv_{k}", c, line=MON_LINE_DARK if k in MON_DARK else MON_LINE, roughness=0.55)
    else:
        for k, c in R41.items():
            if k in R41_GLOW:
                M[k] = cb.mat(f"rv_{k}", c, emission=c, unlit=True)
            elif k == "glass":
                M[k] = cb.mat(f"rv_{k}", c, alpha=0.4, line=R41_LINE["visor"])
            else:
                M[k] = cb.mat(f"rv_{k}", c, line=R41_LINE.get(k, R41_LINE["shell"]), roughness=0.5)
    M["collider"] = cb.mat("collider", "#ff00ff", unlit=True, alpha=0.0)
    return M


# ================================================================== 2D outlines

def round_poly(pts, r, n=3):
    """다각형 (u, v) 꼭짓점을 둥글린다. r = 반지름(숫자 또는 꼭짓점별 목록), n = 꼭짓점당 분할.

    n=1이면 45° 모따기가 된다 (R41 형태 언어). 반지름은 이웃 변 길이의 절반을 넘지 않게 줄인다.
    """
    N = len(pts)
    rs = list(r) if isinstance(r, (list, tuple)) else [r] * N
    out = []
    for i in range(N):
        P = Vector(pts[i])
        A = Vector(pts[i - 1])
        B = Vector(pts[(i + 1) % N])
        ri = rs[i]
        u1 = A - P
        u2 = B - P
        l1, l2 = u1.length, u2.length
        if ri <= 0 or l1 < 1e-9 or l2 < 1e-9:
            out.append((P.x, P.y))
            continue
        u1.normalize()
        u2.normalize()
        ang = math.acos(max(-1.0, min(1.0, u1.dot(u2))))
        if ang < 1e-3 or ang > math.pi - 1e-3:
            out.append((P.x, P.y))
            continue
        d = min(ri / math.tan(ang / 2), l1 * 0.49, l2 * 0.49)
        p1, p2 = P + u1 * d, P + u2 * d
        for k in range(n + 1):
            t = k / n
            q = (1 - t) ** 2 * p1 + 2 * (1 - t) * t * P + t * t * p2
            out.append((q.x, q.y))
    return out


def mirror_pts(half):
    """오른쪽 반쪽 외곽선 [(u>=0, v) 아래→위] 을 좌우 대칭 닫힌 외곽선으로 (반시계)."""
    left = [(-u, v) for u, v in reversed(half) if abs(u) > 1e-9]
    return list(half) + left


# ================================================================== solids

def sculpt(name, side_pts, sec_pts, *, bevel=0.0, seg=3, mat=None, x_center=0.0):
    """옆모습(y, z) ∩ 단면(x, z) 둥근 덩어리 (모나티엄). home_weapons.sculpt와 같다."""
    return hw.sculpt(name, side_pts, sec_pts, x_center=x_center, bevel=bevel, seg=seg, mat=mat)


def facet(name, side_pts, sec_pts, *, ch=0.0, mat=None, x_center=0.0):
    """옆모습(y, z) ∩ 단면(x, z) 모따기 덩어리 (R41). r41.faceted와 같다."""
    return r41.faceted(name, side_pts, sec_pts, x_center=x_center, ch=ch, seg=1, mat=mat)


def side(name, pts, width, x=0.0, *, bevel=0.0, seg=2, mat=None):
    """옆모습 (y, z)를 X 두께로 돌출 (x = 중심)."""
    return hw.side(name, pts, width, x, bevel=bevel, seg=seg, mat=mat)


def plate(name, pts, depth, center, *, axis="Z", bevel=0.0, seg=2, mat=None):
    """2D 외곽선을 axis 방향 두께로 돌출. axis='Z': (u=X, v=Y), 'X': (u=Y, v=Z), 'Y': (u=X, v=Z)."""
    o = cb.profile_extrude(name, pts, depth, axis=axis, loc=center, material=mat)
    if bevel > 0:
        cb.add_bevel(o, bevel, seg, angle=40)
    else:
        cb.smooth(o, angle=35)
    return o


def rbox(name, x0, x1, y0, y1, z0, z1, *, r=0.0, seg=1, mat=None):
    """범위로 주는 상자. r = 베벨 (모나티엄은 seg 2~3, R41은 seg 1)."""
    return cb.box(name, size=(x1 - x0, y1 - y0, z1 - z0), loc=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                  bevel=r, bevel_segments=seg, material=mat)


def bar(name, p0, p1, r, *, verts=8, mat=None, r1=None, cap=True):
    """두 점을 잇는 원기둥(봉). verts=6이면 육각 봉 (R41 롤케이지)."""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    L = d.length
    o = cb.cylinder(name, radius=r, radius2=r if r1 is None else r1, depth=L, verts=verts, material=mat, cap=cap)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    o.matrix_world = Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4()
    cb.smooth(o, angle=40 if verts > 6 else 30)
    return o


def lathe(name, prof, center, *, axis="X", seg=24, mat=None, smooth=40.0, closed=True, rot0=0.0):
    """(반지름, 축 오프셋) 닫힌 외곽선을 축 둘레로 돌린 회전체 (타이어, 휠, 돔).

    axis: 'X' | 'Y' | 'Z'. closed=False면 처음과 끝 고리를 잇지 않는다 (반지름 0인 끝점은 넣지 말 것).
    """
    bm = bmesh.new()
    cx, cy, cz = center
    rings = []
    for (r, a) in prof:
        ring = []
        for i in range(seg):
            t = 2 * math.pi * i / seg + rot0
            c, s = math.cos(t) * r, math.sin(t) * r
            if axis == "X":
                p = (cx + a, cy + c, cz + s)
            elif axis == "Y":
                p = (cx + c, cy + a, cz + s)
            else:
                p = (cx + c, cy + s, cz + a)
            ring.append(bm.verts.new(p))
        rings.append(ring)
    n = len(rings)
    for k in range(n if closed else n - 1):
        A, B = rings[k], rings[(k + 1) % n]
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new((A[i], A[j], B[j], B[i]))
    if not closed:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = cb._new_mesh_obj(name, bm)
    cb.smooth(o, angle=smooth)
    if mat:
        cb.assign(o, mat)
    return o


def dome(name, center, rx, ry, rz, *, seg=24, rings=8, mat=None, z_cut=0.0):
    """반구 돔 (아래가 열림). center = 바닥 중심. z_cut>0이면 그 높이(비율)부터 시작."""
    prof = []
    for i in range(rings + 1):
        a = math.pi / 2 * (z_cut + (1 - z_cut) * i / rings)
        prof.append((max(math.cos(a), 0.02), math.sin(a)))
    bm = bmesh.new()
    cx, cy, cz = center
    rr = []
    for (c, s) in prof:
        ring = [bm.verts.new((cx + rx * c * math.cos(2 * math.pi * j / seg), cy + ry * c * math.sin(2 * math.pi * j / seg),
                              cz + rz * s)) for j in range(seg)]
        rr.append(ring)
    for k in range(len(rr) - 1):
        A, B = rr[k], rr[k + 1]
        for j in range(seg):
            j2 = (j + 1) % seg
            bm.faces.new((A[j], A[j2], B[j2], B[j]))
    bm.faces.new(rr[-1])
    bm.faces.new(list(reversed(rr[0])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = cb._new_mesh_obj(name, bm)
    cb.smooth(o, angle=60)
    if mat:
        cb.assign(o, mat)
    return o


def slab(name, pts, origin, u, v, depth, *, mat=None, bevel=0.0, seg=2, lift=0.0):
    """평면 (u, v) 위의 2D 외곽선을 법선(u x v) 방향으로 depth만큼 세운 판 (기운 면 위의 창, 문, 패드)."""
    U, W = Vector(u).normalized(), Vector(v).normalized()
    N = U.cross(W).normalized()
    O = Vector(origin) + N * lift
    bm = bmesh.new()
    bot = [bm.verts.new(O + U * a + W * b) for a, b in pts]
    top = [bm.verts.new(O + U * a + W * b + N * depth) for a, b in pts]
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(top)
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = cb._new_mesh_obj(name, bm)
    if bevel > 0:
        cb.add_bevel(o, bevel, seg, angle=40)
    else:
        cb.smooth(o, angle=35)
    if mat:
        cb.assign(o, mat)
    return o


def paint(obj, rules, *, slots):
    """면 색칠: 베벨을 적용하고 평면으로 자른 뒤, 조건에 맞는 면에 머티리얼을 준다.

    slots: 머티리얼 목록 (첫 번째 = 기본). rules: [(머티리얼, 조건 함수(중심 Vector, 법선 Vector) -> bool, 자를 평면 목록)]
    자를 평면 = (축 'x'|'y'|'z', 값). 나중 규칙이 앞 규칙을 덮어쓴다.
    """
    cb.apply_modifiers(obj)
    me = obj.data
    me.materials.clear()
    for m in slots:
        me.materials.append(m)
    bm = bmesh.new()
    bm.from_mesh(me)
    mw = obj.matrix_world
    inv = mw.inverted()
    for _, _, planes in rules:
        for ax, val in planes:
            co_w = Vector((val if ax == "x" else 0, val if ax == "y" else 0, val if ax == "z" else 0))
            no_w = Vector((1 if ax == "x" else 0, 1 if ax == "y" else 0, 1 if ax == "z" else 0))
            co = inv @ co_w
            no = (mw.to_3x3().transposed() @ no_w).normalized()   # 법선은 역전치로 (월드 → 로컬)
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, dist=1e-6)
    bm.normal_update()
    for f in bm.faces:
        c = mw @ f.calc_center_median()
        n = (mw.to_3x3() @ f.normal).normalized()
        for mat, cond, _ in rules:
            if cond(c, n):
                f.material_index = slots.index(mat)
    bm.to_mesh(me)
    bm.free()
    me.update()
    return obj


def shell(obj, thickness, inner_mat):
    """닫힌 차체를 속이 빈 껍데기로 만든다 (안쪽 면 = inner_mat). paint 뒤, 창 구멍(cut_through) 전에 쓴다.

    좌석 카메라가 차체 안에 있으므로, 창 구멍으로 밖이 보이고 나머지는 실내색 벽이 보인다.
    """
    cb.apply_modifiers(obj)
    n = len(obj.data.materials)
    for _ in range(n):
        obj.data.materials.append(inner_mat)
    mod = obj.modifiers.new("Shell", "SOLIDIFY")
    mod.thickness = thickness
    mod.offset = -1.0
    mod.use_even_offset = True
    mod.material_offset = n
    mod.material_offset_rim = n
    cb.apply_modifiers(obj)
    # 같은 머티리얼 슬롯이 여러 개면 glTF에 머티리얼 없는 프리미티브가 생긴다 → 안쪽 면을 슬롯 하나로 모은다
    me = obj.data
    for p in me.polygons:
        if p.material_index >= n:
            p.material_index = n
    for _ in range(n - 1):
        me.materials.pop(index=len(me.materials) - 1)
    me.update()
    return obj


def cut_through(obj, pts, origin, u, v, *, out=0.08, inn=0.12):
    """평면 (u, v) 위 외곽선으로 껍데기에 창 구멍을 뚫는다 (바깥 out, 안쪽 inn 만큼 걸친 프리즘)."""
    c = slab("win_cut", pts, origin, u, v, out + inn, lift=-inn)
    return cut(obj, c)


def loop_frame(name, pts, origin, u, v, *, r=0.015, lift=0.0, mat=None, verts=6):
    """평면 위 닫힌 외곽선을 따라 도는 테 (창틀). 가운데가 비어 있어 시야를 막지 않는다."""
    U, W = Vector(u).normalized(), Vector(v).normalized()
    N = U.cross(W).normalized()
    O = Vector(origin) + N * lift
    path = [tuple(O + U * a + W * b) for a, b in pts]
    path = path + path[:2]
    sec = [(math.cos(2 * math.pi * k / verts) * r, math.sin(2 * math.pi * k / verts) * r) for k in range(verts)]
    o = hw.sweep(name, path[:-1], sec, side_vec=tuple(N), cap=False, mat=mat, smooth=60)
    return o


def place(obj, M4):
    """오브젝트를 4x4 행렬로 배치 (현재 변환 위에 곱한다)."""
    obj.matrix_world = M4 @ obj.matrix_world
    return obj


def rot_about(objs, pivot, axis, deg):
    """objs를 pivot 둘레로 axis('X'|'Y'|'Z') deg만큼 회전 (월드)."""
    bpy.context.view_layer.update()
    T = Matrix.Translation(Vector(pivot))
    R = Matrix.Rotation(math.radians(deg), 4, axis)
    for o in objs:
        o.matrix_world = T @ R @ T.inverted() @ o.matrix_world
    return objs


def cut(obj, cutter, op="DIFFERENCE"):
    """불리언을 바로 적용하고 커터를 지운다. 베벨 모디파이어가 있으면 불리언을 먼저 적용한다."""
    m = obj.modifiers.new("Bool", "BOOLEAN")
    m.object = cutter
    m.operation = op
    m.solver = "EXACT"
    idx = obj.modifiers.find(m.name)
    if idx > 0:
        with bpy.context.temp_override(object=obj, active_object=obj):
            bpy.ops.object.modifier_move_to_index(modifier=m.name, index=0)
    cutter.hide_set(True)
    cb.apply_modifiers(obj)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return obj


# ================================================================== decals (home_weapons 래퍼)
# 데칼 이름은 decal_로 시작하고, finish가 그룹별 <그룹>_decals(noOutline)로 모은다.
def frame(normal, up=None):
    """바깥 법선 normal인 면의 데칼 좌표계 (right, up). 법선 = right x up. 글자는 밖에서 볼 때 바로 읽힌다."""
    n = Vector(normal).normalized()
    u = Vector(up) if up else (Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((0, -1, 0)))
    right = u.cross(n).normalized()
    u = n.cross(right).normalized()
    return dict(right=tuple(right), up=tuple(u))


SIDE_L = frame((1, 0, 0))     # +X 면 (차량 왼쪽): 글자가 앞→뒤로 읽힘
SIDE_R = frame((-1, 0, 0))    # -X 면 (차량 오른쪽): 글자가 뒤→앞으로 읽힘
FACE_F = frame((0, -1, 0))    # -Y 면 (정면)
FACE_B = frame((0, 1, 0))     # +Y 면 (뒷면)
FACE_T = frame((0, 0, 1), up=(0, 1, 0))   # +Z 면 (위): 위에서 볼 때(앞이 아래) 바로 읽힘


def decal(name, pts, center, frame, *, lift=0.004, mat=None):
    return hw.decal(name, pts, center, lift=lift, mat=mat, **frame)


def ring(name, center, r_out, r_in, frame, *, lift=0.004, mat=None, seg=28):
    return hw.ring_decal(name, center, r_out, r_in, lift=lift, mat=mat, seg=seg, **frame)


def text(name, s, size, center, frame, *, mat=None, lift=0.004, align="CENTER"):
    return hw.text(name, s, size, center, mat=mat, lift=lift, align=align, **frame)


def logo(name, center, size, frame, *, mat=None, lift=0.006):
    """원작 엘프 로고 데칼 (public/ui/elf_logo_mono.svg). 바탕 원판(lift 0.004) 위로 띄운다."""
    o = hw.elf_logo(name, center, size, mat=mat, lift=lift, **frame)
    if o is None:
        raise FileNotFoundError("엘프 로고 SVG가 없음 (public/ui/elf_logo_mono.svg)")
    return o


def logo_disc(prefix, center, size, frame, *, disc, rim, mark, lift=0.004):
    """원판 + 테 + 엘프 로고 (교주 차원 병기의 엠블럼 자리). size = 로고 높이."""
    R = size * 0.80
    return [decal(prefix + "disc", hw.circle(R, 36), center, frame, lift=lift, mat=disc),
            ring(prefix + "rim", center, R, R * 0.92, frame, lift=lift + 0.0015, mat=rim, seg=36),
            logo(prefix + "logo", center, size, frame, mat=mark, lift=lift + 0.003)]


# ================================================================== wheels

def tire_profile(R, W, *, rim=0.62, style="mon"):
    """타이어 단면 (반지름, x) 닫힌 외곽선. style 'mon' = 둥근 풍선 타이어, 'r41' = 각진 험지 타이어."""
    h = W / 2
    Rr = R * rim
    if style == "mon":
        half = [(Rr, -h * 0.80), (R * 0.80, -h), (R * 0.93, -h * 0.94), (R * 0.985, -h * 0.74),
                (R, -h * 0.50), (R * 0.975, -h * 0.14)]
    else:
        half = [(Rr, -h * 0.86), (R * 0.84, -h), (R * 0.96, -h), (R, -h * 0.84), (R * 0.975, -h * 0.18)]
    other = [(r, -x) for r, x in reversed(half)]
    return half + other


def wheel_parts(name, c, R, W, M, *, faction, side=1, seg=None, lugs=None):
    """바퀴 한 짝의 파츠 목록 (타이어 + 휠 + 캡 + 볼트 + 트레드 블록). side = 바깥 면 방향 (+1 = +X)."""
    cx, cy, cz = c
    out = []
    mon = faction == "monatium"
    seg = seg or (20 if mon else 18)
    h = W / 2
    out.append(lathe(name + "_tire", tire_profile(R, W, style="mon" if mon else "r41"), c, seg=seg,
                     mat=M["rubber"], smooth=50))
    # 트레드 블록: 모나티엄 = 어깨에 엇갈린 둥근 블록, R41 = 셰브론
    n = lugs or (10 if mon else 12)
    for i in range(n):
        t = 2 * math.pi * (i + 0.5) / n
        if mon:
            for k, xo in enumerate((-h * 0.60, h * 0.60)):
                tt = t + (math.pi / n if k else 0)
                b = cb.box(f"{name}_lug{i}_{k}", size=(h * 0.46, R * 0.16, R * 0.05), material=M["rubber"])
                b.matrix_world = (Matrix.Translation((cx + xo, cy, cz)) @ Matrix.Rotation(tt, 4, "X")
                                  @ Matrix.Translation((0, 0, R * 0.975)))   # 바깥 끝 = R (지면 z=0)
                out.append(b)
        else:
            for k, sx in enumerate((-1, 1)):
                b = cb.box(f"{name}_lug{i}_{k}", size=(h * 0.62, R * 0.11, R * 0.06), material=M["rubber"])
                b.matrix_world = (Matrix.Translation((cx, cy, cz)) @ Matrix.Rotation(t + (0.07 if k else 0), 4, "X")
                                  @ Matrix.Translation((sx * h * 0.45, 0, R * 0.97))
                                  @ Matrix.Rotation(math.radians(sx * 24), 4, "Z"))
                out.append(b)
    # 휠 (바깥 면 접시 + 안쪽 면 막음)
    Rr = R * 0.62
    xo = side * h
    if mon:
        dish = [(Rr * 1.01, xo * 0.80), (Rr * 0.92, xo * 0.86), (Rr * 0.55, xo * 0.80), (Rr * 0.42, xo * 0.95),
                (Rr * 0.05, xo * 0.95), (Rr * 1.01, -xo * 0.60)]
        out.append(lathe(name + "_rim", dish, c, seg=seg, mat=M["hull_d"], smooth=45))
        cap = [(Rr * 0.36, xo * 0.94), (Rr * 0.30, xo * 1.05), (Rr * 0.02, xo * 1.08), (Rr * 0.02, xo * 0.90)]
        out.append(lathe(name + "_cap", cap, c, seg=16, mat=M["steel"], smooth=60))
        for i in range(6):     # 둥근 구멍 6개 (교주 차원 '구멍 줄' 문법)
            t = 2 * math.pi * i / 6
            p = (cx + xo * 0.84 + side * 0.002, cy + math.cos(t) * Rr * 0.72, cz + math.sin(t) * Rr * 0.72)
            out.append(decal(f"{name}_hole{i}", hw.circle(Rr * 0.12, 12), p,
                             frame((side, 0, 0)), lift=0.001, mat=M["gear"]))
        for i in range(5):     # 볼트
            t = 2 * math.pi * i / 5 + 0.3
            p = (cx + xo * 0.95, cy + math.cos(t) * Rr * 0.30, cz + math.sin(t) * Rr * 0.30)
            out.append(cb.cylinder(f"{name}_nut{i}", radius=Rr * 0.045, depth=W * 0.06, loc=p, rot=(0, 90, 0), verts=6,
                                   material=M["steel"]))
    else:
        dish = [(Rr * 1.01, xo * 0.86), (Rr * 0.88, xo * 0.92), (Rr * 0.62, xo * 0.88), (Rr * 0.46, xo * 1.0),
                (Rr * 0.05, xo * 1.0), (Rr * 0.05, -xo * 0.75), (Rr * 1.01, -xo * 0.75)]
        out.append(lathe(name + "_rim", dish, c, seg=6, mat=M["shell"], smooth=20, rot0=math.radians(30)))
        out.append(lathe(name + "_band", [(Rr * 0.70, xo * 0.93), (Rr * 0.70, xo * 0.99), (Rr * 0.60, xo * 0.99),
                                          (Rr * 0.60, xo * 0.93)], c, seg=6, mat=M["amber"], smooth=20,
                         rot0=math.radians(30)))
        cap = [(Rr * 0.40, xo * 0.98), (Rr * 0.30, xo * 1.10), (Rr * 0.02, xo * 1.10), (Rr * 0.02, xo * 0.95)]
        out.append(lathe(name + "_cap", cap, c, seg=6, mat=M["metal"], smooth=20))
        for i in range(6):
            t = 2 * math.pi * i / 6
            p = (cx + xo * 1.02, cy + math.cos(t) * Rr * 0.32, cz + math.sin(t) * Rr * 0.32)
            out.append(cb.cylinder(f"{name}_nut{i}", radius=Rr * 0.05, depth=W * 0.06, loc=p, rot=(0, 90, 0), verts=6,
                                   material=M["steel"]))
    return out


# ================================================================== assembler

def _bake_into(obj, node):
    """obj의 월드 형상을 node 로컬 공간에 굽고 node의 자식으로 (로컬 변환 = 단위)."""
    bpy.context.view_layer.update()
    m = node.matrix_world.inverted() @ obj.matrix_world
    obj.data.transform(m)
    obj.parent = node
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_basis = Matrix.Identity(4)
    obj.data.update()


def _join(objs, name):
    objs = [o for o in objs if o is not None]
    for o in objs:
        cb.apply_modifiers(o)
    out = cb.join(objs, name) if len(objs) > 1 else objs[0]
    out.name = name
    out.data.name = name
    return out


def _tris(o):
    o.data.calc_loop_triangles()
    return len(o.data.loop_triangles)


AIM_ROT = Matrix.Rotation(math.pi, 4, "Z")


class Veh:
    """차량 한 대 조립기 (위 모듈 설명 참고).

    body(*objs)                       정지 파츠 → body_<머티리얼>
    group(name, loc, parent, aim)     빈 노드 + 머티리얼별 자식 메시 (turret, gun_pitch)
    part(name, loc, parent, props)    한 메시로 합치는 움직이는 파츠 (바퀴, 해치, 문, 등)
    empty(name, loc, parent, aim, props)
    to(node, *objs)                   group/part에 파츠 추가
    wheel(name, c, R, W, steer)       바퀴 파츠 + radius/steer 속성
    col(name, ...) / col_hull(name, pts)   충돌 전용 메시
    """

    PREFIX = {"turret": "turret", "gun_pitch": "gun", "body": "body"}

    def __init__(self, name, faction):
        self.name = name
        self.faction = faction
        self.M = mats(faction)
        self.nodes: dict[str, dict] = {}
        self.order: list[str] = []
        self.cols: list[tuple] = []
        self.group("body", (0, 0, 0))

    # ---- 선언
    def _decl(self, name, kind, loc, parent, aim, props):
        if name in self.nodes:
            raise ValueError(f"노드 이름 중복: {name}")
        if parent and parent not in self.nodes:
            raise ValueError(f"{name}: 부모 {parent}가 먼저 선언돼야 함")
        if "." in name:
            raise ValueError(f"노드 이름에 점 금지: {name}")
        self.nodes[name] = dict(kind=kind, loc=tuple(loc), parent=parent, aim=aim, props=dict(props or {}), objs=[])
        self.order.append(name)
        return name

    def group(self, name, loc, parent=None, *, aim=False, props=None):
        return self._decl(name, "group", loc, parent, aim, props)

    def part(self, name, loc, parent=None, *, props=None):
        return self._decl(name, "part", loc, parent, False, props)

    def empty(self, name, loc, parent=None, *, aim=False, props=None):
        """aim=True: 거치 무기 노드 (Z축 180°, restYawDeg=180)."""
        if aim:
            props = dict(props or {}, restYawDeg=180)
        return self._decl(name, "empty", loc, parent, aim, props)

    def to(self, node, *objs):
        flat = []
        for o in objs:
            if isinstance(o, (list, tuple)):
                flat.extend(o)
            elif o is not None:
                flat.append(o)
        self.nodes[node]["objs"].extend(flat)
        return flat[0] if flat else None

    def body(self, *objs):
        return self.to("body", *objs)

    def wheel(self, name, c, R, W, *, steer=0, side=None, parent=None, props=None, **kw):
        side = side if side is not None else (1 if c[0] >= 0 else -1)
        p = {"radius": round(R, 4), "steer": int(steer), "width": round(W, 4)}
        p.update(props or {})
        self.part(name, c, parent, props=p)
        self.to(name, wheel_parts(name, c, R, W, self.M, faction=self.faction, side=side, **kw))

    def col(self, name, x0, x1, y0, y1, z0, z1, parent=None):
        o = rbox(name, x0, x1, y0, y1, z0, z1, mat=self.M["collider"])
        self.cols.append((name, o, parent))
        return o

    def col_hull(self, name, pts, parent=None):
        """점들의 볼록 껍질로 충돌 메시."""
        bm = bmesh.new()
        for p in pts:
            bm.verts.new(p)
        bmesh.ops.convex_hull(bm, input=bm.verts)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        o = cb._new_mesh_obj(name, bm)
        cb.assign(o, self.M["collider"])
        self.cols.append((name, o, parent))
        return o

    # ---- 마무리
    def finish(self, rel_path, *, props, budget, outline=0.01):
        import os
        if os.environ.get("VE_DEBUG"):
            deps = bpy.context.evaluated_depsgraph_get()
            per = {}
            for info in self.nodes.values():
                for o in info["objs"]:
                    me = o.evaluated_get(deps).to_mesh()
                    me.calc_loop_triangles()
                    key = o.name.split(".")[0]
                    per[key] = per.get(key, 0) + len(me.loop_triangles)
                    o.evaluated_get(deps).to_mesh_clear()
            print("[ve] debug top: " + ", ".join(f"{k}={v}" for k, v in sorted(per.items(), key=lambda kv: -kv[1])[:40]))
        root = cb.empty(self.name, size=0.3)
        made: dict[str, bpy.types.Object] = {}
        report: dict[str, int] = {}

        def make_empty(name, info):
            e = bpy.data.objects.new(name, None)
            e.empty_display_type = "PLAIN_AXES"
            e.empty_display_size = 0.15
            cb.link(e)
            par = made[info["parent"]] if info["parent"] else root
            world = Matrix.Translation(Vector(info["loc"])) @ (AIM_ROT if info["aim"] else Matrix.Identity(4))
            e.parent = par
            e.matrix_parent_inverse = Matrix.Identity(4)
            bpy.context.view_layer.update()
            e.matrix_basis = par.matrix_world.inverted() @ world
            bpy.context.view_layer.update()
            return e

        for name in self.order:
            info = self.nodes[name]
            if info["kind"] in ("group", "empty"):
                node = make_empty(name, info)
                made[name] = node
                if info["kind"] == "group":
                    prefix = self.PREFIX.get(name, name)
                    by_mat: dict[str, list] = {}
                    decals = []
                    for o in info["objs"]:
                        if o.name.startswith("decal_"):
                            decals.append(o)
                        else:
                            key = o.data.materials[0].name if o.data.materials else "none"
                            by_mat.setdefault(key, []).append(o)
                    for key, objs in by_mat.items():
                        short = key.replace("UNLIT_", "").split("_", 1)[-1]
                        m = _join(objs, f"{prefix}_{short}")
                        _bake_into(m, node)
                        report[m.name] = _tris(m)
                    if decals:
                        d = _join(decals, f"{prefix}_decals")
                        d["noOutline"] = 1
                        _bake_into(d, node)
                        report[d.name] = _tris(d)
            else:   # part: 한 메시, 원점 = loc
                objs = [o for o in info["objs"] if not o.name.startswith("decal_")]
                decals = [o for o in info["objs"] if o.name.startswith("decal_")]
                node = make_empty(name + "__tmp", info)
                m = _join(objs, name)
                _bake_into(m, node)
                # 임시 빈 노드 자리를 메시가 차지하게
                bpy.context.view_layer.update()
                mw = m.matrix_world.copy()
                m.parent = node.parent
                m.matrix_parent_inverse = Matrix.Identity(4)
                m.matrix_basis = node.matrix_basis.copy()
                bpy.data.objects.remove(node, do_unlink=True)
                made[name] = m
                report[name] = _tris(m)
                if decals:
                    d = _join(decals, name + "_fine")
                    d["noOutline"] = 1
                    _bake_into(d, m)
                    report[d.name] = _tris(d)
                _ = mw
            for k, v in info["props"].items():
                made[name][k] = v

        for name, o, parent in self.cols:
            par = made[parent] if parent else root
            _bake_into(o, par)
            o["noOutline"] = 1
            o["collider"] = 1
            report[name] = _tris(o)

        for m in list(bpy.data.materials):
            if m.users == 0:
                bpy.data.materials.remove(m)
        p = {"outline": outline}
        p.update(props)
        total = sum(report.values())
        col_tris = sum(report[n] for n, _, _ in self.cols)
        mats_used = sorted({s.material.name for o in bpy.context.scene.objects if o.type == "MESH"
                            for s in o.material_slots if s.material})
        top = sorted(report.items(), key=lambda kv: -kv[1])
        print("[ve] tris per node: " + ", ".join(f"{k}={v}" for k, v in top))
        print(f"[ve] total tris {total} (render {total - col_tris}, colliders {col_tris}) / budget {budget}")
        print(f"[ve] materials ({len(mats_used)}): {', '.join(mats_used)}")
        print("[ve] nodes: " + ", ".join(o.name for o in bpy.context.scene.objects if o.type == "EMPTY"))
        if total - col_tris > budget:
            raise RuntimeError(f"[ve] 예산 초과: {total - col_tris} / {budget}")
        return cb.export(rel_path, props=p, root=root)


# ================================================================== 거치 무기 조립기

class Mount:
    """차량 거치 무기 한 정 (weapons/<진영>/mount_*.glb).

    무기 규약(ART_GUIDE 7장)을 따른다: 원점 = 회전축(받침 피벗), 총구 +Y, 위 +Z, 사수 오른쪽 +X.
    s(obj) 정지 파츠 → body (머티리얼별 메시가 아니라 한 메시, 머티리얼 슬롯 여러 개)
    f(obj) 데칼·글자 → body_fine (noOutline)
    p(part, obj) / pivot(part, pt, **props) 움직이는 파츠
    anchor(name, pt, parent=None)
    """

    def __init__(self, name, faction):
        self.name = name
        self.M = mats(faction)
        self.static, self.fine = [], []
        self.parts: dict[str, list] = {}
        self.pfine: dict[str, list] = {}
        self.pivots: dict[str, tuple] = {}
        self.pprops: dict[str, dict] = {}
        self.anchors: list[tuple] = []

    def s(self, *objs):
        for o in objs:
            if isinstance(o, (list, tuple)):
                self.s(*o)
            elif o is not None:
                (self.fine if o.name.startswith("decal_") else self.static).append(o)

    def p(self, part, *objs):
        for o in objs:
            if isinstance(o, (list, tuple)):
                self.p(part, *o)
            elif o is not None:
                (self.pfine if o.name.startswith("decal_") else self.parts).setdefault(part, []).append(o)

    def pivot(self, part, pt, **props):
        self.pivots[part] = tuple(pt)
        self.pprops.setdefault(part, {}).update(props)

    def anchor(self, name, pt, parent=None):
        self.anchors.append((name, tuple(pt), parent))

    def finish(self, rel_path, *, outline, props=None, budget=8000, max_mats=10, origin=(0, 0, 0)):
        """origin: 이 점을 glb 원점으로 옮긴다 (예: 상하 회전축 = 트러니언). 앵커·피벗도 같이 옮긴다."""
        off = Vector(origin)
        if off.length > 0:
            T = Matrix.Translation(-off)
            objs = self.static + self.fine + [o for v in self.parts.values() for o in v] \
                + [o for v in self.pfine.values() for o in v]
            bpy.context.view_layer.update()
            for o in objs:
                o.matrix_world = T @ o.matrix_world
            self.pivots = {k: tuple(Vector(v) - off) for k, v in self.pivots.items()}
            self.anchors = [(n, tuple(Vector(pt) - off), par) for n, pt, par in self.anchors]
        root = cb.empty(self.name, size=0.1)
        report = {}
        body = _join(self.static, "body")
        _bake_into(body, root)
        report["body"] = _tris(body)
        if self.fine:
            f = _join(self.fine, "body_fine")
            f["noOutline"] = 1
            _bake_into(f, root)
            report["body_fine"] = _tris(f)
        made = {}
        for part, objs in self.parts.items():
            o = _join(objs, part)
            pt = Vector(self.pivots.get(part, (0, 0, 0)))
            bpy.context.view_layer.update()
            o.data.transform(Matrix.Translation(-pt) @ o.matrix_world)
            o.matrix_world = Matrix.Identity(4)
            o.parent = root
            o.matrix_parent_inverse = Matrix.Identity(4)
            o.matrix_basis = Matrix.Translation(pt)
            for k, v in self.pprops.get(part, {}).items():
                o[k] = v
            made[part] = o
            report[part] = _tris(o)
            if part in self.pfine:
                f = _join(self.pfine[part], part + "_fine")
                f["noOutline"] = 1
                _bake_into(f, o)
                report[f.name] = _tris(f)
        for name, pt, par in self.anchors:
            e = cb.empty(name, size=0.03)
            p = made[par] if par else root
            e.parent = p
            e.matrix_parent_inverse = Matrix.Identity(4)
            bpy.context.view_layer.update()
            e.matrix_basis = p.matrix_world.inverted() @ Matrix.Translation(Vector(pt))
        for m in list(bpy.data.materials):
            if m.users == 0:
                bpy.data.materials.remove(m)
        mats_used = sorted({s.material.name for o in bpy.context.scene.objects if o.type == "MESH"
                            for s in o.material_slots if s.material})
        total = sum(report.values())
        print("[ve] mount part tris:", ", ".join(f"{k}={v}" for k, v in report.items()))
        print(f"[ve] total tris {total} / {budget}, materials {len(mats_used)}: {', '.join(mats_used)}")
        if total > budget or len(mats_used) > max_mats:
            raise RuntimeError(f"[ve] 예산 초과: tris {total}/{budget}, materials {len(mats_used)}/{max_mats}")
        p = {"outline": outline, "mountWeapon": 1}
        p.update(props or {})
        return cb.export(rel_path, props=p, root=root)
