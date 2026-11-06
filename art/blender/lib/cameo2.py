"""원작 카메오 2차 공용 헬퍼 (cameo2).

헤일리, 아멜리아, 아멜리아(R41), 로네, 뮤트, 에르핀, 시온 모델이 같이 쓴다. 키트(elf.py)와 1차 헬퍼(cameo.py)는
읽기 전용이라 필요한 기능을 여기에 복사·확장했다. 근거와 인물별 사용처는 docs/art/characters-cameo2.md.
[키트 후보] 표시는 키트로 올릴 만한 기능이다.

헤어 v2 위에서 쓰는 것
    h = cameo2.hair(e, "#e9d3c4", lock_fn=...)      # 키트 Hair + 다발 목록 후처리(비대칭 옆머리 등)
    cameo2.tail(h, "hair_tail_L", ctrl, 0.08, 0.05)  # 한쪽 꼬리(사이드테일) + 본 사슬
    cameo2.braid(h, ctrl, 0.05, 0.04)               # 머리 위를 지나는 땋은 머리(크라운 브레이드)
    cameo2.on_hair_band(e, h, mat, ...)             # 머리띠·모자 띠 (머리 덩어리 바깥 면을 따라감)
    cameo2.stripe(h, mat, z0, z1)                   # 머리 덩어리에 가로 색 띠(평면으로 잘라 칠함)
    cameo2.vc_gradient(obj, ...)                    # finalize 뒤 머리끝 색 그라데이션(정점색)
"""
from __future__ import annotations

import math

import bmesh
import bpy

import cb
import elf
from elf import V, Matrix, Buf, loft, band, rbox, disc, keys, lerp, smoothstep, mixw, clamp, frame, catmull


# =========================================================================== 얼굴: 비대칭 표정

def face_expr(e, name, *, both=None, L=None, R=None, M=None, corner=(0.0, 0.0), mouth_dx=0.0, blink_fix=True):
    """비대칭 표정 셰이프 키 (윙크, 한쪽 입꼬리, 한쪽 눈썹). cameo.face_expr와 같다. [키트 후보]
    both: 공통, L: 캐릭터 왼쪽(+X) 눈·눈썹, R: 오른쪽(-X), M: 입(없으면 both). corner=(왼쪽, 오른쪽) 입꼬리 올림(m).
    blink 교정 키 'blink_<이름>'도 만든다 (눈을 감는 쪽이 있으면 만들지 않는다). ELF_KIT.md 6장."""
    f = e.face_builder
    ob = e.face_obj
    base = f.base

    def P(*ovs):
        p = base
        for o in ovs:
            if o:
                p = elf._merge_expr(p, o)
        return p

    neutral = f._build(base).v
    th = f.ex * 0.45
    ez = f.ez

    def comp(extra=None):
        bl = f._build(P(both, L, extra)).v
        br = f._build(P(both, R, extra)).v
        bm = f._build(P(both, M, extra)).v
        mq = P(both, M)["mouth"]
        mw = mq["w"] * f.sz / 2
        out = []
        for i, q in enumerate(neutral):
            if q.x > th:
                c = bl[i].copy()
            elif q.x < -th:
                c = br[i].copy()
            else:
                c = bm[i].copy()
                if q.z < ez - 0.03 * e.k and (corner != (0.0, 0.0) or mouth_dx):
                    x = c.x
                    y0 = e.face_project(c.x, c.z)[0].y
                    c.z += corner[0] * smoothstep(-0.2 * mw, mw, x) + corner[1] * smoothstep(0.2 * mw, -mw, x)
                    c.x += mouth_dx
                    # 얼굴 곡면을 따라 앞뒤 위치를 다시 맞춘다 (위로 올린 입꼬리가 볼 속으로 묻히지 않게)
                    c.y += e.face_project(c.x, c.z)[0].y - y0
            out.append(c)
        return out

    co = comp()
    _add_key(ob, name, co)
    closes = [((o or {}).get("eye", {}).get("close", 0.0)) for o in (both, L, R)]
    if blink_fix and max(closes) < 1.0 and ob.data.shape_keys and "blink" in ob.data.shape_keys.key_blocks:
        vb = [v.co.copy() for v in ob.data.shape_keys.key_blocks["blink"].data]
        comb = comp({"eye": {"close": 1.0}})
        _add_key(ob, f"blink_{name}", [c - x - b + o * 2 for c, x, b, o in zip(comb, co, vb, neutral)])
    return name


def _add_key(ob, name, co_list):
    assert len(co_list) == len(ob.data.vertices), f"표정 {name}: 정점 수 불일치"
    key = ob.shape_key_add(name=name, from_mix=False)
    for i, c in enumerate(co_list):
        key.data[i].co = c
    key.value = 0.0
    return key


def recolor_face(e, pred, mapping, *, tol=6):
    """얼굴 정점색에서 pred(면 중심)이 참인 면의 색을 mapping{원래 hex: 새 hex}대로 바꾼다 (오드아이·컬러 렌즈).
    e.face() 직후에 부른다. 셰이프 키는 위치만 바꾸므로 색은 모든 표정에서 유지된다. [키트 후보: 좌우 눈색]"""
    ob = e.face_obj
    me = ob.data
    ca = me.color_attributes.get("Col")
    src = [(elf.hex_srgb(a), elf.hex_srgb(b)) for a, b in mapping.items()]
    n = 0
    for poly in me.polygons:
        if not pred(poly.center):
            continue
        for li in poly.loop_indices:
            c = ca.data[li].color_srgb
            for a, b in src:
                if max(abs(c[i] - a[i]) for i in range(3)) * 255 <= tol:
                    ca.data[li].color_srgb = (*b, 1.0)
                    n += 1
                    break
    return n


def face_marks(e, name, strokes, mat, *, off=0.0045, group="head"):
    """얼굴 위 작은 표식(눈물 자국·볼 빗금·눈 밑 다크서클 선). strokes: [[(x, z), ...], ...] 얼굴 정면 좌표의 점 띠
    (각 띠는 폭 있는 사각 띠 4점, 반시계). 아웃라인 없는 노드로 남긴다 (noOutline)."""
    b = Buf()
    for st in strokes:
        ids = [b.vert(e.face_project(x, z, off)[0], {"head": 1.0}) for x, z in st]
        b.face(tuple(ids), mat)
    ob = b.obj(f"{e.name}_{name}", smooth=False)
    e.add(ob, group=group, tag=name, node=name, props={"noOutline": 1})
    return ob


