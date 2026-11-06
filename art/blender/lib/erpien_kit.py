"""에르피엔 키트: 세계수 엘드르와 그 밑동을 두른 요정 왕국 (모든 에르피엔 장면이 같은 디자인을 쓴다).

[원작] 「요정(트릭컬 리바이브)」 에르피엔 안내서 서문: 세계수를 세상의 중심으로 삼아 요정들의 왕국은 엘리아스 중심에
       자리 잡았고, 왕국 한가운데 세계수를 모셨다. 왕국 외곽에는 호수가 있고 강이 흐른다. 왕궁 주변과 도시에 성곽이 있는
       이중 성벽 구조다. 「세계수(트릭컬 리바이브)」: 요정 왕국에 자리 잡은 거대한 나무. 수도는 정령산 정상에서도 잘 보인다.
       원작 에르피엔 전경 그림의 인상(레퍼런스로만 봄): 뭉게구름처럼 둥글게 부푼 큰 수관, 여러 가닥이 꼬인 굵은 줄기,
       그 밑동에 붙은 흰 성(청록 원뿔·양파 지붕, 금 장식), 성 밖의 알록달록한 지붕 마을.
[오리지널] 3D 형태 전부: 꼬인 줄기 다발·판뿌리·큰 가지, 수관 덩어리 배치, 왕궁이 밑동을 고리로 두르는 배치,
       안쪽 성벽, 시가 고리와 방사형 큰길(여섯 갈래), 바깥 성벽과 문루. 원작 그림을 옮기지 않았다.

  world_tree(C, cx, cy, z0, h, detail=0|1)        세계수만 (detail 1 = 가까운 장면, 0 = 원경 실루엣)
  kingdom(C, cx, cy, z0, h, ...)                  왕궁 고리 + 안쪽 성벽 + 시가 고리 + 바깥 성벽 (원경 LOD)
  erpien(C, cx, cy, z0, h, ...)                   둘 다 (원경 한 줄). 반환 dict: center, top, crown_bottom, palace_top, r_wall
  gate_plan(cx, cy, h, face, ...)                 바깥 성문 둘레 가까운 세트 계획 (원경 성벽 마디·탑과 같은 자리, skip 함수)
  city_gate(C, plan, hfun, ...)                   그 계획대로 가까이서 보는 성문루·성벽·탑 (원경 kingdom(skip=plan.skip)과 이어진다)
  haze(color, k)                                  키트 색을 공기 원근 색 쪽으로 섞는다 (수 km 원경)

크기는 나무 높이 h에 비례한다 (기본 비율, 원작 그림의 비례를 3D로 옮김):
  수관 밑 0.36h, 수관 반지름 0.6h (폭 약 1.3h), 밑동 반지름 0.08h, 판뿌리 끝 0.17h
  왕궁 단 0.25h, 왕궁 고리 0.17~0.24h(날개 0.07h, 탑 0.13h, 정면 첨탑 0.26h), 안쪽 성벽 0.28h, 시가 0.31~0.68h, 바깥 성벽 0.72h
머티리얼: eld_*(나무 6색), erk_*(왕국 9색). 원경은 kind="far"(얇은 아웃라인이 거리에 따라 스며 사라짐),
가까운 장면은 그룹에 굵은 outline 속성을 주고 kind="main"으로 쌓는다.
"""
import math
import random

import bmesh
from mathutils import Vector

import monatium_city_kit as mk

# ---------------------------------------------------------------- 팔레트 (원작 전경 그림의 색 방향, 값은 새로 골랐다)
BASE = {
    "eld_bark": "#8c6c58",      # 줄기 (따뜻한 갈색)
    "eld_bark_d": "#6f5345",    # 판뿌리·줄기 그늘 가닥
    "eld_bark_l": "#a5866d",    # 밝은 가닥
    "eld_leaf": "#64a865",      # 수관 (중간 초록)
    "eld_leaf_l": "#86c27a",    # 위쪽 밝은 덩어리
    "eld_leaf_d": "#478a57",    # 아래 그늘 덩어리
    "erk_wall": "#f7f2ea",      # 흰 석재
    "erk_wall_d": "#d8cdbf",    # 기단·성벽 띠
    "erk_roof": "#3f9c88",      # 청록 원뿔·양파 지붕 (왕궁)
    "erk_roof_l": "#62b8a0",    # 밝은 청록
    "erk_roof_r": "#c95a4e",    # 마을 붉은 지붕
    "erk_roof_p": "#8c70c2",    # 마을 보라 지붕
    "erk_roof_o": "#e3954c",    # 마을 주황 지붕
    "erk_roof_b": "#5a86c4",    # 마을 파랑 지붕
    "erk_gold": "#e6bd6e",      # 금 장식
    "erk_door": "#7d5638",      # 성문 문짝 (참나무)
    "erk_door_d": "#5c3e29",    # 문짝 널 틈·그늘
    "erk_iron": "#3e3b44",      # 문짝 쇠띠·징
    "erk_slit": "#3a3340",      # 활 쏘는 틈·창 안 그늘
    "erk_pave": "#cdbfaa",      # 성문 앞 포석
    "erk_soot": "#5a4636",      # 그을음 (포위전 흔적, 문짝 위)
    "erk_vault": "#a89a8a",     # 성문 통로 안 (그늘진 석재)
}
mk.PAL.update(BASE)


