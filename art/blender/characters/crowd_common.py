"""대관식 군중 키트 (에필로그 에르핀 3차 대관식). [오리지널] 무명 군중: 요정 왕국 주민, 모나티엄 엘프 시민, 수인.

원작: 3차 대관식에는 왕국의 모든 요정이 광장에 모여 만세를 외치며 환호했고(발 디딜 틈이 없을 정도), 각 종족의
지도자들이 헌사를 했다(에르핀(왕도) 문서, 테마극장 「여왕님의 마음으로 만든 나라」 12화). 그래서 군중은 요정이 가장
많고, 엘프와 수인이 섞인다. 근거: docs/art/characters-cameo3.md.

- 수십 명이 한 화면에 나오므로 키트를 성글게 쓴다(segs 0.42, hand_q 0.28, 머리 cap(segs=10, rows=3)): 4~6k 삼각형.
- 원경 LOD: build()가 본 모델 바로 뒤에 같은 뼈대로 characters/crowd_lod/<이름>.glb(약 2k 삼각형)를 내보낸다(export_lod,
  CROWD_LOD=0이면 건너뜀). 대관식·퍼레이드의 인스턴스 군중(src/game/cinematic/crowd.ts)이 먼 사람에게 쓴다.
- 종족 표식
    요정: 둥근 귀(또는 머리에 가림) + 작은 깃털 날개(fairy.wings, 원작 요정 종족 특징)
    엘프: 키트의 뾰족한 귀, 날개 없음
    수인: 엘프 귀를 지우고 머리 위 동물 귀 + 꼬리(본 2개). 원작 수인은 사람 형태에 원형 동물의 귀·뿔·꼬리가 난 모습이고
          대부분 포유류(털 수인)다(「수인(트릭컬 리바이브)」 문서).
- 체형: 성인 군중이라 변형마다 bust(키트 Elf(bust=), ca439e1)를 0~0.5 사이로 섞는다(양식화, 비성적).
- 섞어 쓰기: 변형마다 머리색·머리 모양·옷 색·머리 장식이 다르다. 손깃발(에르피엔 군기, lib/erpien_flag.py)은 별도 노드
  '<이름>_flag'(socket_hand_R)라 숨기거나 켤 수 있다.
- 애니메이션(glTF 클립, 24fps): idle(숨쉬기, 반복), cheer(두 팔 환호, 반복), wave(오른손 흔들기, 반복),
  clap(박수, 반복), flag(깃발 든 손 흔들기, 반복), manse(만세 한 번: 0.0 내림 → 0.33 s 팔 올림 → 0.83 s까지 유지 →
  1.33 s 내림), manse3(만세 세 번 연속, 4.0 s). 만세삼창은 manse를 구호마다 한 번씩 다시 틀거나 manse3을 한 번 튼다.

    build(name, race, v)   race: 'fairy' | 'elf' | 'beast',  v: 변형 사전 (아래 키)
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import cb  # noqa: E402
import elf  # noqa: E402
import fairy  # noqa: E402
import erpien_flag as ef  # noqa: E402
import cameo2 as c2  # noqa: E402
import cameo3 as c3  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, smoothstep, frame  # noqa: E402

SEGS, HQ = 0.38, 0.28
FPS = 24


# =========================================================================== 몸·얼굴·머리

def _body(name, race, v):
    kw = dict(height=v.get("height", 1.18), segs=SEGS, hand_q=HQ, cheek=v.get("cheek", 0.12),
              chest=v.get("chest", 0.25), hips=v.get("hips", 1.02), bust=v.get("bust", 0.0))
    for kk in ("head", "shoulders", "limb"):       # 아이 체형 (키가 작고 머리 비율이 크다)
        if kk in v:
            kw[kk] = v[kk]
    if race == "fairy":
        e = fairy.Fairy(name, ears=v.get("ears", "round"), **kw)
    else:
        e = elf.Elf(name, ear_inner=False, **kw)
        if race == "beast":
            e.remove("ear_L")
            e.remove("ear_R")
    return e


def _face(e, v):
    e.face(eye_color=v["eye"], lash="#3a2a2c", brow=elf.mix_hex(v["hair_d"], "#2a2024", 0.45),
           brow_th=v.get("brow_th", 1.0), eye_size=v.get("eye_size", 1.0), blush="#f7a3a6",
           base={"eye": {"top": v.get("eye_top", 0.026), "ktop": 3.4},
                 "brow": {"ang": v.get("brow_ang", 2.0), "dz": 0.066},
                 "mouth": {"w": 0.020, "curve": 0.0050}},
           expr={"cheer": {"eye": {"top": 0.018, "lift": 0.014, "kbot": 2.4},
                           "brow": {"ang": 10.0, "dz": 0.072},
                           "mouth": {"w": 0.034, "curve": 0.0100, "open": 0.0240, "top_arch": -0.0015}}})


def _hair(e, v):
    h = e.hair(v["hair"], dark=v["hair_d"], light=v.get("hair_l"), volume=v.get("volume", 1.0))
    h.cap(front=28, side=-8, back=-48, part=v.get("part", 0), segs=10, rows=3)
    h.bangs(n=5, spread=54, tip_el=-2, sweep=v.get("sweep", 0), part=v.get("part", 0), jag=0.15,
            seed=v.get("seed", 1.0))
    st = v.get("style", "bob")
    if st == "bob":
        h.sides(length=0.07, width=0.074, curl=0.7)
        h.back(length=0.05, n=5)
    elif st == "short":
        h.sides(length=0.02, width=0.068, curl=0.4)
        h.back(length=0.0, n=5)
    elif st == "long":
        h.sides(length=0.22, width=0.074, curl=0.4)
        h.back(length=0.30, n=5)
    elif st == "pony":
        h.sides(length=0.05, width=0.070, curl=0.4)
        h.back(length=0.02, n=5)
        h.ponytail(height=36, length=0.22, width=0.090, clumps=1, tie=elf.mat(f"{e.name}_tie", v.get("acc", "#e05a6a")))
    elif st == "twin":
        h.sides(length=0.05, width=0.070, curl=0.4)
        h.back(length=0.03, n=5)
        h.twintails(height=28, az=120, length=0.20, width=0.075)
    elif st == "buns":
        h.sides(length=0.05, width=0.070, curl=0.5)
        h.back(length=0.02, n=5)
        for az in (130.0, -130.0):
            h.bun(az=az, el=40.0, size=0.050)
    return h


# =========================================================================== 수인 귀·꼬리

def _ear_geo(buf, e, v, side):
    """동물 귀 한 쪽. kind: cat, fox, wolf, dog(접힌 귀), rabbit(긴 귀), bear(둥근 귀), sheep(늘어진 귀 + 말린 뿔)."""
    k = e.k
    kind = v["ear"]
    fur = elf.mat(f"{e.name}_fur", v.get("ear_col", v["hair"]))
    inner = elf.mat(f"{e.name}_ear_inner", v.get("ear_in", "#f2b4b4"))
    w = {"head": 1.0}
    az = side * {"rabbit": 26.0, "bear": 48.0, "sheep": 80.0, "dog": 66.0}.get(kind, 44.0)
    el = {"rabbit": 62.0, "bear": 52.0, "sheep": 20.0, "dog": 36.0}.get(kind, 50.0)
    # 귀 뿌리는 머리카락 셸 바깥 면에 둔다 (늘어진 귀·둥근 귀가 머리카락에 묻히지 않게)
    lift = {"bear": 0.044, "dog": 0.046, "sheep": 0.044}.get(kind, 0.030)
    p, n = e.head_point(az, el, lift * k * v.get("volume", 1.0))
    out = V((math.sin(math.radians(az)), -math.cos(math.radians(az)), 0.0))
    if kind in ("cat", "fox", "wolf"):
        L = {"cat": 0.070, "fox": 0.095, "wolf": 0.085}[kind] * k
        W = {"cat": 0.062, "fox": 0.068, "wolf": 0.064}[kind] * k
        up = (n * 0.75 + out * 0.25 + V((0, 0.10, 0))).normalized()
        fwd = V((0, -1, 0))
        side_v = up.cross(fwd).normalized()
        fwd = side_v.cross(up).normalized()
        st = []
        for i, t in enumerate((0.0, 0.35, 0.70, 1.0)):
            r = W * 0.5 * (1.0 - t) ** 0.9 + 0.0008
            st.append({"c": p + up * (L * t), "rx": r, "ry": r * 0.42, "w": w, "ref": tuple(side_v)})
        loft(buf, st, segs=6, cap0="flat", cap1="flat", mat=fur)
        st2 = [{"c": p + up * (L * t) - fwd * (0.0055 * k), "rx": W * 0.32 * (1.0 - t) + 0.0006,
                "ry": 0.0012 * k, "w": w, "ref": tuple(side_v)} for t in (0.10, 0.55, 0.85)]
        loft(buf, st2, segs=4, cap0="flat", cap1="flat", mat=inner)
        if kind == "fox":      # 여우: 귀 끝이 짙다
            dark = elf.mat(f"{e.name}_tip", v.get("tip_d", "#3a2a26"))
            loft(buf, [{"c": p + up * (L * 0.72), "rx": W * 0.15, "ry": W * 0.08, "w": w, "ref": tuple(side_v)},
                       {"c": p + up * (L * 1.01), "rx": 0.0008, "ry": 0.0006, "w": w, "ref": tuple(side_v)}],
                 segs=6, cap0="flat", cap1="flat", mat=dark)
    elif kind == "rabbit":
        L = 0.15 * k
        up = (n * 0.85 + out * 0.15).normalized()
        bend = V((0, 0.35, -0.2)) * side * 0.0 + V((side * 0.15, 0.25, 0))
        pts = [p, p + up * L * 0.5, p + up * L * 0.92 + bend * L * 0.25]
        side_v = up.cross(V((0, -1, 0))).normalized()
        st = []
        for i, q in enumerate(pts):
            t = i / 2
            r = 0.022 * k * (0.75 + 0.35 * math.sin(math.pi * t)) * (1.0 - 0.5 * t ** 3)
            st.append({"c": q, "rx": r, "ry": r * 0.40, "w": w, "ref": tuple(side_v)})
        loft(buf, st, segs=6, cap0="flat", cap1="round", mat=fur)
        loft(buf, [{"c": q + V((0, -0.006 * k, 0)), "rx": 0.011 * k * (1 - 0.4 * i / 2), "ry": 0.0012 * k, "w": w,
                    "ref": tuple(side_v)} for i, q in enumerate(pts)], segs=4, cap0="flat", cap1="flat", mat=inner)
    elif kind == "bear":
        # 둥근 귀: 앞을 보는 납작한 원반 (얇은 축 = 앞뒤), 안쪽 판은 앞면에
        r = 0.036 * k
        c = p + n * r * 0.55
        c2.ellipsoid(buf, c, V((0, 1, 0)), V((1, 0, 0)), V((0, 0, 1)), r * 0.42, r, r, segs=10, rings=4, mat=fur,
                     w=w)
        c2.ellipsoid(buf, c + V((0, -r * 0.30, -r * 0.08)), V((0, 1, 0)), V((1, 0, 0)), V((0, 0, 1)), r * 0.20,
                     r * 0.58, r * 0.58, segs=8, rings=3, mat=inner, w=w)
    elif kind in ("dog", "sheep"):
        # 아래로 늘어진 귀 (머리 옆)
        L = (0.110 if kind == "dog" else 0.080) * k
        down = (V((0, 0, -1)) * 0.80 + out * 0.45 + V((0, 0.10, 0))).normalized()
        side_v = down.cross(V((0, -1, 0))).normalized()
        st = []
        for t in (0.0, 0.4, 0.8, 1.0):
            r = 0.036 * k * (0.75 + 0.30 * math.sin(math.pi * min(t * 1.1, 1.0))) * (1.0 - 0.6 * t ** 4)
            st.append({"c": p + out * 0.010 * k + down * (L * t), "rx": r, "ry": r * 0.38, "w": w,
                       "ref": tuple(side_v)})
        loft(buf, st, segs=6, cap0="flat", cap1="round", mat=fur)
        if kind == "sheep":    # 말린 뿔 (크림색 고리)
            horn = elf.mat(f"{e.name}_horn", "#a88a66")
            hp, hn = e.head_point(side * 74.0, 34.0, 0.052 * k)
            hout = V((side, 0.0, 0.0))
            pts = []
            for i in range(13):
                a = math.radians(i / 12 * 330.0)
                rr = 0.042 * k * (1.0 - 0.35 * i / 12)
                # 귀 위에서 뒤·아래로 말리는 숫양 뿔 (머리 옆면에 평행한 나선)
                pts.append(hp + hout * (0.012 * k + 0.010 * k * i / 12) + V((0, rr * (1 - math.cos(a)),
                                                                              rr * math.sin(a) * 0.9)))
            loft(buf, [{"c": q, "rx": 0.017 * k * (1 - 0.55 * i / 12), "ry": 0.017 * k * (1 - 0.55 * i / 12), "w": w}
                       for i, q in enumerate(pts)], segs=6, cap0="flat", cap1="round", mat=horn)


def _tail(e, v):
    """꼬리 (본 tail_01..02, hips 자식). kind: cat(가늘고 긴, 위로 휨), fox/wolf(굵은 붓, 끝 흰색/짙은색),
    dog(짧게 위로 말림), rabbit/bear/sheep(동그란 방울)."""
    k = e.k
    kind = v["tail"]
    fur = elf.mat(f"{e.name}_fur", v["hair"])
    base = V((0, 0.085 * k, e.hipj_z - 0.010 * k))
    buf = Buf()
    if kind in ("rabbit", "bear", "sheep"):
        r = {"rabbit": 0.030, "bear": 0.024, "sheep": 0.030}[kind] * k
        tip = elf.mat(f"{e.name}_tailtip", v.get("tail_tip", v["hair"]))
        c2.ellipsoid(buf, base + V((0, r * 0.7, 0)), V((0, 1, 0)), V((1, 0, 0)), V((0, 0, 1)), r, r, r, segs=8,
                     rings=5, mat=tip, w={"hips": 1.0})
        e.add(buf.obj(f"{e.name}_tail", angle=50.0), group="body", tag="tail")
        return
    shapes = {
        "cat": ([(0, 0, 0), (0, 0.10, -0.03), (0, 0.18, 0.06), (0.02, 0.20, 0.17)], 0.013, 0.010, 0.0),
        "fox": ([(0, 0, 0), (0, 0.09, -0.06), (0.03, 0.17, -0.04), (0.06, 0.22, 0.04)], 0.020, 0.040, 0.30),
        "wolf": ([(0, 0, 0), (0, 0.08, -0.08), (0.02, 0.15, -0.10), (0.03, 0.20, -0.08)], 0.018, 0.034, 0.25),
        "dog": ([(0, 0, 0), (0, 0.06, 0.03), (0, 0.08, 0.09), (0, 0.06, 0.12)], 0.016, 0.018, 0.0),
    }
    ctrl, r0, rmax, tip_len = shapes[kind]
    pts = [base + V(c) * k for c in ctrl]
    P = elf.catmull(pts, 24)
    joints = [P[0], P[len(P) // 2], P[-1]]
    e.add_bone("tail_01", joints[0], joints[1], "hips")
    e.add_bone("tail_02", joints[1], joints[2], "tail_01")
    ch = elf.Chain(joints, ["tail_01", "tail_02"], start={"hips": 1.0}, start_blend=0.5)
    tip_m = elf.mat(f"{e.name}_tailtip", v.get("tail_tip", v["hair"]))
    n = len(P)
    st, st_tip = [], []
    for i, q in enumerate(P):
        t = i / (n - 1)
        r = lerp(r0, rmax, math.sin(math.pi * min(t * 1.15, 1.0)) ** 0.8) if rmax > r0 else lerp(r0, r0 * 0.75, t)
        r *= (1.0 - smoothstep(0.82, 1.0, t) * 0.85)
        s = {"c": q, "rx": max(r * k, 0.0008), "ry": max(r * k, 0.0008), "w": ch.weights(t)}
        if tip_len and t >= 1.0 - tip_len:
            if not st_tip:
                st.append(dict(s))
            st_tip.append(s)
        else:
            st.append(s)
    loft(buf, st, segs=8, cap0="round", cap1="flat" if st_tip else "round", mat=fur)
    if st_tip:
        loft(buf, st_tip, segs=8, cap0="flat", cap1="round", mat=tip_m)
    e.add(buf.obj(f"{e.name}_tail", angle=50.0), group="body", tag="tail")


# =========================================================================== 옷

def _clothes(e, race, v):
    k = e.k
    M_ = elf.mat
    P = {kk: M_(f"{e.name}_{kk}", hx) for kk, hx in v["pal"].items()}
    cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
    top = v.get("top", "dress")
    q0 = e.q
    e.shirt(P["top"], hem=wz - 0.010 * k, collar=v.get("collar"), collar_mat=P.get("trim", P["top"]), flare=0.006)
    e.sleeves(P.get("sleeve", P["top"]), length=v.get("sleeve_len", 0.55), off=0.012, flare=0.010,
              puff=v.get("puff", 0.008), cuff=(P.get("trim", P["top"]), 0.012, 0.003))
    if top in ("dress", "apron"):
        sk = c2.Shell(e, P["skirt"], wz + 0.004 * k, v.get("hem", 0.30) * k, off=0.016, th=0.004, skirt=True, rows=4,
                      cols=14, flare=[(0.0, 0.0), (1.0, 0.040)], ruffle=(0.006, 7, 0.5), cover=True)
        sk.hem_trim(P.get("trim", P["skirt"]), width=0.010, th=0.002)
        sk.done("skirt")
        if top == "apron":
            ap = c2.Shell(e, P["apron"], wz + 0.002 * k, (v.get("hem", 0.30) + 0.05) * k, gap=118.0, back_only=True,
                          off=0.016, th=0.003, skirt=True, rows=4, cols=6,
                          flare=[(0.0, 0.009), (1.0, 0.044 + 0.012)])
            ap.done("apron")
    else:   # 바지·반바지
        e.q = 0.5
        e.pants(P["skirt"], length=v.get("pants_len", 0.86), bag=0.016, blouse=0.010, off=0.012)
        e.q = q0
    e.ring(P.get("belt", P.get("trim", P["top"])), "torso", wz - 0.004 * k, h=0.016, th=0.004, off=0.018,
           name="sash")
    if "vest" in P:
        vs = c2.Shell(e, P["vest"], e.torso_top - 0.006 * k, wz - 0.004 * k, gap=[(0.0, 34.0), (1.0, 18.0)],
                      off=0.020, th=0.004, rows=3, cols=12)
        vs.done("vest")
    if "scarf" in P:
        e.part("scarf", "body", lambda buf: band(buf, (0, 0.006 * k, e.torso_top + 0.002 * k), (0, 0, 1), (1, 0, 0),
                                                 0.064 * k, 0.060 * k, 0.026 * k, 0.012 * k, segs=10,
                                                 mat=P["scarf"], w={"neck": 0.3, "chest": 0.7}))
    if v.get("legs", "socks") == "socks":
        for sd in ("L", "R"):
            c2.leg_tube(e, P.get("socks", P["top"]), sd, 0.62, 0.86, off=0.004, segs=6, name=f"sock_{sd}")
    _shoes(e, P["shoe"])
    return P


def _shoes(e, mat):
    """싼 신발 (군중용): 발목 관 + 둥근 신 덩어리 하나를 foot 본에. 키트 boots(발 하나 약 540 삼각형) 대신 약 130."""
    k = e.k
    e.hide_feet = True
    for sd in ("L", "R"):
        c2.leg_tube(e, mat, sd, 0.86, 1.0, off=0.008, segs=6, cap1="round", name=f"shoe_cuff_{sd}")
        A = e.A[sd]
        e.part(f"shoe_{sd}", "body", lambda buf, A=A, sd=sd: c2.ellipsoid(
            buf, V((A.x, A.y - 0.024 * k, 0.030 * k)), V((0, -1, 0)), V((1, 0, 0)), V((0, 0, 1)), 0.068 * k,
            0.044 * k, 0.034 * k, segs=8, rings=5, mat=mat, w={f"foot_{sd}": 1.0}))


def _head_acc(e, h, v):
    """머리 장식: flower(꽃관), ribbon(리본), beret(베레모), cap(챙모자), garland(잎 고리), None."""
    k = e.k
    acc = v.get("head_acc")
    if not acc:
        return
    M_ = elf.mat
    am = M_(f"{e.name}_acc", v.get("acc", "#f08aa2"))
    am2 = M_(f"{e.name}_acc2", v.get("acc2", "#fff6c8"))
    w = {"head": 1.0}

    def ring(buf, el0, mat, th=0.010, n=14):
        pts, nrm, ups = [], [], []
        for i in range(n):
            az = 360.0 * i / n
            s = h.s_of_el(az, el0 - 6.0 * (1 - math.cos(math.radians(az))) / 2)
            p, nn = h.path(az, s, 0.004 * k)
            p2, _ = h.path(az, max(s - 0.01 * k, 0.0), 0.004 * k)
            pts.append(p)
            nrm.append(nn)
            ups.append((p2 - p).normalized())
        elf._loop(buf, pts, nrm, ups, th * k, 0.006 * k, mat=mat, w=w)
        return pts, nrm, ups

    if acc in ("flower", "garland"):
        def fn(buf):
            pts, nrm, ups = ring(buf, 46.0, M_(f"{e.name}_leaf", "#6fae62"), n=12)
            step = 3 if acc == "flower" else 4
            for i in range(0, len(pts), step):
                Mf = Matrix.Translation(pts[i] + nrm[i] * 0.006 * k) @ frame(nrm[i], ups[i])
                c2.prism(buf, c2.star_poly(0.018 * k, 0.009 * k, n=5, rot=90.0), 0.003 * k, Mf,
                         mat=am if (i // step) % 2 == 0 else am2, w=w)
        e.part("head_acc", "head", fn)
    elif acc == "ribbon":
        def fn(buf):
            p, nn = h.path(v.get("acc_az", 40.0), h.s_of_el(v.get("acc_az", 40.0), 44.0), 0.006 * k)
            c2.bow_geo(buf, Matrix.Translation(p) @ frame(nn, (0, 0, 1)), 0.060 * k, am, w=w, tails=0.6, segs=5)
        e.part("head_acc", "head", fn)
    elif acc in ("beret", "cap"):
        def dome(buf, edge_fn, lift_fn, mat, n=16, rows=5):
            """머리카락 셸 바깥 면을 따르는 모자 덮개: 정수리에서 edge_fn(az) 높이(도)까지, lift_fn(u) 만큼 띄움."""
            top_i = buf.vert(h.path(0.0, 0.0, lift_fn(0.0))[0], w)
            grid = []
            for j in range(n):
                az = 360.0 * j / n
                se = h.s_of_el(az, edge_fn(az))
                grid.append([buf.vert(h.path(az, se * (i / rows) ** 0.85, lift_fn(i / rows))[0], w)
                             for i in range(1, rows + 1)])
            for j in range(n):
                j2 = (j + 1) % n
                buf.face((top_i, grid[j][0], grid[j2][0]), mat)
                for i in range(rows - 1):
                    buf.face((grid[j][i], grid[j][i + 1], grid[j2][i + 1], grid[j2][i]), mat)
            inner = []
            for j in range(n):
                az = 360.0 * j / n
                inner.append(buf.vert(h.path(az, h.s_of_el(az, edge_fn(az)), 0.0)[0], w))
            for j in range(n):
                j2 = (j + 1) % n
                buf.face((grid[j][-1], inner[j], inner[j2], grid[j2][-1]), mat)

        def fn(buf):
            if acc == "beret":
                # 캐릭터 왼쪽으로 기운 납작하고 부푼 베레모 + 꼭지
                edge = lambda az: 44.0 + 10.0 * math.cos(math.radians(az - 70.0))
                dome(buf, edge, lambda u: (0.008 + 0.026 * math.sin(math.pi * min(u * 1.25, 1.0))) * k, am)
                tp = h.path(0.0, 0.0, 0.030 * k)[0]
                c2.ellipsoid(buf, tp + V((0.010 * k, 0, 0.004 * k)), V((0, 0, 1)), V((1, 0, 0)), V((0, 1, 0)),
                             0.010 * k, 0.010 * k, 0.010 * k, segs=6, rings=3, mat=am2, w=w)
            else:
                # 챙모자: 머리를 덮는 크라운 + 앞 챙(크라운 앞 가장자리에서 앞·아래로)
                edge = lambda az: 30.0 - 6.0 * (1 - math.cos(math.radians(az))) / 2
                dome(buf, edge, lambda u: (0.008 + 0.010 * math.sin(math.pi * u)) * k, am)
                m_ = 9
                rows_ = []
                for jj in range(m_):
                    az = lerp(-62.0, 62.0, jj / (m_ - 1))
                    p0, n0 = h.path(az, h.s_of_el(az, edge(az)), 0.006 * k)
                    a = math.radians(az)
                    out = V((math.sin(a), -math.cos(a), 0.0))
                    f = math.cos(a) ** 0.7
                    p1 = p0 + out * (0.060 * k * f) + V((0, 0, -0.014 * k * f))
                    rows_.append([buf.vert(q, w) for q in (p0, p1, p1 - V((0, 0, 0.005 * k)), p0 - V((0, 0, 0.005 * k)))])
                for jj in range(m_ - 1):
                    for a_ in range(3):
                        buf.face((rows_[jj][a_], rows_[jj + 1][a_], rows_[jj + 1][a_ + 1], rows_[jj][a_ + 1]), am2)
        e.part("head_acc", "head", fn)
        hat_rim = (lambda az: 44.0 + 10.0 * math.cos(math.radians(az - 70.0))) if acc == "beret" else \
            (lambda az: 30.0 - 6.0 * (1 - math.cos(math.radians(az))) / 2)
        _ = hat_rim


# =========================================================================== 손깃발 (별도 노드)

def flag(e, v):
    """에르피엔 손깃발 = 에르피엔 군기 (lib/erpien_flag.hand_flag: 초록 천 + 노란 나비, 원작 도안, 사용자 결정 2026-11-02).
    로컬: 원점 = 파지점, 막대 = +Z. socket_hand_R에 붙인다 (소켓 소품이라 정점 색 머티리얼 하나로 합쳐진다)."""
    k = e.k
    M_ = elf.mat
    mats = {key: M_(f"{e.name}_fl_{key[4:]}", col) for key, col in ef.PAL.items()}
    b = Buf()
    ef.hand_flag(ef.buf_sink(b, mats, {}), Matrix.Scale(k, 4), W=0.17, stick=0.30)
    ob = b.obj(f"{e.name}_flag_geo", smooth=False)
    # 소켓 로컬(무기 규약: +Y 손가락, +Z 엄지 쪽)에 그대로 붙인다: 막대가 주먹을 엄지 쪽으로 관통한다
    sock = bpy.data.objects["socket_hand_R"]
    bpy.context.view_layer.update()
    # 막대 방향 = 손가락 쪽 0.8 + 엄지 쪽 0.6: 팔을 들면 막대가 위로 선다 (깃발 흔들기·만세)
    Mw = sock.matrix_world @ Matrix.Rotation(math.radians(-53.0), 4, "X")
    c3.socket_prop(e, ob, "socket_hand_R", Mw, name="flag", outline=0.002)


# =========================================================================== 애니메이션 (glTF 클립)

FIST = {f"{f}_{s}_{sd}": (a, 0, 0) for sd in ("L", "R") for f, a in (("f1", 0), ("f2", 0), ("f3", 0))
        for s in ("01", "02")}


def _fist(sd, amt=1.0):
    d = {}
    for f in ("f1", "f2", "f3"):
        d[f"{f}_01_{sd}"] = (70 * amt, 0, 0)
        d[f"{f}_02_{sd}"] = (80 * amt, 0, 0)
    d[f"thumb_01_{sd}"] = (25 * amt, 0, 0)
    d[f"thumb_02_{sd}"] = (40 * amt, 0, 0)
    return d


ANIM_BONES = ["spine", "chest", "neck", "head", "upperarm_L", "upperarm_R", "forearm_L", "forearm_R", "hand_L",
              "hand_R"] + [f"{f}_{s}_{sd}" for sd in ("L", "R") for f in ("f1", "f2", "f3", "thumb")
                           for s in ("01", "02")]


def _P(**over):
    """한 자세: 키 = 본 이름, 값 = (x, y, z) 도. 지정하지 않은 본은 0 (팔은 차렷에 가까운 내림)."""
    d = {b: (0.0, 0.0, 0.0) for b in ANIM_BONES}
    d["upperarm_L"] = (4.0, 0.0, -30.0)       # A 포즈(40° 내림)에서 몸 옆으로 더 내림
    d["upperarm_R"] = (4.0, 0.0, 30.0)
    d["forearm_L"] = (12.0, 0.0, 0.0)
    d["forearm_R"] = (12.0, 0.0, 0.0)
    for kk, vv in over.items():
        if kk == "fists":
            for sd in vv:
                d.update(_fist(sd))
        else:
            d[kk] = vv
    return d


def AIM(x, y, z):
    """위팔을 방향으로 겨눈다 (아마추어 공간, 캐릭터 왼팔 기준: +X 바깥, -Y 앞, +Z 위). 오른팔은 x를 뒤집는다.
    SD 머리가 커서 팔을 곧게 위로 들면 머리 뒤로 숨는다 → 만세는 V자로 벌리고 살짝 앞으로."""
    return ("aim", (x, y, z))


ARMS_UP = dict(upperarm_L=AIM(0.62, -0.28, 0.73), upperarm_R=AIM(0.62, -0.28, 0.73), forearm_L=(10.0, 0, 0),
               forearm_R=(10.0, 0, 0), chest=(-6.0, 0, 0), head=(-10.0, 0, 0))


def clips(e):
    """클립 이름 → [(초, 자세), ...]. 마지막 키와 첫 키가 같으면 반복용."""
    rest = _P()
    up_fist = _P(fists="LR", **ARMS_UP)
    up_open = _P(**ARMS_UP)
    up_low = _P(fists="LR", upperarm_L=AIM(0.70, -0.30, 0.55), upperarm_R=AIM(0.70, -0.30, 0.55),
                forearm_L=(35.0, 0, 0), forearm_R=(35.0, 0, 0), chest=(-2.0, 0, 0), head=(-6.0, 0, 0))
    wave_a = _P(upperarm_R=AIM(0.60, -0.28, 0.75), forearm_R=(20.0, 0, 0), head=(-4.0, -8.0, 0), chest=(0, -4.0, 0))
    wave_b = _P(upperarm_R=AIM(0.75, -0.28, 0.55), forearm_R=(55.0, 0, 0), head=(-4.0, -8.0, 0),
                chest=(0, -4.0, 0))
    clap_open = _P(upperarm_L=(58.0, 0, -12.0), upperarm_R=(58.0, 0, 12.0), forearm_L=(62.0, 0, 0),
                   forearm_R=(62.0, 0, 0), chest=(2.0, 0, 0))
    clap_shut = _P(upperarm_L=(60.0, 0, -32.0), upperarm_R=(60.0, 0, 32.0), forearm_L=(64.0, 0, 0),
                   forearm_R=(64.0, 0, 0), chest=(3.0, 0, 0))
    flag_a = _P(fists="R", upperarm_R=AIM(0.62, -0.30, 0.72), forearm_R=(15.0, 0, 0), chest=(0, 6.0, 0),
                head=(-6, 0, 0))
    flag_b = _P(fists="R", upperarm_R=AIM(0.35, -0.30, 0.88), forearm_R=(15.0, 0, 0), chest=(0, -6.0, 0),
                head=(-6, 0, 0))
    breathe = _P(chest=(2.0, 0, 0), head=(2.0, 0, 3.0))
    manse_one = [(0.00, rest), (0.33, up_open), (0.83, up_open), (1.33, rest)]
    manse3 = []
    for i in range(3):
        for t, p in manse_one[:-1] if i < 2 else manse_one:
            manse3.append((i * 1.33 + t, p))
    return {
        "idle": [(0.0, rest), (1.5, breathe), (3.0, rest)],
        "cheer": [(0.0, up_fist), (0.25, up_low), (0.5, up_fist)],
        "wave": [(0.0, wave_a), (0.3, wave_b), (0.6, wave_a)],
        "clap": [(0.0, clap_open), (0.18, clap_shut), (0.36, clap_open)],
        "flag": [(0.0, flag_a), (0.45, flag_b), (0.9, flag_a)],
        "manse": manse_one,
        "manse3": manse3,
    }


QUAT_BONES = ("upperarm_L", "upperarm_R")


def _local_quat(arm, bn, val):
    """위팔 값 → 본 로컬 쿼터니언. val = (x, y, z) 오일러(도) 또는 ("aim", 방향)."""
    from mathutils import Euler, Vector
    b = arm.data.bones[bn]
    if isinstance(val, tuple) and len(val) == 2 and val[0] == "aim":
        d = Vector(val[1])
        if bn.endswith("_R"):
            d.x = -d.x
        d.normalize()
        rest_q = b.matrix_local.to_quaternion()
        r = (rest_q @ Vector((0, 1, 0))).normalized()
        q_arm = r.rotation_difference(d)
        return rest_q.inverted() @ q_arm @ rest_q
    return Euler([math.radians(x) for x in val], "XYZ").to_quaternion()


def add_clips(e):
    arm = e.arm_obj
    arm.animation_data_create()
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION" if pb.name in QUAT_BONES else "XYZ"
    names = set(pb.name for pb in arm.pose.bones)
    for name, keys_ in clips(e).items():
        act = bpy.data.actions.new(name)
        act.use_fake_user = True
        arm.animation_data.action = act
        for t, pose in keys_:
            f = round(t * FPS)
            for bn, r in pose.items():
                if bn not in names:
                    continue
                pb = arm.pose.bones[bn]
                if bn in QUAT_BONES:
                    pb.rotation_quaternion = _local_quat(arm, bn, r)
                    pb.keyframe_insert("rotation_quaternion", frame=f)
                else:
                    pb.rotation_euler = [math.radians(x) for x in r]
                    pb.keyframe_insert("rotation_euler", frame=f)
        tr = arm.animation_data.nla_tracks.new()
        tr.name = name
        tr.strips.new(name, 0, act)
        arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.rotation_euler = (0.0, 0.0, 0.0)
        pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)


# =========================================================================== 싼 손 (군중용)

def _cheap_hand(self, side, material, *, inflate=0.0, cuff=None, name=None):
    """키트 Elf.hand와 같은 모양·같은 손가락 본 웨이트, 링과 분할만 줄였다 (손 하나 약 230 삼각형, 키트 최소 464).
    인스턴스 메서드로 갈아 끼운다 (elf.py는 고치지 않는다)."""
    k = self.k * self.arm_k
    W, L, P = self.W[side], self.adir[side], self.palm_n[side]
    T = V((0, -1, 0))
    buf = Buf()
    hb = f"hand_{side}"
    st = []
    tab = [(0.0, (0.021, 0.013)), (0.40, (0.0278, 0.0155)), (1.0, (0.026, 0.013))]
    n = 4
    for i in range(n):
        t = i / (n - 1)
        rx, ry = elf.keys(tab, t)
        c = W + L * (lerp(-0.004, 1.0, t) * self.hand_len) + P * (0.001 * k) + T * (0.001 * k)
        w = elf.mixw({f"forearm_{side}": 1.0}, {hb: 1.0}, smoothstep(0.0, 0.25, t))
        st.append({"c": c, "rx": rx * k + inflate, "ry": ry * k + inflate, "w": w, "ref": tuple(T), "p": 2.6})
    loft(buf, st, segs=6, cap0="round", cap1="round", mat=material, cap_len0=0.006 * k, cap_len1=0.007 * k,
         cap_rings=1)
    for nm, base, mid, tip in self._finger_joints(side):
        r0 = (0.0112 if nm == "thumb" else 0.0102) * k + inflate
        r1 = (0.0098 if nm == "thumb" else 0.0090) * k + inflate
        back = base - (mid - base).normalized() * 0.008 * k
        ch = elf.Chain([back, base, mid, tip], [hb, f"{nm}_01_{side}", f"{nm}_02_{side}"], blend=0.45)
        st = []
        for i in range(3):
            t = i / 2
            c, tan = ch.at(t)
            r = lerp(r0, r1, t)
            st.append({"c": c, "rx": r, "ry": r * 0.92, "w": ch.weights(t), "ref": tuple(T)})
        loft(buf, st, segs=4, cap0="round", cap1="round", mat=material, cap_len1=r1 * 0.9, cap_rings=1)
    return buf.obj(name or f"{self.name}_hand_{side}")


# =========================================================================== 원경 LOD (characters/crowd_lod/<이름>.glb)

#: 파츠별 줄이는 비율 (메시 이름 끝). 얇게 겹친 옷(치마 위 앞치마)이 서로 파고들지 않게 파츠마다 따로 줄인다
LOD_RATIO = {"body": 0.34, "arms": 0.3, "head": 0.4, "hair": 0.3, "hair_in": 0.3}
LOD_FACE = 0.45        # 얼굴 파츠 (UNLIT 하이라이트는 뺀다)
LOD_EXPR = "cheer"     # 원경 얼굴 표정 (모프를 굳힌다)


def _decimate(ob, ratio):
    if ratio >= 0.999:
        return
    m = ob.modifiers.new("lod", "DECIMATE")
    m.decimate_type = "COLLAPSE"
    m.ratio = ratio
    m.use_collapse_triangulate = True
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=m.name)
    ob.select_set(False)


def _tris(ob):
    ob.data.calc_loop_triangles()
    return len(ob.data.loop_triangles)


def export_lod(e, name):
    """원경 군중(인스턴싱)이 쓰는 같은 인물의 줄인 메시. 본·바인드는 본 모델과 같다(같은 빌드에서 내보냄).
    - 몸·팔·머리·머리카락을 파츠마다 LOD_RATIO로 줄여 하나로 합치고(<이름>_lod), 얼굴은 표정(LOD_EXPR)을 굳혀 head 본 100%로
      스키닝한 뒤 따로 줄인다(<이름>_lod_face: 런타임이 이름으로 알아보고 깊이를 당긴다).
    - 손깃발(소켓 소품)과 얼굴 하이라이트(UNLIT_)는 뺀다: 런타임이 본 모델의 깃발을 빌려 붙이고, 원경에서 하이라이트는 보이지 않는다.
    - 애니메이션은 넣지 않는다(본 모델 클립을 같은 본 이름으로 튼다)."""
    import bmesh
    arm = e.arm_obj
    arm.data.pose_position = "REST"         # NLA 클립이 자세를 바꾸지 않게 (레스트 = 바인드)
    bpy.context.view_layer.update()
    src = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.visible_get() and not o.get("prop")]
    body, face = [], None
    for o in src:
        c = o.copy()
        c.data = o.data.copy()
        cb.collection().objects.link(c)
        if o == e.face_obj or o.name.endswith("_face"):
            face = c
        else:
            body.append(c)
    for o in src:
        o.hide_set(True)
    for o in bpy.context.scene.objects:
        if o.type == "MESH" and o.get("prop"):
            o.hide_set(True)
    # 몸 쪽: 아마추어 모디파이어는 떼고(적용하면 자세가 구워진다) 합친 뒤 줄인다
    for c in body:
        for m in list(c.modifiers):
            if m.type == "ARMATURE":
                c.modifiers.remove(m)
        part = c.name.split(".")[0][len(name) + 1:]
        _decimate(c, LOD_RATIO.get(part, 0.34))
    lod = cb.join(body, name=f"{name}_lod")
    if face is not None:
        bpy.context.view_layer.update()
        keys = face.data.shape_keys
        if keys:
            for kb in keys.key_blocks:
                kb.value = 1.0 if kb.name == LOD_EXPR else 0.0
            bpy.ops.object.select_all(action="DESELECT")
            face.select_set(True)
            bpy.context.view_layer.objects.active = face
            bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
            face.select_set(False)
        mw = face.matrix_world.copy()
        face.parent = None
        face.matrix_world = Matrix.Identity(4)
        face.data.transform(mw)
        bm = bmesh.new()
        bm.from_mesh(face.data)
        unlit = {i for i, s in enumerate(face.material_slots) if s.material and s.material.name.startswith("UNLIT_")}
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in unlit], context="FACES")
        bm.to_mesh(face.data)
        bm.free()
        face.vertex_groups.clear()
        vg = face.vertex_groups.new(name="head")
        vg.add(list(range(len(face.data.vertices))), 1.0, "REPLACE")
        _decimate(face, LOD_FACE)
        face.name = face.data.name = f"{name}_lod_face"
    outs = [lod] + ([face] if face is not None else [])
    for ob in outs:
        # 남은 빈 머티리얼 칸 정리 (UNLIT 칸)
        for i in reversed(range(len(ob.material_slots))):
            s = ob.material_slots[i]
            if s.material is None or s.material.name.startswith("UNLIT_"):
                ob.active_material_index = i
                bpy.ops.object.select_all(action="DESELECT")
                ob.select_set(True)
                bpy.context.view_layer.objects.active = ob
                bpy.ops.object.material_slot_remove()
        ob.parent = arm
        ob.matrix_parent_inverse = Matrix.Identity(4)
        mod = ob.modifiers.new("Armature", "ARMATURE")
        mod.object = arm
        for kk in list(ob.keys()):
            del ob[kk]
        for pl in ob.data.polygons:
            pl.use_smooth = True
        ob["lod"] = 1
        ob.data.validate(clean_customdata=False)
    if face is not None:
        face["noOutline"] = 1     # 얼굴 스티커는 런타임이 깊이를 당긴다 (이름 _face)
    print(f"[crowd] {name} LOD tris={sum(_tris(o) for o in outs)}")
    path = os.path.join(cb.MODELS_DIR, "characters", "crowd_lod", f"{name}.glb")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.context.view_layer.update()
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=False, use_visible=True,
                              export_apply=False, export_yup=True, export_extras=True, export_cameras=False,
                              export_lights=False, export_animations=False, export_skins=True,
                              export_materials="EXPORT", export_image_format="AUTO")
    print(f"[cb] exported characters/crowd_lod/{name}.glb")
    arm.data.pose_position = "POSE"


# =========================================================================== 조립

def build(name, race, v):
    cb.reset()
    e = _body(name, race, v)
    import types
    e.hand = types.MethodType(_cheap_hand, e)
    _face(e, v)
    h = _hair(e, v)
    _head_acc(e, h, v)
    _clothes(e, race, v)
    if race == "fairy":
        fairy.wings(e, span=0.34, height=0.26, sweep=8.0, raise_=8.0, prim=2, cov=1, rings=1, style="erpin",
                    color=v.get("wing", "#fffdf9"), color2=v.get("wing2", "#f6e6cf"))
    if race == "beast":
        e.part("animal_ears", "head", lambda buf: (_ear_geo(buf, e, v, 1), _ear_geo(buf, e, v, -1)))
        _tail(e, v)
    e.finalize()
    if v.get("flag_prop", True):
        flag(e, v)
    add_clips(e)
    e.export(f"characters/{name}.glb")
    if os.environ.get("CROWD_LOD", "1") != "0":
        export_lod(e, name)
    return e
