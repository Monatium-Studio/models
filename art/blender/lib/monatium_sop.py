"""모나티엄 진압반 특수작전부(SOP) 현장 복장·장비 모듈 (monatium_sop).

[오리지널] 교주 차원 모나티엄 진압반 산하 '특수작전부'(정찰·침투·표적 지정)의 현장 복장과 장비.
진압반 시각 언어(docs/art/reference-notes.md 6장: 자줏빛 회색 장비, 남보라 지휘색, 금색은 지휘관만)를
바탕으로 정찰 부서 요소(청록 부서 스카프, HUD 헤드셋, 낮은 가슴 장비, 나침반 바늘 휘장)를 더했다.
설정·디자인 근거: docs/art/characters-rita-squad.md

    import monatium_sop as sop
    M = sop.mats("rita")
    sop.uniform(e, M)                 # 전투복 상하의·군화·벨트 + 팔(소매·장갑·휘장)
    sop.scarf(e, M, style="tails")   # 부서 스카프 (tails | neat | cowl | arm)
    sop.headset(e, M, monocle=True)  # HUD 헤드셋 (모나티엄 네트워크 단말)
    sop.chest_rig(e, M)

1인칭 팔 뷰모델 도구(Viewmodel)도 여기에 있다. 무기 glb의 fpOffset·fpRot·grip_support를 읽어
오른손을 무기 원점에, 왼손을 grip_support에 맞춘 포즈 클립을 만든다 (viewmodels/rita*.py).

R41(docs/art/r41-style.md)과의 구분: R41은 밝은 회색 전투복·헬멧 + 앰버 휘장 + 마젠타 기계 발광 + 모따기 형태.
특수작전부는 어두운 남보라 회색 전투복 + 청록 스카프 + 시안 발광 + 둥근 덩어리 + 붉은 갈색 먹선.
"""
from __future__ import annotations

import json
import math
import os
import struct
import sys

import bpy
from mathutils import Euler, Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb  # noqa: E402
import elf  # noqa: E402
from elf import Buf, band, catmull, disc, frame, lerp, loft, mixw, rbox, smoothstep  # noqa: E402,F401

V = Vector

# =========================================================================== palette

PAL = {
    # 천: 진압반 남보라(#706478) 계열의 회보라. R41의 밝은 회색 전투복(#9e9aa1)보다 채도가 있고 바지는 훨씬 어둡다
    "cloth": "#8f8597",      # 전투복 상의
    "cloth_d": "#6d6375",    # 깃·여밈·소맷단
    "pants": "#625969",
    "pants_d": "#4f4757",
    # 장비: 원작 진압반 자줏빛 회색 (#655d64, #4b424a)을 천보다 한 단 어둡게 (천과 장비가 명도로 갈리게)
    "gear": "#433c44",       # 조끼·웨빙·끈
    "gear_l": "#5f575f",     # 파우치 덮개·보호대
    "gear_d": "#312b32",     # 몰리 띠·그늘
    "belt": "#342d34",
    "metal": "#cfcac4",      # 은색 금속 (일반 반원은 은색만)
    "gold": "#d6b25e",       # 금색: 지휘관(분대장)만
    "boots": "#4a4148",
    "boots_d": "#3a333a",
    "sole": "#2a252b",
    "tab": "#b9b2a8",
    "glove": "#4f6f6d",      # 장갑: 부서 청록을 누른 회청록 (검은 총몸·보라 소매와 갈림. R41은 손가락 없는 검은 장갑)
    # 부서 표식: 청록 스카프 (모나티엄 네트워크·창고 관리색 계열, 시안 발광과 짝)
    "scarf": "#3f9a94",
    "scarf_d": "#2f7671",
    "unit": "#706478",       # 남보라 패치 바탕 (진압반 지휘색)
    "lens": "#26303a",       # 꺼진 렌즈·화면
    "tan": "#b9a98a",        # 지도·종이·밧줄
    "hazard": "#e8c34a",     # 폭파 경고 띠 (교주 측 노랑. R41은 노랑을 쓰지 않는다)
    "charge": "#d9cfb0",     # 폭약 블록
    "olive": "#7d7a5c",      # 위장 천 조각 (지정사수)
    "white": "#ebe6de",      # 의무 표식 (흰 십자 대신 흰 더하기 막대를 청록 원 위에)
    "glow": "#7ff0ea",       # 시안 발광 (UNLIT)
}


def mats(prefix: str, over: dict | None = None) -> dict:
    """PAL로 머티리얼 사전. over={"cloth": "#..."}로 개인별 색을 바꾼다. 'glow'는 UNLIT."""
    pal = dict(PAL)
    pal.update(over or {})
    M = {}
    for k, v in pal.items():
        if k == "glow":
            M[k] = elf.mat(f"{prefix}_glow", "#ffffff", emission=v, unlit=True)
        else:
            M[k] = elf.mat(f"{prefix}_{k}", v)
    return M


# =========================================================================== geometry helpers

def tube(buf, pts, r0, r1=None, *, segs=8, n=None, mat=None, w=None, cap0="round", cap1="round", ref=(0, 0, 1)):
    """제어점을 지나는 원형 관 (안테나, 줄, 손잡이). w: 웨이트 사전 또는 t→사전."""
    pts = [V(p) for p in pts]
    n = n or max(4, len(pts) * 3)
    P = catmull(pts, n) if len(pts) > 2 else [pts[0].lerp(pts[1], i / (n - 1)) for i in range(n)]
    r1 = r0 if r1 is None else r1
    st = []
    for i, c in enumerate(P):
        t = i / (n - 1)
        st.append({"c": c, "rx": lerp(r0, r1, t), "ry": lerp(r0, r1, t), "w": w(t) if callable(w) else (w or {})})
    return loft(buf, st, segs=segs, cap0=cap0, cap1=cap1, mat=mat, ref=ref)


def torus(buf, c, rx, ry, rt, *, segs=24, tsegs=8, mat=None, wfn=None, squash=1.0, lump=0.0, lumps=5,
          drop=0.0):
    """수평 타원 고리(스카프 고리, 감은 줄). rt: 관 반지름, squash: 관 세로 배율, lump: 천 주름 굴곡,
    drop: 앞쪽(-Y)을 이만큼 아래로 처지게."""
    c = V(c)
    rings = []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        rad = V((math.sin(a), -math.cos(a), 0.0))
        cc = c + V((rx * math.sin(a), -ry * math.cos(a), -drop * max(0.0, math.cos(a)) ** 2))
        r = rt * (1 + lump * math.sin(lumps * a + 0.7))
        ring = []
        for j in range(tsegs):
            b = 2 * math.pi * j / tsegs
            p = cc + rad * (r * math.cos(b)) + V((0, 0, r * squash * math.sin(b)))
            ring.append(buf.vert(p, wfn(p) if wfn else {}))
        rings.append(ring)
    for i in range(segs):
        r0, r1 = rings[i], rings[(i + 1) % segs]
        for j in range(tsegs):
            j2 = (j + 1) % tsegs
            buf.face((r0[j], r1[j], r1[j2], r0[j2]), mat)


def ribbon(buf, pts, nrms, width, th, *, mat=None, w=None, n=None, twist=None):
    """점들을 지나는 납작한 띠 (스카프 꼬리, 끈). nrms: 바깥 법선(점마다). twist(t)→도: 띠 비틀기."""
    pts = [V(p) for p in pts]
    n = n or max(6, len(pts) * 4)
    P = catmull(pts, n)
    N = catmull([V(x) for x in nrms], n)
    ups = []
    for i in range(n):
        tan = P[min(i + 1, n - 1)] - P[max(i - 1, 0)]
        nn = N[i].normalized()
        u = tan.cross(nn).normalized() if tan.length > 1e-9 else V((1, 0, 0))
        if twist:
            ang = math.radians(twist(i / (n - 1)))
            q = Matrix.Rotation(ang, 3, tan.normalized())
            u = q @ u
            nn = q @ nn
        N[i] = nn
        ups.append(u)
    elf._loop(buf, P, N, ups, width, th, mat=mat, w=w, closed=False)


def torso_panel(e, mat, z0, z1, a0, a1, *, off=0.02, th=0.012, rows=4, cols=9, bulge=0.0, name="panel",
                group="body", round_=0.25):
    """몸통을 감싸는 휜 판 (가슴 장비 판, 방탄판, 등판). a0~a1: 각도(0=앞), z0~z1: 높이. 모서리 살짝 둥글림."""
    k = e.k

    def fn(buf):
        top, bot = [], []
        for i in range(rows):
            u = i / (rows - 1)
            z = lerp(z0, z1, u)
            rt, rb = [], []
            for j in range(cols):
                v = j / (cols - 1)
                a = lerp(a0, a1, v)
                # 모서리 둥글림: 네 귀퉁이를 안쪽으로
                cu = abs(u * 2 - 1)
                cv = abs(v * 2 - 1)
                corner = max(0.0, (cu ** 6 + cv ** 6) ** (1 / 6) - (1 - round_)) / max(round_, 1e-3)
                zz = lerp(z, (z0 + z1) / 2, 0.18 * corner * cu)
                aa = lerp(a, (a0 + a1) / 2, 0.10 * corner * cv)
                bul = bulge * k * math.sin(math.pi * u) * math.sin(math.pi * v)
                p, nrm = e.torso_point(zz, aa, off * k + bul)
                wv = e._torso_wfn(p, 0)
                rb.append(buf.vert(p, wv))
                rt.append(buf.vert(p + nrm * th * k * (1 - 0.35 * corner), wv))
            top.append(rt)
            bot.append(rb)
        for i in range(rows - 1):
            for j in range(cols - 1):
                buf.face((top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1]), mat)
                buf.face((bot[i][j], bot[i][j + 1], bot[i + 1][j + 1], bot[i + 1][j]), mat)
        for i in range(rows - 1):
            for j, flip in ((0, False), (cols - 1, True)):
                q = (top[i][j], bot[i][j], bot[i + 1][j], top[i + 1][j])
                buf.face(tuple(reversed(q)) if flip else q, mat)
        for j in range(cols - 1):
            for i, flip in ((0, False), (rows - 1, True)):
                q = (top[i][j], top[i][j + 1], bot[i][j + 1], bot[i][j])
                buf.face(tuple(reversed(q)) if flip else q, mat)
    return e.part(name, group, fn)


def head_arc(e, phi, off, tilt=12.0):
    """머리 위를 넘는 원호 위의 점. phi: -90(오른쪽 귀 위) ~ 0(정수리) ~ +90(왼쪽), tilt: 뒤로 기울임(도)."""
    a, t = math.radians(phi), math.radians(tilt)
    d = V((math.sin(a), math.sin(t) * math.cos(a), math.cos(t) * math.cos(a))).normalized()
    c = e.head_c
    hit = e.head_bvh.ray_cast(c + d * 1.0, -d)
    if hit[0] is None:
        return c + d * (e.hh / 2 + off), d
    n = hit[1].normalized()
    return hit[0] + n * off, n


# =========================================================================== insignia

def emblem(e, M, at, *, size=0.036, name="sop_emblem", lift=0.0):
    """특수작전부 휘장: 남보라 원형 패치 + 은색 나침반 바늘(세로로 긴 마름모) + 청록 중심점.
    '먼저 들어가 길을 가리키는 사람'. 원작 문양과 겹치지 않는 기하 도형만 쓴다."""
    k = e.k
    e.patch(M["unit"], at, size=(size, size), shape="round", name=f"{name}_bg", lift=lift)
    e.patch(M["metal"], at, size=(size * 0.30, size * 0.80), shape="diamond", name=f"{name}_needle",
            lift=lift + 0.0016)
    e.patch(M["scarf"], at, size=(size * 0.20, size * 0.20), shape="round", name=f"{name}_dot", lift=lift + 0.0032)
    return k


def rank(e, M, at, *, bars=1, gold=False, size=0.026, name="rank"):
    """계급장: 남보라 사각 바탕 + 은색(일반) 또는 금색(지휘관) 막대."""
    e.patch(M["unit"], at, size=(size, size * 0.78), name=f"{name}_bg")
    shape = {1: "rect", 2: "bars2", 3: "bars3"}.get(bars, "chevron")
    sz = (size * 0.66, size * 0.16) if bars == 1 else (size * 0.66, size * 0.52)
    e.patch(M["gold" if gold else "metal"], at, size=sz, shape=shape, name=f"{name}_fg", lift=0.0016)


# =========================================================================== uniform

