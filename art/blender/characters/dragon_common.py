"""용족(트릭컬 리바이브) 공용 도우미: 키디언, 리츠.

원작 용족의 공통 특징을 엘프 키트(elf.py) 위에 더한다. 키트와 카메오·요정 헬퍼(cameo2, fairy)는 읽기 전용이라
필요한 것만 여기에 둔다. 근거: docs/art/characters-cameo3.md 키디언·리츠 절.

    용족 = 엘프 키트 몸·얼굴 + 짧은 뾰족 귀 + 머리 위 뿔 한 쌍 + 막 날개(박쥐형) + 굵은 꼬리

사용
    import dragon_common as dc
    dc.horn(e, h, "horn_L", az=40, el=52, ctrl=[...], r0=0.020, mat=horn_m)       # 머리 덩어리 위에서 솟은 뿔
    dc.wings(e, span=0.30, height=0.32, mem=mem_m, bone=bone_m)                   # 막 날개 + 본 wing_L_01/02/f1..f3
    dc.tail(e, ctrl, 0.045, mat=tail_m, belly=belly_m)                            # 꼬리 + 본 tail_01..04 (hips 자식)

본 규약 (리그 확장, three.js에서 이름으로 찾는다)
    wing_L_01 (chest 자식, 뿌리 → 팔꿈치) → wing_L_02 (팔꿈치 → 손목) → wing_L_f1, f2, f3 (손목 → 손가락 끝, 바깥 → 안쪽)
    wing_R_* 대칭. tail_01 (hips 자식) → tail_02 → ... 끝까지.
    날개 접기: wing_*_02를 몸 쪽으로, 손가락 본은 서로 모이게 돌린다. 꼬리 흔들기: tail_*를 차례로 조금씩.
"""
from __future__ import annotations

import math

import elf
import fairy
from elf import V, Matrix, Buf, loft, lerp, smoothstep, clamp, mixw, catmull


# =========================================================================== 뿔

def horn(e, h, name, *, az, el, ctrl, r0, mat, lift=-0.004, sink=0.014, n=14, segs=10, flat=0.86, tip=0.0012,
         p=2.0, taper=0.85, group="head"):
    """머리 덩어리 바깥 면(az, el)에서 솟는 뿔. ctrl: 뿌리에서의 오프셋 목록(m, 키트 기준 → e.k를 곱한다).
    단면은 납작한 타원(flat)이고 끝은 둥글게 모인다. 뿌리는 머리카락 안으로 sink만큼 묻는다.
    반환: (중심선 점 목록, 반지름 함수 r(t), 뿌리 점, 뿌리 법선)."""
    k = e.k
    base, nrm = h.path(az, h.s_of_el(az, el), lift * k)
    pts = [base - nrm * sink * k, base] + [base + V(o) * k for o in ctrl]
    P = catmull(pts, n)

    def r_at(t):
        return max(r0 * k * (1.0 - t) ** taper, tip * k)

    def fn(buf):
        st = []
        for i, q in enumerate(P):
            t = i / (len(P) - 1)
            r = r_at(t)
            st.append({"c": q, "rx": r, "ry": r * flat, "w": {"head": 1.0}, "ref": tuple(nrm), "p": p})
        loft(buf, st, segs=segs, cap0="flat", cap1="round", mat=mat)
    e.part(name, group, fn)
    return P, r_at, base, nrm


def path_at(P, t):
    """점 목록 P의 길이 비율 t 위치와 접선."""
    cum = [0.0]
    for a, b in zip(P, P[1:]):
        cum.append(cum[-1] + (b - a).length)
    s = clamp(t) * cum[-1]
    for i in range(len(P) - 1):
        if s <= cum[i + 1] or i == len(P) - 2:
            L = cum[i + 1] - cum[i]
            a = (s - cum[i]) / L if L > 1e-9 else 0.0
            return P[i].lerp(P[i + 1], clamp(a)), (P[i + 1] - P[i]).normalized()
    return P[-1], (P[-1] - P[-2]).normalized()


def horn_sleeve(buf, P, r_at, t0, t1, mat, *, grow=0.0035, n=6, segs=4, rot=45.0, w=None, k=1.0):
    """뿔에 씌운 모난 덮개(금속 뿔 가리개): 뿔 중심선 t0~t1 구간을 각진 단면(segs각형)으로 감싼다."""
    st = []
    for i in range(n):
        t = lerp(t0, t1, i / (n - 1))
        c, T = path_at(P, t)
        r = r_at(t) * 1.45 + grow * k      # 각진 단면의 면이 뿔 표면 밖으로 나오게 (내접 → 외접)
        st.append({"c": c, "rx": r, "ry": r, "w": w or {"head": 1.0}, "rot": math.radians(rot)})
    loft(buf, st, segs=segs, cap0="flat", cap1="flat", mat=mat, p=2.0)