# =========================================================================== 머리카락 (헤어 v2 확장)

class Hair2(elf.Hair):
    """키트 헤어 v2 + 다발 목록 후처리 훅. [키트 후보: lock_fn 훅]

    lock_fn(h, locks) → locks: 셸을 만들기 직전에 다발 목록을 고친다. 다발 사전의 키는 a0/a1(방위, 도),
    L(정수리에서 끝까지 길이), free(끝에서 갈라지는 길이), region('front'|'side'|'back'|'fill'), side('L'|'R'),
    sweep/curl/puff/th/p/mat. 예: 한쪽 옆머리만 길게, 앞머리 한 다발만 눈을 덮게.
    post: done() 직후 머리카락 오브젝트(바깥층, 속층)에 적용할 함수 목록 (stripe 등)."""

    def __init__(self, e, color, *, lock_fn=None, vol_fn=None, hug_fn=None, **kw):
        super().__init__(e, color, **kw)
        self.lock_fn = lock_fn
        self.vol_fn = vol_fn
        self.hug_fn = hug_fn
        self.post = []

    def _volume(self, az, el):
        v = super()._volume(az, el)
        return v * self.vol_fn(az, el) if self.vol_fn else v

    def _prep(self):
        """hug_fn(az) → 높이(도, 예: -58)를 주는 경도는 머리가 가장 넓은 곳에서 아래로 떨어지지 않고 두피를 따라
        그 높이까지 감싼다 (올림머리·묶은 머리의 뒤통수). None/False면 키트와 같다. True는 -60°."""
        if self._T is not None:
            return
        if not self.hug_fn:
            return super()._prep()
        c = self.e.head_c
        n_az = 144
        self._daz = 360.0 / n_az
        els = [89.0 - 2.0 * j for j in range(70)]
        T = []
        for i in range(n_az):
            az = i * self._daz
            P, N = [], []
            for el in els:
                p, n = self._surf_n(az, el)
                P.append(p + n * self._volume(az, el))
                N.append(n)
            hug = self.hug_fn(az)
            if hug is not None and hug is not False:
                lo = -60.0 if hug is True else float(hug)
                jb = max(j for j, el in enumerate(els) if el >= lo)
            else:
                best = None
                for j, el in enumerate(els):
                    if -40.0 <= el <= 12.0:
                        r = math.hypot(P[j].x - c.x, P[j].y - c.y)
                        if best is None or r > best[0] + 1e-6:
                            best = (r, j)
                jb = best[1]
            P, N = P[:jb + 1], N[:jb + 1]
            cum = [0.0]
            for a_, b_ in zip(P, P[1:]):
                cum.append(cum[-1] + (b_ - a_).length)
            rad = V((P[-1].x - c.x, P[-1].y - c.y, 0.0)).normalized()
            T.append({"P": P, "N": N, "cum": cum, "sb": cum[-1], "rad": rad, "drift": self._drift(az),
                      "elb": els[jb]})
        self._T = T
        self._els = els

    def _locks(self):
        L = super()._locks()
        if self.lock_fn:
            L = self.lock_fn(self, L) or L
        return L

    def done(self, name=None):
        if getattr(self, "_done", False):
            return None
        ob = super().done(name)
        ob_in = None
        for p in self.e.parts:
            if p.tag == "hair_in" and p.obj.name.startswith(ob.name):
                ob_in = p.obj
        for fn in self.post:
            fn(ob, ob_in)
        return ob


def hair(e, color, *, lock_fn=None, vol_fn=None, hug_fn=None, **kw):
    """e.hair()와 같지만 Hair2를 쓴다 (lock_fn, vol_fn, hug_fn, post 훅)."""
    h = Hair2(e, color, lock_fn=lock_fn, vol_fn=vol_fn, hug_fn=hug_fn, **kw)
    e._hairs = getattr(e, "_hairs", []) + [h]
    return h


def lock_edit(fn_each):
    """lock_fn 도우미: 다발마다 fn_each(h, lk)를 부른다 (사전을 바로 고친다)."""
    def fn(h, locks):
        for lk in locks:
            fn_each(h, lk)
        return locks
    return fn


def bone_chain(e, prefix, joints, parent="head", start_blend=0.5):
    """joints(N점)를 잇는 본 N-1개 (prefix_01, _02, ...) → elf.Chain. 첫 본은 parent의 자식."""
    names = []
    prev = parent
    for i in range(len(joints) - 1):
        nm = f"{prefix}_{i + 1:02d}"
        e.add_bone(nm, joints[i], joints[i + 1], prev)
        names.append(nm)
        prev = nm
    return elf.Chain([V(p) for p in joints], names, start={parent: 1.0}, start_blend=start_blend)


def _path(ctrl, n=72):
    pts = catmull([V(p) for p in ctrl], n)
    cum = [0.0]
    for a_, b_ in zip(pts, pts[1:]):
        cum.append(cum[-1] + (b_ - a_).length)
    return pts, cum


def _at(pts, cum, t):
    s = clamp(t) * cum[-1]
    for i in range(len(cum) - 1):
        if s <= cum[i + 1] or i == len(cum) - 2:
            L = cum[i + 1] - cum[i]
            a = (s - cum[i]) / L if L > 1e-9 else 0.0
            return pts[i].lerp(pts[i + 1], clamp(a)), (pts[i + 1] - pts[i]).normalized()
    return pts[-1], (pts[-1] - pts[-2]).normalized()