def arms(e, M, *, sleeve_len=0.95, roll=False, emblem_on=True, rank_bars=1, gold=False, wrist_pad=False,
         arm_band=None, elbow_pads=False):
    """팔 그룹 전부 (소매, 장갑, 팔 휘장·계급장, 손목 단말). 3인칭 전신과 1인칭 팔이 반드시 같은 함수를 쓴다.
    roll=True: 소매를 걷어 올린 모양(분대원 변형). arm_band: 'L'|'R' 위팔에 청록 띠."""
    k = e.k
    if roll:
        e.sleeves(M["cloth"], length=0.62, cuff=(M["cloth_d"], 0.040, 0.008), puff=0.004)
    else:
        e.sleeves(M["cloth"], length=sleeve_len, cuff=(M["cloth_d"], 0.022, 0.0045))
    e.gloves(M["glove"], cuff=M["gear"])
    sleeve_lining(e, M["cloth_d"], 0.62 if roll else sleeve_len, flare=0.006, puff=0.004 if roll else 0.0)
    so = 0.010 * k + 0.0015   # 소매 표면
    if emblem_on:
        emblem(e, M, ("arm_L", 0.17, 62, so), name="arm_emblem")
    if rank_bars:
        rank(e, M, ("arm_R", 0.17, -62, so), bars=rank_bars, gold=gold, name="arm_rank")
    if arm_band:
        e.ring(M["scarf"], f"arm_{arm_band}", 0.36, h=0.018, th=0.004, off=0.012, name=f"arm_band_{arm_band}")
    if elbow_pads:
        for sd in ("L", "R"):
            e.pad(M["gear_l"], (f"arm_{sd}", 0.53, 180, 0.013 * k), size=(0.05, 0.014, 0.05), strap=None,
                  name=f"elbow_pad_{sd}")
    if wrist_pad:
        # 왼 손목 안쪽 단말: 나침반 + 작은 지도 화면 (총을 쥐면 손바닥이 위로 와서 1인칭에 보인다)
        def wp(buf, Mx, w):
            rbox(buf, (0.040 * k, 0.010 * k, 0.034 * k), Mx @ Matrix.Translation((0, -0.004 * k, 0)), mat=M["gear"],
                 w=w, r=0.35, segs=1)
            rbox(buf, (0.032 * k, 0.004 * k, 0.026 * k), Mx @ Matrix.Translation((0, -0.0105 * k, 0)),
                 mat=M["gear_d"], w=w, r=0.35, segs=1)
            n = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
            up = Mx.to_3x3() @ V((0, 0, 1))
            c = Mx @ V((0, -0.0128 * k, 0))
            disc(buf, c, n, up, 0.0105 * k, 0.0105 * k, 0.0008 * k, segs=14, mat=M["lens"], w=w)
            disc(buf, c + n * 0.0008 * k, n, up, 0.0016 * k, 0.0085 * k, 0.0006 * k, segs=4, mat=M["glow"], w=w)
            # 손목 끈
        # 소매(off 0.010 + 끝 퍼짐) 바깥에 얹는다
        e.gear("wrist_pad", ("arm_L", 0.82, -90, 0.0175 * k), wp)
        e.ring(M["gear"], "arm_L", 0.82, h=0.012, th=0.003, off=0.0165, name="wrist_pad_band")


def sleeve_lining(e, mat, length, *, off=0.010, flare=0.006, puff=0.0, name="sleeve_lining"):
    """소매 끝 안감 고리: 소매 안쪽과 장갑 손목 사이 틈을 막는다 (1인칭에서 소매 속 맨살이 비치지 않게).
    키트 소매(e.sleeves)와 같은 반지름 식을 쓴다. 키트에 올릴 후보."""
    k = e.k
    for side in ("L", "R"):
        ch = e.arm_chain(side)
        t = length - 0.012
        c, tan = ch.at(t)
        rx, ry = e.arm_r(t)
        ex = (flare * smoothstep(length - 0.35, length, t) + puff * math.sin(math.pi * elf.clamp(t / 0.5))) * k
        r_out = off * k + ex

        def fn(buf, c=c, tan=tan, rx=rx, ry=ry, ch=ch, t=t, r_out=r_out):
            # 안쪽 반지름 = 팔 표면 살짝 안, 두께 = 소매 안쪽 면까지
            band(buf, c, tan, (0, -1, 0), rx * 0.92, ry * 0.92, 0.012 * k, r_out + rx * 0.08 - 0.0015, segs=e._s(16),
                 mat=mat, w=ch.weights(t))
        e.part(f"{name}_{side}", "arms", fn)


def uniform(e, M, *, hem=None, pants_bag=0.013, blouse=0.020, boots_top=0.64, buttons=True, arms_kw=None,
            knee_pads=True, belt=True, lean=False):
    """특수작전부 전투복 일체: 상의(차이나 칼라, 앞여밈), 바지(블라우징), 군화, 벨트, 무릎 보호대, 팔.
    lean=True: 분대원 예산용 (군화 끈판·벨트 고리·보호대 끈 생략)."""
    k = e.k
    e.shirt(M["cloth"], hem=hem, collar="stand", collar_mat=M["cloth_d"], placket=M["cloth_d"],
            buttons=M["metal"] if buttons else None, flare=0.012)
    arms(e, M, **(arms_kw or {}))
    e.pants(M["pants"], bag=pants_bag, blouse=blouse)
    e.boots(M["boots"], top=boots_top, sole=(M["sole"], 0.017), cuff=M["boots_d"],
            laces=None if lean else M["boots_d"], tab=M["tab"])
    if belt:
        e.belt(M["belt"], buckle=M["metal"], loops=None if lean else M["belt"])
    if knee_pads:
        for sd in ("L", "R"):
            e.pad(M["gear_l"], (f"leg_{sd}", 0.535, 0, 0.022 * k), size=(0.066, 0.017, 0.064),
                  strap=None if lean else M["gear"], name=f"knee_pad_{sd}")


# =========================================================================== department scarf

def scarf(e, M, *, style="tails", knot_az=150.0, tail_len=(0.20, 0.15), width=0.056, rt=0.020, color=None,
          sway=1.0, name="scarf"):
    """특수작전부 청록 스카프. 같은 천을 사람마다 다르게 맨다.
    tails: 목에 감고 뒤로 긴 꼬리 둘 (리타) / neat: 앞 매듭 + 짧은 꼬리 (분대장) /
    cowl: 어깨까지 덮는 두꺼운 두건 고리 (지정사수) / arm: 왼팔 위팔에 묶음 (통신·폭파)."""
    k = e.k
    m = color or M["scarf"]
    md = M["scarf_d"]
    if style == "arm":
        ch = e.arm_chain("L")
        t = 0.30
        c, tan = ch.at(t)
        rx, ry = e.arm_r(t)

        def fn(buf):
            o = 0.012 * k
            band(buf, c, tan, (0, -1, 0), rx + o, ry + o, 0.034 * k, 0.007 * k, segs=e._s(16), mat=m,
                 w=ch.weights(t))
            # 매듭 + 꼬리 두 가닥 (바깥쪽으로 늘어짐)
            p, nn = e.limb_point("arm_L", t, 90, o + 0.008 * k)
            rbox(buf, (0.026 * k, 0.018 * k, 0.022 * k), Matrix.Translation(p) @ frame(nn, -tan), mat=md,
                 w=ch.weights(t), r=0.45, segs=1)
            for j, (ln, sp) in enumerate(((0.07, -8), (0.055, 14))):
                pts = [p, p + nn * 0.01 * k + tan * 0.02 * k + V((0, sp * 0.001 * k, 0)),
                       p + nn * 0.016 * k + tan * ln * k + V((0, sp * 0.0022 * k, -0.01 * k))]
                ribbon(buf, pts, [nn, nn, nn], 0.022 * k, 0.004 * k, mat=m, w=ch.weights(t), n=7)
        return e.part(name, "arms", fn)

    z = e.torso_top - 0.004 * k
    rx0, ry0, cy0 = e.torso_at(e.torso_top - 0.03 * k)

    def neck_w(p):
        # 목 고리: 가슴과 목 사이 (고개를 돌려도 크게 찢어지지 않게)
        return {"chest": 0.65, "neck": 0.35}

    def fn_loop(buf):
        if style == "cowl":
            torus(buf, (0, cy0 + 0.004 * k, z - 0.012 * k), 0.092 * k, 0.082 * k, rt * 1.45 * k, segs=e._s(26),
                  tsegs=8, mat=m, wfn=neck_w, squash=0.85, lump=0.10, lumps=6, drop=0.012 * k)
            torus(buf, (0, cy0 + 0.002 * k, z + 0.014 * k), 0.070 * k, 0.062 * k, rt * 1.05 * k, segs=e._s(22),
                  tsegs=7, mat=m, wfn=neck_w, squash=0.9, lump=0.08, lumps=5)
        else:
            torus(buf, (0, cy0 + 0.003 * k, z), 0.071 * k, 0.064 * k, rt * k, segs=e._s(26), tsegs=8, mat=m,
                  wfn=neck_w, squash=0.95, lump=0.09, lumps=5, drop=0.008 * k)
    e.part(f"{name}_loop", "head", fn_loop)

    if style in ("tails", "neat", "cowl"):
        az = {"tails": knot_az, "neat": 18.0, "cowl": 200.0}[style]
        a = math.radians(az)
        # 매듭: 고리 바깥
        kx, ky = math.sin(a), -math.cos(a)
        knot = V((kx * (0.071 * k + rt * k * 0.9), cy0 + 0.003 * k + ky * (0.064 * k + rt * k * 0.9), z - 0.004 * k))
        nk = V((kx, ky, 0.15)).normalized()
        lens = tail_len if style != "neat" else (0.07, 0.055)
        if style == "cowl":
            lens = (0.10, 0.08)

        def fn_tails(buf):
            wk = e._torso_wfn(knot, 0)
            rbox(buf, (0.034 * k, 0.026 * k, 0.030 * k), Matrix.Translation(knot + nk * 0.006 * k) @ frame(nk),
                 mat=md, w=wk, r=0.45, segs=1)
            for j, ln in enumerate(lens):
                sgn = -1 if j == 0 else 1
                da = sgn * (14 + 10 * j)
                pts, nrm = [], []
                N = 6
                for i in range(N):
                    u = i / (N - 1)
                    zz = knot.z - 0.012 * k - ln * k * u
                    zz = max(zz, e.waist_z - 0.04 * k)
                    ang = az + da * u + sway * 14 * math.sin(u * 2.4 + j) * u
                    lift = (0.030 + (0.055 * u * u) * sway + 0.008 * j) * k
                    if style == "neat":
                        ang = az + sgn * (6 + 18 * u)
                        lift = (0.030 + 0.010 * u) * k
                    p, nn = e.torso_point(zz, ang, lift)
                    pts.append(p)
                    nrm.append(nn)
                pts[0] = knot + nk * 0.004 * k
                wv = lambda t, pts=pts: e._torso_wfn(pts[min(int(t * (len(pts) - 1)), len(pts) - 1)], 0)  # noqa: E731
                tw = (lambda t, j=j: (14 + 10 * j) * math.sin(t * 3.0) * sway)
                ribbon(buf, pts, nrm, width * k * (1 - 0.12 * j), 0.005 * k, mat=m, w=wv, n=10, twist=tw)
                # 꼬리 끝단 (짙은 술)
                p_end = pts[-1]
                rbox(buf, (width * k * 0.95, 0.007 * k, 0.010 * k),
                     Matrix.Translation(p_end + V((0, 0, -0.004 * k))) @ frame(nrm[-1]), mat=md, w=wv(1.0), r=0.3,
                     segs=1)
        e.part(f"{name}_tails", "body", fn_tails)


# =========================================================================== headset (Monatium network HUD)

