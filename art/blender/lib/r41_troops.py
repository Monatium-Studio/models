"""R41 침공군 병력 공용 모듈 (r41_troops).

엘프 키트(elf.py) 위에 R41 군복·장비를 입힌다. 병종 스크립트는 art/blender/enemies/*.py.
설정·팔레트·근거: docs/art/enemies-r41.md, docs/art/r41-style.md 7장 (PV 3:00~3:03, 4:59~5:07)

    import os, sys
    sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
    import cb, r41_troops as T
    cb.reset()
    t = T.Trooper("r41_rifleman_a", variant=T.VARIANTS["a"])   # 몸 + 얼굴(표정 9종) + 머리카락
    t.uniform()                                                # 엘피니아 계보 전투복 (R41 회색)
    t.beret(); t.goggles("down"); t.headset()                  # PV 베레모 + 연기색 고글 + 헤드셋
    t.shoulder_insignia()                                      # 어깨 짙은 패치 + 앰버 원형 휘장 + 엘프 로고
    ...
    t.export("enemies/r41_rifleman_a.glb")

규칙
  - 키트 finalize(merge=True): 불투명 색은 정점색 하나로 합친다. 연기색 고글 렌즈만 반투명 머티리얼로 남는다.
    → 메시 6개(body/arms/head/hair/hair_in/face), 프리미티브 8개.
  - 무기는 넣지 않는다. socket_hand_R(주무기), socket_hand_L(방패 등), socket_hip_R(권총)에 붙인다.
  - 엘프 로고(ART_GUIDE 1장 예외)는 r41.elf_logo_outline()을 그대로 쓴 한 면짜리 데칼이다.
"""
from __future__ import annotations

import math
import os
import sys
import types

from mathutils import Matrix, Vector  # noqa: F401 (병종 스크립트가 T.Matrix로 쓴다)
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb  # noqa: E402
import elf  # noqa: E402
import r41  # noqa: E402
import cameo  # noqa: E402  (Tail: 낮게 묶은 꼬리머리)

V = Vector
lerp = elf.lerp
smoothstep = elf.smoothstep
keys = elf.keys

# =========================================================================== palette
# r41.PAL의 군복 값(PV 3:00~3:03, 4:59~5:07)을 그대로 쓰고, 병력 모델에 필요한 단계만 더했다.
# 바꾸면 docs/art/enemies-r41.md 팔레트 표도 같이 바꾼다.
PAL = {
    "uniform": r41.PAL["uniform"],            # #9e9aa1 회갈색이 섞인 밝은 회색 전투복
    "uniform_d": "#86828b",                   # 여밈·덮개·주머니 (한 단계 어둡게)
    "uniform_light": r41.PAL["uniform_light"],  # #c6c2c8 소맷단·셔츠 깃
    "pants": "#8b8790",                       # 하의 (엘피니아 계보: 상의보다 한 톤 어둡게)
    "pants_d": "#7b7781",
    "dark": r41.PAL["uniform_dark"],          # #3b3940 조끼 끈, 장갑, 헤드셋, 어깨 패치
    "dark2": "#4a4750",                       # 웨빙 2단 (파우치 몸통)
    "shell": r41.PAL["shell"],                # #2a2733 탄입대, 판 조끼, 정모
    "metal": r41.PAL["metal"],                # #4d4959 금속 부품
    "steel": r41.PAL["steel"],                # #aab0bd 버클, 단추 (엘피니아 계보의 은색 버클)
    # 머리 장비: R41은 헬멧이 아니라 베레모다 (PV 3:00~3:03 재확인, 2026-11-01 사용자 정정)
    "beret_grey": r41.PAL["helmet"],          # #b9b6bf 소총병 베레모 (PV의 밝은 회색 크라운)
    "beret_band": "#5f5b67",                  # 베레모 머리띠 (PV: 크라운보다 짙은 회색 + 골 줄)
    "beret_riot": r41.PAL["beret"],           # #7b7596 진압반 베레모 (타이다(R41) 근무모 색)
    "beret_dark": "#45424d",                  # 돌격 편대 베레모 (짙은 회색)
    "beret_black": "#26232e",                 # 지휘관 베레모 (제국 흑에 가깝게)
    "frame": "#cfccd5",                       # 고글 테 (PV: 밝은 회색)
    "frame_d": "#9d9aa5",                     # 헤드셋 덮개, 판 표식
    "visor": r41.PAL["visor"],                # #4f4c58 연기색 고글 렌즈 (반투명)
    "amber": r41.PAL["amber"],                # #f09a3e 어깨 휘장, 진압반 띠, 계급 줄
    "amber_d": "#c97a2e",                     # 앰버 그림자 단 (코드, 테)
    "ceramic": r41.PAL["ceramic"],            # #ddd9e6 지휘관 코트, 경호대 망토, 돌격 편대 판
    "ceramic_d": "#bdb8c9",
    "beret": r41.PAL["beret"],                # #7b7596 진압반 근무모
    "boots": "#45424b",
    "sole": r41.PAL["rubber"],                # #1c1a22
    "glow_dim": r41.PAL["glow_dim"],          # #a070ff 지휘관 태블릿 화면 (UNLIT)
}

# 원작 PV의 연기색 고글은 반투명 렌즈로 해석한다 (눈과 표정이 비친다). 알파는 아래 값.
VISOR_ALPHA = 0.64


def mats() -> dict:
    """병력 머티리얼 세트 (툰, 정점색으로 합쳐짐). 렌즈는 반투명, 화면은 UNLIT."""
    M = {k: elf.mat(f"r41t_{k}", v) for k, v in PAL.items() if k not in ("visor", "glow_dim")}
    M["visor"] = cb.mat("r41t_visor", PAL["visor"], alpha=VISOR_ALPHA, roughness=0.2)
    M["visor_amber"] = cb.mat("r41t_visor_amber", "#e08a3a", alpha=0.58, roughness=0.2)
    M["lens_hl"] = elf.mat("r41t_lens_hl", "#eceaf2")
    M["screen"] = cb.mat("r41t_screen", PAL["glow_dim"], emission=PAL["glow_dim"], unlit=True)
    return M


# =========================================================================== face variants & expressions
# 적이므로 기본은 무표정. 경계·분노·놀람(키트)·동요·겁먹음(투항 장면)을 더한다.
# 모든 표정에 blink_<표정> 교정 키가 자동으로 생긴다 (런타임: blink_<표정> = blink × <표정>).
EXPR = {
    # 경계: 눈을 조금 가늘게, 눈썹을 평평하게 내림, 입 다묾
    "alert": {"eye": {"top": 0.023, "ktop": 3.4, "tilt_in": -0.007, "bot": 0.052},
              "iris": {"pupil": 0.86},
              "brow": {"ang": -10.0, "dz": 0.055, "arch": 0.0, "th": 0.0070},
              "mouth": {"w": 0.016, "curve": -0.0006}},
    # 분노: 눈썹 V, 눈 안쪽을 깎음, 소리치는 입
    "angry": {"eye": {"top": 0.020, "tilt_in": -0.016, "ktop": 3.8, "bot": 0.048, "cin": 0.004},
              "iris": {"pupil": 0.82},
              "brow": {"ang": -26.0, "dz": 0.050, "th": 0.0082, "arch": -0.002},
              "mouth": {"w": 0.032, "curve": -0.0068, "open": 0.017, "top_arch": 0.003}},
    # 동요: 걱정 눈썹, 동공 축소, 떨리는 입 (중성자탄 사건 뒤 돌격 편대)
    "shaken": {"eye": {"top": 0.033, "tilt_in": 0.008, "tilt_out": -0.004, "ktop": 2.6, "bot": 0.056},
               "iris": {"pupil": 0.66, "cz": 0.006},
               "brow": {"ang": 17.0, "dz": 0.071, "arch": 0.0},
               "mouth": {"w": 0.020, "curve": -0.0032, "open": 0.0045, "wave": 0.0019}},
    # 겁먹음: 눈이 커지고 흰자가 보임, 눈썹 /\ 크게, 벌린 물결 입
    "scared": {"eye": {"top": 0.040, "bot": 0.060, "ktop": 2.0, "kbot": 2.0, "tilt_in": 0.010},
               "iris": {"pupil": 0.50, "rx": 0.0240, "ry": 0.031, "cz": 0.0},
               "brow": {"ang": 24.0, "dz": 0.080, "arch": -0.003, "th": 0.0066},
               "mouth": {"w": 0.028, "open": 0.016, "curve": -0.0050, "wave": 0.0026, "top_arch": 0.002}},
}

# 얼굴 변형: 소총병은 이 표에서 골라 쓴다 (눈색, 머리색, 머리 모양). docs/art/enemies-r41.md 3장.
VARIANTS = {
    # a: PV 대열(4:59~5:07)의 짙은 단발
    "a": dict(eye="#5f7aa8", hair="#4a3a3c", style="bob", goggles="down"),
    # b: PV 클로즈업(3:00~3:03)의 밝은 갈색 머리, 낮게 묶은 꼬리
    "b": dict(eye="#a8743a", hair="#c39f78", style="pony", goggles="down"),
    # c: 구릿빛 숏컷, 고글을 헬멧에 올림 (얼굴이 다 보이는 변형)
    "c": dict(eye="#5f8a6e", hair="#9c5a3c", style="short", goggles="up"),
}


# =========================================================================== small geometry helpers

def logo(buf, M, size, mat, w, *, lift=0.0, tol=0.0045):
    """원작 엘프 로고 데칼 (한 면 n각형). M 로컬: +X 옆, -Y 바깥, +Z 위. size = 높이(m)."""
    pts = r41.elf_logo_outline(tol)
    idx = [buf.vert(M @ V((u * size, -lift, v * size)), w) for u, v in pts]
    buf.face(tuple(idx), mat)


