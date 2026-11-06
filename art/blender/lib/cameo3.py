"""원작 카메오 3차 공용 헬퍼 (cameo3).

네르(빡침), 하이디(그리고 시간이 되면 죠안)가 같이 쓴다. 키트(elf.py)와 1·2차 헬퍼(cameo.py, cameo2.py),
요정 헬퍼(fairy.py)는 읽기 전용이라 필요한 기능을 여기에 둔다. 근거와 인물별 사용처는
docs/art/characters-cameo3.md. [키트 후보] 표시는 키트로 올릴 만한 기능이다.

    cameo3.veil(e, h, white, navy, ...)          # 머리 덩어리를 덮는 베일·후드 (앞 트임 + 등 뒤로 늘어짐, 안감 색)
    cameo3.Braid3(e, "hair_braid_R", ctrl, root_bone="head", parent="chest", ...)   # 긴 땋은 머리 (뿌리는 머리, 사슬은 몸)
    cameo3.leaf_poly / gem_drop                  # 잎 모양 다각형, 위가 뾰족한 보석(딸기형)
    cameo3.socket_prop(e, ob, socket, Mw)        # 소품 노드를 소켓 자식으로 붙이고 월드 배치를 지정
    cameo3.ner_body/ner_face/ner_hair/ner_braid  # 네르 공용 몸·얼굴·머리·땋은 머리 (ner.py, ner_coronation.py)
"""
from __future__ import annotations

import math

import bpy

import cb
import elf
import cameo
import cameo2 as c2
import fairy
from elf import V, Matrix, Buf, loft, band, lerp, smoothstep, mixw, clamp, frame


# =========================================================================== 베일 (머리를 덮는 천)