def headset(e, M, *, side="R", monocle=True, mic=False, off=0.0235, tilt=0.0, band=True, pad=True, span=72.0,
            pod_off=0.046, name="headset"):
    """모나티엄 네트워크 HUD 헤드셋. 머리 위 밴드 + 귀 위 단말(청록 LED) + 접어 올린 HUD 렌즈(monocle) 또는 붐 마이크.
    엘프 귀는 단말 아래로 나온다. side: 단말 쪽('R' 캐릭터 오른쪽)."""
    k = e.k
    s = 1 if side == "L" else -1
    o = off * k

    def fn(buf):
        w = {"head": 1.0}
        if band:
            pts, nrm = [], []
            N = 17
            for i in range(N):
                phi = -span + 2 * span * i / (N - 1)
                oo = o + (pod_off * k - o) * smoothstep(0.6, 1.0, abs(phi) / span)
                p, n = head_arc(e, phi, oo, tilt)
                pts.append(p)
                nrm.append(n)
            ups = []
            for i in range(N):
                tan = pts[min(i + 1, N - 1)] - pts[max(i - 1, 0)]
                ups.append(tan.cross(nrm[i]).normalized())
            elf._loop(buf, pts, nrm, ups, 0.015 * k, 0.0055 * k, mat=M["gear"], closed=False, w=w)
        for sd in (1, -1):
            main = sd == s
            p, n = head_arc(e, sd * (span + 6), pod_off * k, tilt)
            fw = V((0, -1, 0))
            if main:
                Mx = Matrix.Translation(p + n * 0.004 * k) @ frame(n, (0, 0, 1))
                rbox(buf, (0.044 * k, 0.026 * k, 0.050 * k), Mx, mat=M["gear"], w=w, r=0.45, segs=2)
                rbox(buf, (0.032 * k, 0.010 * k, 0.036 * k), Mx @ Matrix.Translation((0, -0.015 * k, 0)),
                     mat=M["gear_l"], w=w, r=0.4, segs=1)
                nn = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
                c = Mx @ V((sd * 0.008 * k, -0.0205 * k, 0.010 * k))
                disc(buf, c, nn, (0, 0, 1), 0.0045 * k, 0.0045 * k, 0.0012 * k, segs=10, mat=M["glow"], w=w)
                disc(buf, Mx @ V((-sd * 0.006 * k, -0.0205 * k, -0.008 * k)), nn, (0, 0, 1), 0.003 * k, 0.003 * k,
                     0.0012 * k, segs=8, mat=M["metal"], w=w)
                if monocle:
                    # 접어 올린 HUD 렌즈: 단말 앞에서 눈썹 바깥 위로 (눈과 표정을 가리지 않는다)
                    a0 = Mx @ V((0, -0.006 * k, 0.020 * k))
                    p1, n1 = e.head_point(sd * 68, 26, 0.050 * k)
                    p2, n2 = e.head_point(sd * 42, 22, 0.052 * k)
                    tube(buf, [a0, p1, p2], 0.0048 * k, 0.0040 * k, segs=6, mat=M["gear"], w=w)
                    ln = V((sd * 0.30, -0.72, 0.62)).normalized()
                    lc = p2 + ln * 0.004 * k
                    up = V((0, 0.62, 0.72))
                    disc(buf, lc, ln, up, 0.025 * k, 0.020 * k, 0.008 * k, segs=18, mat=M["gear"], w=w)
                    disc(buf, lc + ln * 0.008 * k, ln, up, 0.019 * k, 0.0145 * k, 0.0012 * k, segs=18,
                         mat=M["glow"], w=w)
                    disc(buf, lc + ln * 0.0094 * k, ln, up, 0.013 * k, 0.0045 * k, 0.0008 * k, segs=10,
                         mat=M["lens"], w=w)
                    # 렌즈 경첩
                    rbox(buf, (0.012 * k, 0.010 * k, 0.010 * k), Matrix.Translation(p2 - ln * 0.002 * k + up.normalized() * 0.016 * k),
                         mat=M["gear_d"], w=w, r=0.45, segs=1)
                if mic:
                    a0 = Mx @ V((0, -0.010 * k, -0.016 * k))
                    p1, _ = e.head_point(sd * 70, -30, 0.040 * k)
                    p2, _ = e.head_point(sd * 34, -52, 0.034 * k)
                    tube(buf, [a0, p1, p2], 0.0035 * k, 0.003 * k, segs=6, mat=M["gear_d"], w=w)
                    rbox(buf, (0.012 * k, 0.012 * k, 0.010 * k), Matrix.Translation(p2) @ frame(V((0, -1, 0))),
                         mat=M["gear"], w=w, r=0.5, segs=1)
            elif pad:
                Mx = Matrix.Translation(p + n * 0.006 * k) @ frame(n, (0, 0, 1))
                rbox(buf, (0.030 * k, 0.014 * k, 0.034 * k), Mx, mat=M["gear"], w=w, r=0.45, segs=1)
            del fw
    return e.part(name, "head", fn)


# =========================================================================== chest & belt gear

def harness(e, M, *, z=None, name="harness"):
    """Y자 멜빵 (앞 가슴 → 어깨 → 등 가운데로 모임)."""
    k = e.k
    cz = e.chest_z
    sz = e.shoulder_z
    pz = z if z is not None else cz + 0.012 * k
    for s in (1, -1):
        e.strap(M["gear"], [("torso", pz, s * 30, 0.020 * k), ("torso", sz - 0.005 * k, s * 40, 0.015 * k),
                            ("torso", sz + 0.02 * k, s * 58, 0.015 * k), ("torso", sz - 0.01 * k, s * 122, 0.015 * k),
                            ("torso", cz, s * 150, 0.017 * k), ("torso", e.waist_z + 0.02 * k, s * 155, 0.021 * k)],
                width=0.020, th=0.0045, name=f"{name}_{'L' if s > 0 else 'R'}")


def knife(e, M, at, *, name="knife", tilt=0.0):
    """거꾸로 단 칼집 (손잡이 위). 가슴 멜빵에 단다."""
    k = e.k

    def fn(buf, Mx, w):
        Mx = Mx @ Matrix.Rotation(math.radians(tilt), 4, "Y")
        rbox(buf, (0.022 * k, 0.010 * k, 0.074 * k), Mx @ Matrix.Translation((0, -0.006 * k, -0.018 * k)),
             mat=M["gear_d"], w=w, r=0.4, segs=1, taper=-0.25)
        rbox(buf, (0.026 * k, 0.004 * k, 0.012 * k), Mx @ Matrix.Translation((0, -0.012 * k, 0.000 * k)),
             mat=M["gear"], w=w, r=0.3, segs=1)
        a = Mx @ V((0, -0.008 * k, 0.020 * k))
        b = Mx @ V((0, -0.008 * k, 0.050 * k))
        tube(buf, [a, b], 0.0075 * k, 0.0068 * k, segs=8, mat=M["belt"], w=w, cap0="flat", cap1="flat")
        up = (Mx.to_3x3() @ V((0, 0, 1))).normalized()
        # 손잡이 끝: 어두운 금속 (1인칭에서 내려다볼 때 흰 원판처럼 튀지 않게)
        disc(buf, b, up, Mx.to_3x3() @ V((1, 0, 0)), 0.0080 * k, 0.0080 * k, 0.004 * k, segs=10, mat=M["gear_l"],
             w=w)
    return e.gear(name, at, fn)


def holster(e, M, *, side="R", t=0.26, name="holster"):
    """허벅지 권총집 (다리 고정 끈 2줄). 권총 손잡이 끝이 보인다."""
    k = e.k
    sgn = 1 if side == "L" else -1
    leg = f"leg_{side}"
    ch = e.leg_chain(side)

    def fn(buf, Mx, w):
        rbox(buf, (0.052 * k, 0.010 * k, 0.090 * k), Mx @ Matrix.Translation((0, -0.004 * k, -0.004 * k)),
             mat=M["gear"], w=w, r=0.3, segs=1)
        rbox(buf, (0.046 * k, 0.030 * k, 0.080 * k), Mx @ Matrix.Translation((0, -0.022 * k, -0.010 * k)),
             mat=M["gear_l"], w=w, r=0.35, segs=1, taper=0.12)
        # 덮개 끈 + 단추
        rbox(buf, (0.020 * k, 0.034 * k, 0.012 * k), Mx @ Matrix.Translation((0, -0.022 * k, 0.026 * k)),
             mat=M["gear"], w=w, r=0.4, segs=1)
        n = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
        disc(buf, Mx @ V((0, -0.040 * k, 0.024 * k)), n, Mx.to_3x3() @ V((0, 0, 1)), 0.004 * k, 0.004 * k,
             0.0015 * k, segs=8, mat=M["metal"], w=w)
        # 권총 손잡이 끝 (뒤로 기울어 나옴)
        g = Mx @ Matrix.Translation((0, -0.020 * k, 0.040 * k)) @ Matrix.Rotation(math.radians(-sgn * 0), 4, "Z") \
            @ Matrix.Rotation(math.radians(-18), 4, "X")
        rbox(buf, (0.026 * k, 0.022 * k, 0.040 * k), g @ Matrix.Translation((0, 0.004 * k, 0.012 * k)),
             mat=M["belt"], w=w, r=0.35, segs=1)
    e.gear(name, (leg, t, sgn * 82, 0.026 * k), fn)
    for j, tt in enumerate((t - 0.05, t + 0.08)):
        e.ring(M["gear"], leg, tt, h=0.013, th=0.0035, off=0.026, name=f"{name}_band{j}")
    del ch


def belt_kit(e, M, *, dump=True, canteen=True, pouches=(), name="beltkit"):
    """벨트 주변 장비: 뒤 허리 물통, 왼쪽 엉덩이 접은 덤프 파우치, 추가 파우치(angle 목록)."""
    k = e.k
    zb = lerp(e.hipj_z, e.waist_z, 0.72)
    if canteen:
        def cfn(buf, Mx, w):
            rbox(buf, (0.050 * k, 0.034 * k, 0.062 * k), Mx @ Matrix.Translation((0, -0.017 * k, -0.012 * k)),
                 mat=M["gear"], w=w, r=0.45, segs=2)
            rbox(buf, (0.054 * k, 0.036 * k, 0.024 * k), Mx @ Matrix.Translation((0, -0.018 * k, 0.020 * k)),
                 mat=M["gear_l"], w=w, r=0.4, segs=1)
            n = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
            disc(buf, Mx @ V((0, -0.0375 * k, 0.018 * k)), n, Mx.to_3x3() @ V((0, 0, 1)), 0.004 * k, 0.004 * k,
                 0.0015 * k, segs=8, mat=M["metal"], w=w)
        e.gear(f"{name}_canteen", ("torso", zb - 0.006 * k, -150, 0.024 * k), cfn)
    if dump:
        def dfn(buf, Mx, w):
            rbox(buf, (0.060 * k, 0.026 * k, 0.040 * k), Mx @ Matrix.Translation((0, -0.013 * k, -0.026 * k)),
                 mat=M["gear_l"], w=w, r=0.5, segs=2)
            rbox(buf, (0.064 * k, 0.012 * k, 0.014 * k), Mx @ Matrix.Translation((0, -0.022 * k, -0.010 * k)),
                 mat=M["gear"], w=w, r=0.4, segs=1)
        e.gear(f"{name}_dump", ("torso", zb - 0.01 * k, 118, 0.024 * k), dfn)
    for i, (ang, size) in enumerate(pouches):
        e.pouch(M["gear"], ("torso", zb - 0.004 * k, ang, 0.024 * k), size=size, flap=M["gear_l"],
                button=M["metal"], name=f"{name}_pouch{i}")


def chest_rig(e, M, *, n_mags=3, spread=24.0, mag_size=(0.034, 0.024, 0.056), panel=True, knife_on=True,
              harness_on=True, light=False, name="rig"):
    """낮은 가슴 장비: 휜 판 + 탄창 파우치(덮개·똑딱단추·몰리) + Y 멜빵 + 거꾸로 단 칼.
    1인칭으로 내려다보면(-60°) 파우치 덮개와 단추가 화면 아래에 보이는 높이다."""
    k = e.k
    cz = e.chest_z
    pz = cz + 0.010 * k
    if harness_on:
        harness(e, M)
    if panel:
        torso_panel(e, M["gear"], pz - 0.050 * k, pz + 0.040 * k, -44, 44, off=0.020, th=0.010, rows=4, cols=9,
                    name=f"{name}_panel")
        e.ring(M["gear"], "torso", pz - 0.048 * k, h=0.018, th=0.004, off=0.016, name=f"{name}_band")
    a0 = -spread * (n_mags - 1) / 2
    for i in range(n_mags):
        a = a0 + spread * i
        e.pouch(M["gear"], ("torso", pz - 0.004 * k, a, 0.031 * k), size=mag_size, flap=M["gear_l"],
                button=M["metal"], molle=M["gear_d"], name=f"{name}_mag{i}")
    if light:
        # 작은 표지 조명 (청록 LED, 꺼진 렌즈)
        def lfn(buf, Mx, w):
            rbox(buf, (0.018 * k, 0.016 * k, 0.026 * k), Mx @ Matrix.Translation((0, -0.008 * k, 0)), mat=M["gear_d"],
                 w=w, r=0.4, segs=1)
            n = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
            disc(buf, Mx @ V((0, -0.0165 * k, 0.004 * k)), n, Mx.to_3x3() @ V((0, 0, 1)), 0.0055 * k, 0.0055 * k,
                 0.0012 * k, segs=10, mat=M["glow"], w=w)
        e.gear(f"{name}_light", ("torso", e.shoulder_z - 0.012 * k, -40, 0.024 * k), lfn)
    if knife_on:
        knife(e, M, ("torso", cz + 0.062 * k, 31, 0.026 * k), name=f"{name}_knife", tilt=-8)


def plate_carrier(e, M, *, name="pc", admin=True, shoulder_pads=True):
    """분대장용 판 조끼: 앞·뒤 판 + 옆 띠 + 어깨 끈 + 행정 파우치(지도 창)."""
    k = e.k
    cz = e.chest_z
    z0, z1 = e.waist_z - 0.010 * k, e.shoulder_z - 0.004 * k
    torso_panel(e, M["gear"], z0, z1, -50, 50, off=0.022, th=0.016, rows=5, cols=11, bulge=0.004, name=f"{name}_front")
    torso_panel(e, M["gear"], z0 + 0.01 * k, z1 - 0.006 * k, 128, 232, off=0.022, th=0.016, rows=5, cols=11,
                bulge=0.004, name=f"{name}_back")
    for s in (1, -1):
        e.strap(M["gear"], [("torso", z1 - 0.010 * k, s * 36, 0.030 * k), ("torso", e.shoulder_z + 0.022 * k, s * 60, 0.020 * k),
                            ("torso", z1 - 0.010 * k, s * 140, 0.030 * k)], width=0.030, th=0.007,
                name=f"{name}_shoulder_{'L' if s > 0 else 'R'}")
        e.strap(M["gear_d"], [("torso", z0 + 0.03 * k, s * 50, 0.034 * k), ("torso", z0 + 0.03 * k, s * 90, 0.026 * k),
                              ("torso", z0 + 0.03 * k, s * 128, 0.034 * k)], width=0.040, th=0.006,
                name=f"{name}_cummer_{'L' if s > 0 else 'R'}")
        if shoulder_pads:
            e.pad(M["gear_l"], (f"arm_{'L' if s > 0 else 'R'}", 0.06, s * 70, 0.014 * k), size=(0.06, 0.016, 0.05),
                  name=f"{name}_spad_{'L' if s > 0 else 'R'}")
    if admin:
        def afn(buf, Mx, w):
            rbox(buf, (0.090 * k, 0.012 * k, 0.060 * k), Mx @ Matrix.Translation((0, -0.006 * k, 0)), mat=M["gear_l"],
                 w=w, r=0.25, segs=1)
            rbox(buf, (0.072 * k, 0.004 * k, 0.042 * k), Mx @ Matrix.Translation((0, -0.0125 * k, -0.002 * k)),
                 mat=M["tan"], w=w, r=0.2, segs=1)
            # 지도 위 경로 선 (남보라)
            for j, (x, zz, ang) in enumerate(((-0.018, 0.006, 20), (0.004, -0.004, -30), (0.020, 0.008, 60))):
                rbox(buf, (0.020 * k, 0.0012 * k, 0.003 * k),
                     Mx @ Matrix.Translation((x * k, -0.0148 * k, zz * k)) @ Matrix.Rotation(math.radians(ang), 4, "Y"),
                     mat=M["unit"], w=w, r=0.3, segs=1)
            rbox(buf, (0.094 * k, 0.014 * k, 0.012 * k), Mx @ Matrix.Translation((0, -0.008 * k, 0.034 * k)),
                 mat=M["gear"], w=w, r=0.4, segs=1)
        e.gear(f"{name}_admin", ("torso", cz + 0.012 * k, 0, 0.040 * k), afn)