# =========================================================================== 막 날개

def _frame(e, side, *, z, angle, sweep, raise_, inset):
    """날개 뿌리 위치와 2D(x=바깥, z=위) → 월드 행렬. 로컬 +Y(두께)는 양쪽 모두 몸 뒤쪽 (오른쪽은 왼손 좌표계)."""
    s = 1 if side == "L" else -1
    k = e.k
    root, _ = e.torso_point(z, s * angle, -inset * k)
    sw = math.radians(sweep)
    ox = V((s * math.cos(sw), math.sin(sw), 0.0))
    up = V((0, 0, 1))
    ra = math.radians(raise_)
    X = (ox * math.cos(ra) + up * math.sin(ra)).normalized()
    Z = (up * math.cos(ra) - ox * math.sin(ra)).normalized()
    Y = Z.cross(X).normalized() if s > 0 else X.cross(Z).normalized()
    M = Matrix((X, Y, Z)).transposed().to_4x4()
    M.translation = root
    return M


#: 기본 날개 골격 (L=폭, H=높이 비율). R 뿌리, E 팔꿈치, W 손목, F 손가락 끝(바깥→안쪽), B 막이 몸에 다시 붙는 곳
WING_SHAPE = {
    "R": (0.0, 0.0), "E": (0.30, 0.52), "W": (0.58, 0.96),
    "F": [(1.00, 0.62), (0.86, 0.04), (0.50, -0.30)],
    "B": (0.05, -0.26), "C": (0.50, 0.32),
}


def _dist_seg(p, a, b):
    ax, az = a
    bx, bz = b
    px, pz = p
    dx, dz = bx - ax, bz - az
    L2 = dx * dx + dz * dz
    t = clamp(((px - ax) * dx + (pz - az) * dz) / L2) if L2 > 1e-12 else 0.0
    return math.hypot(px - (ax + dx * t), pz - (az + dz * t))