class Tail:
    """한 줄기 묶은 머리 (사이드테일·포니테일·긴 트윈테일) + 본 사슬. [키트 후보: ponytail/twintails 위치 인자]

    ctrl: 뿌리(묶은 자리) → 끝 제어점(월드). bones: 본 수. parent: 첫 본의 부모. root_bone: 뿌리 웨이트 본
    (예: parent='chest', root_bone='head' → 머리에서 나와 몸을 따라 늘어지는 긴 꼬리). 굵은 주 다발 + clumps(보조 다발: 옆으로 비켜 끝만 갈라짐).
    ref_fn(t, 점) → 넓은 면이 향할 방향 (기본: 몸 중심축에서 바깥). t_hold: 폭을 유지하다 모이기 시작하는 위치."""

    def __init__(self, h, prefix, ctrl, width, thick=None, *, bones=3, parent="head", t_hold=0.55, root_w=0.75,
                 clumps=((0.30, 0.55, 0.88), (-0.30, 0.55, 0.82)), mat=None, ref_fn=None, segs=12, n=22,
                 start_blend=0.5, root_bone=None, root_t=0.16):
        e = h.e
        self.root_bone, self.root_t = root_bone, root_t
        self.h, self.e = h, e
        self.pts, self.cum = _path(ctrl, 96)
        joints = [_at(self.pts, self.cum, i / bones)[0] for i in range(bones + 1)]
        self.chain = bone_chain(e, prefix, joints, parent, start_blend=start_blend)
        thick = thick if thick is not None else width * 0.62
        c0 = V((0, 0, 0))
        ref_fn = ref_fn or (lambda t, q: V((q.x - c0.x, q.y - c0.y, 0.0)))
        self.ref_fn = ref_fn
        self.width, self.thick = width, thick
        self._sweep(self.pts, width, thick, n=n, segs=segs, t_hold=t_hold, root_w=root_w, mat=mat)
        for (dx, wsc, lsc) in clumps or ():
            self.clump(dx, wsc, lsc, mat=mat)

    def at(self, t):
        return _at(self.pts, self.cum, t)

    def w_at(self, t):
        w = self.chain.weights(clamp(t))
        if self.root_bone:
            # 뿌리는 머리에 붙고(고개를 돌리면 따라감) 아래는 몸에 붙은 사슬을 따른다 (긴 꼬리가 등·어깨에 남는다)
            w = mixw({self.root_bone: 1.0}, w, smoothstep(0.0, self.root_t, t))
        return w

    def _sweep(self, pts, width, thick, *, n, segs, t_hold, root_w, mat, t0=0.0, t1=1.0, side_off=None):
        q = self.e.q
        nn = max(12, int(n * q))
        P = []
        for i in range(nn):
            t = lerp(t0, t1, i / (nn - 1))
            c, T = self.at(t)
            if side_off:
                c = c + side_off(t, c, T)
            P.append(c)

        def prof(t):
            r = lerp(root_w, 1.0, smoothstep(0.0, 0.16, t))
            return r * elf._tip((t - t_hold) / (1 - t_hold), 2.2)

        def wfn(t):
            return self.w_at(lerp(t0, t1, t))

        def ref(t):
            c, _ = self.at(lerp(t0, t1, t))
            return self.ref_fn(lerp(t0, t1, t), c)
        elf.sweep(self.h.buf, P, lambda t: width / 2 * prof(t), lambda t: thick / 2 * max(prof(t), 0.22),
                  segs=max(10, int(segs * q) // 2 * 2), ref_fn=ref, mat=mat or self.h.m, w=wfn, bend=0.22)

    def clump(self, dx, wsc=0.55, lsc=0.85, *, mat=None, t0=0.08):
        """보조 다발: 주 다발 옆(dx = 폭 비율, +면 넓은 면 기준 오른쪽)으로 비켜서 끝만 갈라져 보이게."""
        w = self.width

        def off(t, c, T):
            out = self.ref_fn(t, c)
            out = (out - T * out.dot(T))
            out = out.normalized() if out.length > 1e-6 else V((1, 0, 0))
            S = T.cross(out).normalized()
            return S * (dx * w * smoothstep(0.25, 0.9, t)) - out * (0.12 * w)
        self._sweep(self.pts, w * wsc, self.thick * wsc * 1.05, n=16, segs=10, t_hold=0.45, root_w=0.9, mat=mat,
                    t0=t0, t1=lsc, side_off=off)

    def tie(self, mat, t=0.05, size=1.0, h_=0.022, th=0.008):
        """묶은 자리 띠."""
        c, T = self.at(t)
        out = self.ref_fn(t, c)
        out = (out - T * out.dot(T)).normalized()
        band(self.h.buf, c, T, out, self.width * 0.36 * size, self.thick * 0.42 * size, h_ * self.e.k, th * self.e.k,
             segs=14, mat=mat, w=self.w_at(t))
        return self


def tail(h, prefix, ctrl, width, thick=None, **kw):
    return Tail(h, prefix, ctrl, width, thick, **kw)


def braid(h, ctrl, w0, w1=None, *, beads=12, tilt=34.0, mat=None, face_fn=None, w=None, flat=0.70, segs=8, rings=5):
    """경로를 따라 납작한 마디를 좌우로 번갈아 기울여 반씩 겹친 땋은 머리 (머리 위를 두르는 크라운 브레이드 등).
    키트 h.braid()는 귀 뒤에서 아래로 늘어지는 모양만 만든다. 여기서는 임의 경로를 쓴다. [키트 후보]
    face_fn(점) → 마디 넓은 면이 향할 방향 (기본: 머리 중심에서 바깥). w: 웨이트(사전 또는 t 함수)."""
    e = h.e
    w1 = w0 if w1 is None else w1
    pts, cum = _path(ctrl, 80)
    L = cum[-1]
    sp = L / beads
    c0 = e.head_c
    face_fn = face_fn or (lambda q: (q - c0))
    q = e.q
    for i in range(beads):
        t = (i + 0.5) / beads
        c, T = _at(pts, cum, t)
        F = V(face_fn(c))
        F = (F - T * F.dot(T))
        F = F.normalized() if F.length > 1e-6 else V((0, -1, 0))
        S = T.cross(F).normalized()
        sg = 1 if i % 2 == 0 else -1
        wd = lerp(w0, w1, t)
        th = math.radians(-sg * tilt)
        Ax = (T * math.cos(th) + S * math.sin(th)).normalized()
        cen = c + S * (sg * 0.14 * wd)
        ww = w(t) if callable(w) else (w or {"head": 1.0})
        st = []
        nr = max(4, int(rings * q + 0.5))
        for r in range(nr):
            u = -1 + 2 * r / (nr - 1)
            rad = math.sqrt(max(0.0, 1 - u * u))
            st.append({"c": cen + Ax * (u * sp * 1.08), "rx": max(0.46 * wd * rad, 0.0006),
                       "ry": max(0.46 * flat * wd * rad, 0.0005), "w": ww, "ref": tuple(S)})
        loft(h.buf, st, segs=max(6, int(segs * q + 0.5)), cap0="flat", cap1="flat", mat=mat or h.m)
    return pts


def on_hair_band(e, h, mat, *, az0=-100.0, az1=100.0, el_fn=None, width=0.016, th=0.006, lift=0.003, n=40,
                 name="headband", group="head", s_fn=None):
    """머리 덩어리 바깥 면을 따라 두르는 띠 (머리띠·리본 띠). el_fn(az) → 띠 중심 높이(도) 또는
    s_fn(az) → 정수리에서의 길이. 머리 셸을 만들기 전에도 h.path()로 위치를 구한다."""
    k = e.k
    el_fn = el_fn or (lambda az: 58.0 - 40.0 * (abs(az) / 90.0) ** 2)

    def fn(buf):
        pts, nrm, ups = [], [], []
        for i in range(n):
            az = lerp(az0, az1, i / (n - 1))
            s = s_fn(az) if s_fn else h.s_of_el(az, el_fn(az))
            p, nn = h.path(az, s, lift * k)
            p2, _ = h.path(az, s + 0.01 * k, lift * k)
            up = (p - p2)
            up = (up - nn * up.dot(nn)).normalized()
            pts.append(p + nn * th * k * 0.5)
            nrm.append(nn)
            ups.append(up)
        elf._loop(buf, pts, nrm, ups, width * k, th * k, mat=mat, w={"head": 1.0}, closed=False)
    return e.part(name, group, fn)


def _bisect(ob, co, no):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-6, plane_co=co, plane_no=no)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


def _slot(ob, mat):
    me = ob.data
    for i, m in enumerate(me.materials):
        if m == mat:
            return i
    me.materials.append(mat)
    return len(me.materials) - 1


def stripe(h, mat, z0, z1, *, tilt=(0.0, 0.0), mat_in=None, pred=None, only=None):
    """머리 덩어리를 가로 평면 두 장(z0, z1)으로 잘라 그 사이 면을 mat으로 칠한다 (뮤트의 청록 띠 등).
    면을 잘라서 칠하므로 경계가 선명하다 (정점색 병합에서도 그대로). tilt=(앞뒤, 좌우) 기울기(z/m).
    pred(면 중심) → False면 칠하지 않는다 (예: 꼬리 제외). only: 이 머티리얼이 칠해진 면만 (예: h.bangs(mat=...)로
    앞머리에만 준 머티리얼 → 띠 끝이 다발 경계에서 끊긴다). [키트 후보: 헤어 영역 색]"""
    nrm = V((-tilt[1], -tilt[0], 1.0)).normalized()
    c = h.e.head_c

    def post(ob, ob_in):
        for o, m in ((ob, mat), (ob_in, mat_in)):
            if o is None or m is None:
                continue
            for z in (z0, z1):
                _bisect(o, V((c.x, c.y, z)), nrm)
            si = _slot(o, m)
            oi = None
            if only is not None:
                oi = [i for i, mm in enumerate(o.data.materials) if mm == only]
            for poly in o.data.polygons:
                if oi is not None and poly.material_index not in oi:
                    continue
                cc = poly.center
                # 평면 법선 (-t1, -t0, 1): z - t0·(y-cy) - t1·(x-cx) 가 z0~z1 사이면 띠 안
                dz = cc.z - (cc.y - c.y) * tilt[0] - (cc.x - c.x) * tilt[1]
                if z0 < dz < z1 and (pred is None or pred(cc)):
                    poly.material_index = si
    h.post.append(post)


def vc_gradient(obj, base_hex, stops, *, tol=8, axis=2, pred=None, fn=None):
    """finalize() 뒤 합쳐진 메시에서 색이 base_hex인 모서리의 정점색을 위치에 따라 부드럽게 바꾼다 (머리끝 물들임).
    stops: [(값, hex), ...] 값이 커지는 순서. 값 = 정점 좌표[axis] (기본 z), 또는 fn(정점 좌표).
    pred(좌표) → False면 건드리지 않는다. [키트 후보: 헤어 그라데이션]"""
    me = obj.data
    ca = me.color_attributes.get("Col")
    if ca is None:
        return 0
    base = elf.hex_srgb(base_hex)
    cols = [(t, elf.hex_srgb(hx)) for t, hx in stops]

    def col(t):
        if t <= cols[0][0]:
            return cols[0][1]
        for (t0, c0), (t1, c1) in zip(cols, cols[1:]):
            if t <= t1:
                a = smoothstep(t0, t1, t)
                return tuple(lerp(x, y, a) for x, y in zip(c0, c1))
        return cols[-1][1]
    n = 0
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            c = ca.data[li].color_srgb
            if max(abs(c[i] - base[i]) for i in range(3)) * 255 > tol:
                continue
            co = me.vertices[vi].co
            if pred is not None and not pred(co):
                continue
            v = fn(co) if fn else co[axis]
            r, g_, bb = col(v)
            ca.data[li].color_srgb = (r, g_, bb, 1.0)
            n += 1
    return n


# =========================================================================== 몸에서 떨어지는 천 (셸)

def ring_pt(rx, ry, cy, z, a_deg, p=2.3):
    """몸통 단면(초타원) 위 점과 바깥 법선. a: 0=앞(-Y), 90=왼쪽(+X), 180=뒤."""
    a = math.radians(a_deg)
    dx, dy = math.sin(a), -math.cos(a)
    ee = 2.0 / p
    x = math.copysign(abs(dx) ** ee, dx) * rx
    y = math.copysign(abs(dy) ** ee, dy) * ry + cy
    n = V((x / (rx * rx), (y - cy) / (ry * ry), 0.0))
    n = n.normalized() if n.length > 1e-9 else V((dx, dy, 0))
    return V((x, y, z)), n


def bust_off(e, z, a_deg, off_m):
    """키트 가슴 볼륨(Elf.bust)이 이 높이·방위·옷 층에서 더하는 바깥 두께(m). 키트에 없거나 0이면 0."""
    fn = getattr(e, "bust_off", None)
    return fn(z, a_deg, off_m) if fn is not None else 0.0


def bust_normal(e, z, a_deg, off_m, p, rx, ry, cy, n):
    """가슴 볼륨이 있는 곳의 셸 바깥 법선 (유한 차분). 볼륨이 없으면 n 그대로."""
    if bust_off(e, z, a_deg, off_m) <= 1e-7:
        return n

    def S(zz, aa):
        q, nn = ring_pt(rx, ry, cy, zz, aa, p)
        return q + nn * bust_off(e, zz, aa, off_m)
    dz = 0.003 * e.k
    n2 = (S(z, a_deg + 1.5) - S(z, a_deg - 1.5)).cross(S(z + dz, a_deg) - S(z - dz, a_deg))
    if n2.length < 1e-12:
        return n
    return (n2 if n2.dot(n) >= 0 else -n2).normalized()


def section(e, z, skirt=False, shoulder=0.0):
    """높이 z의 몸통 단면 (rx, ry, cy). skirt=True면 엉덩이 아래로 골반과 다리 바깥을 감싼다.
    shoulder>0이면 어깨 높이 근처에서 어깨 관절까지 덮도록 옆으로 넓힌다 (망토·걸친 코트)."""
    rx, ry, cy = e.torso_at(z)
    if skirt:
        zw = e.crotch_z + 0.17 * (e.torso_top - e.crotch_z)
        a = smoothstep(zw + 0.10 * e.k, zw - 0.02 * e.k, z)
        if a > 0:
            hx, hy, hc = e.torso_at(min(z, zw) if z > zw else zw)
            tx = max(hx, 0.158 * e.k * e.hp)
            ty = max(hy, ry)
            rx = max(rx, lerp(rx, tx, a))
            ry = max(ry, lerp(ry, ty, a))
            cy = lerp(cy, hc, a)
    if shoulder:
        sz = e.shoulder_z
        a = math.exp(-((z - sz) / (0.09 * e.k)) ** 2) if z < sz else 1.0
        rx = max(rx, lerp(rx, (0.136 + 0.045) * e.k * e.sh * shoulder, a))
    return rx, ry, cy


def skirt_w(e, p):
    """치마·코트 자락 웨이트: 골반 위는 몸통 규칙, 아래로 갈수록 좌우 허벅지를 반쯤 따라간다."""
    if p.z >= e.hipj_z:
        return e._torso_wfn(p, 0)
    a = smoothstep(e.hipj_z, e.knee_z, p.z)
    s = clamp(p.x / (0.12 * e.k), -1.0, 1.0)
    wl = 0.5 + 0.5 * s
    leg = {k: v for k, v in (("thigh_L", wl), ("thigh_R", 1 - wl)) if v > 1e-4}
    return mixw({"hips": 1.0}, leg, a * 0.65)


class Shell:
    """몸통을 감싸는 두께 있는 천 (앞트임 재킷·가운, 치마, 망토, 코트 자락). cameo.Shell 확장. [키트 후보: e.drape()]

    z_top → z_hem. gap: 앞트임 반각(도) 또는 [(u, 도)] 표. 0이면 닫힌 고리. back_only=True면 gap을 뒤쪽 기준으로
    바꿔 앞이 크게 열린 망토가 된다. off/flare/th/rows/cols/skirt/p/cover/wfn/drop/ruffle은 cameo.Shell과 같다.
    pleat=(진폭 m, 주름 수, 시작 u): 삼각파 주름 (주름치마). shoulder: 어깨 관절까지 덮는 폭(1=어깨 끝).
    키트 가슴 볼륨(Elf.bust)을 따른다. bust_drape(m, e.k 곱함): 볼륨 모양을 정할 옷 층 거리. 없으면 off+flare
    (바깥 옷일수록 천처럼 걸쳐 떨어짐). 가슴 붕대·성형 흉갑처럼 몸에 붙어야 하는 층은 0~0.012로 준다."""

    def __init__(self, e, mat, z_top, z_hem, *, gap=0.0, off=0.012, flare=None, th=0.005, rows=None, cols=None,
                 skirt=False, p=2.3, cover=False, wfn=None, drop=None, ruffle=None, pleat=None, shoulder=0.0,
                 back_only=False, a_fn=None, pleat_mat=None, bust_drape=None):
        self.e = e
        self.mat = mat
        k = e.k
        self.buf = Buf()
        self.closed = (gap == 0 or gap is None)
        self.prm = dict(z_top=z_top, z_hem=z_hem, off=off, flare=flare, skirt=skirt, p=p, drop=drop, ruffle=ruffle,
                        pleat=pleat, shoulder=shoulder, bust_drape=bust_drape)
        rows = rows or max(4, int(abs(z_top - z_hem) / (0.026 * k)) + 2)
        cols = cols or max(12, int(26 * e.q))
        self.rows, self.cols = rows, cols
        self.col_mat = None
        if pleat and pleat_mat is not None and self.closed:
            nw = pleat[1]
            # 주름 골짜기 쪽 면(삼각파의 내려가는 쪽)을 어둡게: 셀 셰이딩에서도 주름이 읽힌다
            self.col_mat = lambda j: pleat_mat if ((j + 0.5) / cols * nw) % 1.0 >= 0.5 else mat
        gfn = (lambda u: keys(gap, u)) if isinstance(gap, (list, tuple)) else (lambda u: gap or 0.0)
        wfn = wfn or ((lambda q: skirt_w(e, q)) if skirt else (lambda q: e._torso_wfn(q, 0)))
        self.P, self.N, self.W = [], [], []
        for i in range(rows):
            u = i / (rows - 1)
            z = lerp(z_top, z_hem, u)
            rx, ry, cy = section(e, z, skirt, shoulder)
            fl = keys(flare, u) if flare else 0.0
            dz = keys(drop, u) if drop else 0.0
            g = gfn(u)
            rowP, rowN, rowW = [], [], []
            for j in range(cols):
                if self.closed:
                    a = 360.0 * j / cols
                else:
                    a = g + (360.0 - 2 * g) * j / (cols - 1)
                    if back_only:
                        a = a + 180.0
                if a_fn:
                    a = a_fn(a, u)
                rf = 0.0
                if ruffle:
                    amp, nw, u0 = ruffle
                    rf = amp * smoothstep(u0, 1.0, u) * math.cos(math.radians(a) * nw)
                if pleat:
                    amp, nw, u0 = pleat
                    x = (a / 360.0 * nw) % 1.0
                    rf += amp * smoothstep(u0, u0 + 0.35, u) * (abs(x - 0.5) * 4 - 1)
                q, n = ring_pt(rx + (off + fl + rf) * k, ry + (off + fl + rf) * k, cy, z, a, p)
                bo = bust_off(e, z, a, (off + fl if bust_drape is None else bust_drape) * k)
                if bo > 0.0:
                    q = q + n * bo
                if dz:
                    q.z -= dz * k * (0.5 - 0.5 * math.cos(math.radians(a)))
                rowP.append(q)
                rowN.append(n)
                rowW.append(wfn(q))
            self.P.append(rowP)
            self.N.append(rowN)
            self.W.append(rowW)
        self._build(th * k)
        if cover and self.closed:
            e.cover["torso"].append((z_hem, z_top))

    def _build(self, th):
        b, P, N, W = self.buf, self.P, self.N, self.W
        R, C = self.rows, self.cols
        m = self.mat
        o = [[b.vert(P[i][j], W[i][j]) for j in range(C)] for i in range(R)]
        n = [[b.vert(P[i][j] - N[i][j] * th, W[i][j]) for j in range(C)] for i in range(R)]
        jr = range(C) if self.closed else range(C - 1)
        for i in range(R - 1):
            for j in jr:
                j2 = (j + 1) % C
                mo = self.col_mat(j) if self.col_mat else m
                b.face((o[i][j], o[i + 1][j], o[i + 1][j2], o[i][j2]), mo)
                b.face((n[i][j], n[i][j2], n[i + 1][j2], n[i + 1][j]), m)
        for j in jr:
            j2 = (j + 1) % C
            b.face((o[0][j], o[0][j2], n[0][j2], n[0][j]), m)
            b.face((o[R - 1][j], n[R - 1][j], n[R - 1][j2], o[R - 1][j2]), m)
        if not self.closed:
            for i in range(R - 1):
                b.face((o[i][0], n[i][0], n[i + 1][0], o[i + 1][0]), m)
                jl = C - 1
                b.face((o[i][jl], o[i + 1][jl], n[i + 1][jl], n[i][jl]), m)

    def surface(self, u, a_deg, lift=0.0):
        """셸 바깥면 위의 점과 법선 (u: 0=윗단, 1=밑단, a: 0=앞, 90=왼쪽)."""
        e, q = self.e, self.prm
        k = e.k
        z = lerp(q["z_top"], q["z_hem"], u)
        rx, ry, cy = section(e, z, q["skirt"], q["shoulder"])
        fl = keys(q["flare"], u) if q["flare"] else 0.0
        r2x, r2y = rx + (q["off"] + fl) * k, ry + (q["off"] + fl) * k
        om = (q["off"] + fl if q.get("bust_drape") is None else q["bust_drape"]) * k
        pt, n = ring_pt(r2x, r2y, cy, z, a_deg, q["p"])
        bo = bust_off(e, z, a_deg, om)
        if bo > 0.0:
            pt = pt + n * bo
            n = bust_normal(e, z, a_deg, om, q["p"], r2x, r2y, cy, n)
        return pt + n * lift, n

    def frame_at(self, u, a_deg, lift=0.0):
        """surface 위치의 배치 행렬 (로컬 -Y=바깥, +Z=위)."""
        pt, n = self.surface(u, a_deg, lift)
        return Matrix.Translation(pt) @ frame(n, (0, 0, 1))

    def _strip(self, pts, nrm, ups, width, th, mat, ws, lift=0.0):
        k = self.e.k
        c = [p + nn * (lift * k) for p, nn in zip(pts, nrm)]
        elf._loop(self.buf, c, nrm, ups, width * k, th * k, mat=mat, closed=False,
                  w=lambda t, ws=ws: ws[min(int(round(t * (len(ws) - 1))), len(ws) - 1)])

    def edge_trim(self, mat, width=0.008, th=0.0025, i0=0, i1=None, lift=0.0004, width_fn=None):
        """앞트임 양쪽 가장자리 띠 (금색 테두리, 가운 여밈단). width_fn(u)로 위아래 폭을 바꿀 수 있다."""
        if self.closed:
            return self
        i1 = self.rows if i1 is None else i1
        for jj, jn in ((0, 1), (self.cols - 1, self.cols - 2)):
            pts, nrm, ups, ws = [], [], [], []
            for i in range(i0, i1):
                u = i / (self.rows - 1)
                wd = width * (width_fn(u) if width_fn else 1.0)
                d = (self.P[i][jn] - self.P[i][jj]).normalized()
                pts.append(self.P[i][jj] + d * (wd * self.e.k * 0.45))
                nrm.append(self.N[i][jj])
                ups.append(d)
                ws.append(self.W[i][jj])
            if width_fn:
                for a in range(len(pts) - 1):
                    u = (i0 + a) / (self.rows - 1)
                    wd = width * width_fn(u)
                    if wd < 1e-4:
                        continue
                    self._strip(pts[a:a + 2], nrm[a:a + 2], ups[a:a + 2], wd, th, mat, ws[a:a + 2], lift)
            else:
                self._strip(pts, nrm, ups, width, th, mat, ws, lift)
        return self

    def hem_trim(self, mat, width=0.008, th=0.0025, lift=0.0004, row=None):
        i = self.rows - 1 if row is None else row
        return self._row_trim(i, i - 1, mat, width, th, lift)

    def top_trim(self, mat, width=0.008, th=0.0025, lift=0.0004):
        return self._row_trim(0, 1, mat, width, th, lift)

    def _row_trim(self, i, ia, mat, width, th, lift):
        C = self.cols
        idx = list(range(C)) + ([0] if self.closed else [])
        pts, nrm, ups, ws = [], [], [], []
        for j in idx:
            d = (self.P[ia][j] - self.P[i][j]).normalized()
            pts.append(self.P[i][j] + d * (width * self.e.k * 0.45))
            nrm.append(self.N[i][j])
            ups.append(d)
            ws.append(self.W[i][j])
        self._strip(pts, nrm, ups, width, th, mat, ws, lift)
        return self

    def done(self, name, group="body", angle=50.0):
        ob = self.buf.obj(f"{self.e.name}_{name}", angle=angle)
        return self.e.add(ob, group=group, tag=name)


# =========================================================================== 팔다리 덧옷

def leg_tube(e, mat, side, t0, t1, *, off=0.012, extra=None, name=None, cap0=None, cap1=None, segs=None):
    """다리에 감기는 관 (스타킹, 니삭스, 각반, 갑옷 정강이). t: 0=고관절, 1=발목. 덮은 구간의 맨살은 만들지 않는다."""
    k = e.k
    e.cover[f"leg_{side}"].append((t0, t1))
    ch = e.leg_chain(side)
    buf = Buf()
    ex = (lambda t: extra(t) * k) if extra else None
    e._limb_loft(buf, ch, e.leg_r, t0, t1, mat, segs=segs or int(16 * e.q), cap0=cap0, cap1=cap1, off=off * k,
                 extra=ex)
    ob = buf.obj(name or f"{e.name}_legtube_{side}{len(e.parts)}", angle=50.0)
    e.add(ob, group="body", tag=name or "legtube")
    return ob


def arm_tube(e, mat, side, t0, t1, *, off=0.012, extra=None, name=None, cap0=None, cap1=None, segs=None):
    """팔에 감기는 관 (긴 장갑, 토시, 건틀릿). t: 0=어깨, 1=손목."""
    k = e.k
    e.cover[f"arm_{side}"].append((t0, t1))
    ch = e.arm_chain(side)
    buf = Buf()
    ex = (lambda t: extra(t) * k) if extra else None
    e._limb_loft(buf, ch, e.arm_r, t0, t1, mat, segs=segs or int(14 * e.q), cap0=cap0, cap1=cap1, off=off * k,
                 extra=ex)
    ob = buf.obj(name or f"{e.name}_armtube_{side}{len(e.parts)}", angle=50.0)
    e.add(ob, group="arms", tag=name or "armtube")
    return ob


def limb_band(e, mat, limb, t, *, h=0.012, th=0.004, off=0.0, name=None):
    """팔다리에 두르는 띠 (e.ring과 같지만 off를 덧옷 두께에 맞춰 준다)."""
    return e.ring(mat, limb, t, h=h, th=th, off=off, name=name)


# =========================================================================== 작은 소품 도형

def ellipsoid(buf, c, A, B, F, ra, rb, rf, *, segs=8, rings=5, mat=None, wfn=None, w=None):
    """타원체. A=긴 축(반경 ra), B·F=단면 축. wfn(점) → 웨이트 사전 (없으면 w)."""
    wf = wfn or (lambda q: w or {})
    c = V(c)
    ringv = []
    for i in range(1, rings - 1):
        ph = -math.pi / 2 + math.pi * i / (rings - 1)
        row = []
        for j in range(segs):
            t = 2 * math.pi * j / segs
            q = c + A * (ra * math.sin(ph)) + (B * (rb * math.cos(t)) + F * (rf * math.sin(t))) * math.cos(ph)
            row.append(buf.vert(q, wf(q)))
        ringv.append(row)
    p0 = c - A * ra
    p1 = c + A * ra
    i0 = buf.vert(p0, wf(p0))
    i1 = buf.vert(p1, wf(p1))
    for i in range(len(ringv) - 1):
        r0, r1 = ringv[i], ringv[i + 1]
        for j in range(segs):
            j2 = (j + 1) % segs
            buf.face((r0[j], r0[j2], r1[j2], r1[j]), mat)
    for j in range(segs):
        j2 = (j + 1) % segs
        buf.face((i0, ringv[0][j2], ringv[0][j]), mat)
        buf.face((ringv[-1][j], ringv[-1][j2], i1), mat)


def prism(buf, poly, depth, M, *, mat=None, w=None, chamfer=0.0):
    """2D 다각형 poly[(x, z)] (중심에서 별 모양으로 보이는 다각형: 볼록, 별, 마름모)를 로컬 -Y(바깥)로 돌출.
    chamfer>0이면 앞면 모서리를 45°로 깎는다."""
    n = len(poly)
    cx = sum(p[0] for p in poly) / n
    cz = sum(p[1] for p in poly) / n

    def ins(p, d):
        if d <= 0:
            return p
        vx, vz = p[0] - cx, p[1] - cz
        L = math.hypot(vx, vz) or 1.0
        s = max(L - d, L * 0.2) / L
        return (cx + vx * s, cz + vz * s)
    back = [buf.vert(M @ V((x, 0.0, z)), w) for x, z in poly]
    mid = [buf.vert(M @ V((x, -(depth - chamfer), z)), w) for x, z in poly]
    front = [buf.vert(M @ V((ins((x, z), chamfer)[0], -depth, ins((x, z), chamfer)[1])), w) for x, z in poly]
    cb_ = buf.vert(M @ V((cx, 0.0, cz)), w)
    cf = buf.vert(M @ V((cx, -depth, cz)), w)
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1]))
    order = range(n) if area > 0 else range(n - 1, -1, -1)
    order = list(order)
    for ii in range(n):
        i = order[ii]
        j = order[(ii + 1) % n]
        buf.face((cb_, back[j], back[i]), mat)
        buf.face((back[i], back[j], mid[j], mid[i]), mat)
        if chamfer > 0:
            buf.face((mid[i], mid[j], front[j], front[i]), mat)
        buf.face((cf, front[i], front[j]), mat)