def haze(color, k):
    """키트 색을 color 쪽으로 k만큼 섞는다 (수 km 원경의 공기 원근. 레벨 스크립트가 C를 만들기 전에 부른다)."""
    def rgb(h):
        h = h.lstrip("#")
        return [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    c2 = rgb(color)
    for key, v in BASE.items():
        c1 = rgb(v)
        mk.PAL[key] = "#" + "".join(f"{round(a + (b - a) * k):02x}" for a, b in zip(c1, c2))


# ---------------------------------------------------------------- 도형
def _tube(b, pts, radii, sides=10, cap=True, smooth=True):
    """폴리라인을 따라 반지름이 바뀌는 관 (평행 이동 틀). 끝은 뾰족하게 닫는다."""
    pts = [Vector(p) for p in pts]
    n = len(pts)
    T = []
    for i in range(n):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == n - 1:
            t = pts[-1] - pts[-2]
        else:
            t = pts[i + 1] - pts[i - 1]
        T.append(t.normalized())
    up = Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((1, 0, 0))
    N = (up - T[0] * up.dot(T[0])).normalized()
    rings = []
    for i in range(n):
        N = (N - T[i] * N.dot(T[i]))
        if N.length < 1e-6:
            N = T[i].orthogonal()
        N.normalize()
        B = T[i].cross(N)
        ring = []
        for k in range(sides):
            a = 2 * math.pi * k / sides
            ring.append(b.verts.new(pts[i] + (N * math.cos(a) + B * math.sin(a)) * radii[i]))
        rings.append(ring)
    for i in range(n - 1):
        for k in range(sides):
            k2 = (k + 1) % sides
            f = b.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
            f.smooth = smooth
    if cap:
        tip = b.verts.new(pts[-1] + T[-1] * radii[-1] * 0.6)
        for k in range(sides):
            f = b.faces.new((rings[-1][k], rings[-1][(k + 1) % sides], tip))
            f.smooth = smooth
        base = b.verts.new(pts[0] - T[0] * radii[0] * 0.3)
        for k in range(sides):
            f = b.faces.new((rings[0][(k + 1) % sides], rings[0][k], base))
            f.smooth = smooth


def _arc(p0, p1, p2, n):
    """2차 베지어 점 n+1개."""
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(p0 * (1 - t) ** 2 + p1 * 2 * t * (1 - t) + p2 * t * t)
    return out


# ================================================================ 세계수

def world_tree(C, cx, cy, z0, h, *, detail=0, kind="far", seed=7, crown_r=0.6, crown_bottom=0.36):
    """세계수 엘드르. 꼬인 줄기 다발(가닥마다 큰 가지로 갈라져 수관 속으로) + 판뿌리 + 뭉게구름 수관.
    detail 1: 가까운 장면 (가닥 7, 뿌리 10, 수관 덩어리 약 70), 0: 원경 (가닥 4, 뿌리 6, 덩어리 약 30).
    반환: dict(top, crown_bottom, crown_r, trunk_r)."""
    rng = random.Random(seed)
    near = detail >= 1
    c = Vector((cx, cy, z0))
    R = crown_r * h
    hb = crown_bottom * h                 # 수관 밑 높이
    r0 = 0.08 * h                         # 밑동 반지름 (가닥 다발)
    sides = 10 if near else 7
    bark = C.bm("eld_bark", kind)
    bark_d = C.bm("eld_bark_d", kind)
    bark_l = C.bm("eld_bark_l", kind)

    # 가운데 심 (가닥 사이 틈을 메운다)
    _tube(bark_d, [c + Vector((0, 0, -4)), c + Vector((0, 0, hb * 0.5)), c + Vector((0, 0, hb + 0.1 * h))],
          [r0 * 0.8, r0 * 0.62, r0 * 0.42], sides=sides + 2)
    # 가닥: 밑에서 꼬여 오르다가 수관 밑에서 큰 가지로 벌어져 수관 속으로 들어간다
    ns = 7 if near else 4
    twist = 0.55
    for i in range(ns):
        a0 = 2 * math.pi * i / ns + rng.uniform(-0.12, 0.12)
        K = 9 if near else 5
        pts, rad = [], []
        for k in range(K + 1):
            t = k / K
            z = -3 + t * (hb * 0.92 + 3)
            rb = r0 * (0.72 - 0.3 * t) + r0 * 0.5 * max(0.0, 0.18 - t) / 0.18      # 밑에서 벌어진다
            a = a0 + twist * t
            pts.append(c + Vector((math.cos(a) * rb, math.sin(a) * rb, z)))
            rad.append(r0 * (0.5 - 0.16 * t) * (1.25 if t < 0.08 else 1.0))
        # 큰 가지: 바깥 위로 휘어 수관 속 0.45R 높이까지
        a = a0 + twist + 0.25
        out = Vector((math.cos(a), math.sin(a), 0))
        p0 = pts[-1]
        p1 = c + out * (R * 0.22) + Vector((0, 0, hb + 0.05 * h))
        p2 = c + out * (R * rng.uniform(0.48, 0.6)) + Vector((0, 0, hb + rng.uniform(0.13, 0.2) * h))
        limb = _arc(p0, p1, p2, 4 if near else 2)[1:]
        for j, p in enumerate(limb):
            pts.append(p)
            rad.append(r0 * (0.32 - 0.24 * (j + 1) / len(limb)))
        _tube((bark if i % 3 else bark_l) if near else bark, pts, rad, sides=sides)
        # 곁가지 (가까운 장면만): 가지 중간에서 옆으로
        if near:
            for s in (-1, 1):
                q0 = limb[len(limb) // 2]
                side = Vector((-out.y, out.x, 0)) * s
                q2 = q0 + side * R * 0.28 + out * R * 0.1 + Vector((0, 0, 0.07 * h))
                _tube(bark, _arc(q0, q0 + side * R * 0.12 + Vector((0, 0, 0.02 * h)), q2, 3),
                      [r0 * 0.16, r0 * 0.12, r0 * 0.08, r0 * 0.04], sides=8)
    # 판뿌리: 밑동에서 바깥으로 휘어 내려 땅에 박힌다
    nr = 10 if near else 6
    for j in range(nr):
        b0 = 2 * math.pi * (j + 0.5) / nr + rng.uniform(-0.15, 0.15)
        o = Vector((math.cos(b0), math.sin(b0), 0))
        side = Vector((-o.y, o.x, 0)) * rng.uniform(-0.25, 0.25)
        reach = rng.uniform(1.9, 2.2)
        pts = [c + o * (r0 * 0.55) + Vector((0, 0, r0 * 1.5)),
               c + o * (r0 * 1.05) + side * r0 * 0.3 + Vector((0, 0, r0 * 0.75)),
               c + o * (r0 * 1.55) + side * r0 * 0.6 + Vector((0, 0, r0 * 0.3)),
               c + o * (r0 * 2.0) + side * r0 * 0.8 + Vector((0, 0, r0 * 0.04)),
               c + o * (r0 * reach) + side * r0 * 0.9 + Vector((0, 0, -r0 * 0.12))]
        rad = [r0 * 0.38, r0 * 0.3, r0 * 0.21, r0 * 0.13, r0 * 0.06]
        _tube(bark_d if j % 2 else bark, pts, rad, sides=sides - 2 if near else 6)

    # 수관: 아래 그늘 판 + 속 돔 + 가장자리 고리 + 가운데 고리 + 위 고리 + 꼭대기 + (가까이) 뭉게 혹
    seg, rings = (15, 8) if near else (11, 6)
    span = h - hb

    def lobe(key, x, y, z, r, sz=0.82, rot=0.0, segs=seg, rgs=rings):
        C.blob(key, (cx + x, cy + y, z0 + z), r, (1.0, 1.0, sz), segs=segs, rings=rgs, kind=kind, rot_z=rot)

    lobe("eld_leaf_d", 0, 0, hb + span * 0.13, R * 0.8, sz=0.17, segs=seg + 8, rgs=rings)
    lobe("eld_leaf", 0, 0, hb + span * 0.46, R * 0.76, sz=span * 0.44 / (R * 0.76), segs=seg + 6, rgs=rings + 2)
    tiers = (  # (반지름 비, 높이 비, 덩어리 반지름 비, 개수 near/far, 색)
        (0.8, 0.2, 0.25, (16, 10), ("eld_leaf", "eld_leaf_d", "eld_leaf", "eld_leaf_d", "eld_leaf_l")),
        (0.58, 0.47, 0.27, (12, 7), ("eld_leaf", "eld_leaf_l", "eld_leaf", "eld_leaf_l")),
        (0.31, 0.7, 0.28, (7, 4), ("eld_leaf_l", "eld_leaf", "eld_leaf_l")),
    )
    tip = 0.0
    for ri, (rr, zz, lr, cnt, keys) in enumerate(tiers):
        n = cnt[0] if near else cnt[1]
        for i in range(n):
            a = 2 * math.pi * (i + rng.uniform(-0.18, 0.18)) / n + ri * 0.4
            d = R * rr * rng.uniform(0.92, 1.06)
            r = R * lr * rng.uniform(0.88, 1.1)
            z = hb + span * zz * rng.uniform(0.96, 1.04)
            lobe(keys[i % len(keys)], math.cos(a) * d, math.sin(a) * d, z, r, sz=0.8, rot=a)
            tip = max(tip, z + r * 0.8)
    # 꼭대기: 위가 h에 닿게
    rt = R * 0.27
    lobe("eld_leaf_l", R * 0.05, -R * 0.03, h - rt * 0.85, rt, sz=0.85)
    if near:
        lobe("eld_leaf_l", -R * 0.12, R * 0.08, h - rt * 0.95 - span * 0.04, rt * 0.85, sz=0.85)
        # 뭉게 혹: 돔 겉면 위의 작은 덩어리 (뭉게구름 결)
        for i in range(20):
            a = rng.uniform(0, 2 * math.pi)
            u = rng.uniform(0.25, 0.92)
            d = R * u
            # 돔 겉면 높이 (대략): 가운데가 높고 가장자리로 내려온다
            z = hb + span * (0.92 - 0.72 * u * u)
            r = R * rng.uniform(0.09, 0.14)
            lobe("eld_leaf_l" if z > hb + span * 0.55 else "eld_leaf", math.cos(a) * d, math.sin(a) * d, z, r,
                 sz=0.78, segs=10, rgs=6)
    return {"top": Vector((cx, cy, z0 + h)), "crown_bottom": z0 + hb, "crown_r": R, "trunk_r": r0,
            "root_r": r0 * 2.2}


# ================================================================ 땅

def ground(C, cx, cy, *, r_flat, r_out, amp=10.0, seed=4, key="grass", z=0.0, segs=56, kind="main"):
    """세계수(cx, cy)를 가운데 둔 방사형 땅: r_flat 안은 평평(왕국), 밖으로 갈수록 언덕. 반환: 높이 함수 h(x, y)."""
    def h(x, y):
        r = math.hypot(x - cx, y - cy)
        t = max(0.0, min(1.0, (r - r_flat) / max(1.0, (r_out - r_flat) * 0.5)))
        t = t * t * (3 - 2 * t)
        return z + amp * t * (mk.noise2(x, y, seed) + 1.2)
    b = C.bm(key, kind)
    radii = [0.0, r_flat * 0.35, r_flat * 0.7, r_flat]
    rr = r_flat
    while rr < r_out:
        rr = min(r_out, rr * 1.18)
        radii.append(rr)
    rows = []
    for r in radii:
        if r == 0:
            rows.append([b.verts.new((cx, cy, h(cx, cy)))])
            continue
        rows.append([b.verts.new((cx + math.cos(2 * math.pi * i / segs) * r, cy + math.sin(2 * math.pi * i / segs) * r,
                                  h(cx + math.cos(2 * math.pi * i / segs) * r, cy + math.sin(2 * math.pi * i / segs) * r)))
                     for i in range(segs)])
    for i in range(segs):
        b.faces.new((rows[0][0], rows[1][i], rows[1][(i + 1) % segs]))
    for k in range(1, len(rows) - 1):
        for i in range(segs):
            i2 = (i + 1) % segs
            f = b.faces.new((rows[k][i], rows[k + 1][i], rows[k + 1][i2], rows[k][i2]))
            f.smooth = True
    return h


# ================================================================ 왕국

def _tower(C, x, y, z, r, hh, *, kind, roof="erk_roof", onion=False, segs=10, gold=True):
    """둥근 탑: 흰 몸통 + 금 띠 + 청록 원뿔(또는 양파) 지붕 + 금 꼭지. 반환: 꼭대기 높이."""
    C.cyl("erk_wall", (x, y, z - 2), (x, y, z + hh), r, segs=segs, kind=kind, cap=False)
    if gold:
        C.cyl("erk_gold", (x, y, z + hh), (x, y, z + hh + r * 0.18), r * 1.1, segs=segs, kind=kind, cap=False)
    zr = z + hh + r * 0.18
    if onion:
        C.blob(roof, (x, y, zr + r * 0.75), r * 1.15, (1, 1, 0.95), segs=segs, rings=6, kind=kind)
        C.cyl(roof, (x, y, zr + r * 1.4), (x, y, zr + r * 2.6), r * 0.55, r2=0.0, segs=segs, kind=kind)
        top = zr + r * 2.6
    else:
        C.cyl(roof, (x, y, zr), (x, y, zr + r * 2.3), r * 1.22, r2=0.0, segs=segs, kind=kind, smooth=False)
        top = zr + r * 2.3
    if gold:
        C.cyl("erk_gold", (x, y, top - r * 0.2), (x, y, top + r * 0.7), r * 0.09, r2=0.0, segs=4, kind=kind,
              smooth=False)
    return top + r * 0.7


def _wall_ring(C, cx, cy, r, z_of, hh, thick, *, n, kind, key="erk_wall", skip=None):
    """성벽 고리 (n각, 마디마다 땅 높이를 따른다). skip(x, y)가 참인 마디는 빼서 문·큰길을 낸다."""
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        pa = Vector((cx + math.cos(a0) * r, cy + math.sin(a0) * r, 0))
        pb = Vector((cx + math.cos(a1) * r, cy + math.sin(a1) * r, 0))
        mid = (pa + pb) / 2
        if skip and skip(mid.x, mid.y):
            continue
        nrm = Vector((math.cos((a0 + a1) / 2), math.sin((a0 + a1) / 2), 0)) * (thick / 2)
        # 반시계(위에서 볼 때): 면이 바깥을 본다. 거꾸로 감으면 양면 머티리얼이라 겉보기는 같지만 외곽선 헐(뒷면)이 보이는 면
        # 바로 뒤에 붙어 멀리서 깊이 다툼을 한다 (docs/art/zfight-audit.md '뒤집힌 껍질')
        q = [pa + nrm, pb + nrm, pb - nrm, pa - nrm]
        za, zb = z_of(pa.x, pa.y), z_of(pb.x, pb.y)
        b = C.bm(key, kind)
        lo = [b.verts.new((p.x, p.y, z - 3)) for p, z in zip(q, (za, zb, zb, za))]
        hi = [b.verts.new((p.x, p.y, z + hh)) for p, z in zip(q, (za, zb, zb, za))]
        b.faces.new(hi)
        for k in range(4):
            k2 = (k + 1) % 4
            b.faces.new((lo[k], lo[k2], hi[k2], hi[k]))


def kingdom(C, cx, cy, z0, h, *, hfun=None, face=(0.0, -1.0), kind="far", seed=11, skip=None, avenues=6,
            density=1.0, palace=True, inner_wall=True, outer_wall=True, town=True, lit=None, palace_scale=1.0):
    """세계수 밑동을 두른 에르피엔: 왕궁 고리(날개 + 탑 + 보는 쪽 정면의 큰 첨탑) → 안쪽 성벽 → 시가 고리(방사형 큰길
    avenues 갈래, 하나는 face 쪽) → 바깥 성벽(큰길마다 문루). hfun(x, y) = 땅 높이(없으면 z0). skip(x, y) = 비울 자리
    (가까운 세트가 이미 있는 곳). lit = 창불 머티리얼 키(밤·새벽 장면), 없으면 창불 없음.
    palace_scale: 건물 높이·탑 굵기만 줄인다(고리 반지름은 나무에 맞춘 그대로). 원경은 1(원작 그림처럼 성이 밑동에서 크게
    읽히게), 가까운 세트는 그 세트 건물과 키를 맞춘다.
    반환: dict(palace_top, r_wall, gate (face 쪽 바깥 문))."""
    rng = random.Random(seed)
    z_of = hfun or (lambda x, y: z0)
    F = Vector((face[0], face[1], 0)).normalized()
    a_face = math.atan2(F.y, F.x)
    s = max(1.0, h / 360.0)                    # 집 크기 배율 (큰 원경일수록 덩어리를 키운다)
    ph = h * palace_scale                      # 왕궁 건물 높이 기준
    r_terr = 0.25 * h                          # 왕궁 단 (밑동을 두른 낮은 원형 단)
    r_p0, r_p1 = 0.17 * h, 0.24 * h            # 왕궁 고리 (날개 건물)
    r_iw = 0.28 * h                            # 안쪽 성벽
    r_t0, r_t1 = 0.315 * h, 0.66 * h           # 시가
    r_ow = 0.72 * h                            # 바깥 성벽
    av = [a_face + 2 * math.pi * k / avenues for k in range(avenues)]

    def on_avenue(x, y, half):
        a = math.atan2(y - cy, x - cx)
        d = math.hypot(x - cx, y - cy)
        for b in av:
            da = (a - b + math.pi) % (2 * math.pi) - math.pi
            if abs(da) * d < half and math.cos(da) > 0:
                return True
        return False

    def bad(x, y):
        return bool(skip and skip(x, y))

    out = {"r_wall": r_ow, "palace_top": Vector((cx, cy, z0))}
    # ---- 왕궁: 밑동을 두른 낮은 원형 단 위에 날개 건물 고리(청록 지붕), 날개 사이 탑, 보는 쪽 정면의 큰 첨탑과 쌍탑
    #      (원작 그림의 인상: 밑동에 붙은 흰 성, 가운데 높은 양파 첨탑, 둘레의 가는 원뿔 탑들)
    if palace:
        zt = z_of(cx, cy)
        th = 0.022 * ph
        C.cyl("erk_wall_d", (cx, cy, zt - 4), (cx, cy, zt + th), r_terr, r2=r_terr * 0.985, segs=40, kind=kind)
        C.cyl("erk_gold", (cx, cy, zt + th - 0.004 * ph), (cx, cy, zt + th), r_terr * 0.99, segs=40, kind=kind, cap=False)
        zt += th
        nw = 12
        rm = (r_p0 + r_p1) / 2
        depth = r_p1 - r_p0
        for i in range(nw):
            a0 = a_face + 2 * math.pi * (i + 0.14) / nw
            a1 = a_face + 2 * math.pi * (i + 0.86) / nw
            am = (a0 + a1) / 2
            m = Vector((cx + math.cos(am) * rm, cy + math.sin(am) * rm, 0))
            if bad(m.x, m.y):
                continue
            L = 2 * rm * math.sin((a1 - a0) / 2)
            hh = 0.07 * ph * (1.0 if i % 2 else 0.86)
            # 날개: 둘레 방향으로 놓인 박공 건물 (상자 + 지붕 두 면 + 박공 둘)
            t = Vector((-math.sin(am), math.cos(am), 0))
            o = Vector((math.cos(am), math.sin(am), 0))
            corners = [m - t * L / 2 - o * depth / 2, m + t * L / 2 - o * depth / 2, m + t * L / 2 + o * depth / 2,
                       m - t * L / 2 + o * depth / 2]
            # corners는 시계 방향(접선·바깥 틀이 왼손계)이라 뒤집어 반시계로 준다 (_bm_prism은 반시계를 바깥 면으로 세운다)
            mk._bm_prism(C.bm("erk_wall", kind), [(p.x, p.y) for p in reversed(corners)], zt - 2, zt + hh, top=False,
                         bottom=False)
            b = C.bm("erk_roof" if i % 2 else "erk_roof_l", kind)
            ov = 0.004 * ph
            e = [p + (p - m).normalized() * ov for p in corners]
            ridge0 = m - t * (L / 2 + ov)
            ridge1 = m + t * (L / 2 + ov)
            zr = zt + hh + depth * 0.5
            v = [b.verts.new((p.x, p.y, zt + hh - 0.002 * ph)) for p in e]
            r0v = b.verts.new((ridge0.x, ridge0.y, zr))
            r1v = b.verts.new((ridge1.x, ridge1.y, zr))
            fs = [b.faces.new((v[0], v[1], r1v, r0v)), b.faces.new((v[2], v[3], r0v, r1v)),
                  b.faces.new((v[3], v[0], r0v)), b.faces.new((v[1], v[2], r1v))]
            bmesh.ops.recalc_face_normals(b, faces=fs)
            # 금 처마 띠
            mk._bm_prism(C.bm("erk_gold", kind), [(p.x, p.y) for p in reversed(e)], zt + hh - 0.006 * ph, zt + hh - 0.002 * ph,
                         top=False, bottom=False)
            if lit:
                p = m + o * (depth / 2 + 0.3)
                C.rect(lit, (p.x, p.y, zt + hh * 0.5), tuple(o), L * 0.5, hh * 0.25, lift=0.0, kind="fine")
        for i in range(nw):
            a = a_face + 2 * math.pi * i / nw
            for rr, k in ((r_p1 + 0.004 * h, 1.0), (r_p0 - 0.004 * h, 1.25)):
                x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
                if bad(x, y) or (i == 0 and k == 1.0):
                    continue
                top = _tower(C, x, y, zt, 0.013 * ph * (1.1 if k > 1 else 1.0), (0.1 + 0.03 * (i % 3)) * ph * k, kind=kind,
                             roof="erk_roof" if (i + (k > 1)) % 2 == 0 else "erk_roof_l", onion=(i % 4 == 2 and k > 1),
                             segs=10)
                if top > out["palace_top"].z:
                    out["palace_top"] = Vector((x, y, top))
        # 보는 쪽 정면: 큰 첨탑(양파 지붕, 왕궁에서 가장 높다) + 쌍탑 + 정문 건물
        fr = r_p1 + 0.012 * h
        fx, fy = cx + math.cos(a_face) * fr, cy + math.sin(a_face) * fr
        if not bad(fx, fy):
            T = Vector((-F.y, F.x, 0))
            g = Vector((fx, fy, 0))
            q = [g - T * 0.07 * h - F * 0.03 * h, g + T * 0.07 * h - F * 0.03 * h, g + T * 0.07 * h + F * 0.02 * h,
                 g - T * 0.07 * h + F * 0.02 * h]
            mk._bm_prism(C.bm("erk_wall", kind), [(p.x, p.y) for p in reversed(q)], zt - 2, zt + 0.09 * ph, top=True,
                         bottom=False)
            mk._bm_prism(C.bm("erk_gold", kind), [(p.x, p.y) for p in reversed(q)], zt + 0.09 * ph, zt + 0.094 * ph, top=True,
                         bottom=False)
            top = _tower(C, fx, fy, zt + 0.09 * ph, 0.03 * ph, 0.13 * ph, kind=kind, roof="erk_roof", onion=True, segs=14)
            out["palace_top"] = Vector((fx, fy, top))
            for sx in (-1, 1):
                p = g + T * (sx * 0.075 * h) - F * 0.004 * h
                _tower(C, p.x, p.y, zt, 0.016 * ph, 0.15 * ph, kind=kind, roof="erk_roof_l", segs=12)
    # ---- 안쪽 성벽 (왕궁 성곽)
    if inner_wall:
        _wall_ring(C, cx, cy, r_iw, z_of, 0.028 * ph, 0.012 * ph, n=28, kind=kind,
                   skip=lambda x, y: bad(x, y) or on_avenue(x, y, 0.02 * h))
        for i in range(14):
            a = 2 * math.pi * (i + 0.5) / 14 + a_face
            x, y = cx + math.cos(a) * r_iw, cy + math.sin(a) * r_iw
            if bad(x, y):
                continue
            _tower(C, x, y, z_of(x, y), 0.01 * ph, 0.05 * ph, kind=kind, roof="erk_roof", segs=8)
    # ---- 시가: 고리 거리를 따라 줄지은 박공집 (알록달록한 지붕), 큰길은 비운다
    if town:
        roofs = ("erk_roof_r", "erk_roof", "erk_roof_p", "erk_roof_o", "erk_roof_r", "erk_roof_b", "erk_roof_l")
        walls = ("erk_wall", "erk_wall", "erk_wall_d")
        step = 22.0 * s / max(0.4, density) ** 0.5
        r = r_t0
        while r < r_t1:
            circ = 2 * math.pi * r
            n = int(circ / (step * 1.15))
            for i in range(n):
                if rng.random() > 0.9 * min(1.0, density + 0.2):
                    continue
                a = 2 * math.pi * (i + rng.uniform(-0.15, 0.15)) / n
                rr = r + rng.uniform(-2, 2) * s
                x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
                if on_avenue(x, y, 0.018 * h + 6 * s) or bad(x, y):
                    continue
                L = rng.uniform(0.6, 0.95) * step
                D = rng.uniform(8, 12) * s
                hh = rng.uniform(6, 10) * s * (1.25 if r < 0.35 * h else 1.0)
                zz = z_of(x, y)
                t = Vector((-math.sin(a), math.cos(a), 0))
                o = Vector((math.cos(a), math.sin(a), 0))
                p = Vector((x, y, 0))
                q = [p - t * L / 2 - o * D / 2, p + t * L / 2 - o * D / 2, p + t * L / 2 + o * D / 2, p - t * L / 2 + o * D / 2]
                mk._bm_prism(C.bm(rng.choice(walls), kind), [(v.x, v.y) for v in reversed(q)], zz - 1.5, zz + hh, top=False,
                             bottom=False)
                b = C.bm(rng.choice(roofs), kind)
                ov = 0.5 * s
                e = [v + (v - p).normalized() * ov for v in q]
                ra, rb = p - t * (L / 2 + ov), p + t * (L / 2 + ov)
                zr = zz + hh + D * 0.45
                vv = [b.verts.new((v.x, v.y, zz + hh - 0.2)) for v in e]
                va, vb = b.verts.new((ra.x, ra.y, zr)), b.verts.new((rb.x, rb.y, zr))
                fs = [b.faces.new((vv[0], vv[1], vb, va)), b.faces.new((vv[2], vv[3], va, vb)),
                      b.faces.new((vv[3], vv[0], va)), b.faces.new((vv[1], vv[2], vb))]
                bmesh.ops.recalc_face_normals(b, faces=fs)
                if lit and rng.random() < 0.3:
                    w = p - o * (D / 2 + 0.2)
                    C.rect(lit, (w.x, w.y, zz + hh * 0.5), tuple(-o), 2.4 * s, 2.4 * s, lift=0.0, kind="fine")
            r += step * rng.uniform(1.0, 1.2)
        # 시가 속 첨탑 신전 (고리마다 몇 개)
        for k in range(8):
            a = a_face + 2 * math.pi * (k + 0.5) / 8 + rng.uniform(-0.15, 0.15)
            d = rng.uniform(0.32, 0.55) * h
            x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
            if bad(x, y) or on_avenue(x, y, 0.03 * h):
                continue
            _tower(C, x, y, z_of(x, y), 0.009 * ph, rng.uniform(0.06, 0.085) * ph, kind=kind,
                   roof=("erk_roof", "erk_roof_p", "erk_roof_l")[k % 3], onion=k % 3 == 1, segs=8)
    # ---- 바깥 성벽 + 탑 + 큰길 문루
    if outer_wall:
        _wall_ring(C, cx, cy, r_ow, z_of, 0.026 * ph, 0.012 * ph, n=40, kind=kind,
                   skip=lambda x, y: bad(x, y) or on_avenue(x, y, 0.016 * h))
        for i in range(20):
            a = a_face + 2 * math.pi * (i + 0.5) / 20
            x, y = cx + math.cos(a) * r_ow, cy + math.sin(a) * r_ow
            if bad(x, y) or on_avenue(x, y, 0.03 * h):
                continue
            _tower(C, x, y, z_of(x, y), 0.009 * ph, 0.042 * ph, kind=kind,
                   roof="erk_roof" if i % 2 else "erk_roof_l", segs=8)
        for k, b0 in enumerate(av):
            for sx in (-1, 1):
                a = b0 + sx * 0.022 * h / r_ow
                x, y = cx + math.cos(a) * r_ow, cy + math.sin(a) * r_ow
                if bad(x, y):
                    continue
                _tower(C, x, y, z_of(x, y), 0.012 * ph, 0.055 * ph, kind=kind, roof="erk_roof", segs=10)
        gx, gy = cx + math.cos(a_face) * r_ow, cy + math.sin(a_face) * r_ow
        out["gate"] = Vector((gx, gy, z_of(gx, gy)))
    return out


def erpien(C, cx, cy, z0, h, *, hfun=None, face=(0.0, -1.0), kind="far", detail=0, seed=11, skip=None, lit=None,
           density=1.0, **kw):
    """세계수 + 왕국 (원경 한 줄). 반환: dict(center, top, crown_bottom, crown_r, palace_top, r_wall, gate)."""
    t = world_tree(C, cx, cy, z0, h, detail=detail, kind=kind, seed=seed + 1)
    k = kingdom(C, cx, cy, z0, h, hfun=hfun, face=face, kind=kind, seed=seed, skip=skip, lit=lit, density=density,
                **kw)
    return {"center": Vector((cx, cy, z0)), **t, **k}


# ================================================================ 바깥 성문 (가까운 세트)
# [원작] 왕궁 주변과 도시에 성곽이 있는 이중 성벽 (「요정(트릭컬 리바이브)」 에르피엔 안내서 서문).
# [오리지널] 성문루 생김새 전부: 원경 kingdom()의 바깥 성벽 마디·탑과 같은 자리·같은 크기(높이 0.026h, 두께 0.012h, 문루 탑
#   반지름 0.012h·높이 0.055h, 고리 탑 0.009h·0.042h, 청록 원뿔 지붕과 금 띠)를 가까이서 보는 판으로 다시 짓는다.
#   흉벽(총안 흉벽), 밑단, 활 쏘는 틈, 탑 내쌓기, 아치 문과 참나무 문짝(쇠띠·징), 문 위 둥근 판에 에르피엔 군기의 나비
#   (lib/erpien_flag.emblem, 원작 군기 도안 그대로), 문루 탑의 세로 현수막(erpien_flag.banner)과 지붕 꼭대기 깃발(far_flag).
#   원경 성벽은 plan["skip"]으로 이 구간을 비우고, 가까운 성벽이 같은 꼭짓점에서 이어진다.

def _wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def gate_plan(cx, cy, h, face, *, segs=40, near=2, towers=20, palace_scale=1.0):
    """face 쪽 바깥 성문 둘레를 가까운 세트로 바꿀 계획. 원경 kingdom()과 같은 수식(성벽 40마디, 탑 20개)을 쓴다.
    near = 성문 마디 양옆으로 몇 마디를 더 바꿀지. 반환 dict:
      a_face, F(바깥), T(오른쪽 = 반시계 방향), r_wall, A0·A1(바꾸는 각 범위), seg_angles[(a0, a1, gate?)],
      ring_towers[(x, y)], gate_towers[(x, y)], gate(성문 중심선 위 점), yaw(로컬 -Y = 바깥인 Z 회전, 도), skip(x, y)."""
    ph = h * palace_scale
    Fv = Vector((face[0], face[1], 0)).normalized()
    a_face = math.atan2(Fv.y, Fv.x)
    r_ow = 0.72 * h
    step = 2 * math.pi / segs
    ig = int(math.floor((a_face % (2 * math.pi)) / step))
    A0, A1 = (ig - near) * step, (ig + near + 1) * step
    seg_angles = [((ig + k) * step, (ig + k + 1) * step, k == 0) for k in range(-near, near + 1)]
    mid = (A0 + A1) / 2
    half = (A1 - A0) / 2

    def inside(a, tol=0.0):
        return abs(_wrap(a - mid)) <= half + tol

    ring_towers = []
    for i in range(towers):
        a = a_face + 2 * math.pi * (i + 0.5) / towers
        if inside(a, -step * 0.25):
            ring_towers.append((cx + math.cos(a) * r_ow, cy + math.sin(a) * r_ow))
    gate_towers = []
    for sx in (-1, 1):
        a = a_face + sx * 0.022 * h / r_ow
        gate_towers.append((cx + math.cos(a) * r_ow, cy + math.sin(a) * r_ow))
    # 성문 중심선과 성문 마디 현(chord)이 만나는 점
    a0, a1 = ig * step, (ig + 1) * step
    pa = Vector((cx + math.cos(a0) * r_ow, cy + math.sin(a0) * r_ow, 0))
    pb = Vector((cx + math.cos(a1) * r_ow, cy + math.sin(a1) * r_ow, 0))
    c0 = Vector((cx, cy, 0))
    d = pb - pa
    # c0 + Fv * s = pa + d * t
    den = Fv.x * (-d.y) - Fv.y * (-d.x)
    s = ((pa.x - c0.x) * (-d.y) - (pa.y - c0.y) * (-d.x)) / den
    gate = c0 + Fv * s

    def skip(x, y):
        dd = math.hypot(x - cx, y - cy)
        if abs(dd - r_ow) > 8.0:
            return False
        return inside(math.atan2(y - cy, x - cx), -step * 0.2)

    return {"center": (cx, cy), "h": h, "ph": ph, "a_face": a_face, "F": Fv, "T": Vector((-Fv.y, Fv.x, 0)),
            "r_wall": r_ow, "A0": A0, "A1": A1, "step": step, "seg_angles": seg_angles, "ring_towers": ring_towers,
            "gate_towers": gate_towers, "gate": gate, "yaw": math.degrees(a_face) + 90.0, "skip": skip,
            "wall_h": 0.026 * ph, "wall_t": 0.012 * ph, "gate_tower_r": 0.012 * ph, "gate_tower_h": 0.055 * ph,
            "ring_tower_r": 0.009 * ph, "ring_tower_h": 0.042 * ph}


class _Fr:
    """로컬 틀 (원점 + Z 회전, 로컬 -Y = 바깥)."""

    def __init__(self, o, yaw_deg):
        from mathutils import Matrix
        self.o = Vector(o)
        self.M = Matrix.Translation(self.o) @ Matrix.Rotation(math.radians(yaw_deg), 4, "Z")
        self.R = self.M.to_3x3()
        self.yaw = yaw_deg

    def p(self, x, y, z=0.0):
        return self.M @ Vector((x, y, z))

    def d(self, x, y, z=0.0):
        return self.R @ Vector((x, y, z))

    def box(self, C, key, x0, x1, y0, y1, z0, z1, kind="main"):
        mk._bm_box(C.bm(key, kind), x0, x1, y0, y1, z0, z1, matrix=self.M)


def _profile(C, key, Fr, prof, x0, x1, kind="main"):
    """(y, z) 단면 다각형을 로컬 x0..x1로 민 기둥 (끝면 포함)."""
    b = C.bm(key, kind)
    a = [b.verts.new(Fr.p(x0, y, z)) for y, z in prof]
    c = [b.verts.new(Fr.p(x1, y, z)) for y, z in prof]
    n = len(prof)
    fs = [b.faces.new(list(reversed(a))), b.faces.new(c)]
    for i in range(n):
        j = (i + 1) % n
        fs.append(b.faces.new((a[i], a[j], c[j], c[i])))
    bmesh.ops.recalc_face_normals(b, faces=fs)


def _arc_pts(r, zc, n, a0=math.pi, a1=0.0):
    return [(r * math.cos(a0 + (a1 - a0) * i / n), zc + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def _wall_piece(C, P, pa, pb, z, *, kind, slits=True, cols=True, merlon_w=1.1, pitch=2.0):
    """가까운 성벽 한 조각 (중심선 pa → pb, 바닥 z). 원경 성벽과 같은 두께·높이, 바깥 총안 흉벽 + 밑단 + 활 쏘는 틈."""
    cx, cy = P["center"]
    A = Vector((pa[0], pa[1], 0))
    B = Vector((pb[0], pb[1], 0))
    d = B - A
    L = d.length
    if L < 0.5:
        return
    yaw = math.degrees(math.atan2(d.y, d.x))
    Fr = _Fr((A.x, A.y, z), yaw)
    # 로컬 -Y가 바깥이어야 한다: 아니면 반대로 돌린다
    if Fr.d(0, -1).dot(Vector(((A.x + B.x) / 2 - cx, (A.y + B.y) / 2 - cy, 0))) < 0:
        Fr = _Fr((B.x, B.y, z), yaw + 180.0)
    t = P["wall_t"] / 2
    hh = P["wall_h"]
    walk = hh - 1.0
    prof = [(-t, -3.0), (t, -3.0), (t, walk + 0.6), (t - 0.45, walk + 0.6), (t - 0.45, walk), (-t + 0.55, walk),
            (-t + 0.55, walk + 0.45), (-t, walk + 0.45)]
    _profile(C, "erk_wall", Fr, prof, 0.0, L, kind)
    # 밑단 (바깥으로 비스듬히 두툼): 몸통 안으로 파묻힌 띠. 양 끝을 몸통 끝면보다 3 cm 내밀어 끝면끼리 같은 평면에 겹치지 않게 한다
    # (이웃 조각과 꺾여 만나는 바깥 모서리에 두 끝면이 드러나 깊이 다툼을 했다)
    # 밑면도 몸통 밑면(-3.0)보다 5 cm 아래 (땅속이지만 같은 평면 쌍을 남기지 않는다)
    _profile(C, "erk_wall_d", Fr, [(-t - 0.35, -3.05), (-t + 0.3, -3.05), (-t + 0.3, 1.75), (-t - 0.05, 1.75),
                                   (-t - 0.35, 1.2)], -0.03, L + 0.03, kind)
    # 흉벽 위 마디 (총안): 양 끝은 반 마디 비운다
    n = max(1, int((L - 0.4) // pitch))
    x0 = (L - n * pitch) / 2 + (pitch - merlon_w) / 2
    for k in range(n):
        u = x0 + k * pitch
        Fr.box(C, "erk_wall", u, u + merlon_w, -t, -t + 0.55, walk + 0.4, hh + 0.4, kind)
    if slits:
        m = max(1, int(L // 6.5))
        for k in range(m):
            u = (k + 0.5) * L / m
            C.rect("erk_slit", Fr.p(u, -t, 4.6), Fr.d(0, -1), 0.24, 1.35, lift=0.025, kind="detail")
    if cols:
        c = Fr.p(L / 2, 0.0, -3.0)
        C.ocol((c.x, c.y, c.z), (L, 2 * t + 0.7, hh + 3.4), yaw=Fr.yaw)


def _near_tower(C, x, y, z, r, hh, out, *, kind, roof="erk_roof", segs=24, slits=3, lit=None, flag=True, cols=True,
                corbels=True):
    """가까이서 보는 둥근 탑. 원경 _tower와 같은 실루엣(흰 몸통 + 금 띠 + 청록 원뿔 + 금 꼭지)에 밑단, 내쌓기,
    활 쏘는 틈, 꼭대기 군기를 더한다. out = 바깥 방향 (x, y). 반환: 꼭대기 높이."""
    import erpien_flag as ef
    from mathutils import Matrix
    # 밑단 밑면은 성벽 조각 밑면(-3.0)보다 5 cm 아래 (같은 평면 겹침 방지)
    C.cyl("erk_wall_d", (x, y, z - 3.05), (x, y, z + 2.4), r + 0.5, r2=r + 0.12, segs=segs, kind=kind, smooth=True)
    C.cyl("erk_wall", (x, y, z + 2.0), (x, y, z + hh), r, segs=segs, kind=kind, cap=False)
    o = Vector((out[0], out[1], 0)).normalized()
    if corbels:
        C.cyl("erk_wall_d", (x, y, z + hh - 0.95), (x, y, z + hh - 0.02), r + 0.34, segs=segs, kind=kind)
        nc = max(10, int(2 * math.pi * r / 1.0))
        for i in range(nc):
            a = 2 * math.pi * (i + 0.5) / nc
            q = Vector((math.cos(a), math.sin(a), 0))
            C.beam("erk_wall_d", (x + q.x * (r - 0.05), y + q.y * (r - 0.05), z + hh - 1.25),
                   (x + q.x * (r + 0.3), y + q.y * (r + 0.3), z + hh - 1.25), 0.32, 0.6, kind="detail")
    C.cyl("erk_gold", (x, y, z + hh), (x, y, z + hh + r * 0.18), r * 1.1, segs=segs, kind=kind, cap=False)
    zr = z + hh + r * 0.18
    C.cyl(roof, (x, y, zr), (x, y, zr + r * 2.3), r * 1.22, r2=0.0, segs=segs, kind=kind, smooth=False)
    top = zr + r * 2.3
    C.cyl("erk_gold", (x, y, top - r * 0.2), (x, y, top + r * 0.7), r * 0.09, r2=0.0, segs=6, kind=kind, smooth=False)
    tip = top + r * 0.7
    if flag:
        # 꼭지 위 작은 에르피엔 군기 (원경 깃발, 앞면 = 바깥)
        yaw = math.atan2(o.y, o.x) + math.pi / 2
        ef.far_flag(ef.city(C), Matrix.Translation((x, y, tip - r * 0.3)) @ Matrix.Rotation(yaw, 4, "Z"), W=max(1.6, r * 0.55),
                    pole=r * 0.75, layers={"cloth": "detail"})
    # 활 쏘는 틈 (바깥 반쪽), 위층 창 (해 질 녘이면 불빛)
    base = math.atan2(o.y, o.x)
    for row, zz in enumerate((z + 5.0, z + 9.5, z + 14.0)[:slits]):
        if zz > z + hh - 2.5:
            continue
        for k, da in enumerate((-0.75, 0.0, 0.75)):
            a = base + da + (0.37 if row % 2 else 0.0)
            q = Vector((math.cos(a), math.sin(a), 0))
            key = lit if (lit and row == len((z + 5.0, z + 9.5, z + 14.0)[:slits]) - 1 and k == 1) else "erk_slit"
            w, hgt = (0.55, 1.0) if key == lit else (0.22, 1.25)
            C.rect(key, (x + q.x * r, y + q.y * r, zz), (q.x, q.y, 0), w, hgt, lift=0.03, kind="detail")
    if cols:
        C.ccyl(x, y, r + 0.45, z - 3.0, z + hh + 0.5)
    return tip


def city_gate(C, P, hfun, *, kind="main", banners=True, flags=True, scorch=0.0, cols=True, lit=None, seed=5, passage=None):
    """gate_plan(P) 구간의 가까운 성문루·성벽·탑. hfun(x, y) = 땅 높이. scorch(0..1) = 문짝·문 둘레 그을음(포위전 흔적).
    passage (기본 = cols, 놀이 레벨): 문루를 꿰뚫는 통로(아치 폭 · 홍예 꼭대기 높이, 바닥 포석이 성 안 30 m까지)와 열리는 문짝.
      문짝 둘은 이름 있는 노드 GATE_door_L·GATE_door_R(성 밖에서 볼 때 왼쪽·오른쪽, 노드 원점은 레벨 원점, 경첩 = 속성
      hinge_x/y/z, 블렌더 좌표)로 따로 내보내고
      안쪽(성 안)으로 연다 (미션이 경첩 둘레로 돌린다: M9 끝 성문 돌입). 문짝 자리 충돌체는 레벨에 넣지 않는다: 닫힌 동안은 미션이
      세운다(내비메시가 통로를 알고, 열면 미션이 치운다). 문루 몸통 충돌체는 통로 양옆 덩어리와 통로 위 덩어리로 나눈다.
    반환 dict: front(문루 앞면 가운데, 바닥), door(문짝 앞 가운데, 1.5 m), emblem(문장 가운데), towers[(x, y, tip)],
               out(바깥 단위 벡터), right(바깥을 볼 때 오른쪽 = -T), z(성문 바닥), hinges[(x, y, z) 성 밖에서 볼 때 왼쪽·오른쪽]."""
    if passage is None:
        passage = cols
    import erpien_flag as ef
    from mathutils import Matrix
    rng = random.Random(seed)
    cx, cy = P["center"]
    r_ow = P["r_wall"]
    t = P["wall_t"] / 2
    g = P["gate"]
    zg = hfun(g.x, g.y)
    Fr = _Fr((g.x, g.y, zg), P["yaw"])
    Fv = P["F"]
    gtr = P["gate_tower_r"]
    lat = 0.022 * P["h"]
    # ---- 성벽 조각: 성문 마디는 문루 탑 가운데에서 끊는다
    for (a0, a1, is_gate) in P["seg_angles"]:
        pa = (cx + math.cos(a0) * r_ow, cy + math.sin(a0) * r_ow)
        pb = (cx + math.cos(a1) * r_ow, cy + math.sin(a1) * r_ow)
        za, zb = hfun(*pa), hfun(*pb)
        z = min(za, zb)
        if is_gate:
            A, B = Vector((*pa, 0)), Vector((*pb, 0))
            dv = (B - A).normalized()
            gl = Vector((g.x, g.y, 0))
            # 현 위에서 문루 탑 가운데까지
            _wall_piece(C, P, pa, tuple((gl - dv * lat).xy), z, kind=kind, cols=cols)
            _wall_piece(C, P, tuple((gl + dv * lat).xy), pb, z, kind=kind, cols=cols)
        else:
            _wall_piece(C, P, pa, pb, z, kind=kind, cols=cols)
    # ---- 고리 탑 (원경과 같은 자리)
    towers = []
    for i, (x, y) in enumerate(P["ring_towers"]):
        o = (x - cx, y - cy)
        tip = _near_tower(C, x, y, hfun(x, y), P["ring_tower_r"], P["ring_tower_h"], o, kind=kind,
                          roof="erk_roof" if i % 2 else "erk_roof_l", segs=20, slits=2, lit=lit, flag=flags, cols=cols)
        towers.append((x, y, tip))
    # ---- 문루 탑 둘
    for (x, y) in P["gate_towers"]:
        tip = _near_tower(C, x, y, hfun(x, y), gtr, P["gate_tower_h"], (x - cx, y - cy), kind=kind, roof="erk_roof",
                          segs=28, slits=3, lit=lit, flag=flags, cols=cols)
        towers.append((x, y, tip))
        if banners:
            # 바깥 면의 세로 현수막 (에르피엔 군기)
            o = Vector((x - cx, y - cy, 0)).normalized()
            p = Vector((x, y, 0)) + o * (gtr + 0.32)
            yaw = math.atan2(o.y, o.x) + math.pi / 2
            ef.banner(ef.city(C), Matrix.Translation((p.x, p.y, hfun(x, y) + 17.2)) @ Matrix.Rotation(yaw, 4, "Z"),
                      W=2.3, H=7.6, res=2)
    # ---- 문루 가운데 (아치 문). 로컬: x = 오른쪽(T), -y = 바깥, z = 위
    W2 = 5.8                      # 반폭 (양옆은 탑 속에 묻힌다)
    YF = -(t + 1.6)               # 앞면
    DEP = 1.2                     # 앞 판 두께 (문 홈 깊이)
    ZT = 13.4                     # 지붕(통로) 높이
    AW, SPR = 3.1, 5.4            # 아치 반폭, 홍예 시작 높이
    yd = YF + DEP
    ZC = SPR + AW                 # 홍예 꼭대기 (통로 천장)
    if not passage:
        # 몸통 (문 홈 뒤)
        Fr.box(C, "erk_wall", -W2, W2, yd, t, -3.0, ZT, kind)
    else:
        # 몸통: 통로 양옆 덩어리 + 통로 위 덩어리. 통로 안은 그늘진 석재로 덧댄다 (벽 0.12 m, 천장 0.12 m)
        Fr.box(C, "erk_wall", -W2, -AW, yd, t, -3.0, ZT, kind)
        Fr.box(C, "erk_wall", AW, W2, yd, t, -3.0, ZT, kind)
        Fr.box(C, "erk_wall", -AW, AW, yd, t, ZC, ZT, kind)
        for sx in (-1, 1):
            Fr.box(C, "erk_vault", sx * (AW - 0.12), sx * AW, yd + 0.02, t + 0.02, -0.4, ZC, kind)
        Fr.box(C, "erk_vault", -AW, AW, yd + 0.02, t + 0.02, ZC - 0.12, ZC, kind)
        # 성 안쪽 면: 통로 입구 둘레 테
        Fr.box(C, "erk_wall_d", -AW - 0.5, -AW, t, t + 0.25, -0.4, ZC + 0.5, "detail")
        Fr.box(C, "erk_wall_d", AW, AW + 0.5, t, t + 0.25, -0.4, ZC + 0.5, "detail")
        Fr.box(C, "erk_wall_d", -AW - 0.5, AW + 0.5, t, t + 0.25, ZC, ZC + 0.5, "detail")
        # 바닥 포석: 문 홈 앞에서 통로를 지나 성 안 30 m까지 (땅 높이를 따라 1 m마다)
        pb = C.bm("erk_pave", "detail")
        hw = AW - 0.14
        rows = []
        y = YF - 0.6
        while y <= t + 30.0 + 1e-6:
            row = []
            for u in (-hw, hw):
                q = Fr.p(u, y, 0)
                row.append(pb.verts.new((q.x, q.y, (zg if y <= t + 0.5 else hfun(q.x, q.y)) + 0.05)))
            rows.append(row)
            y += 1.0
        for a, b in zip(rows, rows[1:]):
            f = pb.faces.new((a[0], a[1], b[1], b[0]))
            if f.normal.z < 0:
                f.normal_flip()
    # 앞 판: 아치를 판 U자 외곽선
    out = [(-W2, -3.0), (-AW, -3.0), (-AW, SPR)] + _arc_pts(AW, SPR, 12)[1:-1] + [(AW, SPR), (AW, -3.0), (W2, -3.0),
                                                                                   (W2, ZT), (-W2, ZT)]
    C.plate("erk_wall", out, Fr.p(0, YF + DEP, 0), Fr.d(0, -1), DEP, kind=kind)
    # 아치 테 (홍예석 띠 + 금 테), 이맛돌
    band = _arc_pts(AW + 0.75, SPR, 14) + list(reversed(_arc_pts(AW, SPR, 14)))
    C.decal("erk_wall_d", band, Fr.p(0, YF, 0), Fr.d(0, -1), lift=0.02, kind="detail")
    gb = _arc_pts(AW + 0.95, SPR, 14) + list(reversed(_arc_pts(AW + 0.75, SPR, 14)))
    C.decal("erk_gold", gb, Fr.p(0, YF, 0), Fr.d(0, -1), lift=0.02, kind="detail")
    Fr.box(C, "erk_wall_d", -0.42, 0.42, YF - 0.12, YF + 0.3, SPR + AW - 0.1, SPR + AW + 1.0, "detail")
    # 문루 지붕: 앞 총안 흉벽 + 금 띠
    Fr.box(C, "erk_gold", -W2, W2, YF - 0.1, YF + 0.4, ZT - 1.05, ZT - 0.8, "detail")
    Fr.box(C, "erk_wall_d", -W2, W2, YF - 0.25, YF + 0.6, ZT - 0.05, ZT + 0.35, kind)
    for k in range(6):
        u = -W2 + 0.45 + k * (2 * W2 - 0.9 - 1.15) / 5
        Fr.box(C, "erk_wall", u, u + 1.15, YF - 0.2, YF + 0.45, ZT + 0.3, ZT + 1.55, kind)
    # 문짝 둘 (참나무 + 쇠띠 + 징), 아치 안 1.2 m. 통로가 있으면 문짝마다 이름 있는 노드(GATE_door_L/R, 경첩 속성)로 따로
    hinges = []
    prev_grp = C.grp
    for sx in (-1, 1):
        if passage:
            hp = Fr.p(sx * (AW - 0.04), yd, 0.0)
            hinges.append((hp.x, hp.y, hp.z))
            # 성 밖에서 성문을 볼 때 오른쪽 = 로컬 +x
            C.group("GATE_door_R" if sx > 0 else "GATE_door_L", hinge_x=round(hp.x, 4), hinge_y=round(hp.y, 4),
                    hinge_z=round(hp.z, 4), outline=0.03)
        pts = [(0.0, 0.0), (sx * (AW - 0.04), 0.0), (sx * (AW - 0.04), SPR)]
        arc = _arc_pts(AW - 0.04, SPR, 8, 0.0 if sx > 0 else math.pi, math.pi / 2)
        pts += arc[1:] + [(0.0, SPR + AW - 0.04)]
        pts = [(u + sx * 0.03, v) for u, v in pts]
        if sx < 0:
            pts.reverse()
        C.plate("erk_door", pts, Fr.p(0, yd, 0), Fr.d(0, -1), 0.16, kind=kind)
        zf = yd - 0.16
        for k in range(1, 6):
            u = sx * (AW * k / 6.0)
            top = SPR + math.sqrt(max(0.0, (AW - 0.1) ** 2 - u * u)) - 0.15
            C.rect("erk_door_d", Fr.p(u, zf, top / 2), Fr.d(0, -1), 0.05, top - 0.1, lift=0.012, kind="detail")
        for zb in (1.0, 3.2, 5.4):
            C.rect("erk_iron", Fr.p(sx * AW / 2, zf, zb), Fr.d(0, -1), AW - 0.3, 0.2, lift=0.02, kind="detail")
            for k in range(4):
                u = sx * (0.35 + k * (AW - 0.7) / 3)
                C.blob("erk_iron", tuple(Fr.p(u, zf - 0.03, zb)), 0.055, (1, 1, 1), segs=6, rings=4, kind="detail")
        # 문고리 (쇠 고리)
        C.ring("erk_iron", [(0.22 * math.cos(2 * math.pi * i / 10), 0.22 * math.sin(2 * math.pi * i / 10)) for i in range(10)],
               [(0.16 * math.cos(2 * math.pi * i / 10), 0.16 * math.sin(2 * math.pi * i / 10)) for i in range(10)],
               Fr.p(sx * 0.45, zf, 2.3), Fr.d(0, -1), lift=0.03, kind="detail")
        # 그을음은 문짝 위 얼룩이라 그 문짝 노드에 (통로가 있으면 함께 열린다)
        if scorch > 0 and passage:
            for i in range(int(1 + 2 * scorch)):
                u = sx * rng.uniform(0.6, AW - 0.7)
                v = rng.uniform(0.5, 1.9)
                rx, ry = rng.uniform(0.35, 0.6), rng.uniform(0.25, 0.42)
                blob = [(rx * math.cos(2 * math.pi * k / 12), ry * math.sin(2 * math.pi * k / 12)) for k in range(12)]
                C.decal("erk_soot", blob, Fr.p(u, yd - 0.16, v), Fr.d(0, -1), lift=0.03 + 0.003 * i, kind="fine")
        if passage:
            C.group(prev_grp)
    # 문 위 둥근 판: 에르피엔 군기 (초록 바탕 + 노란 나비, 원작 군기 도안 그대로)
    ZE = SPR + AW + 2.35
    disc = [(1.75 * math.cos(2 * math.pi * i / 28), 1.75 * math.sin(2 * math.pi * i / 28)) for i in range(28)]
    C.plate("erf_green", disc, Fr.p(0, YF, ZE), Fr.d(0, -1), 0.14, up=(0, 0, 1), kind="detail")
    # 금 테는 아래쪽이 아치 홍예석 띠(같은 앞면, 같은 들림)에 겹친다: fine 편향으로 늘 띠 위에 그린다
    C.ring("erk_gold", [(1.98 * math.cos(2 * math.pi * i / 28), 1.98 * math.sin(2 * math.pi * i / 28)) for i in range(28)],
           disc, Fr.p(0, YF, ZE), Fr.d(0, -1), lift=0.02, kind="fine")
    ef.city(C)
    ef.emblem(ef.city(C), Fr.M @ Matrix.Translation((0.0, YF - 0.14, ZE)), 2.5, res=2, lift=0.03,
              layers={"under": "fine"})
    # 그을음 (포위전: R41이 문짝을 부수려 한 흔적): 문짝 아래쪽에 옅은 얼룩 몇 개 (둥근 타원, 문짝 판 위)
    if scorch > 0 and not passage:
        for i in range(int(2 + 3 * scorch)):
            u = rng.uniform(-AW + 0.7, AW - 0.7)
            v = rng.uniform(0.5, 1.9)
            rx, ry = rng.uniform(0.35, 0.65), rng.uniform(0.25, 0.45)
            blob = [(rx * math.cos(2 * math.pi * k / 12), ry * math.sin(2 * math.pi * k / 12)) for k in range(12)]
            C.decal("erk_soot", blob, Fr.p(u, yd - 0.16, v), Fr.d(0, -1), lift=0.03 + 0.003 * i, kind="fine")
    if cols and not passage:
        c = Fr.p(0, (YF + t) / 2, -3.0)
        C.ocol((c.x, c.y, c.z), (2 * W2, t - YF, ZT + 4.6), yaw=Fr.yaw)
    elif cols:
        # 통로 양옆 덩어리 (아치 홍예 아래 앞 판 포함), 통로 위 덩어리. 문짝 자리(통로)는 비운다
        for sx in (-1, 1):
            c = Fr.p(sx * (W2 + AW) / 2, (YF + t) / 2, -3.0)
            C.ocol((c.x, c.y, c.z), (W2 - AW, t - YF, ZT + 4.6), yaw=Fr.yaw)
        c = Fr.p(0, (YF + t) / 2, ZC - 0.12)
        C.ocol((c.x, c.y, c.z), (2 * AW, t - YF, ZT + 1.6 - ZC + 0.12), yaw=Fr.yaw)
    return {"front": Fr.p(0, YF, 0), "door": Fr.p(0, yd - 0.2, 1.5), "emblem": Fr.p(0, YF - 0.2, ZE), "towers": towers,
            "out": Vector((Fv.x, Fv.y, 0)), "right": Fr.d(-1, 0), "z": zg, "frame": Fr, "hinges": hinges}