def backpack_radio(e, M, *, name="radio", antenna_len=0.42):
    """통신병 무전기 배낭: 큰 둥근 상자 + 덮개 + 휘는 채찍 안테나 + 짧은 안테나 + 경고 테이프 + 송수화기."""
    k = e.k
    cz = e.chest_z

    def fn(buf, Mx, w):
        body = Mx @ Matrix.Translation((0, -0.060 * k, 0.010 * k))
        rbox(buf, (0.24 * k, 0.110 * k, 0.25 * k), body, mat=M["gear"], w=w, r=0.35, segs=2)
        rbox(buf, (0.25 * k, 0.116 * k, 0.060 * k), body @ Matrix.Translation((0, 0, 0.105 * k)), mat=M["gear_l"],
             w=w, r=0.4, segs=1)
        # 측면 주머니
        for sx in (-1, 1):
            rbox(buf, (0.034 * k, 0.080 * k, 0.14 * k), body @ Matrix.Translation((sx * 0.134 * k, 0, -0.03 * k)),
                 mat=M["gear_l"], w=w, r=0.4, segs=1)
        # 무전기 본체 노출면 (뒤 아래) + 손잡이 + 다이얼
        face = body @ Matrix.Translation((0, -0.057 * k, -0.045 * k))
        rbox(buf, (0.12 * k, 0.010 * k, 0.07 * k), face, mat=M["gear_d"], w=w, r=0.25, segs=1)
        n = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
        up = Mx.to_3x3() @ V((0, 0, 1))
        for j, x in enumerate((-0.035, -0.005, 0.025)):
            disc(buf, face @ V((x * k, -0.005 * k, 0.012 * k)), n, up, 0.009 * k, 0.009 * k, 0.006 * k, segs=10,
                 mat=M["metal"] if j != 1 else M["belt"], w=w)
        disc(buf, face @ V((0.038 * k, -0.005 * k, -0.014 * k)), n, up, 0.004 * k, 0.004 * k, 0.0014 * k, segs=8,
             mat=M["glow"], w=w)
        # 경고 테이프 (노랑-짙은 회색 줄무늬)
        for j in range(9):
            x = (j - 4) * 0.026 * k
            rbox(buf, (0.016 * k, 0.003 * k, 0.020 * k),
                 body @ Matrix.Translation((x, -0.0565 * k, 0.062 * k)) @ Matrix.Rotation(math.radians(35), 4, "Y"),
                 mat=M["hazard"] if j % 2 == 0 else M["belt"], w=w, r=0.2, segs=1)
        # 채찍 안테나: 큰 머리(헬멧)를 피해 뒤로 비스듬히 솟았다가 끝이 휜다 (분대에서 가장 높은 점)
        base = body @ V((0.085 * k, 0.020 * k, 0.130 * k))
        L = antenna_len * k
        side = (Mx.to_3x3() @ V((1, 0, 0))).normalized()
        back = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
        pts = [base, base + back * L * 0.22 + V((0, 0, L * 0.20)) + side * 0.01 * k,
               base + back * L * 0.45 + V((0, 0, L * 0.55)) + side * 0.03 * k,
               base + back * L * 0.62 + V((0, 0, L * 0.92)) + side * 0.05 * k]
        tube(buf, pts, 0.0055 * k, 0.0022 * k, segs=6, n=14, mat=M["belt"], w=w, cap0="flat")
        rbox(buf, (0.020 * k, 0.020 * k, 0.026 * k), Matrix.Translation(base + V((0, 0, 0.004 * k))), mat=M["gear_d"],
             w=w, r=0.4, segs=1)
        tip = pts[-1]
        rbox(buf, (0.010 * k, 0.010 * k, 0.010 * k), Matrix.Translation(tip), mat=M["scarf"], w=w, r=0.5, segs=1)
        # 짧은 안테나
        b2 = body @ V((-0.085 * k, 0.020 * k, 0.130 * k))
        tube(buf, [b2, b2 + back * 0.05 * k + V((0, 0, 0.09 * k))], 0.006 * k, 0.004 * k, segs=6, mat=M["belt"], w=w)
    e.gear(name, ("torso", cz - 0.015 * k, 180, 0.018 * k), fn)
    # 어깨끈 둘
    for s in (1, -1):
        e.strap(M["gear"], [("torso", cz + 0.02 * k, s * 26, 0.022 * k), ("torso", e.shoulder_z + 0.02 * k, s * 50, 0.018 * k),
                            ("torso", e.shoulder_z + 0.01 * k, s * 120, 0.02 * k), ("torso", cz + 0.03 * k, s * 160, 0.03 * k)],
                width=0.024, th=0.006, name=f"{name}_strap_{'L' if s > 0 else 'R'}")


def handset(e, M, at, *, name="handset"):
    """멜빵에 단 무전 송수화기 + 감긴 줄."""
    k = e.k

    def fn(buf, Mx, w):
        rbox(buf, (0.026 * k, 0.020 * k, 0.060 * k), Mx @ Matrix.Translation((0, -0.012 * k, 0)), mat=M["belt"], w=w,
             r=0.45, segs=1)
        for zz in (0.020, -0.020):
            rbox(buf, (0.030 * k, 0.024 * k, 0.018 * k), Mx @ Matrix.Translation((0, -0.014 * k, zz * k)),
                 mat=M["gear_d"], w=w, r=0.5, segs=1)
        n = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
        disc(buf, Mx @ V((0, -0.0225 * k, 0.003 * k)), n, Mx.to_3x3() @ V((0, 0, 1)), 0.006 * k, 0.003 * k,
             0.0012 * k, segs=8, mat=M["metal"], w=w)
    return e.gear(name, at, fn)


def charges(e, M, *, angles=(-40, 40), name="charge"):
    """폭약 블록 (벨트 앞, 테이프로 감은 상아색 덩어리 + 기폭선 끝)."""
    k = e.k
    zb = lerp(e.hipj_z, e.waist_z, 0.72)
    for i, a in enumerate(angles):
        def fn(buf, Mx, w, i=i):
            rbox(buf, (0.040 * k, 0.022 * k, 0.050 * k), Mx @ Matrix.Translation((0, -0.012 * k, -0.018 * k)),
                 mat=M["charge"], w=w, r=0.25, segs=1)
            for zz in (-0.004, -0.032):
                rbox(buf, (0.043 * k, 0.025 * k, 0.007 * k), Mx @ Matrix.Translation((0, -0.012 * k, zz * k)),
                     mat=M["hazard"], w=w, r=0.25, segs=1)
            n = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
            p0 = Mx @ V((0.012 * k, -0.024 * k, -0.010 * k))
            tube(buf, [p0, p0 + n * 0.006 * k + V((0, 0, 0.010 * k)), p0 + n * 0.002 * k + V((0.008 * k, 0, 0.022 * k))],
                 0.0022 * k, segs=5, mat=M["scarf_d"], w=w)
        e.gear(f"{name}{i}", ("torso", zb - 0.002 * k, a, 0.024 * k), fn)


def goggles(e, M, *, el=36.0, off=0.040, name="goggles"):
    """헬멧 위로 올린 고글 (두 렌즈 + 끈). 렌즈는 꺼진 짙은 색 + 청록 반사 점."""
    k = e.k

    def fn(buf):
        w = {"head": 1.0}
        for sd in (1, -1):
            p, n = e.head_point(sd * 22, el, off * k)
            up = V((0, 0.4, 1.0))
            disc(buf, p, n, up, 0.026 * k, 0.020 * k, 0.012 * k, segs=16, mat=M["gear_d"], w=w)
            disc(buf, p + n * 0.012 * k, n, up, 0.019 * k, 0.014 * k, 0.0015 * k, segs=16, mat=M["lens"], w=w)
            disc(buf, p + n * 0.0136 * k + up.normalized() * 0.006 * k + V((sd * -0.006 * k, 0, 0)), n, up,
                 0.004 * k, 0.003 * k, 0.0008 * k, segs=8, mat=M["metal"], w=w)
        pa, _ = e.head_point(8, el, (off + 0.006) * k)
        pb, _ = e.head_point(-8, el, (off + 0.006) * k)
        rbox(buf, (0.020 * k, 0.012 * k, 0.012 * k), Matrix.Translation(pa.lerp(pb, 0.5)), mat=M["gear_d"], w=w,
             r=0.45, segs=1)
        pts, nrm = [], []
        for i in range(13):
            az = 30 + (330 - 30) * i / 12
            p, n = e.head_point(az, el - 6 * math.sin(math.radians(az - 30) / 2), (off - 0.004) * k)
            pts.append(p)
            nrm.append(n)
        ups = []
        for i in range(len(pts)):
            tan = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
            ups.append(tan.cross(nrm[i]).normalized())
        elf._loop(buf, pts, nrm, ups, 0.014 * k, 0.003 * k, mat=M["scarf_d"], closed=False, w=w)
    return e.part(name, "head", fn)


def boonie(e, M, *, crown=None, brim_w=0.05, band_mat=None, name="boonie", strips=None):
    """챙 넓은 정글모: 낮은 돔 + 처진 챙 + 모자 띠 + 위장 천 조각. 귀는 챙 아래로 나온다."""
    k = e.k
    m = crown or M["cloth"]
    front, side, back = 14.0, 10.0, -6.0
    e.helmet(m, off=0.030, front=front, side=side, back=back, rim=None, band_mat=band_mat or M["scarf"],
             band_el=30.0, name=f"{name}_crown")

    def rim_el(az):
        a = abs(((az + 180) % 360) - 180)
        return front + (side - front) * smoothstep(0, 90, a) + (back - side) * smoothstep(90, 180, a)

    def fn(buf):
        w = {"head": 1.0}
        segs = e._s(36)
        inner, outer, outer2, under = [], [], [], []
        for j in range(segs):
            az = 360.0 * j / segs
            el = rim_el(az)
            p, n = e.head_point(az, el + 1.0, 0.030 * k)
            rad = V((p.x - e.head_c.x, p.y - e.head_c.y, 0)).normalized()
            bw = brim_w * k * (1.0 + 0.15 * math.cos(math.radians(az)))  # 앞챙 조금 넓게
            droop = 0.024 * k * (1 + 0.5 * (abs(math.sin(math.radians(az))) ** 2))
            q1 = p + rad * bw - V((0, 0, droop))
            inner.append(buf.vert(p, w))
            outer.append(buf.vert(q1, w))
            outer2.append(buf.vert(q1 - V((0, 0, 0.006 * k)), w))
            under.append(buf.vert(p - V((0, 0, 0.007 * k)) + rad * 0.003 * k, w))
        for j in range(segs):
            j2 = (j + 1) % segs
            buf.face((inner[j], outer[j], outer[j2], inner[j2]), m)
            buf.face((outer[j], outer2[j], outer2[j2], outer[j2]), m)
            buf.face((outer2[j], under[j], under[j2], outer2[j2]), m)
            buf.face((under[j], inner[j], inner[j2], under[j2]), m)
        # 위장 천 조각 (띠에 꽂음)
        for i, az in enumerate(strips or ()):
            p, n = e.head_point(az, 32, 0.036 * k)
            tip = p + n * 0.012 * k + V((0, 0, -0.04 * k)) + V((math.sin(math.radians(az)), -math.cos(math.radians(az)), 0)) * 0.03 * k
            ribbon(buf, [p, p + n * 0.012 * k + V((0, 0, 0.004 * k)), tip], [n, n, n], 0.014 * k, 0.003 * k,
                   mat=M["olive"] if i % 2 == 0 else M["tan"], w=w, n=6)
    return e.part(f"{name}_brim", "head", fn)