def star_poly(r_out, r_in, n=5, rot=90.0, cx=0.0, cz=0.0):
    """별 다각형 (반시계, 첫 꼭짓점 rot도)."""
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + 180.0 * i / n)
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def diamond_poly(w, h_, cx=0.0, cz=0.0):
    return [(cx, cz - h_ / 2), (cx + w / 2, cz), (cx, cz + h_ / 2), (cx - w / 2, cz)]


def crescent(buf, M, r, *, width=0.42, th=0.30, a0=40.0, a1=320.0, mat=None, w=None, n=16, segs=8):
    """초승달 (호를 따라 가운데가 굵고 양끝이 뾰족한 매끈한 볼륨). M 로컬: X-Z 평면, -Y 바깥. r=호 반경.
    width·th: 가장 굵은 곳의 폭·두께 (r 비율). a0~a1: 호 범위(도, 0=+X)."""
    st = []
    for i in range(n):
        t = i / (n - 1)
        a = math.radians(lerp(a0, a1, t))
        rad = math.sin(math.pi * t) ** 0.8
        c = M @ V((r * math.cos(a), -th * r * 0.5, r * math.sin(a)))
        st.append({"c": c, "rx": max(width * r * 0.5 * rad, 0.0004), "ry": max(th * r * 0.5 * rad, 0.0004),
                   "w": w or {}, "ref": tuple(M.to_3x3() @ V((math.cos(a), 0, math.sin(a))))})
    loft(buf, st, segs=segs, cap0="flat", cap1="flat", mat=mat)