def flat_quad(buf, M, w, h, mat, wt):
    """한 면 사각 데칼 (로컬 XZ, -Y 바깥)."""
    idx = [buf.vert(M @ V((x * w / 2, 0.0, z * h / 2)), wt) for x, z in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    buf.face(tuple(idx), mat)


def ribbon(buf, pts, nrm, ups, width, mat, w):
    """두께 없는 띠 (골 줄, 렌즈 반사). ups가 None이면 진행 방향 × 법선."""
    n = len(pts)
    if ups is None:
        ups = []
        for i in range(n):
            t = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
            ups.append(nrm[i].cross(t).normalized())     # 면 법선 = 진행 × 위 = 바깥
    L = [buf.vert(p + u * width / 2, w) for p, u in zip(pts, ups)]
    R = [buf.vert(p - u * width / 2, w) for p, u in zip(pts, ups)]
    for i in range(n - 1):
        buf.face((R[i], R[i + 1], L[i + 1], L[i]), mat)


def hex_plate(buf, M, r, th, mat, w, *, rot=30.0, sy=1.0):
    """육각 판 (로컬 XZ 평면, -Y 바깥). r = 외접원 반지름. sy = 세로 배율."""
    n = 6
    front, back = [], []
    for i in range(n):
        a = math.radians(rot + 60 * i)
        x, z = math.cos(a) * r, math.sin(a) * r * sy
        front.append(buf.vert(M @ V((x, -th, z)), w))
        back.append(buf.vert(M @ V((x, 0.0, z)), w))
    buf.face(tuple(front), mat)
    buf.face(tuple(reversed(back)), mat)
    for i in range(n):
        j = (i + 1) % n
        buf.face((back[i], back[j], front[j], front[i]), mat)


def ngon_disc(buf, M, r, th, mat, w, n=12):
    """로컬 XZ 원판 (-Y 바깥). elf.disc보다 정점 수를 고르기 쉽다."""
    c = M.to_translation()
    nrm = (M.to_3x3() @ V((0, -1, 0))).normalized()
    up = M.to_3x3() @ V((0, 0, 1))
    elf.disc(buf, c, nrm, up, r, r, th, segs=n, mat=mat, w=w)


def tube_path(buf, pts, r, mat, w, *, segs=6, cap0="round", cap1="round"):
    """점 경로를 따라가는 가는 관 (코드, 붐 마이크, 안테나)."""
    st = [{"c": p, "rx": r, "ry": r, "w": w(i / max(len(pts) - 1, 1)) if callable(w) else w} for i, p in enumerate(pts)]
    elf.loft(buf, st, segs=segs, cap0=cap0, cap1=cap1, mat=mat, cap_len0=r * 0.8, cap_len1=r * 0.8, cap_rings=2)


# =========================================================================== trooper

def _layered_squash(h, off, rim_el, margin=0.7, bufs=None):
    """키트 Hair.squash 대체 (모자 아래): 키트는 바깥 셸과 속층을 같은 거리로 눌러서 두 면이 겹치고, 어두운 속층이
    바깥 셸 사이로 비쳐 머리띠 아래에 검은 점선이 생긴다. 바깥 셸은 키트 그대로 누르고, 속층은 4 mm 더 안쪽으로
    누른다. [키트 버그 보고: Hair.squash가 buf와 buf_in을 같은 cap 거리로 누름]"""
    elf.Hair.squash(h, off, rim_el, margin, bufs=(h.buf,))
    elf.Hair.squash(h, off - 0.004 * h.k, rim_el, margin, bufs=(h.buf_in,))


class Trooper:
    """R41 병사 한 명. 엘프 키트 위에 PV 근거 군복과 장비를 입힌다.

    variant: VARIANTS 항목 또는 같은 키를 가진 사전 (eye, hair, style, goggles).
    body: elf.Elf 인자 덮어쓰기 (height, shoulders, limb ...). 단역 기본 segs=0.65, hand_q=0.6 (헤어 v2 셸이 v1보다 무거워 0.7에서 낮췄다).
    face: e.face 인자 덮어쓰기 (base, eye_size ...).
    """

    def __init__(self, name, *, variant=None, body=None, face=None, hair_kw=None, segs=0.65, hand_q=0.6):
        self.name = name
        self.v = dict(VARIANTS["a"])
        if variant:
            self.v.update(variant)
        kw = dict(segs=segs, hand_q=hand_q)
        kw.update(body or {})
        self.e = elf.Elf(name, **kw)
        self.k = self.e.k
        self.M = mats()
        hair_c = self.v["hair"]
        fkw = dict(eye_color=self.v["eye"], lash=elf.mix_hex(elf.shade(hair_c, -0.55), "#2a1a20", 0.5),
                   brow=elf.shade(hair_c, -0.35), blush_size=0.92, expr=EXPR)
        fkw.update(face or {})
        self.e.face(**fkw)
        self.hair_kw = hair_kw or {}
        self._goggle_mode = None

    # ------------------------------------------------------------------ hair
    def hair(self, style=None, **kw):
        """베레모 아래 머리카락 (헤어 v2). style: bob | pony | short | long | bun.
        머리띠 위는 키트 squash가 두피 쪽으로 눌러 넣는다(_layered_squash로 속층을 한 겹 더 깊게).
        베레모가 정수리를 덮으므로 셸은 성글게(cap 해상도 힌트) 한다. 테 아래로 보이는 띠만 중요하다."""
        e, k = self.e, self.k
        style = style or self.v["style"]
        o = dict(self.hair_kw)
        if self.v.get("goggles") == "down":
            o.setdefault("tip_el", -2)     # 고글을 내리면 앞머리가 고글 테까지 (PV 3:00 클로즈업)
        o.update(kw)
        h = e.hair(self.v["hair"])
        # 키트가 속층을 더 깊이 누르도록 고쳐진 뒤(c2ade49)에는 키트 squash를 그대로 쓴다.
        # 이전 키트(skip 인자 없음)에서만 대체 함수를 쓴다.
        if 'skip' not in elf.Hair.squash.__code__.co_varnames:
            h.squash = types.MethodType(_layered_squash, h)
        h.cap(front=o.get("front", 30), side=-10, back=-52, part=o.get("part", 0), segs=o.get("cap_segs", 16),
              rows=o.get("cap_rows", 4))
        if style == "short":
            h.bangs(n=5, spread=50, tip_el=o.get("tip_el", 10), sweep=o.get("sweep", 14), part=12, jag=0.4)
            h.sides(length=0.0, width=0.058)
            h.back(length=0.0, n=5, spread=80)
        elif style == "pony":
            h.bangs(n=5, spread=52, tip_el=o.get("tip_el", 6), sweep=-6)
            h.sides(length=0.03, width=0.062)
            h.back(length=0.01, n=5, spread=84)
            self._pony = dict(el=o.get("tail_h", -30), length=o.get("tail_len", 0.20))
        elif style == "long":
            h.bangs(n=5, spread=52, tip_el=o.get("tip_el", 4), sweep=o.get("sweep", 8), part=o.get("part", -10))
            h.sides(length=o.get("side_len", 0.09), width=0.066)
            h.back(length=o.get("back_len", 0.16), n=5, spread=86)
        elif style == "bun":
            h.bangs(n=5, spread=52, tip_el=o.get("tip_el", 8))
            h.sides(length=0.0, width=0.06)
            h.back(length=0.0, n=5, spread=84)
            h.bun(az=180, el=-38, size=0.07)
        else:  # bob
            h.bangs(n=5, spread=52, tip_el=o.get("tip_el", 6))
            h.sides(length=0.025, width=0.064)
            h.back(length=0.02, n=5, spread=86)
        self.h = h
        self._hair_bvh = None
        if style == "pony":
            self._pony_tail()
        return h

    def _pony_tail(self):
        """PV 3:02 밝은 갈색 꼬리머리: 목덜미 위(뒤에서 약 -30°)에서 묶어 등 위로 늘어진다. cameo.Tail(본 3개)."""
        e, h, k, M = self.e, self.h, self.k, self.M
        el, L = self._pony["el"], self._pony["length"]
        base, nb = h.path(180.0, h.s_of_el(180.0, el))
        hc = e.head_c
        ctrl = [base - nb * 0.024 * k, base + nb * 0.012 * k,
                base + nb * 0.034 * k + V((0, 0, -0.030)) * k,
                V((0.0, base.y + 0.030 * k, base.z - L * 0.40 * k)),
                V((0.008 * k, base.y + 0.012 * k, base.z - L * 0.75 * k)),
                V((0.016 * k, base.y - 0.004 * k, base.z - L * k))]
        _ = hc
        tl = cameo.Tail(e, h, "hair_tail", ctrl, width=0.078 * k, thick=0.058 * k, lat=(1, 0, 0), bones=3,
                        tie_at=0.06, root=0.78, puff=0.24, hold=0.50, body_end=0.88, ends=2, split=0.66, spread=0.5,
                        end_w=0.55, end_len=(1.0, 0.92), tie=None, n=14, segs=8)
        tl.done()

    # ------------------------------------------------------------------ 머리카락 위 표면
    def lift(self, az, el, extra=0.0, min_off=0.0):
        """(az, el)에서 머리카락 바깥 면(없으면 두피) 위로 extra만큼 띄운 점과 두피 법선.
        헤드셋·고글 끈이 옆머리에 묻히지 않게 할 때 쓴다. 처음 부를 때 머리카락을 완성한다(h.done(),
        베레모 squash 포함). 그래서 beret() 뒤에 부른다."""
        e = self.e
        if self._hair_bvh is None:
            self.h.done()
            hb = self.h.buf
            self._hair_bvh = BVHTree.FromPolygons([tuple(v) for v in hb.v], [tuple(f) for f in hb.f])
        sp, n = e.head_point(az, el, 0.0)
        hit = self._hair_bvh.ray_cast(sp + n * 0.25, -n)
        d = 0.0
        if hit[0] is not None:
            d = max(0.0, (hit[0] - sp).dot(n))
        return sp + n * max(d + extra, min_off), n

    # ------------------------------------------------------------------ uniform (엘피니아 계보)
    def uniform(self, *, jacket=True, sleeves=True, pants=True, boots=True, belt=True, epaulet=True, pockets=True,
                cuff_light=True, knee=False, thigh_pouch=True, gloves="fingerless", collar="stand", buttons=False):
        """PV 회색 전투복. 엘피니아 전투복(_kit_elfinia_soldier)의 재단을 그대로 따른다:
        차이나 칼라, 앞 여밈 띠와 은색 단추, 견장, 가슴 주머니, 블라우징 바지, 카고 주머니, 허벅지 파우치, 끈 군화."""
        e, M, k = self.e, self.M, self.k
        if jacket:
            # 단추는 조끼에 가려지므로 기본은 생략 (buttons=True: 조끼 없는 복장)
            e.shirt(M["uniform"], collar=collar, collar_mat=M["uniform_d"], placket=M["uniform_d"],
                    buttons=M["steel"] if buttons else None, flare=0.012)
        if sleeves:
            cm = M["uniform_light"] if cuff_light else M["uniform_d"]
            e.sleeves(M["uniform"], length=0.95, cuff=(cm, 0.022, 0.0045))
        if pants:
            e.pants(M["pants"], bag=0.013, blouse=0.020)
        if boots:
            e.boots(M["boots"], top=0.66, sole=(M["sole"], 0.016), cuff=M["dark"], laces=M["dark"])
        if belt:
            e.belt(M["dark"], buckle=M["steel"])
        if epaulet:
            e.epaulet(M["uniform_d"], button=M["steel"])
        if pockets:
            e.pouch(M["pants"], ("leg_L", 0.34, 85, 0.022 * k), size=(0.05, 0.010, 0.058), flap=M["pants_d"],
                    button=M["pants_d"], name="cargo_L")
        if thigh_pouch:
            e.pouch(M["dark2"], ("leg_R", 0.30, -75, 0.024 * k), size=(0.052, 0.026, 0.062), flap=M["dark"],
                    button=M["steel"], strap=M["dark"], name="thigh_pouch")
        if knee:
            for s, a in (("L", 0), ("R", 0)):
                e.pad(M["dark"], (f"leg_{s}", 0.53, a, 0.014 * k), size=(0.066, 0.016, 0.066), name=f"knee_{s}")
        if gloves == "fingerless":
            self.fingerless_gloves(M["dark"])
        elif gloves:
            e.gloves(gloves, cuff=M["dark2"])

    def fingerless_gloves(self, mat, *, cuff=None, inflate=0.0028):
        """손가락 없는 장갑 (PV 3:00~3:03): 손바닥 감싸개 + 손가락 첫 마디까지. 손가락 끝은 맨살."""
        e = self.e
        k = e.k * e.arm_k
        e.hide_hands = True          # 맨손은 만들지 않고, 장갑 밖으로 나온 손가락 끝만 맨살로 만든다
        for side in ("L", "R"):
            e.cover[f"arm_{side}"].append((0.97, 1.2))
            W, L, P = e.W[side], e.adir[side], e.palm_n[side]
            T = V((0, -1, 0))
            hb = f"hand_{side}"
            inf = inflate * e.k

            def fn(buf, W=W, L=L, P=P, T=T, hb=hb, side=side, inf=inf):
                tab = [(0.0, (0.021, 0.013)), (0.35, (0.0275, 0.0155)), (0.75, (0.0285, 0.015)), (1.0, (0.026, 0.013))]
                st = []
                for i in range(5):
                    t = i / 4
                    rx, ry = keys(tab, t)
                    c = W + L * (lerp(-0.10, 0.96, t) * e.hand_len) + P * (0.001 * k) + T * (0.001 * k)
                    w = elf.mixw({f"forearm_{side}": 1.0}, {hb: 1.0}, smoothstep(0.0, 0.25, t))
                    st.append({"c": c, "rx": rx * k + inf, "ry": ry * k + inf, "w": w, "ref": tuple(T), "p": 2.6})
                elf.loft(buf, st, segs=8, cap0=None, cap1="round", mat=mat, cap_len1=0.006 * k, cap_rings=2)
                for nm, base, mid, tip in e._finger_joints(side):
                    r0 = (0.0112 if nm == "thumb" else 0.0102) * k + inf
                    back = base - (mid - base).normalized() * 0.008 * k
                    ch = elf.Chain([back, base, mid, tip], [hb, f"{nm}_01_{side}", f"{nm}_02_{side}"], blend=0.45)
                    t1 = 0.52 if nm == "thumb" else 0.50
                    stf = []
                    for i in range(3):
                        t = lerp(0.0, t1, i / 2)
                        c, _ = ch.at(t)
                        stf.append({"c": c, "rx": r0, "ry": r0 * 0.92, "w": ch.weights(t), "ref": tuple(T)})
                    elf.loft(buf, stf, segs=6, cap0=None, cap1=None, mat=mat)
                    # 맨살 손가락 끝 (장갑 안에서 시작)
                    rs0 = (0.0112 if nm == "thumb" else 0.0102) * k
                    rs1 = (0.0098 if nm == "thumb" else 0.0090) * k
                    sts = []
                    for i in range(3):
                        t = lerp(t1 - 0.12, 1.0, i / 2)
                        c, _ = ch.at(t)
                        r = lerp(rs0, rs1, t)
                        sts.append({"c": c, "rx": r, "ry": r * 0.92, "w": ch.weights(t), "ref": tuple(T)})
                    elf.loft(buf, sts, segs=6, cap0=None, cap1="round", mat=e.skin_mat, cap_len1=rs1 * 0.9, cap_rings=2)
                if cuff is not None:
                    ar = e.arm_r(1.0)
                    elf.band(buf, W - L * (0.022 * k * 0.35), L, T, ar[0] + inf * 0.6, ar[1] + inf * 0.6, 0.022 * k,
                             0.004 * k, segs=10, mat=cuff, w={f"forearm_{side}": 0.6, hb: 0.4})
            e.part(f"fglove_{side}", "arms", fn)

    # ------------------------------------------------------------------ chest rig (소총병)
    def panel(self, mat, z0, z1, a0, a1, *, off=0.017, th=0.005, cols=9, rows=4, name="vest", bulge=0.0):
        """몸통을 감싸는 판 (조끼 앞판·뒤판, 판 조끼). a0..a1: 둘레 각(0=앞, +90=왼쪽). 두께 있는 휜 판.
        bulge: 가운데를 바깥으로 부풀리는 양(m, 판 조끼의 둥근 앞면)."""
        e, k = self.e, self.k

        def fn(buf):
            P = []
            for i in range(rows):
                z = lerp(z0, z1, i / (rows - 1))
                row = []
                for j in range(cols):
                    u = j / (cols - 1)
                    a = lerp(a0, a1, u)
                    p, n = e.torso_point(z, a, (off + bulge * math.sin(math.pi * u)) * k)
                    row.append((p, n, e._torso_wfn(p, 0)))
                P.append(row)
            o = [[buf.vert(p + n * th * k, w) for p, n, w in row] for row in P]
            n_ = [[buf.vert(p, w) for p, n, w in row] for row in P]
            for i in range(rows - 1):
                for j in range(cols - 1):
                    buf.face((o[i][j], o[i][j + 1], o[i + 1][j + 1], o[i + 1][j]), mat)
                    buf.face((n_[i][j], n_[i + 1][j], n_[i + 1][j + 1], n_[i][j + 1]), mat)
            for j in range(cols - 1):
                buf.face((o[0][j], n_[0][j], n_[0][j + 1], o[0][j + 1]), mat)
                buf.face((o[-1][j], o[-1][j + 1], n_[-1][j + 1], n_[-1][j]), mat)
            for i in range(rows - 1):
                buf.face((o[i][0], o[i + 1][0], n_[i + 1][0], n_[i][0]), mat)
                buf.face((o[i][-1], n_[i][-1], n_[i + 1][-1], o[i + 1][-1]), mat)
        return e.part(name, "body", fn)

    def chest_rig(self, *, pouches=3, radio=True, grenades=1, vest=True):
        """PV 가슴 장비: 짙은 조끼 앞·뒤판 + Y자 멜빵 + 가슴 띠 + 탄입대(shell) + 무전기 + 허리 G-5 수류탄."""
        e, M, k = self.e, self.M, self.k
        cz, sz = e.chest_z, e.shoulder_z
        pz = cz + 0.012 * k
        po = 0.018
        if vest:
            z0, z1 = e.waist_z - 0.012 * k, cz + 0.058 * k
            self.panel(M["dark2"], z0, z1, -54, 54, off=0.016, th=0.005, name="vest_front")
            self.panel(M["dark2"], z0, z1 - 0.01 * k, 128, 232, off=0.016, th=0.005, name="vest_back")
            # 등 다용도 파우치 (덮개 + 똑딱단추)
            e.pouch(M["shell"], ("torso", e.waist_z + 0.03 * k, 180, 0.021 * k), size=(0.07, 0.024, 0.05), flap=M["dark"],
                    button=M["steel"], name="back_pouch")
            po = 0.022
        for s in (1, -1):
            e.strap(M["dark"], [("torso", pz, s * 30, (po + 0.001) * k), ("torso", sz - 0.005 * k, s * 40, 0.016 * k),
                                ("torso", sz + 0.02 * k, s * 58, 0.014 * k), ("torso", sz - 0.01 * k, s * 122, 0.016 * k),
                                ("torso", cz, s * 150, (po + 0.001) * k),
                                ("torso", e.waist_z + 0.02 * k, s * 150, (po + 0.002) * k)],
                    width=0.022, th=0.004, name=f"harness_{'L' if s > 0 else 'R'}")
        if not vest:
            e.ring(M["dark"], "torso", pz - 0.035 * k, h=0.022, th=0.004, off=0.014, name="rig_band")
        angs = {3: (-26, 0, 26), 2: (-14, 14), 4: (-36, -12, 12, 36)}[pouches]
        for i, a in enumerate(angs):
            e.pouch(M["shell"], ("torso", pz - 0.006 * k, a, po * k), size=(0.036, 0.026, 0.058), flap=M["dark"],
                    button=M["steel"], name=f"mag_pouch_{i}")
        if radio:
            self.radio(("torso", pz + 0.022 * k, 50, po * k))
        for i in range(grenades):
            self.grenade(("torso", e.waist_z - 0.03 * k, 62 + 22 * i, 0.03 * k), name=f"g5_{i}")

    def radio(self, at, name="radio"):
        """가슴 왼쪽 무전기 (짙은 몸통 + 앰버 채널 노브 + 짧은 안테나)."""
        M, k = self.M, self.k

        def fn(buf, Mx, w):
            elf.rbox(buf, (0.030 * k, 0.020 * k, 0.046 * k), Mx @ Matrix.Translation((0, -0.010 * k, 0)), mat=M["shell"],
                     w=w, r=0.3, segs=1)
            elf.rbox(buf, (0.022 * k, 0.004 * k, 0.014 * k), Mx @ Matrix.Translation((0, -0.021 * k, -0.008 * k)),
                     mat=M["metal"], w=w, r=0.3, segs=1)
            c = Mx @ V((0.008 * k, -0.012 * k, 0.026 * k))
            elf.disc(buf, c, Mx.to_3x3() @ V((0, 0, 1)), Mx.to_3x3() @ V((0, -1, 0)), 0.0042 * k, 0.0042 * k, 0.004 * k,
                     segs=8, mat=M["amber"], w=w)
            base = Mx @ V((-0.009 * k, -0.010 * k, 0.022 * k))
            tube_path(buf, [base, base + Mx.to_3x3() @ V((0, 0.004 * k, 0.05 * k))], 0.0022 * k, M["dark"], w,
                      segs=6, cap0="flat")
        self.e.gear(name, at, fn)

    def grenade(self, at, name="g5"):
        """허리에 건 G-5 '땅벌' (단순화: 어두운 육각 캔 + 회백 띠 + 앰버 고리 + 레버)."""
        M, k = self.M, self.k

        def fn(buf, Mx, w):
            r = 0.019 * k
            for z0, z1, m, rr in ((-0.030, -0.006, M["shell"], r), (-0.006, 0.006, M["frame"], r * 1.04),
                                  (0.006, 0.030, M["shell"], r), (0.030, 0.038, M["amber"], r * 0.62)):
                c = Mx @ V((0, -r * 1.05, (z0 + z1) / 2 * k))
                elf.loft(buf, [{"c": c - Mx.to_3x3() @ V((0, 0, (z1 - z0) / 2 * k)), "rx": rr, "ry": rr, "w": w},
                               {"c": c + Mx.to_3x3() @ V((0, 0, (z1 - z0) / 2 * k)), "rx": rr, "ry": rr, "w": w}],
                         segs=6, cap0="flat", cap1="flat", mat=m, ref=tuple(Mx.to_3x3() @ V((1, 0, 0))))
            elf.rbox(buf, (0.006 * k, 0.004 * k, 0.040 * k), Mx @ Matrix.Translation((r * 0.9, -r * 1.9, 0.004 * k)),
                     mat=M["metal"], w=w, r=0.3, segs=0)   # 6 mm 레버: 모서리 없는 상자로 충분
        self.e.gear(name, at, fn)

    # ------------------------------------------------------------------ insignia
    def shoulder_insignia(self, *, sides=("L", "R"), t=0.17, ang=62, size=1.0, ring=None, shape="round", bars=2,
                          patch=None, disc=None):
        """PV 3:00~3:03 어깨: 짙은 회색 패치 + 앰버 원형 휘장 + 원작 엘프 로고(제국 흑).
        shape: 'round'(소총병, PV) | 'hex'(진압반: 앰버 육각) | 'chevron'(돌격 편대: 원 아래 앰버 꺾쇠).
        ring = 휘장 둘레 테 색(없으면 생략). bars = 패치 위 막대 부호 수(0~3)."""
        patch = patch or self.M["dark"]
        disc = disc or self.M["amber"]
        e, M, k = self.e, self.M, self.k
        for side in sides:
            s = 1 if side == "L" else -1
            a = e.anchor((f"arm_{side}", t, s * ang, 0.012 * k))

            def fn(buf, a=a):
                Mx = a.matrix(lift=0.0012 * k)
                elf.rbox(buf, (0.050 * k * size, 0.004 * k, 0.056 * k * size), Mx, mat=patch, w=a.w, r=0.32, segs=1)
                Md = Mx @ Matrix.Translation((0, -0.002 * k, -0.002 * k))
                if shape == "hex":
                    hex_plate(buf, Md, 0.0205 * k * size, 0.0016 * k, disc, a.w, rot=90)
                else:
                    ngon_disc(buf, Md, 0.0185 * k * size, 0.0016 * k, disc, a.w, n=14)
                if shape == "chevron":
                    for sg in (-1, 1):
                        R = Md @ Matrix.Translation((sg * 0.0085 * k * size, -0.0012 * k, -0.0235 * k * size)) @ \
                            Matrix.Rotation(math.radians(sg * 30), 4, "Y")
                        flat_quad(buf, R, 0.019 * k * size, 0.0045 * k * size, M["amber"], a.w)
                if ring is not None:
                    elf.band(buf, Md.to_translation(), Md.to_3x3() @ V((0, -1, 0)), Md.to_3x3() @ V((0, 0, 1)),
                             0.0185 * k * size, 0.0185 * k * size, 0.0018 * k, 0.0016 * k, segs=14, mat=ring, w=a.w)
                logo(buf, Md, 0.024 * k * size, M["shell"], a.w, lift=0.0026 * k, tol=0.010)   # 2.4 cm: 거칠게 해도 같다
                # 패치 위 막대 부호 (부대 식별, 3차 디테일): 한 면 사각 데칼
                for i, dx in enumerate((-0.0085, 0.0, 0.0085)[:bars]):
                    flat_quad(buf, Mx @ Matrix.Translation(((dx - 0.0042 * (bars - 1)) * k * size, -0.0022 * k,
                                                           0.0228 * k * size)),
                              0.0032 * k, 0.0058 * k, M["uniform_light"], a.w)
            e.part(f"insignia_{side}", "arms", fn)

    def arm_band(self, mat, *, sides=("L", "R"), t=0.42, h=0.016, name="armband"):
        """팔 띠 (진압반 = 양팔 앰버 한 줄)."""
        for side in sides:
            self.e.ring(mat, f"arm_{side}", t, h=h, th=0.0035, off=0.0125, name=f"{name}_{side}")

    def pads(self, mat, *, knees=True, elbows=True, shoulders=False, strap=None, shoulder_size=(0.074, 0.016, 0.064)):
        """보호대: 무릎(다리 앞), 팔꿈치(팔 뒤), 어깨(팔 위 바깥). 끈은 비싸서(띠 2개, 약 190 tris) 기본 생략."""
        e, k = self.e, self.k
        for side in ("L", "R"):
            s = 1 if side == "L" else -1
            if knees:
                e.pad(mat, (f"leg_{side}", 0.53, 0, 0.014 * k), size=(0.068, 0.018, 0.068), strap=strap,
                      name=f"knee_{side}")
            if elbows:
                e.pad(mat, (f"arm_{side}", 0.50, 180 - s * 25, 0.012 * k), size=(0.054, 0.014, 0.05), strap=strap,
                      name=f"elbow_{side}")
            if shoulders:
                e.pad(mat, (f"arm_{side}", 0.07, s * 88, 0.013 * k), size=shoulder_size, name=f"pauldron_{side}")

    def holster(self, at, *, mat=None, flap=None, name="holster"):
        """P-2 권총집 (권총은 socket_hip_R에 따로 붙인다. 여기서는 덮개 달린 빈 권총집)."""
        M, k = self.M, self.k
        mat = mat or M["shell"]
        flap = flap or M["dark"]

        def fn(buf, Mx, w):
            elf.rbox(buf, (0.034 * k, 0.026 * k, 0.070 * k), Mx @ Matrix.Translation((0, -0.013 * k, -0.006 * k)),
                     mat=mat, w=w, r=0.3, segs=1, taper=-0.15)
            elf.rbox(buf, (0.038 * k, 0.029 * k, 0.026 * k), Mx @ Matrix.Translation((0, -0.0145 * k, 0.026 * k)),
                     mat=flap, w=w, r=0.3, segs=1)
            ngon_disc(buf, Mx @ Matrix.Translation((0, -0.029 * k, 0.020 * k)), 0.004 * k, 0.0015 * k, M["steel"], w, n=6)
        self.e.gear(name, at, fn)

    def plate_vest(self, mat, *, front=(-64, 64), back=(122, 238), off=0.019, th=0.011, bulge=0.010, z0=None, z1=None,
                   trim=None, name="plate"):
        """두꺼운 판 조끼 (진압반·돌격 편대·경호대). 앞판은 둥글게 부풀고, 어깨끈으로 앞뒤를 잇는다.
        trim = 판 윗단 테 색 (없으면 생략)."""
        e, M, k = self.e, self.M, self.k
        z0 = z0 if z0 is not None else e.waist_z - 0.03 * k
        z1 = z1 if z1 is not None else e.chest_z + 0.07 * k
        self._back_off = off + th + bulge * 0.5
        self._front_off = off + th + bulge
        self.panel(mat, z0, z1, front[0], front[1], off=off, th=th, bulge=bulge, cols=11, rows=5, name=f"{name}_front")
        self.panel(mat, z0, z1 - 0.012 * k, back[0], back[1], off=off, th=th, bulge=bulge * 0.5, cols=11, rows=4,
                   name=f"{name}_back")
        if trim is not None:
            for zz, (a0, a1), nm in ((z1, front, "f"), (z1 - 0.012 * k, back, "b")):
                pts, nrm, ups = [], [], []
                for j in range(9):
                    u = j / 8
                    p, n = e.torso_point(zz - 0.004 * k, lerp(a0 + 4, a1 - 4, u),
                                         (off + th + bulge * (1.0 if nm == "f" else 0.5) * math.sin(math.pi * u)) * k)
                    pts.append(p)
                    nrm.append(n)
                    ups.append(V((0, 0, 1)))
                self.e.part(f"{name}_trim_{nm}", "body",
                            lambda buf, pts=pts, nrm=nrm, ups=ups: elf._loop(
                                buf, pts, nrm, ups, 0.008 * k, 0.0025 * k, mat=trim, closed=False,
                                w=lambda t, pts=pts: e._torso_wfn(pts[min(int(t * 8), 8)], 0)))
        # 어깨끈 (판 앞 위 → 어깨 → 판 뒤 위)
        for s in (1, -1):
            e.strap(M["dark"], [("torso", z1 - 0.012 * k, s * 34, (off + th + 0.006) * k),
                                ("torso", e.shoulder_z + 0.004 * k, s * 44, 0.020 * k),
                                ("torso", e.shoulder_z + 0.024 * k, s * 64, 0.016 * k),
                                ("torso", e.shoulder_z - 0.004 * k, s * 118, 0.020 * k),
                                ("torso", z1 - 0.024 * k, s * 146, (off + th + 0.004) * k)],
                    width=0.030, th=0.005, name=f"{name}_strap_{'L' if s > 0 else 'R'}")
        # 옆구리 고정끈 (앞판 끝 → 뒤판 끝)
        for s in (1, -1):
            zz = lerp(z0, z1, 0.35)
            e.strap(M["dark"], [("torso", zz, s * (front[1] - 6), (off + 0.004) * k), ("torso", zz, s * 92, 0.016 * k),
                                ("torso", zz, s * (back[0] + 6), (off + 0.004) * k)],
                    width=0.022, th=0.004, name=f"{name}_side_{'L' if s > 0 else 'R'}")

    def backpack(self, *, size=(0.15, 0.065, 0.16), z=None, mat=None, band=None, antenna=True, logo_mat=None,
                 name="backpack"):
        """등짐 (탄약·무전 팩): 둥근 상자 + 가로 띠 + 덮개 + 짧은 안테나 + 엘프 로고."""
        e, M, k = self.e, self.M, self.k
        mat = mat or M["shell"]
        z = z if z is not None else e.chest_z - 0.01 * k
        off = getattr(self, "_back_off", 0.02)

        def fn(buf, Mx, w):
            sx, sy, sz = (v * k for v in size)
            elf.rbox(buf, (sx, sy, sz), Mx @ Matrix.Translation((0, -sy / 2, 0)), mat=mat, w=w, r=0.25, segs=1)
            elf.rbox(buf, (sx * 1.04, sy * 0.55, sz * 0.36), Mx @ Matrix.Translation((0, -sy * 0.75, sz * 0.36)),
                     mat=M["dark"], w=w, r=0.3, segs=1)
            if band is not None:
                elf.rbox(buf, (sx * 1.02, sy * 1.03, sz * 0.13), Mx @ Matrix.Translation((0, -sy / 2, -sz * 0.12)),
                         mat=band, w=w, r=0.2, segs=1)
            if logo_mat is not None:
                logo(buf, Mx @ Matrix.Translation((0, -sy * 1.03, -sz * 0.31)), 0.040 * k, logo_mat, w, lift=0.0, tol=0.008)
            if antenna:
                base = Mx @ V((sx * 0.36, -sy * 0.5, sz * 0.5))
                tube_path(buf, [base, base + Mx.to_3x3() @ V((0.01 * k, 0.012 * k, 0.11 * k))], 0.0028 * k, M["dark"], w,
                          segs=6, cap0="flat")
        self.e.gear(name, ("torso", z, 180, off * k), fn)

    def coat_skirt(self, mat, *, z_top=None, z_hem=None, gap=16.0, flare=0.035, off=0.016, th=0.005, hem=None,
                   edge=None, rows=7, cols=None, back_slit=8.0, spans=None, lining=None, name="coat_skirt"):
        """몸에서 떨어지는 코트 자락 (허리 → 무릎). 키트에 없는 '떨어지는 천'(ELF_KIT.md 12장)을 직접 만든다.
        앞트임(gap, 반각 도)과 뒤트임(back_slit)이 있고, 웨이트는 골반 → 좌우 허벅지로 섞는다(걷기 대응).
        hem/edge = 밑단·앞여밈 테 색. spans = [(각0, 각1), ...]로 덮는 둘레를 바꾸면 망토가 된다(cape()).
        lining = 안쪽 면 색."""
        e, k = self.e, self.k
        z_top = z_top if z_top is not None else e.waist_z - 0.01 * k
        z_hem = z_hem if z_hem is not None else e.knee_z + 0.02 * k
        cols = cols or max(18, int(30 * e.q))
        zw = e.crotch_z + 0.17 * (e.torso_top - e.crotch_z)

        def sect(z):
            rx, ry, cy = e.torso_at(max(z, zw))
            if z < zw:   # 골반 아래: 가장 넓은 골반과 다리 바깥을 감싼다
                rx = max(rx, 0.158 * k * e.hp)
            return rx, ry, cy

        def wfn(q):
            if q.z >= e.hipj_z:
                return e._torso_wfn(q, 0)
            a = smoothstep(e.hipj_z, e.knee_z, q.z)
            sx = elf.clamp(q.x / (0.12 * k), -1.0, 1.0)
            wl = 0.5 + 0.5 * sx
            leg = {kk: v for kk, v in (("thigh_L", wl), ("thigh_R", 1 - wl)) if v > 1e-4}
            return elf.mixw({"hips": 1.0}, leg, a * 0.7)

        # 둘레 각: 앞트임(0 근처)과 뒤트임(180 근처)을 비운 두 장 (왼쪽 자락, 오른쪽 자락)
        halves = spans or [(gap, 180.0 - back_slit), (180.0 + back_slit, 360.0 - gap)]
        lin = lining or mat

        def fn(buf):
            for hi, (a0, a1) in enumerate(halves):
                nc = cols // 2
                P = []
                for i in range(rows):
                    u = i / (rows - 1)
                    z = lerp(z_top, z_hem, u)
                    rx, ry, cy = sect(z)
                    fl = flare * (u * u if spans is None else u)
                    row = []
                    for j in range(nc):
                        a = math.radians(lerp(a0, a1, j / (nc - 1)))
                        dx, dy = math.sin(a), -math.cos(a)
                        ee = 2 / 2.3
                        x = math.copysign(abs(dx) ** ee, dx) * (rx + (off + fl) * k)
                        y = math.copysign(abs(dy) ** ee, dy) * (ry + (off + fl) * k) + cy
                        q = V((x, y, z))
                        nrm = V((x / max(rx, 1e-4) ** 2, (y - cy) / max(ry, 1e-4) ** 2, 0)).normalized()
                        row.append((q, nrm, wfn(q)))
                    P.append(row)
                o = [[buf.vert(q, w) for q, nn, w in row] for row in P]
                n_ = [[buf.vert(q - nn * th * k, w) for q, nn, w in row] for row in P]
                for i in range(rows - 1):
                    for j in range(nc - 1):
                        buf.face((o[i][j], o[i][j + 1], o[i + 1][j + 1], o[i + 1][j]), mat)
                        buf.face((n_[i][j], n_[i + 1][j], n_[i + 1][j + 1], n_[i][j + 1]), lin)
                for j in range(nc - 1):
                    buf.face((o[-1][j], o[-1][j + 1], n_[-1][j + 1], n_[-1][j]), mat)
                    buf.face((o[0][j], n_[0][j], n_[0][j + 1], o[0][j + 1]), mat)
                for i in range(rows - 1):
                    buf.face((o[i][0], o[i + 1][0], n_[i + 1][0], n_[i][0]), mat)
                    buf.face((o[i][-1], n_[i][-1], n_[i + 1][-1], o[i + 1][-1]), mat)
                if hem is not None:   # 밑단 테
                    pts = [P[-1][j][0] + V((0, 0, 0.006 * k)) + P[-1][j][1] * 0.0006 * k for j in range(nc)]
                    nr = [P[-1][j][1] for j in range(nc)]
                    ribbon(buf, pts, nr, [V((0, 0, 1))] * nc, 0.010 * k, hem, [P[-1][j][2] for j in range(nc)][nc // 2])
                if edge is not None:  # 앞여밈 테 (앞트임 쪽 세로 띠)
                    jj = 0 if hi == 0 else nc - 1
                    pts = [P[i][jj][0] + P[i][jj][1] * 0.0006 * k for i in range(rows)]
                    nr = [P[i][jj][1] for i in range(rows)]
                    side = V((0, 0, 1)).cross(nr[0]).normalized() * (1 if hi == 0 else -1)
                    pts = [p + side * 0.005 * k for p in pts]
                    ribbon(buf, pts, nr, [side] * rows, 0.010 * k, edge, P[rows // 2][jj][2])
        return e.part(name, "body", fn)

    def cape(self, mat, *, lining=None, hem=None, z_top=None, z_hem=None, a0=116.0, off=0.030, flare=0.050, rows=8,
             name="cape"):
        """등 망토 (지휘관): 어깨 뒤에서 무릎까지. 팔(옆, 90°)을 피해 a0~360-a0만 덮는다. 웨이트는 가슴 → 골반 → 허벅지."""
        e, k = self.e, self.k
        z_top = z_top if z_top is not None else e.shoulder_z + 0.010 * k
        z_hem = z_hem if z_hem is not None else e.knee_z - 0.01 * k
        return self.coat_skirt(mat, z_top=z_top, z_hem=z_hem, spans=[(a0, 180.0), (180.0, 360.0 - a0)], off=off,
                               flare=flare, hem=hem, lining=lining, rows=rows, cols=max(16, int(26 * e.q)), name=name)

    def epaulet_boards(self, mat, *, stripes=4, stripe_mat=None, width=0.034, name="board"):
        """견장 판(지휘관): 어깨 위 제국 흑 판 + 앰버 가로 줄. 줄 수 = 계급 (2 분대, 3 중대, 4 현장 지휘관)."""
        e, M, k = self.e, self.M, self.k
        stripe_mat = stripe_mat or M["amber"]
        for side in ("L", "R"):
            s = 1 if side == "L" else -1
            path = [("torso", e.torso_top - 0.016 * k, s * 38, 0.014 * k),
                    ("torso", e.shoulder_z + 0.014 * k, s * 72, 0.014 * k),
                    ("torso", e.shoulder_z - 0.004 * k, s * 90, 0.014 * k)]
            e.strap(mat, path, width=width, th=0.006, name=f"{name}_{side}")
            anchors = [e.anchor(a) for a in path]
            pts = elf.catmull([a.pos for a in anchors], 12)
            nr = elf.catmull([a.n for a in anchors], 12)

            def fn(buf, pts=pts, nr=nr, anchors=anchors):
                for i in range(stripes):
                    t = lerp(0.42, 0.88, i / max(stripes - 1, 1))
                    f = t * (len(pts) - 1)
                    j = min(int(f), len(pts) - 2)
                    p = pts[j].lerp(pts[j + 1], f - j)
                    n = nr[j].lerp(nr[j + 1], f - j).normalized()
                    tan = (pts[j + 1] - pts[j]).normalized()
                    Mx = Matrix.Translation(p + n * 0.0072 * k) @ elf.frame(n, tan)
                    w = elf.mixw(anchors[1].w, anchors[2].w, t)
                    flat_quad(buf, Mx, width * 0.82 * k, 0.0042 * k, stripe_mat, w)
            e.part(f"{name}_stripes_{side}", "body", fn)
            # 끝 단추
            a = e.anchor(("torso", e.torso_top - 0.02 * k, s * 44, 0.020 * k))
            e.part(f"{name}_btn_{side}", "body",
                   lambda buf, a=a: elf.disc(buf, a.pos, a.n, (0, 0, 1), 0.0050 * k, 0.0050 * k, 0.002 * k, segs=8,
                                             mat=M["amber"], w=a.w))

    def aiguillette(self, mat, *, side="R", name="aiguillette"):
        """장식 끈 (지휘관): 어깨 견장 밑에서 가슴 단추까지 늘어진 고리 두 줄."""
        e, k = self.e, self.k
        s = 1 if side == "L" else -1
        a0 = e.anchor(("torso", e.shoulder_z + 0.004 * k, s * 66, 0.020 * k))
        a3 = e.anchor(("torso", e.chest_z + 0.03 * k, s * 14, 0.020 * k))

        def fn(buf):
            for drop, rr in ((0.045, 0.0032), (0.070, 0.0030)):
                mids = []
                for u in (0.25, 0.5, 0.75):
                    z = lerp(e.shoulder_z, e.chest_z + 0.03 * k, u) - drop * k * math.sin(math.pi * u)
                    p, n = e.torso_point(z, s * lerp(66, 14, u), 0.024 * k)
                    mids.append(p)
                pts = elf.catmull([a0.pos] + mids + [a3.pos], 10)
                tube_path(buf, pts, rr * k, mat, lambda t: elf.mixw(a0.w, a3.w, t), segs=6)
            elf.disc(buf, a3.pos, a3.n, (0, 0, 1), 0.006 * k, 0.006 * k, 0.003 * k, segs=8, mat=mat, w=a3.w)
        e.part(name, "body", fn)

    def wrist_tablet(self, *, side="L", name="tablet"):
        """지휘관 손목 태블릿: 제국 흑 테 + 오각 화면(glow_dim, UNLIT) + 앰버 버튼. r41-style 7.3의 오각 화면 태블릿."""
        e, M, k = self.e, self.M, self.k
        s = 1 if side == "L" else -1
        at = (f"arm_{side}", 0.72, s * 40, 0.016 * k)

        def fn(buf, Mx, w):
            elf.rbox(buf, (0.050 * k, 0.012 * k, 0.040 * k), Mx @ Matrix.Translation((0, -0.004 * k, 0)), mat=M["shell"], w=w,
                     r=0.3, segs=1)
            pts = [(math.cos(math.radians(90 + 72 * i)) * 0.016 * k, math.sin(math.radians(90 + 72 * i)) * 0.016 * k)
                   for i in range(5)]
            idx = [buf.vert(Mx @ V((x, -0.0108 * k, z - 0.001 * k)), w) for x, z in pts]
            buf.face(tuple(idx), M["screen"])
            ngon_disc(buf, Mx @ Matrix.Translation((0.019 * k, -0.010 * k, -0.012 * k)), 0.0030 * k, 0.0015 * k,
                      M["amber"], w, n=6)
        e.gear(name, at, fn)

    def capelet(self, mat, *, side="L", lining=None, trim=None, logo_mat=None, off=0.024, name="capelet"):
        """한쪽 어깨 망토 (경호대): 왼쪽 어깨를 덮고 등 왼쪽으로 늘어진다. 팔은 그 아래로 움직인다(어깨·가슴 웨이트).
        lining = 안감 색, trim = 테 색, logo_mat = 등판 엘프 로고 색. off = 몸에서 띄우는 거리(판 조끼 위면 0.04 이상)."""
        e, M, k = self.e, self.M, self.k
        s = 1 if side == "L" else -1
        lining = lining or mat
        cols, rows = 13, 6

        def col_spec(u):
            """u 0(앞 가슴) → 1(등 가운데 너머): 둘레 각, 아랫단 높이, 띄우는 거리."""
            ang = lerp(28, 196, u)
            bottom = keys([(0.0, e.chest_z + 0.035 * k), (0.25, e.shoulder_z - 0.045 * k), (0.42, e.shoulder_z - 0.05 * k),
                           (0.62, e.waist_z + 0.02 * k), (1.0, e.waist_z - 0.03 * k)], u)
            arm = math.exp(-((ang - 90) / 26.0) ** 2)
            return ang, bottom, arm

        def fn(buf):
            P = []
            for i in range(rows):
                v = i / (rows - 1)
                row = []
                for j in range(cols):
                    u = j / (cols - 1)
                    ang, zb, arm = col_spec(u)
                    zt = e.torso_top - 0.01 * k - 0.02 * k * math.sin(math.radians(min(ang, 180)) * 1.0)
                    z = lerp(zt, zb, v)
                    off0 = lerp(0.022, off, smoothstep(0.0, 0.35, v))   # 목 쪽은 몸에 붙고 아래로 갈수록 판 위로
                    o_ = (off0 + 0.030 * arm * smoothstep(0.0, 0.6, v) + 0.012 * v) * k
                    p, n = e.torso_point(z, s * ang, o_)
                    if v < 0.25:   # 목 쪽 윗단은 안으로 오므림
                        p = p.lerp(V((0, 0, p.z)), 0.08 * (1 - v / 0.25))
                    w = e._torso_wfn(p, 0)
                    w = elf.mixw(w, {f"shoulder_{side}": 1.0}, 0.35 * arm)
                    row.append((p, n, w))
                P.append(row)
            th = 0.005 * k
            o = [[buf.vert(p, w) for p, n, w in row] for row in P]
            n_ = [[buf.vert(p - n * th, w) for p, n, w in row] for row in P]
            for i in range(rows - 1):
                for j in range(cols - 1):
                    a, b = (j, j + 1) if s > 0 else (j + 1, j)
                    buf.face((o[i][a], o[i][b], o[i + 1][b], o[i + 1][a])[::-1], mat)
                    buf.face((n_[i][a], n_[i + 1][a], n_[i + 1][b], n_[i][b])[::-1], lining)
            for j in range(cols - 1):
                a, b = (j, j + 1) if s > 0 else (j + 1, j)
                buf.face((o[-1][a], n_[-1][a], n_[-1][b], o[-1][b]), mat)
            for i in range(rows - 1):
                for jj in (0, cols - 1):
                    buf.face((o[i][jj], o[i + 1][jj], n_[i + 1][jj], n_[i][jj]), mat)
            if trim is not None:
                pts = [P[-1][j][0] + V((0, 0, 0.006 * k)) + P[-1][j][1] * 0.0007 * k for j in range(cols)]
                nr = [P[-1][j][1] for j in range(cols)]
                ribbon(buf, pts, nr, [V((0, 0, 1))] * cols, 0.010 * k, trim, P[-1][cols // 2][2])
                pts = [P[i][0][0] + P[i][0][1] * 0.0007 * k for i in range(rows)]
                nr = [P[i][0][1] for i in range(rows)]
                sd = V((0, 0, 1)).cross(nr[2]).normalized() * s
                ribbon(buf, [p + sd * 0.005 * k for p in pts], nr, [sd] * rows, 0.010 * k, trim, P[2][0][2])
            if logo_mat is not None:   # 등 쪽 망토 위 엘프 로고
                j = int(cols * 0.80)
                p, n, w = P[2][j]
                Mx = Matrix.Translation(p + n * 0.0012 * k) @ elf.frame(n, (0, 0, 1))
                logo(buf, Mx, 0.050 * k, logo_mat, w)
            # 왼 가슴 고정 브로치
            p, n, w = P[1][0]
            elf.disc(buf, p + n * 0.001 * k, n, (0, 0, 1), 0.008 * k, 0.008 * k, 0.003 * k, segs=10, mat=M["amber"], w=w)
        e.part(name, "body", fn)

    def chest_logo(self, at, *, size=0.032, plate=None, logo_mat=None, plate_size=None, hexagon=True, name="chest_logo"):
        """가슴 엘프 로고 패치 (판 + 로고)."""
        e, M, k = self.e, self.M, self.k
        plate = plate or M["shell"]
        logo_mat = logo_mat or M["amber"]

        def fn(buf, Mx, w):
            if hexagon:
                hex_plate(buf, Mx, (plate_size or size * 0.78) * k, 0.002 * k, plate, w, rot=90)
            else:
                elf.rbox(buf, ((plate_size or size * 1.3) * k, 0.003 * k, (plate_size or size * 1.3) * k), Mx, mat=plate,
                         w=w, r=0.25, segs=1)
            logo(buf, Mx, size * k, logo_mat, w, lift=0.0032 * k, tol=0.008)
        e.gear(name, at, fn)

    # ------------------------------------------------------------------ beret
    def beret(self, mat=None, *, band=None, rib=None, piping=None, badge="round", badge_mat=None, badge_ring=None,
              badge_az=38.0, drape=1.0, size=1.0, band_el=(28.0, 22.0, 12.0), band_off=0.018, name="beret"):
        """PV 3:00~3:03 베레모 (R41은 헬멧을 쓰지 않는다): 오른쪽(-X)으로 눌러 쓴 납작한 크라운 + 짙은 머리띠(골 두 줄)
        + 왼쪽 앞(왼 눈 위) 휘장 = 원작 엘프 로고. 귀는 머리띠 아래로 밖에 나오고, 머리카락은 머리띠 위로 눌러 넣는다.

        mat: 크라운 색(병종 구분), band: 머리띠 색, rib: 머리띠 골 줄 색, piping: 머리띠 아랫단 테 색(계급).
        badge: 'round' | 'hex' | 'chevron' | None. badge_mat: 휘장 바탕(기본 앰버). badge_ring: 휘장 테 색 또는 색 목록(계급).
        drape: 오른쪽으로 눌러 쓴 정도(0~1.5). band_el: 머리띠 아랫단 높이(앞, 옆, 뒤, 도)."""
        e, M, k = self.e, self.M, self.k
        mat = mat or M["beret_grey"]
        band = band or M["beret_band"]
        rib = rib or M["dark"]
        badge_mat = badge_mat or M["amber"]
        F, S, B = band_el

        def bel(az):
            a = abs(((az + 180) % 360) - 180)
            return F + (S - F) * smoothstep(0, 90, a) + (B - S) * smoothstep(90, 180, a)
        self.band_el = bel
        bo = band_off * k
        BW, BT = 0.028 * k, 0.0065 * k
        self.band_off = bo
        self.band_top = bo + BT
        e._hats = getattr(e, "_hats", [])
        e._hats.append((bo, bel))       # 키트 squash: 머리띠 위의 머리카락을 두피 쪽으로 눌러 넣는다
        W = {"head": 1.0}

        def band_pt(az, du=0.0, extra=0.0):
            el = bel(az)
            p0, n0 = e.head_point(az, el, bo + extra)
            p1, _ = e.head_point(az, el + 4, bo + extra)
            up = (p1 - p0).normalized()
            return p0 + up * (BW * (0.5 + du)), n0, up

        def crown_rows(az):
            """머리띠 윗단에서 시작해 테두리(볼록한 둘레)로 부풀었다가 납작한 윗면으로 닫히는 단면 (el, off)."""
            d = -math.sin(math.radians(az)) * drape          # 오른쪽 +1, 왼쪽 -1
            f = math.cos(math.radians(az))                   # 앞 +1
            eb = bel(az) + 10.0 - 8.0 * d - 3.0 * max(f, 0.0)
            ob = (0.050 + 0.022 * d) * size
            top0 = bel(az) + 6.5
            return [(top0, bo / k + 0.0065), (eb - 3.0, ob * 0.78), (eb, ob), (eb + 8.0, ob * 0.86),
                    (lerp(eb + 8.0, 90.0, 0.45), 0.040 * size), (lerp(eb + 8.0, 90.0, 0.78), 0.035 * size)]

        shift = V((-0.020 * drape, 0.004, 0.0)) * k

        def cp(az, el, off):
            p, nn = e.head_point(az, el, off * k)
            # 위로 갈수록 오른쪽으로 쏠림 (눌러 쓴 크라운)
            u = elf.clamp((el - bel(az) - 6.0) / 40.0)
            return p + shift * smoothstep(0.0, 1.0, u)

        def fn(buf):
            n = 24
            grid = []
            for j in range(n):
                az = 360.0 * j / n
                grid.append([buf.vert(cp(az, el, off), W) for el, off in crown_rows(az)])
            R = len(grid[0])
            for j in range(n):
                j2 = (j + 1) % n
                for i in range(R - 1):
                    buf.face((grid[j][i], grid[j2][i], grid[j2][i + 1], grid[j][i + 1]), mat)
            pole = buf.vert(cp(0.0, 90.0, 0.034 * size) + shift * 0.15, W)
            for j in range(n):
                buf.face((grid[j][R - 1], grid[(j + 1) % n][R - 1], pole), mat)
            # 머리띠 (+ 골 두 줄)
            n = 24
            pts, nrm, ups = [], [], []
            for j in range(n):
                p, nn, up = band_pt(360.0 * j / n)
                pts.append(p)
                nrm.append(nn)
                ups.append(up)
            elf._loop(buf, pts, nrm, ups, BW, BT, mat=band, w=W)
            for du in (-0.18, 0.18):
                rp, rn, ru = [], [], []
                for j in range(n + 1):
                    p, nn, up = band_pt(360.0 * j / n, du, BT + 0.0004 * k)
                    rp.append(p)
                    rn.append(nn)
                    ru.append(up)
                ribbon(buf, rp, rn, ru, 0.0028 * k, rib, W)
            if piping is not None:
                rp, rn, ru = [], [], []
                for j in range(n + 1):
                    p, nn, up = band_pt(360.0 * j / n, -0.40, BT + 0.0005 * k)
                    rp.append(p)
                    rn.append(nn)
                    ru.append(up)
                ribbon(buf, rp, rn, ru, 0.0050 * k, piping, W)
            # 휘장: 왼 눈 위 머리띠 (원작 엘프 로고)
            if badge:
                p, nn, up = band_pt(badge_az, 0.15, BT + 0.0015 * k)
                nn = (nn + V((0, 0, 0.25))).normalized()
                Mx = Matrix.Translation(p) @ elf.frame(nn, up)
                r = 0.0175 * k
                if badge == "hex":
                    hex_plate(buf, Mx, r * 1.12, 0.0018 * k, badge_mat, W, rot=90)
                else:
                    ngon_disc(buf, Mx, r, 0.0018 * k, badge_mat, W, n=14)
                rings = badge_ring if isinstance(badge_ring, (list, tuple)) else ([badge_ring] if badge_ring else [])
                for i, rm in enumerate(rings):
                    rr = r + (0.0030 + 0.0034 * i) * k
                    elf.band(buf, Mx.to_translation() - nn * 0.0004 * k, nn, up, rr, rr, 0.0020 * k, 0.0024 * k, segs=14,
                             mat=rm, w=W)
                if badge == "chevron":
                    for sgn in (-1, 1):
                        R = Mx @ Matrix.Translation((sgn * 0.0080 * k, -0.0019 * k, -0.0215 * k)) @ \
                            Matrix.Rotation(math.radians(sgn * 30), 4, "Y")
                        flat_quad(buf, R, 0.017 * k, 0.0045 * k, M["amber"], W)
                logo(buf, Mx, 0.0235 * k, M["shell"], W, lift=0.0026 * k, tol=0.010)
        e.part(name, "head", fn)

    # ------------------------------------------------------------------ goggles
    def goggles(self, mode="down", *, lens=None, frame=None, strap=None, hl=True, name="goggles"):
        """PV의 얼굴을 감싸는 연기색 고글 (3:00~3:03, 4:59~5:07에서 전원 착용).
        mode='down': 눈 위. 반투명 렌즈로 눈과 표정이 비친다. 끈은 귀 위로 머리를 감는다.
        mode='up'  : 베레모 머리띠 위로 올림 (얼굴이 다 보이는 변형). 휘장은 beret(badge_az=64)로 옆으로 옮긴다."""
        e, M, k = self.e, self.M, self.k
        lens = lens or M["visor"]
        frame = frame or M["frame"]
        strap = strap or M["dark"]
        assert getattr(self, "band_off", None) is not None, "beret()을 먼저 부른다"
        bel = self.band_el
        self._goggle_mode = mode
        W = {"head": 1.0}
        if mode == "down":
            AZ = 64.0

            def top_el(az):
                return -1.5 - 3.0 * (abs(az) / AZ) ** 2

            def bot_el(az):
                a = abs(az) / AZ
                notch = 7.5 * math.exp(-(az / 13.0) ** 2)      # 콧등 홈
                return -35.0 + 3.0 * a * a + notch

            def lp(az, el, extra=0.0):
                # 얼굴에서 띄운 렌즈 면: 가운데는 조금 더 앞으로(감싸는 곡면)
                off = (0.020 + 0.006 * (1 - (az / AZ) ** 2)) * k + extra
                return e.head_point(az, el, off)
        else:
            AZ = 56.0
            base = self.band_top + 0.004 * k

            def top_el(az):
                return bel(az) + 10 - 2 * (abs(az) / AZ) ** 2

            def bot_el(az):
                a = abs(az) / AZ
                return bel(az) - 7 + 2 * a * a + 4.0 * math.exp(-(az / 13.0) ** 2)

            def lp(az, el, extra=0.0):
                return e.head_point(az, el, base + 0.004 * k * (1 - (az / AZ) ** 2) + extra)

        def fn(buf):
            nc, nr = 11, 4
            grid = []
            for j in range(nc):
                az = -AZ + 2 * AZ * j / (nc - 1)
                col = []
                for i in range(nr):
                    el = lerp(bot_el(az), top_el(az), i / (nr - 1))
                    col.append(buf.vert(lp(az, el)[0], W))
                grid.append(col)
            for j in range(nc - 1):
                for i in range(nr - 1):
                    buf.face((grid[j][i], grid[j + 1][i], grid[j + 1][i + 1], grid[j][i + 1]), lens)
            # 테: 렌즈 둘레를 감싸는 고리
            ring = []
            for j in range(nc):
                ring.append((-AZ + 2 * AZ * j / (nc - 1), "top"))
            for i in range(1, 3):
                ring.append((AZ, ("side", i)))
            for j in range(nc - 1, -1, -1):
                ring.append((-AZ + 2 * AZ * j / (nc - 1), "bot"))
            for i in range(2, 0, -1):
                ring.append((-AZ, ("side", i)))
            pts, nrm = [], []
            for az, wh in ring:
                if wh == "top":
                    el = top_el(az) + 1.6
                elif wh == "bot":
                    el = bot_el(az) - 1.6
                else:
                    el = lerp(bot_el(az), top_el(az), wh[1] / 3)
                    az = az + (2.0 if az > 0 else -2.0)
                p, nn = lp(az, el, -0.002 * k)
                pts.append(p)
                nrm.append(nn)
            ups = []
            nP = len(pts)
            for i in range(nP):
                t = pts[(i + 1) % nP] - pts[(i - 1) % nP]
                ups.append(t.cross(nrm[i]).normalized())
            elf._loop(buf, pts, nrm, ups, 0.011 * k, 0.0062 * k, mat=frame, closed=True, w=W)
            # 렌즈 반사 (PV 클로즈업의 비스듬한 밝은 줄): 눈 바깥 렌즈 귀퉁이에만
            if hl:
                for s in (1, -1):
                    for da, ln, wd in ((0.0, 1.0, 0.0040), (6.0, 0.6, 0.0024)):
                        a0, a1 = s * (AZ * 0.66 + da), s * (AZ * 0.82 + da)
                        e0 = lerp(bot_el(a0), top_el(a0), 0.88)
                        e1 = lerp(bot_el(a1), top_el(a1), 0.30)
                        e1 = lerp(e0, e1, ln)
                        a1 = lerp(a0, a1, ln)
                        pp = [lp(lerp(a0, a1, u), lerp(e0, e1, u), 0.0008 * k) for u in (0.0, 0.5, 1.0)]
                        ribbon(buf, [p for p, _ in pp], [nn for _, nn in pp], None, wd * k, M["lens_hl"], W)
            # 고무 끈
            if mode == "down":
                # 렌즈 양 끝 → 귀 위 → 뒤통수 (머리카락 위)
                SEL, BEL, OFF = 8.0, -3.0, 0.036

                def sel(az):
                    return SEL + (BEL - SEL) * smoothstep(84, 180, abs(az))
                for s in (1, -1):
                    e_mid = lerp(bot_el(AZ), top_el(AZ), 0.55)
                    p0, n0 = lp(s * (AZ + 2), e_mid, -0.003 * k)
                    p1, n1 = self.lift(s * 80, sel(80), 0.002 * k, (OFF - 0.006) * k)
                    pm, nm = self.lift(s * 73, lerp(e_mid, sel(80), 0.6), 0.002 * k, (OFF - 0.010) * k)
                    pts2, nr2 = [p0, pm, p1], [n0, nm, n1]
                    ups2 = []
                    for i in range(3):
                        t = pts2[min(i + 1, 2)] - pts2[max(i - 1, 0)]
                        ups2.append(t.cross(nr2[i]).normalized())
                    elf._loop(buf, pts2, nr2, ups2, 0.014 * k, 0.0035 * k, mat=strap, closed=False, w=W)
                azs = [80 + (360 - 160) * i / 18 for i in range(19)]
                # 머리카락 바깥 면을 따라 감는다 (헤어 v2 덩어리에 묻히지 않게)
                spt = [self.lift(((a + 180) % 360) - 180, sel(((a + 180) % 360) - 180), 0.0035 * k,
                                 (OFF - 0.006) * k) for a in azs]
            else:
                # 베레모 머리띠 위를 감는다
                azs = [AZ + 1 + (360 - 2 * AZ - 2) * i / 14 for i in range(15)]
                spt = []
                for a in azs:
                    az = ((a + 180) % 360) - 180
                    spt.append(e.head_point(az, bel(az) + 3.5, self.band_top + 0.0015 * k))
            pts = [p for p, _ in spt]
            nrm = [nn for _, nn in spt]
            ups = []
            for i in range(len(pts)):
                t = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
                ups.append(t.cross(nrm[i]).normalized())
            elf._loop(buf, pts, nrm, ups, 0.016 * k, 0.003 * k, mat=strap, closed=False, w=W)
        e.part(name, "head", fn)

    # ------------------------------------------------------------------ headset
    def headset(self, *, mic=True, side="R", name="headset"):
        """PV의 짙은 헤드셋: 귀 뿌리 바로 아래의 귀마개 두 개 + 오른쪽 붐 마이크.
        귀마개·머리띠·붐은 머리카락 바깥 면(lift) 위에 얹어 옆머리에 가려지지 않는다. beret() 뒤에 부른다."""
        e, M, k = self.e, self.M, self.k
        W = {"head": 1.0}
        AZ, EL = 92.0, -29.0     # 귀 뿌리(약 -12°) 바로 아래, 옆머리 바깥 면 위
        bel = getattr(self, "band_el", lambda az: 20.0)
        cups = {}
        for s in (1, -1):
            p, nn = self.lift(s * AZ, EL, 0.005 * k, 0.010 * k)
            nn = (nn + V((0, 0, -0.10))).normalized()
            cups[s] = (p, nn)

        def fn(buf):
            for s in (1, -1):
                p, nn = cups[s]
                Mx = Matrix.Translation(p) @ elf.frame(nn, (0, 0, 1))
                elf.rbox(buf, (0.044 * k, 0.024 * k, 0.054 * k), Mx @ Matrix.Translation((0, -0.006 * k, 0)),
                         mat=M["dark"], w=W, r=0.45, segs=1)
                # 바깥 덮개: 밝은 회색 판 (PV 클로즈업의 헤드셋 밝은 점) + 짙은 버튼
                ngon_disc(buf, Mx @ Matrix.Translation((0, -0.018 * k, 0.0)), 0.014 * k, 0.002 * k, M["frame_d"], W, n=8)
                ngon_disc(buf, Mx @ Matrix.Translation((0.004 * k, -0.0205 * k, 0.004 * k)), 0.004 * k, 0.0015 * k,
                          M["dark"], W, n=6)
                # 귀마개 위로 올라가 베레모 머리띠 아래로 들어가는 띠: 귀 뿌리 앞을 지나 머리카락 위로
                q0, _ = self.lift(s * (AZ - 8), EL + 13, 0.004 * k, 0.012 * k)
                q1, _ = self.lift(s * (AZ - 10), 4, 0.004 * k, 0.020 * k)
                q2, _ = e.head_point(s * (AZ - 10), bel(AZ - 10) + 2, 0.016 * k)
                tube_path(buf, [Mx @ V((0, 0.0, 0.022 * k)), q0, q1, q2], 0.0045 * k, M["dark"], W, segs=6,
                          cap0="flat", cap1="flat")
            if mic:
                s = 1 if side == "L" else -1
                p, nn = cups[s]
                Mx = Matrix.Translation(p) @ elf.frame(nn, (0, 0, 1))
                path = [Mx @ V((0.0, -0.014 * k, -0.016 * k)),
                        self.lift(s * 70, -40, 0.006 * k, 0.020 * k)[0],
                        self.lift(s * 46, -48, 0.006 * k, 0.020 * k)[0],
                        e.head_point(s * 28, -47, 0.018 * k)[0]]
                tube_path(buf, path, 0.0028 * k, M["dark"], W, segs=6, cap0="flat")
                tip = path[-1]
                elf.rbox(buf, (0.013 * k, 0.010 * k, 0.010 * k),
                         Matrix.Translation(tip) @ elf.frame(e.head_point(s * 28, -47)[1], (0, 0, 1)), mat=M["shell"],
                         w=W, r=0.3, segs=0)
        e.part(name, "head", fn)

    # ------------------------------------------------------------------ export
    def export(self, rel_path, *, outline=0.006, props=None, preview=None):
        """finalize + 내보내기. 환경 변수 R41_PREVIEW=1이면 무기를 든 미리보기 <이름>_preview.glb만 만든다(커밋 안 함).
        preview = {"socket_hand_R": "weapons/r41/r41_carbine.glb", ..., "pose": "rifle"|"pistol"|"shield"}"""
        e = self.e
        e.finalize()
        pr = {"faction": "r41"}
        pr.update(props or {})
        if os.environ.get("R41_PREVIEW") and preview:
            self._preview(preview)
            rel_path = rel_path.replace(".glb", "_preview.glb")
        out = e.export(rel_path, outline=outline, props=pr)
        return out

    POSES = {
        # 낮은 준비 자세 (소총·산탄총): 오른손이 손잡이, 왼손이 총열 아래로
        "rifle": {"upperarm_R": (48, 0, 22), "forearm_R": (62, 0, 0), "hand_R": (-12, 0, 0),
                  "upperarm_L": (62, 0, -38), "forearm_L": (52, 0, 0), "hand_L": (0, 0, 0)},
        "pistol": {"upperarm_R": (40, 0, 28), "forearm_R": (55, 0, 0), "hand_R": (-20, 0, 0),
                   "upperarm_L": (10, 0, 0), "forearm_L": (20, 0, 0)},
        "shield": {"upperarm_R": (40, 0, 24), "forearm_R": (58, 0, 0), "hand_R": (-14, 0, 0),
                   "upperarm_L": (55, 0, -10), "forearm_L": (70, 0, 0), "hand_L": (-10, 0, 0)},
    }

    def _preview(self, spec):
        """미리보기: 포즈 액션('pose') + 소켓에 무기 glb를 붙인다. 뷰어에서 --anim pose로 본다."""
        import bpy
        e = self.e
        rots = dict(self.POSES[spec.get("pose", "rifle")])
        for side in ("L", "R"):   # 주먹
            for f in ("f1", "f2", "f3"):
                rots[f"{f}_01_{side}"] = (70, 0, 0)
                rots[f"{f}_02_{side}"] = (80, 0, 0)
            rots[f"thumb_01_{side}"] = (25, 0, 0)
            rots[f"thumb_02_{side}"] = (40, 0, 0)
        e.pose(rots)
        for sock, rel in spec.items():
            if not sock.startswith("socket_"):
                continue
            before = set(bpy.data.objects)
            bpy.ops.import_scene.gltf(filepath=os.path.join(cb.MODELS_DIR, rel))
            new = [o for o in bpy.data.objects if o not in before]
            roots = [o for o in new if o.parent is None]
            s = bpy.data.objects[sock]
            for r in roots:
                r.parent = s
                r.matrix_parent_inverse = Matrix.Identity(4)
                r.location = (0, 0, 0)
                r.rotation_mode = "XYZ"
                r.rotation_euler = (0, 0, 0)