def veil(e, h, outer, inner, *, el_front=44.0, az_open=74.0, az_full=104.0, z_side=None, z_back=None, lift=0.007,
         lift_lo=0.016, th=0.0035, cols=30, rows=12, front_dip=4.0, name="veil", rim=None, rim_w=0.006,
         pleat=None):
    """머리 덩어리(헤어 v2 셸) 바깥 면을 따라 덮는 베일·후드. [키트 후보: e.veil()]

    정수리부터 덮고, 앞(|az| < az_open)은 이마 위 el_front 높이(티아라 자리)에서 끝난다. 옆·뒤(|az| > az_full)는
    머리가 가장 넓은 곳 아래로 늘어져 z_side(옆)~z_back(등) 높이에서 끝난다. 그 사이는 얼굴 옆을 따라 내려오는
    트임 가장자리다. 바깥 면 outer, 안감 inner(가장자리 두께 면도 inner). h.path()를 쓰므로 셸을 만들기 전에도 된다.
    pleat=(진폭 m, 주름 수, 시작 u): 늘어진 아래쪽에 세로 주름 (뒤에서 볼 때 큰 흰 원판으로 읽히지 않게).
    웨이트: 머리 높이까지 head, 아래로 갈수록 chest로 섞는다(긴 머리 hair_back 사슬과 같은 쪽으로 움직임).
    반환: 가장자리 점 목록(앞 트임 가장자리, 티아라 배치용)."""
    k = e.k
    z_side = z_side if z_side is not None else e.shoulder_z + 0.010 * k
    z_back = z_back if z_back is not None else e.shoulder_z - 0.110 * k
    hc = e.head_c
    z_head = hc.z - 0.04 * k

    def s_at_z(az, z):
        """경도 az에서 높이 z까지 내려간 길이 (머리 아래면 수직 낙하)."""
        lo, hi = 0.0, 2.0 * k
        for _ in range(40):
            mid = (lo + hi) / 2
            if h.path(az, mid)[0].z > z:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    def s_end(az):
        a = abs(((az + 180.0) % 360.0) - 180.0)
        s_front = h.s_of_el(az, el_front - front_dip * (a / az_open) ** 2)
        zz = lerp(z_side, z_back, smoothstep(az_full, 180.0, a))
        s_low = s_at_z(az, zz)
        f = smoothstep(az_open, az_full, a)
        return lerp(s_front, s_low, f ** 0.8)

    def wfn(p):
        f = smoothstep(z_head, e.shoulder_z - 0.02 * k, p.z)
        return mixw({"head": 1.0}, {"neck": 0.25, "chest": 0.75}, 1.0 - f) if f < 1.0 else {"head": 1.0}

    buf = Buf()
    S = [s_end(360.0 * j / cols) for j in range(cols)]
    P, N = [], []
    for i in range(1, rows + 1):
        u = i / rows
        rp, rn = [], []
        for j in range(cols):
            az = 360.0 * j / cols
            s = S[j] * u
            fb = smoothstep(az_open, az_full + 20.0, abs(((az + 180) % 360) - 180))
            dv = (lift + (lift_lo - lift) * smoothstep(0.45, 1.0, u) * fb) * k
            if pleat:
                amp, nw, u0 = pleat
                dv += amp * k * smoothstep(u0, 1.0, u) * fb * (0.5 + 0.5 * math.cos(math.radians(az) * nw))
            p, n = h.path(az, s, dv)
            rp.append(p)
            rn.append(n)
        P.append(rp)
        N.append(rn)
    top, _ = h.path(0.0, 0.0, lift * k)
    ti_o = buf.vert(top, {"head": 1.0})
    ti_i = buf.vert(top - V((0, 0, th * k)), {"head": 1.0})
    o = [[buf.vert(P[i][j], wfn(P[i][j])) for j in range(cols)] for i in range(rows)]
    ii = [[buf.vert(P[i][j] - N[i][j] * th * k, wfn(P[i][j])) for j in range(cols)] for i in range(rows)]
    for j in range(cols):
        j2 = (j + 1) % cols
        buf.face((ti_o, o[0][j], o[0][j2]), outer)
        buf.face((ti_i, ii[0][j2], ii[0][j]), inner)
    for i in range(rows - 1):
        for j in range(cols):
            j2 = (j + 1) % cols
            buf.face((o[i][j], o[i + 1][j], o[i + 1][j2], o[i][j2]), outer)
            buf.face((ii[i][j], ii[i][j2], ii[i + 1][j2], ii[i + 1][j]), inner)
    R = rows - 1
    for j in range(cols):
        j2 = (j + 1) % cols
        buf.face((o[R][j], ii[R][j], ii[R][j2], o[R][j2]), inner)
    # 면 방향 정리 (바깥 = 머리에서 먼 쪽)
    ob = buf.obj(f"{e.name}_{name}", angle=50.0)
    _recalc_outward(ob)
    e.add(ob, group="head", tag=name)
    if rim is not None:
        pts = [P[R][j] for j in range(cols)]
        nrm = [N[R][j] for j in range(cols)]
        ups = []
        for j in range(cols):
            d = (P[R - 1][j] - P[R][j])
            d = (d - nrm[j] * d.dot(nrm[j]))
            ups.append(d.normalized() if d.length > 1e-9 else V((0, 0, 1)))
        e.part(f"{name}_rim", "head",
               lambda b: elf._loop(b, [p + u_ * rim_w * k * 0.5 for p, u_ in zip(pts, ups)], nrm, ups, rim_w * k,
                                   0.0018 * k, mat=rim, w=lambda t: wfn(pts[min(int(t * (cols - 1)), cols - 1)])))
    return [P[R][j] for j in range(cols)], [N[R][j] for j in range(cols)]


def _recalc_outward(ob):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


# =========================================================================== 긴 땋은 머리

class Braid3(cameo.Braid):
    """cameo.Braid + 뿌리 웨이트 본. root_bone='head', parent='chest'면 뿌리는 고개를 따라가고 아래는 몸에 붙은
    사슬을 따른다(바닥까지 오는 긴 땋은 머리가 고개를 돌려도 어깨·등에 남는다). cameo2.Tail(root_bone=)과 같은 규칙."""

    def __init__(self, e, name, ctrl, *, root_bone=None, root_t=0.12, **kw):
        self.root_bone, self.root_t = root_bone, root_t
        super().__init__(e, name, ctrl, **kw)

    def w_at(self, t):
        w = self.chain.weights(clamp(t, 0.0, 1.0))
        if self.root_bone:
            w = mixw({self.root_bone: 1.0}, w, smoothstep(0.0, self.root_t, t))
        return w