def bow_geo(buf, M, size, mat, *, w=None, tails=0.8, knot_mat=None, segs=8):
    """리본 매듭 (둥근 날개 2개 + 매듭 + 꼬리 2개). M 로컬: +Z 위, -Y 앞, X 옆. size = 전체 폭(m)."""
    s = size / 2
    for sg in (1, -1):
        st = []
        for i in range(6):
            t = i / 5
            x = sg * lerp(0.10, 0.92, t) * s
            rz = keys([(0.0, 0.16), (0.45, 0.44), (0.8, 0.40), (1.0, 0.22)], t) * s
            ry = keys([(0.0, 0.14), (0.5, 0.22), (1.0, 0.14)], t) * s
            c = M @ V((x, 0.0, 0.06 * s * math.sin(t * math.pi)))
            st.append({"c": c, "rx": rz, "ry": ry, "w": w or {}, "ref": tuple(M.to_3x3() @ V((0, 0, 1)))})
        loft(buf, st[::2] + [st[-1]], segs=segs, cap0="round", cap1="round", mat=mat, cap_len0=0.05 * s,
             cap_len1=0.18 * s, cap_rings=2)
        if tails:
            a = M @ V((sg * 0.12 * s, -0.04 * s, -0.10 * s))
            b = M @ V((sg * 0.42 * s, -0.02 * s, -tails * s))
            rf = tuple(M.to_3x3() @ V((1, 0, 0)))
            st2 = [{"c": a, "rx": 0.16 * s, "ry": 0.05 * s, "w": w or {}, "ref": rf},
                   {"c": a.lerp(b, 0.5), "rx": 0.19 * s, "ry": 0.05 * s, "w": w or {}, "ref": rf},
                   {"c": b, "rx": 0.22 * s, "ry": 0.05 * s, "w": w or {}, "ref": rf}]
            loft(buf, st2, segs=6, cap0="flat", cap1="flat", mat=mat)
    rbox(buf, (0.30 * s, 0.34 * s, 0.36 * s), M @ Matrix.Translation((0, -0.04 * s, 0)), mat=knot_mat or mat, w=w,
         r=0.45, segs=2)