def rangefinder(e, M, at, *, name="rangefinder"):
    """가슴에 거는 쌍안 거리측정기."""
    k = e.k

    def fn(buf, Mx, w):
        for sx in (-1, 1):
            a = Mx @ V((sx * 0.016 * k, -0.020 * k, -0.026 * k))
            b = Mx @ V((sx * 0.016 * k, -0.020 * k, 0.018 * k))
            tube(buf, [a, b], 0.014 * k, 0.012 * k, segs=10, mat=M["gear_d"], w=w, cap0="flat", cap1="flat")
            disc(buf, a, (Mx.to_3x3() @ V((0, 0, -1))).normalized(), Mx.to_3x3() @ V((0, -1, 0)), 0.010 * k,
                 0.010 * k, 0.0008 * k, segs=10, mat=M["lens"], w=w)
        rbox(buf, (0.030 * k, 0.020 * k, 0.034 * k), Mx @ Matrix.Translation((0, -0.020 * k, -0.002 * k)),
             mat=M["gear"], w=w, r=0.4, segs=1)
        n = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
        disc(buf, Mx @ V((0, -0.031 * k, 0.006 * k)), n, Mx.to_3x3() @ V((0, 0, 1)), 0.004 * k, 0.004 * k,
             0.001 * k, segs=8, mat=M["glow"], w=w)
    return e.gear(name, at, fn)


def sling(e, M, *, name="sling", side="R"):
    """몸을 가로지르는 소총 멜빵 (오른어깨 → 왼허리)."""
    k = e.k
    s = -1 if side == "R" else 1
    e.strap(M["belt"], [("torso", e.shoulder_z + 0.012 * k, s * 64, 0.024 * k), ("torso", e.chest_z + 0.02 * k, s * 20, 0.040 * k),
                        ("torso", e.waist_z - 0.01 * k, -s * 40, 0.036 * k), ("torso", e.waist_z - 0.02 * k, -s * 100, 0.030 * k),
                        ("torso", e.chest_z, -s * 160, 0.034 * k), ("torso", e.shoulder_z, s * 140, 0.026 * k),
                        ("torso", e.shoulder_z + 0.012 * k, s * 64, 0.024 * k)], width=0.020, th=0.004, name=name)


# =========================================================================== squad gear (분대원 개인 장비)

def bump_helmet(e, M, *, gold=False, name="bump"):
    """가벼운 범프 헬멧 (진압 헬멧보다 낮고 귀 위가 트임) + 옆 레일 + 앞 장착판. gold=True면 앞에 금색 줄(지휘관)."""
    k = e.k
    e.helmet(M["gear_l"], off=0.032, front=12.0, side=14.0, back=-16.0, rim=M["gear"], name=name)

    def fn(buf):
        w = {"head": 1.0}
        for sd in (1, -1):
            pts, nrm = [], []
            for i in range(6):
                az = sd * (62 + 46 * i / 5)
                p, n = e.head_point(az, 22 + 4 * math.sin(math.pi * i / 5), 0.040 * k)
                pts.append(p)
                nrm.append(n)
            ups = []
            for i in range(len(pts)):
                tan = pts[min(i + 1, 5)] - pts[max(i - 1, 0)]
                ups.append(tan.cross(nrm[i]).normalized())
            elf._loop(buf, pts, nrm, ups, 0.014 * k, 0.006 * k, mat=M["gear_d"], closed=False, w=w)
        p, n = e.head_point(0, 36, 0.040 * k)
        Mx = Matrix.Translation(p) @ frame(n, (0, 0.3, 1))
        rbox(buf, (0.040 * k, 0.008 * k, 0.026 * k), Mx, mat=M["gear_d"], w=w, r=0.35, segs=1)
        if gold:
            p2, n2 = e.head_point(0, 22, 0.036 * k)
            rbox(buf, (0.060 * k, 0.004 * k, 0.007 * k), Matrix.Translation(p2) @ frame(n2, (0, 0.3, 1)),
                 mat=M["gold"], w=w, r=0.3, segs=1)
    return e.part(f"{name}_rails", "head", fn)


def riot_helmet(e, M, *, name="riot"):
    """진압반 둥근 헬멧 (정수리 통풍구, 앞 챙). 통신·폭파병."""
    return e.helmet(M["gear_l"], off=0.036, front=8.0, side=2.0, back=-22.0, rim=M["gear"], ridge=M["gear"],
                    vents=M["gear_d"], strap=M["gear_d"], name=name)


def bandana(e, M, *, off=0.033, name="bandana"):
    """머리에 동여맨 청록 부서 스카프 (의무병). 뒤통수 매듭 + 짧은 꼬리 둘.
    off: 두피에서 띄운 거리. 헤어 v2 덩어리(옆·뒤 약 0.04)를 squash가 덜 눌러도 되게 0.033으로 둔다
    (0.026이면 테 바로 아래 머리가 심하게 눌려 주름·얼룩이 생기고 두건 위로 비친다)."""
    k = e.k
    e.helmet(M["scarf"], off=off, front=30.0, side=8.0, back=-26.0, rim=None, name=name)

    def fn(buf):
        w = {"head": 1.0}
        p, n = e.head_point(180, -6, (off + 0.010) * k)
        rbox(buf, (0.040 * k, 0.026 * k, 0.030 * k), Matrix.Translation(p) @ frame(n), mat=M["scarf_d"], w=w,
             r=0.45, segs=1)
        for sd, ln in ((1, 0.075), (-1, 0.060)):
            a = p + n * 0.006 * k
            b = a + n * 0.014 * k + V((sd * 0.016 * k, 0, -0.030 * k))
            c = b + V((sd * 0.012 * k, 0.008 * k, -ln * k))
            ribbon(buf, [a, b, c], [n, n, n], 0.030 * k, 0.004 * k, mat=M["scarf"], w=w, n=8,
                   twist=lambda t, sd=sd: sd * 20 * t)
    return e.part(f"{name}_knot", "head", fn)


def glasses(e, M, *, r=(0.050, 0.050), off=0.022, mat=None, name="glasses"):
    """둥근 안경 (테만). 눈을 감싸는 큰 고리 + 코다리 + 귀 쪽 다리. e.face() 뒤에 부른다."""
    k = e.k
    fb = e.face_builder
    m = mat or M["gear_d"]

    def fn(buf):
        w = {"head": 1.0}
        cs = []
        for sd in (1, -1):
            c, n = e.face_project(sd * fb.ex, fb.ez + 0.004 * k, off * k)
            n = (n + V((0, -1, 0))).normalized()
            band(buf, c, n, (0, 0, 1), r[0] * k, r[1] * k, 0.004 * k, 0.0035 * k, segs=e._s(24), mat=m, w=w)
            cs.append((c, n))
            # 다리: 고리 바깥 → 귀 뿌리 위
            o = c + V((sd * r[0] * k, 0, 0.004 * k))
            tip, tn = e.head_point(sd * 80, -2, 0.010 * k)
            ribbon(buf, [o, o.lerp(tip, 0.5) + V((0, 0, 0.003 * k)), tip], [V((0, 0, 1))] * 3, 0.004 * k, 0.003 * k,
                   mat=m, w=w, n=6)
        a = cs[0][0] + V((-r[0] * k * 0.95, 0, 0.006 * k))
        b = cs[1][0] + V((r[0] * k * 0.95, 0, 0.006 * k))
        mid = a.lerp(b, 0.5) + V((0, -0.004 * k, 0.004 * k))
        tube(buf, [a, mid, b], 0.0022 * k, segs=6, mat=m, w=w)
    return e.part(name, "head", fn)


def medic_pack(e, M, *, name="medpack"):
    """의무 배낭: 둥근 상자 + 덮개 + 청록 원 안에 흰 더하기 + 옆 롤(들것 천)."""
    k = e.k

    def fn(buf, Mx, w):
        body = Mx @ Matrix.Translation((0, -0.040 * k, -0.005 * k))
        rbox(buf, (0.17 * k, 0.075 * k, 0.16 * k), body, mat=M["gear"], w=w, r=0.4, segs=2)
        rbox(buf, (0.175 * k, 0.080 * k, 0.045 * k), body @ Matrix.Translation((0, 0, 0.068 * k)), mat=M["gear_l"],
             w=w, r=0.45, segs=1)
        n = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
        up = Mx.to_3x3() @ V((0, 0, 1))
        c = body @ V((0, -0.0385 * k, -0.010 * k))
        disc(buf, c, n, up, 0.034 * k, 0.034 * k, 0.002 * k, segs=e._s(20), mat=M["scarf"], w=w)
        for sz_ in ((0.040, 0.012), (0.012, 0.040)):
            rbox(buf, (sz_[0] * k, 0.003 * k, sz_[1] * k), Matrix.Translation(c + n * 0.003 * k) @ frame(n, up),
                 mat=M["white"], w=w, r=0.3, segs=1)
        # 위에 가로로 묶은 천 롤
        a = body @ V((-0.085 * k, 0.0, 0.098 * k))
        b = body @ V((0.085 * k, 0.0, 0.098 * k))
        tube(buf, [a, b], 0.022 * k, segs=10, mat=M["tan"], w=w, cap0="flat", cap1="flat")
        for x in (-0.05, 0.05):
            band(buf, body @ V((x * k, 0.0, 0.098 * k)), (Mx.to_3x3() @ V((1, 0, 0))).normalized(), up,
                 0.022 * k, 0.022 * k, 0.010 * k, 0.003 * k, segs=10, mat=M["gear_d"], w=w)
    e.gear(name, ("torso", e.chest_z - 0.02 * k, 180, 0.018 * k), fn)
    for s in (1, -1):
        e.strap(M["gear"], [("torso", e.chest_z + 0.01 * k, s * 28, 0.022 * k),
                            ("torso", e.shoulder_z + 0.02 * k, s * 50, 0.018 * k),
                            ("torso", e.shoulder_z + 0.01 * k, s * 120, 0.02 * k),
                            ("torso", e.chest_z + 0.02 * k, s * 160, 0.028 * k)],
                width=0.022, th=0.005, name=f"{name}_strap_{'L' if s > 0 else 'R'}")


def med_pouch(e, M, at, *, size=(0.050, 0.026, 0.056), name="medpouch", strap=None):
    """의무 파우치: 청록 덮개 + 흰 막대 표식."""
    e.pouch(M["gear"], at, size=size, flap=M["scarf_d"], button=M["metal"], strap=strap, name=name)
    k = e.k
    a = e.anchor(at)
    sx, sy, sz = size

    def fn(buf):
        Mx = a.matrix() @ Matrix.Translation((0, -(sy + 0.0045) * k, (sz / 2 - sz * 0.45 / 2) * k))
        for d in ((0.022, 0.007), (0.007, 0.022)):
            rbox(buf, (d[0] * k, 0.002 * k, d[1] * k), Mx, mat=M["white"], w=a.w, r=0.3, segs=1)
    e.part(f"{name}_mark", a.group, fn)


def ghillie(e, M, *, n=7, name="ghillie"):
    """어깨에 꿰맨 위장 천 조각 (지정사수)."""
    k = e.k

    def fn(buf):
        for i in range(n):
            u = i / max(n - 1, 1)
            ang = (-1 if i % 2 else 1) * (60 + 70 * u)
            p, nn = e.torso_point(e.shoulder_z + 0.010 * k, ang, 0.030 * k)
            tip = p + nn * 0.022 * k + V((0, 0, -(0.05 + 0.03 * (i % 3)) * k))
            w = e._torso_wfn(p, 0)
            ribbon(buf, [p, p + nn * 0.012 * k + V((0, 0, 0.004 * k)), tip], [nn, nn, nn], 0.016 * k, 0.003 * k,
                   mat=M["olive"] if i % 2 == 0 else M["tan"], w=w, n=6, twist=lambda t, i=i: (i % 3 - 1) * 30 * t)
    return e.part(name, "body", fn)


def wire_spool(e, M, at, *, name="spool"):
    """기폭선 실패 (허리)."""
    k = e.k

    def fn(buf, Mx, w):
        ax = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
        c = Mx @ V((0, -0.016 * k, 0))
        band(buf, c, ax, Mx.to_3x3() @ V((0, 0, 1)), 0.012 * k, 0.012 * k, 0.026 * k, 0.010 * k, segs=14,
             mat=M["scarf_d"], w=w)
        for d in (-0.014, 0.014):
            disc(buf, c + ax * d * k, ax, Mx.to_3x3() @ V((0, 0, 1)), 0.026 * k, 0.026 * k, 0.003 * k, segs=14,
                 mat=M["gear_d"], w=w)
    return e.gear(name, at, fn)


# =========================================================================== Elfinia combat uniform (prologue)

ELFINIA = {
    "jacket": "#a3ada1", "jacket_d": "#7f8a80", "pants": "#939e98", "pants_d": "#76807b", "web": "#635b62",
    "web_d": "#4f474e", "belt": "#4a4149", "metal": "#cfcac4", "boots": "#58535d", "boots_d": "#443f48",
    "sole": "#2f2b31", "tab": "#b9b2a8", "glove": "#4f474e", "helmet": "#6a636b", "helmet_d": "#524b53",
    "rank_bg": "#2f3644", "rank_fg": "#d6b25e",
}


def elfinia_mats(prefix: str) -> dict:
    """엘피니아 군 전투복 팔레트 (_kit_elfinia_soldier.py와 같은 값, reference-notes.md 5.3)."""
    M = {k: elf.mat(f"{prefix}_{k}", v) for k, v in ELFINIA.items()}
    M["led"] = elf.mat(f"{prefix}_led", "#ffffff", emission="#7ff0ea", unlit=True)
    return M