# =========================================================================== 작은 장식 도형

def leaf_poly(L, W, *, n=6, tip=1.0, base=0.18):
    """잎 모양 (뿌리 (0,0) → 끝 (0, L)), 폭 W. 반시계."""
    right, left = [], []
    for i in range(n + 1):
        t = i / n
        w = W / 2 * math.sin(math.pi * clamp(t * (1 - base) + base * 0.5)) ** 0.9 * (1 - 0.15 * t)
        z = L * t ** tip
        right.append((w, z))
        left.append((-w, z))
    pts = right + list(reversed(left[1:-1]))
    return pts


def drop_poly(r, *, n=10, point=1.55):
    """위가 뾰족한 보석(딸기형 물방울) 다각형, 중심 (0,0). 반시계."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2
        x, z = math.cos(a) * r, math.sin(a) * r
        if z > 0:
            x *= 1 - 0.55 * (z / r) ** 1.2
            z *= point
        pts.append((x, z))
    return pts


def gem_drop(buf, M, r, mat, *, depth=0.004, frame_mat=None, frame_w=0.0025, w=None):
    """딸기형 붉은 보석 (+ 테두리). M 로컬: X-Z 평면, -Y 바깥."""
    d0 = 0.0
    if frame_mat is not None:
        c2.prism(buf, drop_poly(r + frame_w), depth * 0.55, M, mat=frame_mat, w=w, chamfer=depth * 0.2)
        d0 = depth * 0.40
    c2.prism(buf, drop_poly(r), depth, M @ Matrix.Translation((0, -d0, 0)), mat=mat, w=w, chamfer=depth * 0.65)


# =========================================================================== 소품 노드를 소켓에

def socket_prop(e, ob, socket, Mw, *, name, outline=0.003, props=None):
    """로컬 좌표(무기 규약: 원점 = 파지점)로 만든 소품 ob를 '<인물>_<name>' 노드로 남기고 socket(빈 오브젝트)의 자식으로
    붙인다. Mw: 원하는 월드 배치. 런타임에서 다른 소켓으로 옮길 때는 로컬 변환을 0으로 두면 파지점이 손에 온다.
    머티리얼은 인물의 toon_vc로 합친다(UNLIT 제외)."""
    cb.apply_modifiers(ob)
    vc = elf.vc_material(f"{e.name}_toon_vc", e.line)
    elf.bake_vcol(ob)
    elf.remap_to_vc(ob, vc)
    elf.collapse_slots(ob)
    ob.name = f"{e.name}_{name}"
    ob["outline"] = outline
    ob["prop"] = name
    for kk, v in (props or {}).items():
        ob[kk] = v
    sock = bpy.data.objects[socket]
    ob.parent = sock
    ob.matrix_parent_inverse = Matrix.Identity(4)
    bpy.context.view_layer.update()
    ob.matrix_basis = sock.matrix_world.inverted() @ Mw
    return ob


# =========================================================================== 블록 글자 (완장·표식)

GLYPH5 = {
    "P": ["111", "101", "111", "100", "100"],
    "R": ["111", "101", "110", "101", "101"],
    "E": ["111", "100", "111", "100", "111"],
    "S": ["111", "100", "111", "001", "111"],
    "T": ["111", "010", "010", "010", "010"],
    "V": ["101", "101", "101", "101", "010"],
}


def box12(buf, size, M, mat, w=None):
    """가장 싼 상자 (삼각형 12개). M 로컬 중심, size=(x, y, z)."""
    sx, sy, sz = (s / 2 for s in size)
    vs = [buf.vert(M @ V((x * sx, y * sy, z * sz)), w) for z in (-1, 1) for y in (-1, 1) for x in (-1, 1)]
    for f in ((0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)):
        buf.face(tuple(vs[i] for i in f), mat)


def block_word(buf, word, M, cell, depth, mat, w=None):
    """3×5 칸 블록 글자 한 줄 (가로로 이어진 칸은 상자 하나로 합친다). M 로컬: +X = 글자 진행, +Z = 위, -Y = 바깥.
    원작 로고·글꼴이 아니라 기하 칸 글자다 (예: 종군기자 완장 'PRESS')."""
    width = len(word) * 4 - 1
    for li, ch in enumerate(word):
        rows = GLYPH5.get(ch.upper())
        if not rows:
            continue
        for r, row in enumerate(rows):
            c = 0
            while c < 3:
                if row[c] != "1":
                    c += 1
                    continue
                c0 = c
                while c < 3 and row[c] == "1":
                    c += 1
                n = c - c0
                x = ((li * 4 + c0 + (n - 1) / 2) - (width - 1) / 2) * cell
                z = (2 - r) * cell
                box12(buf, (cell * (n + 0.05), depth, cell * 1.05), M @ Matrix.Translation((x, -depth / 2, z)), mat, w)


# =========================================================================== 사슬

def chain(buf, ctrl, link, wire, mat, *, w=None, mat2=None, every=3, segs=6, ring=4, width=0.62, n=None):
    """경로를 따라 이어진 사슬 고리 (고리마다 90° 엇갈림). ctrl: 제어점(월드), link: 고리 길이(m), wire: 철사 반경(m).
    w: 웨이트 사전 또는 t(0~1) → 사전. mat2를 주면 every개마다 그 재질 고리(금·은 섞인 사슬).
    고리 하나 = segs × ring × 2 삼각형."""
    pts = elf.catmull([V(p) for p in ctrl], 96)
    cum = [0.0]
    for a_, b_ in zip(pts, pts[1:]):
        cum.append(cum[-1] + (b_ - a_).length)
    L = cum[-1]
    step = link * 0.78
    count = n or max(1, int(L / step))

    def at(s):
        for i in range(len(cum) - 1):
            if s <= cum[i + 1] or i == len(cum) - 2:
                d = cum[i + 1] - cum[i]
                a = (s - cum[i]) / d if d > 1e-9 else 0.0
                return pts[i].lerp(pts[i + 1], clamp(a)), (pts[i + 1] - pts[i]).normalized()
        return pts[-1], (pts[-1] - pts[-2]).normalized()

    up0 = V((0, 0, 1))
    for li in range(count):
        s = (li + 0.5) * L / count
        c, T = at(s)
        ref = up0 if abs(T.dot(up0)) < 0.9 else V((1, 0, 0))
        A = (ref - T * ref.dot(T)).normalized()
        B = T.cross(A).normalized()
        if li % 2:
            A, B = B, A
        ww = w(s / L) if callable(w) else (w or {})
        m = mat2 if (mat2 is not None and li % every == 0) else mat
        hl, hw = link / 2 - wire, link * width / 2 - wire
        rows = []
        for i in range(segs):
            th = 2 * math.pi * i / segs
            cc = c + T * (hl * math.cos(th)) + A * (hw * math.sin(th))
            rad = (T * (math.cos(th) / max(hl, 1e-6)) + A * (math.sin(th) / max(hw, 1e-6))).normalized()
            row = []
            for j in range(ring):
                ph = 2 * math.pi * j / ring
                row.append(buf.vert(cc + rad * (wire * math.cos(ph)) + B * (wire * math.sin(ph)), ww))
            rows.append(row)
        for i in range(segs):
            i2 = (i + 1) % segs
            for j in range(ring):
                j2 = (j + 1) % ring
                buf.face((rows[i][j], rows[i2][j], rows[i2][j2], rows[i][j2]), m)


# =========================================================================== 곱슬 장발 (헤어 v2 확장)

class CurlyHair(c2.Hair2):
    """풍성한 곱슬 장발: 머리가 가장 넓은 곳 아래로 떨어지는 구간에 짧은 물결을 넣는다. 물결 위상이 경도마다 크게
    달라 이웃 다발끼리 굽이가 엇갈려 곱슬로 읽힌다. 셸·속층·덧다발이 모두 path()를 쓰므로 같은 물결을 따른다.
    (마카샤 WavyHair와 같은 원리, 파장을 줄이고 위상 차를 키웠다.) wave=(진폭, 파장, 시작 거리[, 키우는 구간]) m.
    q_shell: 길이 방향 행을 촘촘하게 하는 배율(물결 해상도). [키트 후보: Hair(wave=)]"""

    def __init__(self, e, color, *, wave=(0.020, 0.110, 0.03), q_shell=1.25, **kw):
        super().__init__(e, color, **kw)
        self.wave = wave
        self.q_shell = q_shell

    def _shell(self):
        q0 = self.e.q
        self.e.q = self.q_shell
        try:
            return super()._shell()
        finally:
            self.e.q = q0

    def _eval(self, L, s):
        p, n = super()._eval(L, s)
        if s > L["sb"]:
            amp, lam, d0 = self.wave[:3]
            ramp = self.wave[3] if len(self.wave) > 3 else 0.10
            d = s - L["sb"]
            az = math.atan2(L["rad"].x, -L["rad"].y)
            ph = 1.7 * math.sin(az * 3.0) + 3.0 * az     # 정수배라야 뒤 가운데(az=±π)에서 위상이 이어진다
            f = smoothstep(d0 * self.k, (d0 + ramp) * self.k, d)
            w = 2 * math.pi * d / (lam * self.k) + ph
            tan = V((-L["rad"].y, L["rad"].x, 0.0))
            p = p + L["rad"] * (amp * self.k * f * (0.6 + 0.4 * math.sin(w))) + tan * (0.35 * amp * self.k * f *
                                                                                   math.cos(w))
        return p, n


def curly_hair(e, color, **kw):
    h = CurlyHair(e, color, **kw)
    e._hairs = getattr(e, "_hairs", []) + [h]
    return h


def ringlet(h, prefix, top, out, *, length=0.16, radius=0.020, turns=2.2, width=0.040, thick=None, bones=2,
            parent="chest", n=24, segs=8, mat=None, twist=1):
    """나선 컬 다발(링렛): top(월드)에서 시작해 out(바깥 방향) 쪽으로 반경만큼 비켜 선 축을 감으며 아래로 내려간다.
    cameo2.Tail(본 사슬, 끝에서 모임)로 만든다. twist=±1 감는 방향."""
    k = h.e.k
    out = V(out)
    out = V((out.x, out.y, 0.0)).normalized()
    side = V((0, 0, 1)).cross(out).normalized()
    ax = V(top) + out * (radius * k)
    ctrl = []
    m = max(8, int(turns * 8))
    for i in range(m + 1):
        t = i / m
        a = 2 * math.pi * turns * t * twist + math.pi
        r = radius * k * (1.0 - 0.25 * t)
        ctrl.append(ax + out * (math.cos(a) * r) + side * (math.sin(a) * r) - V((0, 0, length * k * t)))
    ctrl[0] = V(top)
    return c2.Tail(h, prefix, ctrl, width * k, (thick or width * 0.8) * k, bones=bones, parent=parent, t_hold=0.78,
                   root_w=0.85, clumps=(), segs=segs, n=n, mat=mat)


# =========================================================================== 네르 공용 (ner.py, ner_coronation.py)
# 전투 판(네르(빡침))과 대관식 판(왕관의 수여자)이 같은 사람으로 읽히도록 몸·얼굴·머리·땋은 머리를 같이 쓴다.

NER_HAIR, NER_HAIR_D, NER_HAIR_L = "#f3d99b", "#d8ad6c", "#fff4d8"


def ner_body(name, **kw):
    """네르 몸: 요정(귀는 머리에 가려 만들지 않음), 키 1.26. 가슴 볼륨 bust 0.50 (공식 설정표 '중', characters-cameo3.md '체형')."""
    prm = dict(ears=None, height=1.26, head=0.45, leg=1.04, chest=0.42, bust=0.50, hips=1.04, segs=0.62, hand_q=0.40, cheek=0.10)
    prm.update(kw)
    return fairy.Fairy(name, **prm)


def ner_face(e, expr=None, *, blush="#f6a2a6", blush_size=1.12):
    """네르 얼굴: 남보라빛 파란 눈(아래가 밝음), 반쯤 감긴 엄한 눈매, 옅은 금색 눈썹.
    표정: 키트 5종 + rage, glare, teary, smug(+ expr로 판마다 더하는 표정) + blink 교정 키."""
    k = e.k
    ex = {
        # 빡침: 치켜뜬 눈, 작은 동공, 세게 내린 눈썹, 크게 벌린 입 (원작 '당장 열지 못해?!')
        "rage": {"eye": {"top": 0.034, "ktop": 2.4, "tilt_in": -0.012, "bot": 0.056},
                 "iris": {"pupil": 0.55, "rx": 0.026, "ry": 0.032},
                 "brow": {"ang": -30.0, "dz": 0.050, "th": 0.0078},
                 "mouth": {"w": 0.046, "open": 0.046, "curve": -0.0030, "top_arch": 0.008}},
        # 심판: 가늘게 뜬 차가운 눈, 다문 입 (카드 스탠딩의 표정을 더 차갑게)
        "glare": {"eye": {"top": 0.0085, "ktop": 6.0, "tilt_in": -0.012},
                  "brow": {"ang": -16.0, "dz": 0.056},
                  "mouth": {"w": 0.016, "curve": -0.0025}},
        # 울먹: 눈썹이 안쪽으로 올라가고 입이 물결 (분노 뒤의 여린 심성)
        "teary": {"eye": {"top": 0.030, "lift": 0.012, "tilt_in": 0.010, "ktop": 2.6},
                  "iris": {"pupil": 0.85},
                  "brow": {"ang": 20.0, "dz": 0.070, "arch": -0.002},
                  "mouth": {"w": 0.024, "curve": -0.0050, "open": 0.0060, "wave": 0.0020}},
    }
    # 2026-11-04 사용자 「영상 피드에서 네르 표정이 왜이렇게 우스꽝스럽게 나오는데?」: 원작 네르는 반쯤 감긴 차분한 눈매다.
    # 조용한 격노·결의·사나운 외침은 rage(동그랗게 뜬 눈과 o 입)가 아니라 아래 셋으로 쓴다
    ex.update({
        # 조용한 격노: 반쯤 감긴 눈을 더 내리깔고 눈썹 안쪽을 세게 내림, 꽉 다문 입
        "fury": {"eye": {"top": 0.0095, "ktop": 6.2, "tilt_in": -0.016, "cin": 0.004},
                 "iris": {"pupil": 0.88},
                 "brow": {"ang": -24.0, "dz": 0.050, "th": 0.0076, "arch": 0.0},
                 "mouth": {"w": 0.016, "curve": -0.0032}},
        # 결의: 조금 더 뜬 곧은 눈, 살짝 찌푸린 눈썹, 다문 입 (교주를 올려다보는 물음)
        "resolve": {"eye": {"top": 0.020, "ktop": 4.4, "tilt_in": -0.008},
                    "brow": {"ang": -12.0, "dz": 0.058, "arch": 0.001},
                    "mouth": {"w": 0.015, "curve": -0.0012}},
        # 사나운 외침: 가늘게 치뜬 눈, 세게 내린 눈썹, 옆으로 넓게 벌린 입 (둥근 o가 아니다)
        "shout": {"eye": {"top": 0.012, "ktop": 5.6, "tilt_in": -0.020, "bot": 0.050},
                  "iris": {"pupil": 0.8},
                  "brow": {"ang": -30.0, "dz": 0.047, "th": 0.0080},
                  "mouth": {"w": 0.052, "open": 0.024, "curve": -0.0065, "top_arch": -0.0045}},
    })
    ex.update(expr or {})
    ob = fairy.face(e, eye_color="#7f93db", iris_dark="#4a4f9c", iris_light="#c9d6ff", pupil="#353a78",
                    lash="#5a3a34", brow="#c99a5e", brow_th=0.95, blush=blush, blush_size=blush_size,
                    base={"eye": {"top": 0.0125, "ktop": 5.6, "tilt_in": -0.002, "tilt_out": 0.001, "cout": 0.017},
                          "brow": {"ang": -6.0, "dz": 0.064, "arch": 0.001},
                          "mouth": {"w": 0.014, "curve": -0.0006}},
                    expr=ex)
    c2.face_expr(e, "smug",
                 both={"eye": {"top": 0.017, "lift": 0.008, "ktop": 4.6}, "mouth": {"w": 0.026, "curve": 0.0030}},
                 L={"brow": {"dz": 0.066, "ang": 0.0, "arch": 0.003}}, R={"brow": {"dz": 0.056, "ang": -14.0}},
                 corner=(0.0080, -0.0010), mouth_dx=0.0020 * k)
    return ob


def _ner_soft_bangs(h, lk):
    """앞머리 끝을 뭉툭하게(삐죽한 톱니 대신 원작의 부드러운 다발 끝), 갈라짐은 짧게."""
    if lk["region"] == "front":
        lk["p"] = 2.1
        lk["free"] *= 0.62


def ner_hair(e):
    """네르 머리 (헤어 v2): 바닥까지 오는 금발, 일자에 가까운 앞머리, 가슴까지 오는 옆머리. 광택(h.shine)은 부른 쪽에서."""
    h = fairy.hair(e, NER_HAIR, dark=NER_HAIR_D, light=NER_HAIR_L, volume=1.12,
                   lock_fn=fairy.lock_edit(_ner_soft_bangs))
    h.cap(front=30, side=-6, back=-46, part=0, segs=15, rows=5)
    h.bangs(n=8, spread=56, tip_el=-4, sweep=0, part=0, jag=0.12, curl=1.0, seed=3.0)
    h.sides(length=0.40, width=0.078, az=60, curl=0.5, thick=1.1)
    h.back(length=0.62, n=7, spread=98)
    return h


def ner_braid(e, h, silver, red, *, ribbon=None):
    """굵은 땋은 머리: 캐릭터 오른쪽(-X) 귀 뒤에서 팔 뒤로 바닥까지, 끝이 바깥으로 말리고 은색 꽃 장식 + 붉은 보석.
    본 hair_braid_R_01..03 (chest 자식, 뿌리 head 웨이트). ribbon=(재질, 재질2)면 묶은 자리에 리본(대관식 판)."""
    k = e.k
    sz = e.shoulder_z
    ctrl = [h.sp(-112, -4, h.off * 0.2), h.sp(-122, -28, h.off * 0.95),
            V((-0.196 * k, 0.120 * k, e.torso_top + 0.010 * k)), V((-0.222 * k, 0.130 * k, sz - 0.120 * k)),
            V((-0.250 * k, 0.140 * k, 0.360 * k)), V((-0.262 * k, 0.110 * k, 0.150 * k)),
            V((-0.300 * k, 0.050 * k, 0.060 * k)), V((-0.360 * k, 0.020 * k, 0.085 * k))]
    braid_m = elf.mat(f"{e.name[:2]}_braid" if e.name != "ner" else "ne_braid", NER_HAIR)
    br = Braid3(e, "hair_braid_R", ctrl, w0=0.078 * k, w1=0.050 * k, lobes=14, tilt=28, face=(-0.55, 0.84, 0.0),
                mat=braid_m, bones=3, parent="chest", root_bone="head", root_t=0.10, tie=silver, tie_at=0.92,
                tuft=0.040 * k, segs=7, rings=5)
    br.done()

    def braid_ornament(buf):
        c, T, F = br.tip_c, br.tip_T, br.tip_F
        w = br.w_at(0.92)
        Mx = Matrix.Translation(c + F * 0.020 * k) @ frame(F, -T)
        for i in range(5):
            Ml = Mx @ Matrix.Rotation(math.radians(72.0 * i), 4, "Y")
            c2.prism(buf, [(x * k, z * k) for x, z in leaf_poly(0.022, 0.014, n=4)], 0.004 * k, Ml, mat=silver,
                     w=w)
        gem_drop(buf, Mx @ Matrix.Translation((0, -0.004 * k, 0.0)), 0.008 * k, red, depth=0.005 * k, w=w)
        if ribbon is not None:
            # 묶은 자리 위 리본 (원작 대관식 판: 땋은 머리의 연두·흰 줄무늬 리본)
            Mr = Matrix.Translation(c - T * 0.030 * k + F * 0.022 * k) @ frame(F, -T)
            c2.bow_geo(buf, Mr, 0.060 * k, ribbon[0], w=w, tails=1.0, knot_mat=ribbon[1], segs=6)

    e.part("braid_ornament", "head", braid_ornament)
    return br