def poly_object(name, poly, depth, M, mat, *, bevel=0.0):
    """오목한 2D 다각형(엘프 로고 등)을 bmesh로 돌출한 오브젝트. 로컬 X-Z 평면, -Y 바깥, 두께 depth."""
    bm = bmesh.new()
    vs = [bm.verts.new(M @ V((x, 0.0, z))) for x, z in poly]
    f = bm.faces.new(vs)
    bm.normal_update()
    out = (M.to_3x3() @ V((0, -1, 0))).normalized()
    if f.normal.dot(out) < 0:
        f.normal_flip()
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    nv = [g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=nv, vec=out * depth)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    cb.collection().objects.link(ob)
    me.materials.append(mat)
    if bevel > 0:
        cb.add_bevel(ob, width=bevel, segments=1, angle=30.0)
    return ob


def elf_logo_badge(e, name, M, size, mat, *, depth=0.004, bone="head", group="head", tol=0.0045):
    """원작 엘프 로고(톱니 + 렌치 홈) 휘장 (ART_GUIDE 1장 엘프 로고 예외: 교주 차원 엘피니아 제식 휘장 자리).
    r41.elf_logo_outline()의 외곽선을 돌출한다. M 로컬: X-Z 평면, -Y 바깥. size = 높이(m)."""
    import r41  # noqa: WPS433 (로고 외곽선만 읽는다)
    pts = [(u * size, v * size) for u, v in r41.elf_logo_outline(tol)]
    ob = poly_object(f"{e.name}_{name}", pts, depth, M, mat)
    e.add(ob, bone=bone, group=group, tag=name)
    return ob


# =========================================================================== 별도 노드 소품

def prop(e, name, ob, bone, *, outline=0.003, merge=True):
    """소품(무기·지팡이·단말)을 따로 남긴 노드로 본에 강체로 붙인다. 머티리얼은 인물의 toon_vc로 합친다(UNLIT 제외).
    ob는 월드 위치에 놓인 오브젝트. three.js 노드 이름 = '<인물>_<name>'."""
    cb.apply_modifiers(ob)
    ob.name = f"{e.name}_{name}"
    if merge:
        vc = elf.vc_material(f"{e.name}_toon_vc", e.line)
        elf.bake_vcol(ob)
        elf.remap_to_vc(ob, vc)
        elf.collapse_slots(ob)
    ob["outline"] = outline
    ob["prop"] = name
    cb.parent_to_bone(ob, e.arm_obj, bone)
    return ob


def buf_object(name, buf, *, angle=40.0, smooth=True):
    return buf.obj(name, smooth=smooth, angle=angle)