def elfinia_arms(e, M):
    """엘피니아 전투복 팔 (소매·소맷단·장갑·부대 패치). _kit_elfinia_soldier와 같은 함수·값."""
    k = e.k
    e.sleeves(M["jacket"], length=0.95, cuff=(M["jacket_d"], 0.022, 0.0045))
    e.gloves(M["glove"], cuff=M["web_d"])
    sleeve_lining(e, M["jacket_d"], 0.95)
    e.patch(M["rank_bg"], ("arm_L", 0.16, 60, 0.012 * k), size=(0.028, 0.028), shape="round", name="unit_patch")
    e.patch(M["rank_fg"], ("arm_L", 0.16, 60, 0.0135 * k), size=(0.014, 0.014), shape="diamond", name="unit_mark")


def elfinia_uniform(e, M, *, helmet=True, headset_on=True):
    """엘피니아 군 전투복 일체 (알레트·타이다·레이지 계열). 근거: reference-notes.md 5장, _kit_elfinia_soldier.py.
    리타 프롤로그(지구 침공 당시 정찰 침투조)는 이 복장을 그대로 입는다."""
    k = e.k
    e.shirt(M["jacket"], collar="stand", collar_mat=M["jacket_d"], placket=M["jacket_d"], buttons=M["metal"],
            flare=0.012)
    elfinia_arms(e, M)
    e.pants(M["pants"], bag=0.013, blouse=0.020)
    e.boots(M["boots"], top=0.66, sole=(M["sole"], 0.016), cuff=M["boots_d"], laces=M["boots_d"], tab=M["tab"])
    e.belt(M["belt"], buckle=M["metal"], loops=M["belt"])
    e.epaulet(M["jacket_d"], button=M["metal"])
    cz = e.chest_z
    e.pouch(M["jacket"], ("torso", cz - 0.035 * k, 40, 0.010 * k), size=(0.040, 0.006, 0.040), flap=M["jacket_d"],
            button=M["metal"], name="chest_pocket_L")
    e.patch(M["rank_bg"], ("torso", cz + 0.072 * k, 22, 0.012 * k), size=(0.026, 0.020), name="rank_bg")
    e.patch(M["rank_fg"], ("torso", cz + 0.072 * k, 22, 0.0135 * k), size=(0.018, 0.012), shape="bars2",
            name="rank_fg")
    sz = e.shoulder_z
    pz = cz + 0.012 * k
    for s in (1, -1):
        e.strap(M["web"], [("torso", pz, s * 30, 0.018 * k), ("torso", sz - 0.005 * k, s * 40, 0.014 * k),
                           ("torso", sz + 0.02 * k, s * 58, 0.014 * k), ("torso", sz - 0.01 * k, s * 122, 0.014 * k),
                           ("torso", cz, s * 150, 0.016 * k), ("torso", e.waist_z + 0.02 * k, s * 150, 0.020 * k)],
                width=0.020, th=0.004, name=f"harness_{'L' if s > 0 else 'R'}")
    e.ring(M["web"], "torso", pz - 0.035 * k, h=0.020, th=0.004, off=0.014, name="rig_band")
    for i, a in enumerate((-26, 0, 26)):
        e.pouch(M["web"], ("torso", pz - 0.004 * k, a, 0.018 * k), size=(0.036, 0.024, 0.056), flap=M["web_d"],
                button=M["metal"], molle=M["web_d"], name=f"mag_pouch_{i}")
    e.pouch(M["web"], ("leg_R", 0.30, -75, 0.024 * k), size=(0.052, 0.026, 0.062), flap=M["web_d"], button=M["metal"],
            strap=M["belt"], name="thigh_pouch")
    e.pouch(M["pants"], ("leg_L", 0.34, 85, 0.022 * k), size=(0.05, 0.010, 0.058), flap=M["pants_d"],
            button=M["pants_d"], name="cargo_L")
    if helmet:
        e.helmet(M["helmet"], rim=M["helmet_d"], band_mat=M["web_d"], buckle=M["metal"], strap=M["web_d"])
    if headset_on:
        def hs(buf, Mx, w):
            rbox(buf, (0.05 * k, 0.03 * k, 0.045 * k), Mx @ Matrix.Translation((0, -0.012 * k, 0)), mat=M["web_d"],
                 w=w, r=0.45, segs=2)
            rbox(buf, (0.032 * k, 0.012 * k, 0.03 * k), Mx @ Matrix.Translation((0, -0.03 * k, 0)),
                 mat=M["helmet_d"], w=w, r=0.4, segs=1)
            c = Mx @ V((0.010 * k, -0.037 * k, 0.006 * k))
            n = (Mx.to_3x3() @ V((0, -1, 0))).normalized()
            disc(buf, c, n, (0, 0, 1), 0.0045 * k, 0.0045 * k, 0.0015 * k, segs=10, mat=M["led"], w=w)
            base = Mx @ V((-0.014 * k, -0.02 * k, 0.02 * k))
            st = [{"c": base, "rx": 0.003 * k, "ry": 0.003 * k, "w": w},
                  {"c": base + V((0, 0.02 * k, 0.06 * k)), "rx": 0.002 * k, "ry": 0.002 * k, "w": w}]
            loft(buf, st, segs=6, cap0="flat", cap1="round", mat=M["web_d"])
        e.gear("headset", ("head", -100, 18, 0.034 * k), hs)


# =========================================================================== hair v2 helpers

def hair_locks(h, fn):
    """헤어 v2 다발 배치 손보기: 키트가 정한 다발 목록(h._locks())을 fn(locks)로 고친다.
    다발 사전 키: a0/a1(방위 범위), L(길이), free(갈라진 길이), sweep, curl, puff, p(끝 모양), th, region, side.
    키트 공개 인자로 안 되는 모양(리타의 비대칭 옆머리, 케이트의 뭉툭한 일자 앞머리)에만 쓴다.
    [키트 후보: sides(asym=), bangs(blunt=) 또는 다발 훅]"""
    base = h._locks

    def locks():
        L = base()
        fn(L)
        return L
    h._locks = locks
    return h


def hair_tail(h, *, az=180.0, el=-30.0, length=0.15, width=0.06, out=0.5, droop=0.4, clumps=1,
              prefix="hair_tail", tie=None):
    """묶은 꼬리 하나 (키트 Hair._tail을 out을 정해 부름). out: 묶은 자리에서 셸 밖으로 뻗는 정도.
    키트 ponytail()은 out=1.25, twintails()는 1.0 고정이라 낮은 꼬리가 옆에서 수평으로 튀어나온다.
    prefix: 본 이름 (hair_tail → hair_tail_01/02). [키트 후보: ponytail(out=), twintails(out=)]
    헬멧·모자 아래 꼬리가 squash에 눌리지 않게 따로 만든 버퍼를 <인물>_hair 노드에 합친다(hair_tuft 참고)."""
    e, k = h.e, h.k

    def run():
        buf, keep = Buf(), h.buf
        h.buf = buf
        try:
            h._tail(az, el, length=length * k, width=width * k, droop=droop, clumps=max(1, clumps), prefix=prefix,
                    tie=tie, out=out)
        finally:
            h.buf = keep
        # 키트 끈(반지름 0.33w)은 꼬리 뿌리 단면(반폭 0.375w)보다 작아 대부분 묻힌다 → 끈 정점(마지막 4링)만 키운다
        base, n = h.path(az, h.s_of_el(az, el))
        c = base + n * 0.03 * k * out
        nb = 4 * 14
        if len(buf.v) > nb and all((v - c).length < width * k * 0.6 for v in buf.v[-nb:]):
            for i in range(len(buf.v) - nb, len(buf.v)):
                d = buf.v[i] - c
                along = n * d.dot(n)
                buf.v[i] = c + along + (d - along) * 1.32
        e.add(buf.obj(f"{e.name}_{prefix}"), group="head", tag="hair_tail", node="hair",
              props={"outline": h.outline})
    h._tails.append(run)
    return h


def hair_twintails(h, *, az=120.0, el=-8.0, length=0.24, width=0.075, out=0.7, droop=0.6, clumps=2, tie=None):
    """양옆 뒤 트윈테일 (hair_tail_L/R_01·02). hair_tail과 같은 이유로 out을 정하고 squash를 피한다."""
    for sd, sg in (("L", 1), ("R", -1)):
        hair_tail(h, az=sg * az, el=el, length=length, width=width, out=out, droop=droop, clumps=clumps,
                  prefix=f"hair_tail_{sd}", tie=tie)
    return h