def wings(e, *, span=0.30, height=0.32, mem, bone, z=None, angle=140.0, sweep=26.0, raise_=6.0, inset=0.006,
          th=0.0035, spar=0.0085, scallop=0.17, shape=None, claw=True, name="wings", rings=2, n_scallop=6):
    """박쥐형 막 날개 한 쌍 (용족). 팔(뿌리-팔꿈치-손목)과 손가락 3개 뼈대(bone 재질 관) 사이에 막(mem 재질)을 친다.
    막은 가운데가 두께 th, 가장자리가 얇아지는 판이라 아웃라인이 테두리에 생긴다. 뒷단은 손가락 끝 사이가 오목하게
    파인 물결(scallop). 본: wing_<S>_01/02 + 손가락 wing_<S>_f1..f3 (chest 자식). 웨이트는 가까운 뼈대일수록 크다
    (막이 손가락을 따라 접힌다). 날개는 등 장비라 body 그룹. 반환: {side: 행렬}"""
    k = e.k
    L = span * k
    H = height * k
    S = dict(WING_SHAPE)
    if shape:
        S.update(shape)
    zc = z if z is not None else e.chest_z + 0.040 * k

    def P2(xz):
        return (xz[0] * L, xz[1] * H)
    R, E, W, B, C = P2(S["R"]), P2(S["E"]), P2(S["W"]), P2(S["B"]), P2(S["C"])
    F = [P2(f) for f in S["F"]]
    out = {}
    for side in ("L", "R"):
        M = _frame(e, side, z=zc, angle=angle, sweep=sweep, raise_=raise_, inset=inset)
        Minv = M.inverted()

        def W3(p2, M=M):
            return M @ V((p2[0], 0.0, p2[1]))
        b1, b2 = f"wing_{side}_01", f"wing_{side}_02"
        e.add_bone(b1, W3(R), W3(E), "chest")
        e.add_bone(b2, W3(E), W3(W), b1)
        fb = []
        for i, f in enumerate(F):
            nm = f"wing_{side}_f{i + 1}"
            e.add_bone(nm, W3(W), W3(f), b2)
            fb.append(nm)
        segs2 = [(R, E, b1), (E, W, b2)] + [(W, f, nm) for f, nm in zip(F, fb)]

        def wfn(q, Minv=Minv, segs2=segs2):
            lq = Minv @ V(q)
            p = (lq.x, lq.z)
            acc = {}
            for a, b, nm in segs2:
                d = _dist_seg(p, a, b)
                acc[nm] = acc.get(nm, 0.0) + 1.0 / (d + 0.012 * L) ** 2
            top = sorted(acc.items(), key=lambda kv: -kv[1])[:3]
            tot = sum(v for _, v in top)
            w = {nm: v / tot for nm, v in top}
            # 뿌리 근처는 가슴에 붙는다
            rr = math.hypot(p[0] - R[0], p[1] - R[1])
            a = smoothstep(0.02 * L, 0.20 * L, rr)
            return mixw({"chest": 1.0}, w, a)

        # ---- 막 외곽선 (반시계): R → B → (물결) F3 → (물결) F2 → (물결) F1 → W → E → R
        def straight(a, b, n):
            return [(lerp(a[0], b[0], i / n), lerp(a[1], b[1], i / n)) for i in range(n)]

        def scal(a, b, n):
            mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            dx, dz = C[0] - mx, C[1] - mz
            dl = math.hypot(dx, dz) or 1.0
            seg = math.hypot(b[0] - a[0], b[1] - a[1])
            out_ = []
            for i in range(n):
                t = i / n
                dep = scallop * seg * math.sin(math.pi * t) ** 0.9
                out_.append((lerp(a[0], b[0], t) + dx / dl * dep, lerp(a[1], b[1], t) + dz / dl * dep))
            return out_
        outline = []
        outline += straight(R, B, 3)
        chain = [B] + F[::-1]
        for a, b in zip(chain, chain[1:]):
            outline += scal(a, b, n_scallop)
        outline += straight(F[0], W, 5)
        outline += straight(W, E, 4)
        outline += straight(E, R, 4)
        buf = Buf()
        fairy.pillow(buf, outline, [0.0] * len(outline), C, M, th * k, rings=rings, mat=mem, wfn=wfn, groove=0.0,
                     p=6.0)

        # ---- 뼈대 관: 팔(굵게) + 손가락(가늘게 끝으로 모임) + 손목 갈고리 발톱
        def tube(pts2, r0_, r1_, nn=5, sg=6, cap1="flat"):
            Pp = catmull([W3(p) for p in pts2], nn)
            st = []
            for i, q in enumerate(Pp):
                t = i / (len(Pp) - 1)
                r = lerp(r0_, r1_, t)
                st.append({"c": q, "rx": r, "ry": r, "w": wfn(q)})
            loft(buf, st, segs=sg, cap0="flat", cap1=cap1, mat=bone, cap_rings=2)
        tube([R, E], spar * 1.15 * k, spar * 0.95 * k)
        tube([E, W], spar * 0.95 * k, spar * 0.80 * k, cap1="round")
        for f in F:
            tube([W, f], spar * 0.62 * k, spar * 0.20 * k, nn=4)
        if claw:
            cw = W3(W)
            up = (M.to_3x3() @ V((-0.35, 0.0, 1.0))).normalized()
            st = [{"c": cw, "rx": spar * 0.9 * k, "ry": spar * 0.9 * k, "w": wfn(cw)},
                  {"c": cw + up * 0.020 * k, "rx": spar * 0.55 * k, "ry": spar * 0.55 * k, "w": wfn(cw)},
                  {"c": cw + up * 0.034 * k + (M.to_3x3() @ V((-0.4, 0, 0))).normalized() * 0.010 * k,
                   "rx": 0.0010 * k, "ry": 0.0010 * k, "w": wfn(cw)}]
            loft(buf, st, segs=6, cap0="round", cap1="round", mat=bone)
        ob = buf.obj(f"{e.name}_{name}_{side}", angle=50.0)
        e.add(ob, group="body", tag=f"{name}_{side}")
        out[side] = M
    return out


# =========================================================================== 꼬리