def hair_tuft(h, *, az=180.0, el=-34.0, length=0.12, width=0.056, out=0.030, side=0.0, tie=None,
              prefix="hair_tail"):
    """짧게 묶은 꽁지 (목덜미·헬멧 아래): 묶은 자리에서 셸을 따라 조금 나왔다가 곧게 늘어지는 한 다발 + 끈.
    키트 꼬리(_tail)는 긴 포니테일용 S자(옆으로 3.5cm 휨)라 12cm 꽁지에서는 갈고리처럼 보인다.
    out: 끝이 셸에서 떨어지는 거리(m), side: 끝이 옆(+X)으로 쏠리는 거리(m). 본: prefix_01/02 (head 자식).
    따로 만든 버퍼를 <인물>_hair 노드에 합친다: 키트의 헬멧 squash(머리 중심에서 잰 높이각 기준)가
    셸 밖으로 나온 꽁지를 헬멧 테 근처로 보고 납작하게 눌러 버리지 않게 한다."""
    e, k = h.e, h.k
    base, n = h.path(az, h.s_of_el(az, el))
    n_h = V((n.x, n.y, 0.0))
    n_h = n_h.normalized() if n_h.length > 1e-6 else V((0, 1, 0))
    sx = V((1, 0, 0)) * (side * k)
    L = length * k
    ctrl = [base - n * 0.016 * k,
            base + n * 0.014 * k + V((0, 0, -0.012 * k)),
            base + n_h * (out * 0.9 * k) + sx * 0.4 + V((0, 0, -L * 0.42)),
            base + n_h * (out * k) + sx + V((0, 0, -L))]
    jp = catmull(ctrl[1:], 7)
    js = [jp[0], jp[3], jp[6]]
    names = [f"{prefix}_01", f"{prefix}_02"]
    e.add_bone(names[0], js[0], js[1], "head")
    e.add_bone(names[1], js[1], js[2], names[0])
    ch = elf.Chain([ctrl[0]] + js, ["head"] + names, blend=0.4)
    buf = Buf()
    taper = [(0.0, 0.70), (0.18, 1.0), (0.55, 0.92), (1.0, 0.0)]
    P = catmull(ctrl, max(10, int(round(12 * e.q))))
    wd, th = width * k, width * 0.78 * k
    elf.sweep(buf, P, lambda t: wd / 2 * elf.keys(taper, t), lambda t: th / 2 * max(elf.keys(taper, t), 0.2),
              segs=max(8, int(round(10 * e.q)) // 2 * 2), ref=tuple(n_h), mat=h.m, w=ch.weights)
    # 끈: 꽁지가 아래로 꺾인 첫 자리에서 다발 단면(폭 A, 두께 B)을 감싼다
    P = catmull(ctrl, 25)
    i = next((j for j in range(2, 20) if (P[j + 1] - P[j - 1]).normalized().z < -0.88), 9)
    T = (P[i + 1] - P[i - 1]).normalized()
    A = T.cross(n_h).normalized()
    band(buf, P[i], T, A, width * 0.47 * k, width * 0.38 * k, 0.013 * k, 0.005 * k, segs=14, mat=tie or h.md,
         w=ch.weights(i / (len(P) - 1)))
    e.add(buf.obj(f"{e.name}_hair_tuft"), group="head", tag="hair_tuft", node="hair",
          props={"outline": h.outline})
    return h


# =========================================================================== Rita presets

# 리타 체격: 기본 키트 체격에서 팔다리를 살짝 가늘게 (날렵한 정찰병). 전신·1인칭 팔이 같은 값을 쓴다.
RITA_BODY = dict(height=1.20, head=0.45, limb=0.96, shoulders=0.97, chest=0.12, ear_len=0.100, ear_angle=16.0)
RITA_TRI = dict(hand_q=0.9)   # 전신 모델 분할 (25k 예산). 1인칭 팔은 hand_q=1.2

RITA_FACE = dict(
    eye_color="#c98a2e",          # 호박색 눈
    lash="#3a2027", brow="#6a2a22", brow_th=1.1,
    blush_size=0.92,
    # 무표정 자체가 과묵하다: 윗눈꺼풀을 조금 내리고 눈썹은 일자, 입은 작고 곧게
    base={"eye": {"top": 0.024, "ktop": 3.4, "tilt_in": -0.003}, "brow": {"ang": -5.0, "arch": 0.0015, "dz": 0.062},
          "mouth": {"w": 0.019, "curve": 0.0004}},
    expr={
        # 결의: 이를 악문 듯 눈을 가늘게 뜨고 눈썹 안쪽을 내림 (serious보다 덜 찡그림, 입은 꾹 다묾)
        "determined": {"eye": {"top": 0.018, "tilt_in": -0.013, "ktop": 3.8, "bot": 0.049, "lift": 0.005},
                       "iris": {"pupil": 0.88},
                       "brow": {"ang": -17.0, "dz": 0.050, "th": 0.0078, "arch": -0.001},
                       "mouth": {"w": 0.015, "curve": -0.0022}},
        # 지침: 눈꺼풀이 무겁게 내려오고 시선은 아래, 눈썹 안쪽이 살짝 들림, 입이 조금 벌어짐
        "weary": {"eye": {"top": 0.013, "ktop": 2.4, "tilt_out": -0.004, "lift": 0.004, "bot": 0.050},
                  "iris": {"cz": -0.001},
                  "brow": {"ang": 7.0, "dz": 0.058, "arch": -0.001},
                  "mouth": {"w": 0.015, "curve": -0.0018, "open": 0.0032}},
        # 억누름: 출격 명령이 끝내 오지 않을 때. 눈은 뜬 채 동공이 작아지고, 눈썹 안쪽이 올라가며 입술을 깨묾
        "held_back": {"eye": {"top": 0.027, "tilt_in": 0.007, "lift": 0.009, "ktop": 2.8},
                      "iris": {"pupil": 0.74, "rx": 0.0270},
                      "brow": {"ang": 15.0, "dz": 0.064, "arch": -0.0015, "th": 0.0066},
                      "mouth": {"w": 0.018, "curve": -0.0034, "wave": 0.0007}},
    },
)
RITA_HAIR = "#a8513c"         # 구리빛 붉은 머리
RITA_SCARF_KNOT = 150.0       # 매듭: 등 왼쪽
RITA_HAIR_SEED = 3.0          # 앞머리 다발 폭·길이 변화 씨앗
RITA_LONG_LOCK = 0.20         # 왼쪽 긴 가닥: 옆머리보다 더 내려오는 길이(m)


def rita_face(e):
    return e.face(**RITA_FACE)


def rita_hair(e, *, helmet=False, tail_tie=None):
    """리타 머리 (헤어 v2): 오른쪽으로 쓸어 넘긴 앞머리, 볼 위에서 끊긴 오른쪽 옆머리, 왼쪽 귀 앞으로만
    어깨까지 내린 한 가닥, 끝이 살짝 바깥으로 뻗친 짧은 단발, 목덜미에서 짧게 묶은 꽁지.
    비대칭 실루엣이 리타의 식별 요소다. 긴 가닥은 셸의 옆머리 다발 자체를 늘려 한 장으로 이어진다
    (hair_side_L_01/02 흔들림 본). helmet=True면 헬멧 아래라 정수리 해상도를 낮추고 광택을 뺀다."""
    k = e.k
    h = e.hair(RITA_HAIR, dark="#7e3a2c", light="#d8876a")
    if helmet:
        h.cap(front=27, side=-12, back=-50, part=-16, segs=20, rows=5)
    else:
        h.cap(front=27, side=-12, back=-50, part=-16, segs=24, rows=7)
    # 헬멧(앞 테 높이 8도) 아래에서는 앞머리 끝을 내려 테 밑으로 보이게 한다
    h.bangs(n=7, spread=56, tip_el=-8.0 if helmet else 1.0, part=-16, sweep=-15, jag=0.35, seed=RITA_HAIR_SEED)
    h.sides(length=-0.012, width=0.062, az=66, curl=-0.4)
    h.back(length=0.030, n=7, spread=90)

    def asym(locks):
        for lk in locks:
            if lk["region"] != "side":
                continue
            if lk["side"] == "L":
                # 왼쪽: 어깨까지 내려오는 한 가닥. 끝은 앞으로 살짝 말림
                lk["L"] += RITA_LONG_LOCK * k
                lk["free"] += RITA_LONG_LOCK * k * 0.55
                lk["curl"] = -0.006 * k
                lk["puff"] = 0.004 * k
                lk["p"] = 1.9
            else:
                # 오른쪽: 볼 위에서 짧게 끊김 (흔들림 본 없음)
                lk["L"] -= 0.026 * k
                lk["free"] = max(0.03 * k, lk["free"] - 0.026 * k)
                lk["p"] = 2.3
                lk["curl"] = 0.004 * k
                lk["region"] = "fill"
        for lk in locks:
            if lk["region"] == "back":
                lk["curl"] = 0.006 * k     # 단발 끝이 바깥으로 살짝 뻗침
    hair_locks(h, asym)
    # 목덜미 짧은 꽁지 (끈): 셸에 붙어 곧게 늘어진다 (hair_tail_01/02)
    hair_tuft(h, el=-40 if helmet else -36, length=0.12, width=0.058, out=0.028, tie=tail_tie)
    if not helmet:
        h.shine(el=52, spread=70, n=2, size=1.15)
    return h


RITA_ARMS = dict(sleeve_len=0.95, rank_bars=1, wrist_pad=True)


def rita_arms(e, M):
    """리타의 팔 (전신·1인칭 공용): 표준 소매 + 장갑 + 왼팔 휘장 + 오른팔 계급(은 1줄) + 왼 손목 단말."""
    arms(e, M, **RITA_ARMS)


# 1인칭 팔 포즈 표 (리타 체격 공용: rita_fp_arms, rita_prologue_fp_arms)
# 손 사양: 오른손 grip(손잡이 기울기)·yaw(손잡이 축 둘레), 왼손 base(손 기본 방향)·rot(무기 축 기준)·palm(앵커=손바닥).
# fore: 아래팔 방향(팔꿈치→손목, 카메라 공간), wrist: 손목 꺾기, elbow: 팔꿈치 굽힘, stretch: 위팔 밀어내기(1인칭 과장)
# 손가락 굽힘 (도): (_01, _02[, 벌림])
FIST = {"thumb": (28, 42), "f1": (72, 82), "f2": (76, 84), "f3": (80, 86)}
TRIGGER = {"thumb": (30, 40), "f1": (28, 40), "f2": (78, 86), "f3": (82, 88)}   # 검지는 방아쇠
SUPPORT = {"thumb": (10, 20), "f1": (62, 70), "f2": (66, 74), "f3": (70, 78)}

RIFLE_R = dict(grip=22, yaw=18, wrist=(-45, 0, 0), elbow=10, twist=0, curl=TRIGGER)
RIFLE_L = dict(base="side", rot=(-30, 45, 0), fore=(0.50, 0.16, 0.85), elbow=6, stretch=0.09, twist=0, curl=SUPPORT)
PISTOL_R = dict(grip=18, yaw=55, fore=(-0.75, 0.35, 0.55), elbow=25, twist=0, curl=TRIGGER)
PISTOL_L = dict(base="right", rot=(80, 0, -50), palm=True, fore=(0.75, 0.35, 0.55), elbow=25, twist=0, curl=SUPPORT)

# 근접(전기충격봉): 손잡이가 무기 +Y를 따라 지나가므로 주먹 구멍 축(소켓 z = 엄지 쪽)을 손잡이 축에 맞춘다
# (grip=90: 엄지 = 전극 쪽, 손등 = 무기 +X). 손목을 45° 세워 봉을 들고, 아래팔은 거의 수평으로 화면 아래에 둔다.
# 왼손은 무기와 상관없이 화면 왼쪽 아래의 가드 주먹(엄지 위, 손바닥 오른쪽).
MELEE_R = dict(grip=90, yaw=0, roll=0, fore=(-0.15, 0.95, 0.05), elbow=10, twist=0, curl=FIST)
MELEE_L = dict(cam=(-0.150, 0.330, -0.175), base="right", rot=(90, 0, -20), fore=(0.30, 0.80, 0.50), elbow=10,
               twist=0, curl=FIST)

RITA_FP_POSES = {
    "hold_rifle": {"weapon": "weapons/us/m4a1.glb", "R": RIFLE_R, "L": RIFLE_L},
    "ads_rifle": {"weapon": "weapons/us/m4a1.glb", "ads": True, "R": RIFLE_R, "L": RIFLE_L},
    "hold_pistol": {"weapon": "weapons/us/m17.glb", "R": PISTOL_R, "L": PISTOL_L},
    "ads_pistol": {"weapon": "weapons/us/m17.glb", "ads": True, "R": PISTOL_R, "L": PISTOL_L},
    "hold_melee": {"weapon": "weapons/monatium/monatium_stun_baton.glb", "R": MELEE_R, "L": MELEE_L},
}


# =========================================================================== glb reading (weapons)

def read_glb_json(rel_path: str) -> dict:
    path = os.path.join(cb.MODELS_DIR, rel_path)
    with open(path, "rb") as f:
        b = f.read()
    n = struct.unpack_from("<I", b, 12)[0]
    return json.loads(b[20:20 + n])


C_T2B = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0)))   # three.js(Y-up) → Blender(Z-up): (x, y, z) → (x, -z, y)


def _node_matrix(n) -> Matrix:
    t = V(n.get("translation", (0, 0, 0)))
    q = n.get("rotation", (0, 0, 0, 1))
    s = n.get("scale", (1, 1, 1))
    from mathutils import Quaternion
    R = Quaternion((q[3], q[0], q[1], q[2])).to_matrix().to_4x4()
    S = Matrix.Diagonal((s[0], s[1], s[2], 1.0))
    return Matrix.Translation(t) @ R @ S


def weapon_info(rel_path: str) -> dict:
    """무기 glb에서 fpOffset·fpRot·앵커를 읽는다. 반환 좌표는 Blender 카메라 공간(+Y 정면, +Z 위, +X 오른쪽).
    W: 무기 루트 행렬(1인칭 배치), anchors: 카메라 공간 위치, local: 무기 로컬(Blender) 위치."""
    j = read_glb_json(rel_path)
    nodes = j["nodes"]
    out = {"anchors": {}, "local": {}, "fpOffset": None, "fpRot": "0,0,0"}

    def walk(i, Mp):
        n = nodes[i]
        Mi = Mp @ _node_matrix(n)
        ex = n.get("extras", {})
        if "fpOffset" in ex and out["fpOffset"] is None:
            out["fpOffset"] = ex["fpOffset"]
            out["fpRot"] = ex.get("fpRot", "0,0,0")
        if n.get("name"):
            out["local"][n["name"]] = C_T2B @ Mi.to_translation()
        for c in n.get("children", []):
            walk(c, Mi)
    for r in j["scenes"][0]["nodes"]:
        walk(r, Matrix.Identity(4))
    fo = [float(x) for x in (out["fpOffset"] or "0.13,-0.15,-0.28").split(",")]
    fr = [math.radians(float(x)) for x in str(out["fpRot"]).split(",")]
    # three.js Euler 'XYZ' = Rx @ Ry @ Rz
    Rt = Matrix.Rotation(fr[0], 3, "X") @ Matrix.Rotation(fr[1], 3, "Y") @ Matrix.Rotation(fr[2], 3, "Z")
    Rb = C_T2B @ Rt @ C_T2B.inverted()
    pos = C_T2B @ V(fo)
    W = Matrix.Translation(pos) @ Rb.to_4x4()
    out["W"] = W
    out["anchors"] = {k2: W @ v for k2, v in out["local"].items()}
    return out


def ads_matrix(info: dict) -> Matrix:
    """정조준 배치: sight_eye가 카메라 원점에 오도록 평행 이동, 기울기 없음 (뷰어 --ads 1과 같다)."""
    se = info["local"]["sight_eye"]
    return Matrix.Translation(-se)


# =========================================================================== first-person arms (viewmodel)

ARM_CHAIN = ("shoulder", "upperarm", "forearm", "hand")
FINGERS = ("thumb", "f1", "f2", "f3")


class Viewmodel:
    """키트 엘프의 팔 그룹만 남긴 1인칭 팔. 아마추어 오브젝트를 옮겨 socket_eye = 원점, 정면 = +Y(three.js -Z).

    1인칭 팔은 몸통에 붙어 있지 않으므로 어깨 위치를 자유롭게 둔다(화면 밖). 손 목표(무기 파지점·grip_support)
    에서 거꾸로 손목 → 팔꿈치 → 어깨를 정해 손목과 팔꿈치의 비틀림을 작게 한다.
    """

    def __init__(self, e):
        self.e = e
        self.arm = e.arm_obj
        bpy.context.view_layer.update()
        eye = bpy.data.objects["socket_eye"].matrix_world.translation.copy()
        self.A = Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation(-eye)
        self.arm.matrix_world = self.A
        bpy.context.view_layer.update()
        self.rest = {b.name: self.A @ b.matrix_local for b in self.arm.data.bones}
        self.sock = {s: bpy.data.objects[f"socket_hand_{s}"].matrix_world.copy() for s in ("L", "R")}
        self.clips: dict[str, dict] = {}
        for pb in self.arm.pose.bones:
            pb.rotation_mode = "QUATERNION"

    # ---- helpers
    def bones_of(self, side):
        out = [f"{b}_{side}" for b in ARM_CHAIN]
        for f in FINGERS:
            out += [f"{f}_01_{side}", f"{f}_02_{side}"]
        return out

    def _set_world(self, name, Mw):
        pb = self.arm.pose.bones[name]
        pb.matrix = self.A.inverted() @ Mw
        bpy.context.view_layer.update()

    def reset(self):
        for pb in self.arm.pose.bones:
            pb.location = (0, 0, 0)
            pb.rotation_quaternion = (1, 0, 0, 0)
            pb.scale = (1, 1, 1)
        bpy.context.view_layer.update()

    def solve(self, side, target, *, wrist=(0, 0, 0), elbow=80.0, twist=0.0, curl=None, fore=None, upper=None,
              stretch=0.0):
        """target: 손 소켓(socket_hand_*)이 와야 할 카메라 공간 행렬(4x4, 회전 포함).
        wrist=(x, y, z)도: 소켓 좌표계에서 손목 꺾기 (x: 엄지/새끼 쪽 기울기, y: 비틀기, z: 손바닥 쪽 굽힘).
        elbow: 팔꿈치 굽힘(도), twist: 아래팔 자체 비틀기(도, 팔꿈치 쪽에서 나눠 받음).
        curl: {'thumb': (a1, a2), 'f1': ..., ...} 손가락 마디 굽힘(도, 로컬 X).
        fore: 아래팔 방향(팔꿈치→손목, 카메라 공간)을 직접 준다. 손목 꺾기는 그 방향으로 가는 최소 회전이 된다.
        upper: 위팔 방향(어깨→팔꿈치). 주면 elbow·twist 대신 이 방향에서 굽힘각과 아래팔 비틀기를 구한다.
        stretch: 위팔을 제 축을 따라 이만큼(m) 밀어낸다. 엘프 위팔이 짧아 어깨 끝이 화면에 걸릴 때 쓴다.
            두께는 그대로이고 팔꿈치 섞임 구간이 늘어나 이어진다 (1인칭 전용 과장)."""
        R = self.rest
        hand, fore_b, up, sh = (f"{b}_{side}" for b in ("hand", "forearm", "upperarm", "shoulder"))
        O = R[hand].inverted() @ self.sock[side]                     # 손 본 → 소켓
        H = target @ O.inverted()                                     # 손 본 목표 (월드)
        S_rot = target.to_3x3()
        Rw = Euler([math.radians(x) for x in wrist], "XYZ").to_matrix()
        F0 = R[fore_b].to_3x3()
        S0 = self.sock[side].to_3x3()
        # 휴식 자세에서 아래팔 프레임과 소켓 프레임의 관계
        Rfs = F0.inverted() @ S0
        F_rot = S_rot @ Rw.inverted() @ Rfs.inverted()
        bend = 0.0
        if fore is not None:
            d0 = F_rot.col[1].normalized()
            d1 = V(fore).normalized()
            q = d0.rotation_difference(d1)
            bend = math.degrees(q.angle)
            F_rot = q.to_matrix() @ F_rot
        L2 = (R[hand].translation - R[fore_b].translation).length
        L1 = (R[fore_b].translation - R[up].translation).length
        Fw = Matrix.Translation(H.translation - F_rot.col[1] * L2) @ F_rot.to_4x4()
        U0 = R[up].to_3x3()
        Ruf = U0.inverted() @ F0     # 휴식: 위팔 → 아래팔 (A 포즈에서는 거의 단위)
        if upper is not None:
            # 위팔 방향에서 굽힘각(elbow)과 아래팔 비틀기(twist)를 역산: 경첩 축 = 위팔 × 아래팔
            u = V(upper).normalized()
            fy = F_rot.col[1].normalized()
            elbow = math.degrees(u.angle(fy))
            hinge = u.cross(fy)
            if hinge.length > 1e-6:
                hinge.normalize()
                fx = F_rot.col[0].normalized()
                fz = F_rot.col[2].normalized()
                twist = math.degrees(math.atan2(hinge.dot(fz), hinge.dot(fx)))
            else:
                twist = 0.0
        U_rot = F_rot @ Matrix.Rotation(math.radians(twist), 3, "Y").inverted() \
            @ Matrix.Rotation(math.radians(elbow), 3, "X").inverted() @ Ruf.inverted()
        Uw = Matrix.Translation(Fw.translation - U_rot.col[1] * (L1 + stretch)) @ U_rot.to_4x4()
        Sw = Uw @ R[up].inverted() @ R[sh]
        for name, Mw in ((sh, Sw), (up, Uw), (fore_b, Fw), (hand, H)):
            self._set_world(name, Mw)
        # 손가락
        curl = curl or {}
        for f in FINGERS:
            a1, a2 = curl.get(f, (0.0, 0.0))[:2]
            spread = curl.get(f, (0, 0, 0))[2] if len(curl.get(f, ())) > 2 else 0.0
            for seg, a in (("01", a1), ("02", a2)):
                pb = self.arm.pose.bones[f"{f}_{seg}_{side}"]
                pb.rotation_quaternion = Euler((math.radians(a), 0, math.radians(spread if seg == "01" else 0)),
                                               "XYZ").to_quaternion()
        bpy.context.view_layer.update()
        self.last = {"bend": bend, "elbow": elbow, "twist": twist}
        return {"wrist": H.translation.copy(), "elbow": Fw.translation.copy(), "shoulder": Uw.translation.copy()}

    def record(self, clip):
        """현재 포즈(양팔 전부)를 아마추어 공간 행렬로 저장."""
        mats_ = {}
        for side in ("L", "R"):
            for b in self.bones_of(side):
                mats_[b] = self.arm.pose.bones[b].matrix.copy()
        self.clips[clip] = mats_

    def _apply_recorded(self, clip):
        self.reset()
        for side in ("L", "R"):
            for b in self.bones_of(side):
                self.arm.pose.bones[b].matrix = self.clips[clip][b]
                bpy.context.view_layer.update()

    def bake_rest(self, clip):
        """clip 포즈를 레스트 포즈로 굳힌다 (엔진이 클립을 재생하지 않아도 그 자세로 보인다)."""
        self._apply_recorded(clip)
        arm = self.arm
        meshes = [o for o in bpy.data.objects if o.type == "MESH" and any(m.type == "ARMATURE" for m in o.modifiers)]
        for o in meshes:
            cb.apply_modifiers(o)
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = arm
        arm.select_set(True)
        bpy.ops.object.mode_set(mode="POSE")
        bpy.ops.pose.armature_apply(selected=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        arm.select_set(False)
        for o in meshes:
            mod = o.modifiers.new("Armature", "ARMATURE")
            mod.object = arm
        bpy.context.view_layer.update()
        self.reset()

    def write_clips(self, names):
        """저장한 포즈를 액션 + NLA 트랙으로 (glTF 애니메이션 클립). 모든 팔 본의 위치·회전을 키로 넣는다."""
        arm = self.arm
        ad = arm.animation_data_create()
        for name in names:
            self._apply_recorded(name)
            act = bpy.data.actions.new(name)
            ad.action = act
            for side in ("L", "R"):
                for b in self.bones_of(side):
                    pb = arm.pose.bones[b]
                    for f in (1, 2):
                        pb.keyframe_insert("location", frame=f)
                        pb.keyframe_insert("rotation_quaternion", frame=f)
            ad.action = None
            tr = ad.nla_tracks.new()
            tr.name = name
            tr.strips.new(name, 1, act)
        self.reset()


def screen_ndc(p, fov=70.0, aspect=16 / 9):
    """카메라 공간(Blender, +Y 정면) 점의 화면 좌표(-1~1). y≤0이면 None(카메라 뒤)."""
    if p.y <= 1e-4:
        return None
    t = math.tan(math.radians(fov) / 2)
    return (p.x / (p.y * t * aspect), p.z / (p.y * t))


_HAND_BASES = {
    # 왼손 소켓 기본 프레임. 열: x=손바닥 법선(쥐는 물체 쪽), y=손가락 방향, z=엄지 방향
    "up": Matrix(((0, 1, 0), (0, 0, 1), (1, 0, 0))),      # 손바닥 위, 손가락 오른쪽, 엄지 앞
    "right": Matrix(((1, 0, 0), (0, 0, 1), (0, -1, 0))),  # 손바닥 오른쪽(+X), 손가락 아래, 엄지 앞
    "side": Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0))),   # 손바닥 오른쪽(+X), 손가락 위, 엄지 뒤 (총몸 왼쪽 면을 감쌈)
}


def hand_target(info, side, spec, *, ads=False):
    """포즈 사양 → 손 소켓 목표 행렬 (카메라 공간).
    오른손: 무기 원점(파지점), 손잡이 기울기(grip, 도)와 손잡이 축 둘레 회전(yaw)을 준다.
    왼손: 무기의 앵커(기본 grip_support) + 무기 좌표 오프셋, 기본 프레임(palm 'up' | 'right' | 'left')에
    무기 축 기준 오일러 회전(rot, 도)을 더한다."""
    if "cam" in spec:
        # 무기와 상관없는 자유 자세: 카메라 공간 위치 + 기본 프레임(base) + 오일러 회전(rot, 카메라 축 기준)
        B = _HAND_BASES[spec.get("base", "right")]
        r = spec.get("rot", (0, 0, 0))
        Rr = Matrix.Rotation(math.radians(r[2]), 3, "Z") @ Matrix.Rotation(math.radians(r[1]), 3, "Y") \
            @ Matrix.Rotation(math.radians(r[0]), 3, "X")
        return Matrix.Translation(V(spec["cam"])) @ (Rr @ B).to_4x4()
    W = ads_matrix(info) if ads else info["W"]
    Wr = W.to_3x3()
    if side == "R":
        anchor = V(spec.get("at", (0, 0, 0)))
        R = Matrix.Rotation(math.radians(-spec.get("grip", 20.0)), 3, "X")
        R = R @ Matrix.Rotation(math.radians(spec.get("yaw", 0.0)), 3, "Z")
        R = R @ Matrix.Rotation(math.radians(spec.get("roll", 0.0)), 3, "Y")
        return Matrix.Translation(W @ anchor) @ (Wr @ R).to_4x4()
    a = info["local"][spec.get("anchor", "grip_support")] + V(spec.get("off", (0, 0, 0)))
    palm = spec.get("palm", False)   # True: 앵커가 손바닥 위치 (M17 grip_support). 소켓은 손바닥에서 2.6 cm 안쪽
    B = _HAND_BASES[spec.get("base", "up")]
    r = spec.get("rot", (0, 0, 0))
    Rr = Matrix.Rotation(math.radians(r[2]), 3, "Z") @ Matrix.Rotation(math.radians(r[1]), 3, "Y") \
        @ Matrix.Rotation(math.radians(r[0]), 3, "X")
    R = Wr @ Rr @ B
    p = W @ a
    if palm:
        p = p + R.col[0] * 0.026
    return Matrix.Translation(p) @ R.to_4x4()


def build_fp_arms(e, poses: dict, rest: str, out: str, *, outline=0.0022, report=True):
    """키트 엘프(옷 입힌 상태)에서 팔 그룹만 남겨 1인칭 팔 뷰모델을 만든다.
    poses: {클립: {"weapon": glb, "ads": bool, "R": {...}, "L": {...}}}. rest 클립을 레스트 포즈로 굳힌다
    (엔진이 클립을 재생하지 않아도 그 자세). 모든 클립은 glTF 애니메이션으로 들어간다."""
    e.finalize(only=("arms",))
    vm = Viewmodel(e)
    infos = {}
    for clip, spec in poses.items():
        wp = spec["weapon"]
        info = infos.setdefault(wp, weapon_info(wp))
        vm.reset()
        for side in ("R", "L"):
            hs = spec[side]
            tgt = hand_target(info, side, hs, ads=spec.get("ads", False))
            pts = vm.solve(side, tgt, wrist=hs.get("wrist", (0, 0, 0)), elbow=hs.get("elbow", 80.0),
                           twist=hs.get("twist", 0.0), curl=hs.get("curl"), fore=hs.get("fore"),
                           upper=hs.get("upper"), stretch=hs.get("stretch", 0.0))
            if report:
                desc = "  ".join(f"{k2}=({v.x:+.3f},{v.y:+.3f},{v.z:+.3f}) ndc={_fmt_ndc(screen_ndc(v))}"
                                 for k2, v in pts.items())
                lt = vm.last
                print(f"[vm] {clip} {side}: {desc}  wrist_bend={lt['bend']:.0f} elbow={lt['elbow']:.0f} "
                      f"twist={lt['twist']:.0f}")
        vm.record(clip)
    vm.bake_rest(rest)
    vm.write_clips(list(poses.keys()))
    e.export(out, outline=outline, props={"fpArms": 1, "restClip": rest})
    return vm


def _fmt_ndc(p):
    return "behind" if p is None else f"{p[0]:+.2f},{p[1]:+.2f}"


def debug_scene(vm, clip, weapon, out, *, ads=False):
    """점검용: 포즈한 팔 + 무기를 한 장면으로 내보낸다 (public/models/viewmodels/_debug_*.glb, 커밋하지 않음).
    npm run shot -- viewmodels/_debug_x.glb --views front,side,top,34"""
    if vm is not None and clip in vm.clips:
        vm._apply_recorded(clip)
    info = weapon_info(weapon)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(cb.MODELS_DIR, weapon))
    new = [o for o in bpy.data.objects if o not in before]
    roots = [o for o in new if o.parent is None]
    W = ads_matrix(info) if ads else info["W"]
    for r in roots:
        r.matrix_world = W @ r.matrix_world
    cam = cb.empty("camera_eye", loc=(0, 0, 0))
    cb.box("debug_cam", size=(0.02, 0.04, 0.02), loc=(0, 0.0, 0), material=elf.mat("dbg", "#ff3030"))
    cb.export(out)
    for o in new + [cam, bpy.data.objects["debug_cam"]]:
        bpy.data.objects.remove(o, do_unlink=True)