def tail(e, ctrl, r0, *, mat, belly=None, r1=None, bones=4, n=26, segs=12, flat=0.82, belly_arc=110.0,
         tip_len=0.18, name="tail", parent="hips", up_fn=None, extra=None):
    """굵은 용 꼬리: ctrl(월드 제어점, 뿌리 → 끝)을 따라 타원 단면 관이 끝으로 모인다. belly: 아랫면 띠 재질
    (단면 아래쪽 belly_arc도 구간). 본 tail_01..N (parent 자식), 웨이트는 사슬을 따라 부드럽게.
    up_fn(t, 접선) → 단면 '위' 방향 (기본: 월드 위를 접선에 수직으로). extra(buf, P, r_at, wfn): 장식 추가.
    반환: (중심선 점 목록, 반지름 함수, 웨이트 함수)"""
    k = e.k
    P = catmull([V(c) for c in ctrl], 96)
    cum = [0.0]
    for a, b in zip(P, P[1:]):
        cum.append(cum[-1] + (b - a).length)

    def at(t):
        s = clamp(t) * cum[-1]
        for i in range(len(P) - 1):
            if s <= cum[i + 1] or i == len(P) - 2:
                Ls = cum[i + 1] - cum[i]
                a = (s - cum[i]) / Ls if Ls > 1e-9 else 0.0
                return P[i].lerp(P[i + 1], clamp(a)), (P[i + 1] - P[i]).normalized()
        return P[-1], (P[-1] - P[-2]).normalized()
    joints = [at(i / bones)[0] for i in range(bones + 1)]
    names = []
    prev = parent
    for i in range(bones):
        nm = f"tail_{i + 1:02d}"
        e.add_bone(nm, joints[i], joints[i + 1], prev)
        names.append(nm)
        prev = nm
    ch = elf.Chain(joints, names, start={parent: 1.0}, start_blend=0.6)
    r1 = r1 if r1 is not None else r0 * 0.12

    def r_at(t):
        tt = (t - (1 - tip_len)) / tip_len
        body = lerp(r0, r1 * 2.2, t ** 1.1)
        if tt > 0:
            body *= (1 - tt ** 1.6) ** 0.6
        return max(body, 0.0008) * k

    def wfn(t):
        return ch.weights(clamp(t))

    buf = Buf()
    rings = []
    prev_up = None
    for i in range(n):
        t = i / (n - 1)
        c, T = at(t)
        up = up_fn(t, T) if up_fn else V((0, 0, 1))
        up = up - T * up.dot(T)
        if up.length < 1e-4:
            up = prev_up or V((0, -1, 0))
        up.normalize()
        prev_up = up
        side = T.cross(up).normalized()
        r = r_at(t)
        ring = []
        for j in range(segs):
            a = 2 * math.pi * j / segs
            q = c + side * (math.sin(a) * r) + up * (math.cos(a) * r * flat)
            ring.append(buf.vert(q, wfn(t)))
        rings.append(ring)
    for i in range(n - 1):
        for j in range(segs):
            j2 = (j + 1) % segs
            ac = math.degrees(2 * math.pi * (j + 0.5) / segs)
            m = belly if (belly is not None and abs(ac - 180.0) < belly_arc / 2) else mat
            buf.face((rings[i][j], rings[i + 1][j], rings[i + 1][j2], rings[i][j2]), m)
    c0, T0 = at(0.0)
    root = buf.vert(c0 - T0 * 0.010 * k, wfn(0.0))
    for j in range(segs):
        buf.face((root, rings[0][(j + 1) % segs], rings[0][j]), mat)
    cE, TE = at(1.0)
    tip = buf.vert(cE + TE * 0.004 * k, wfn(1.0))
    for j in range(segs):
        buf.face((rings[-1][j], rings[-1][(j + 1) % segs], tip), mat)
    if extra:
        extra(buf, at, r_at, wfn)
    ob = buf.obj(f"{e.name}_{name}", angle=60.0)
    e.add(ob, group="body", tag=name)
    return at, r_at, wfn


def tail_band(buf, at, r_at, wfn, t, mat, *, h=0.016, th=0.003, segs=12, k=1.0):
    """꼬리에 감은 띠 (붕대 등)."""
    c, T = at(t)
    ref = V((1, 0, 0)) if abs(T.x) < 0.9 else V((0, 1, 0))
    r = r_at(t) + th * 0.5 * k
    elf.band(buf, c, T, ref, r, r * 0.86, h * k, th * k, segs=segs, mat=mat, w=wfn(t))


# =========================================================================== 작은 장식

def stud(buf, c, n, r, mat, *, w=None, depth=0.6, segs=8, rings=4):
    """반구 징·돌 (뒤는 묻힘): 법선 n 방향으로 볼록."""
    n = V(n).normalized()
    a = V((1, 0, 0)) if abs(n.x) < 0.9 else V((0, 1, 0))
    A = n.cross(a).normalized()
    Bv = n.cross(A).normalized()
    fairy.ellipsoid(buf, V(c), n, A, Bv, r * depth, r, r, segs=segs, rings=rings, mat=mat, w=w)
