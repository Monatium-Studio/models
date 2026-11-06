"""벨리타: 마녀 왕국 벨리티엔의 여왕이자 에르핀의 쌍둥이 언니. 엘리아스 침공전 종반에 프리클·리뉴아와 함께
마녀군 한 부대를 이끌고 모나티엄으로 진군해 도시를 탈환한다(원작). 3막 M9·에필로그 배경 장면용 카메오.

원작 벨리타(트릭컬 리바이브, '최고위 마녀')의 기본 복장을 따른다. 근거: docs/art/characters-cameo3.md.
- 식별 요소: 발목까지 오는 흰 생머리(끝이 옅은 크림빛 노랑), 캐릭터 왼쪽(+X)으로 가르마를 탄 옆으로 쓸린 앞머리,
  왼쪽 귀 뒤의 작은 땋은 머리, 이마 왼쪽 가장자리의 검은 뿔 하나(마녀 공통), 가시 돋은 검은 가지 머리띠와 붉은 마름모
  보석, 오드아이(오른눈 붉은색 = 에르핀과 같은 색, 왼눈 노란색 = 마녀의 눈)와 세로 동공, 반쯤 감은 무표정한 눈매,
  요정처럼 등에 달린 짙은 회색 깃털 날개(마녀 중 벨리타만), 붉은 상의(세운 깃, 깃의 붉은 마름모), 앞으로 늘어진
  붉은 앞자락과 짙은 문자 무늬, 오른 어깨를 덮고 가슴을 가로지르는 갈색빛 숄, 짧은 붉은 치마, 앞이 트인 바닥까지
  오는 짙은 붉은 겉자락과 밑단의 짙은 회색 털, 짙은 회색 팔 토시, 왼다리를 X자로 감은 가시덩굴(마녀 공통), 지팡이.
- 재해석: 지팡이는 별도 노드 belita_staff(오른손 본, 강체). 원작 지팡이의 둥근 머리(붉은 안테 + 금색 V 문장 원판),
  위로 휜 두 갈래, 떠 있는 붉은 마름모, 늘어진 붉은 리본, 아래 창끝을 3D로 다시 그렸다. 귀는 긴 머리에 가려 만들지
  않았다(요정 계열). 신은 발목 띠 두 줄의 크림색 단화로 단순화했다.
- 표정: 키트 5종 + command(여왕의 호령) + glare(내려다보는 차가운 눈) + fluster(동생 앞에서 허둥지둥) +
  proud(동생 자랑: 눈을 감은 듯 웃는 얼굴) + blink 교정 키.

npm run model -- art/blender/characters/belita.py
npm run shot -- characters/belita.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import cb  # noqa: E402
import elf  # noqa: E402
import fairy  # noqa: E402
import cameo2 as c2  # noqa: E402
import erpin_common as ec  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, smoothstep, frame, keys  # noqa: E402

cb.reset()
M_ = elf.mat
e = fairy.Fairy("belita", ears=None, height=1.20, chest=0.08, hips=0.98, leg=1.05, segs=0.64, hand_q=0.55,
                cheek=0.10, skin="#fbe6df")
k = e.k

# ---- 팔레트 (원작 카드 실측: 머리 #f3eeea → 끝 #f2e2b4, 상의 #b6404a, 겉자락 #8e2d3b, 숄 #8c5a5c, 뿔·가지 #4f484d)
red = M_("be_red", "#b8414c")
red_d = M_("be_red_d", "#8a2a39")
red_dd = M_("be_red_dd", "#5e1c29")
shawl = M_("be_shawl", "#94534f")
shawl_d = M_("be_shawl_d", "#6d4146")
dark = M_("be_dark", "#4d464c")
dark_d = M_("be_dark_d", "#37323a")
horn_m = M_("be_horn", "#5a5258")
gem_m = M_("be_gem", "#e0485a")
gem_l = M_("be_gem_l", "#f58a90")
gold = M_("be_gold", "#e3b14e")
cream = M_("be_cream", "#f1e4de")
fur = M_("be_fur", "#4a4449")


# ---- 얼굴: 오드아이 + 세로 동공 (마녀). 키트 얼굴 위에 동공만 바꾼다.
class WitchFace(elf.Face):
    """키트 얼굴 + 마녀의 세로 동공. 둥근 동공은 아주 작게 접고, 같은 자리에 세로로 긴 동공을 그린다.
    정점 수는 표정과 무관하게 같다(clip_to). 시선 키(gx, gz)도 따라간다."""

    def _build(self, P):
        pr = P["iris"]["pupil"]
        Q = elf._merge_expr(P, {"iris": {"pupil": 0.02}})
        buf = super()._build(Q)
        sz = self.sz
        for side in (1, -1):
            outline, _ = self.eye_outline(side, P)
            ip = P["iris"]
            icx = side * self.ex + side * ip["cx"] * sz + ip.get("gx", 0.0) * sz
            icz = self.ez + ip["cz"] * sz + ip.get("gz", 0.0) * sz
            iris = elf.clip_to(elf.ellipse2(icx, icz, ip["rx"] * sz, ip["ry"] * sz, max(16, int(24 * self.e.q))),
                               outline)
            w_ = ip["rx"] * sz * 0.17 * (0.6 + 0.4 * pr)
            h_ = ip["ry"] * sz * 0.66
            n = 14
            slit = []
            for i in range(n):
                a = 2 * math.pi * i / n
                c_ = math.cos(a)
                slit.append((icx + w_ * c_ * abs(c_) ** 0.2, icz - 0.002 * sz + h_ * math.sin(a)))
            self._fill(buf, elf.clip_to(slit, iris), 0.0026, self.m["pupil"], rings=())
        return buf


def witch_face(**kw):
    f = WitchFace(e, **kw)
    ob = f.build()
    vc = elf.vc_material(f"{e.name}_toon_vc", e.line)
    elf.bake_vcol(ob)
    elf.remap_to_vc(ob, vc)
    elf.collapse_slots(ob)
    e.face_obj = ob
    e.face_builder = f
    return ob


# 왼눈(+X) 노란색으로 만들고, 오른눈(-X)만 붉은색으로 바꾼다
witch_face(eye_color="#f2a42c", iris_dark="#9a4a1e", iris_light="#ffe27a", pupil="#3a1810",
           lash="#4a2a30", brow="#d9cdc8", brow_th=1.0, blush="#f2a3a0", blush_size=1.0,
           base={"eye": {"top": 0.015, "ktop": 5.2, "tilt_out": -0.002, "cout": 0.013, "bot": 0.050},
                 "iris": {"cz": 0.0010, "ry": 0.0380},
                 "brow": {"dz": 0.058, "ang": -3.0, "arch": 0.002, "len": 0.038},
                 "mouth": {"w": 0.014, "curve": 0.0003}},
           expr={
               # 여왕의 호령: 눈을 뜨고 눈썹을 내리며 입을 벌린다
               "command": {"eye": {"top": 0.026, "ktop": 3.6, "tilt_in": -0.010},
                           "brow": {"ang": -16.0, "dz": 0.054, "th": 0.0070},
                           "mouth": {"w": 0.024, "open": 0.020, "curve": -0.0004, "top_arch": 0.004}},
               # 내려다보는 차가운 눈: 더 가늘게, 바깥 눈꼬리를 내린다
               "glare": {"eye": {"top": 0.012, "ktop": 5.0, "tilt_in": -0.006, "tilt_out": -0.004},
                         "iris": {"pupil": 0.8},
                         "brow": {"ang": -12.0, "dz": 0.054},
                         "mouth": {"w": 0.016, "curve": -0.0020}},
               # 동생 앞에서 허둥지둥: 동그랗게 뜬 눈, 올라간 눈썹, 물결 입
               "fluster": {"eye": {"top": 0.036, "ktop": 2.2, "bot": 0.056},
                           "iris": {"pupil": 0.6, "rx": 0.0250, "ry": 0.034},
                           "brow": {"ang": 18.0, "dz": 0.074, "arch": 0.004},
                           "mouth": {"w": 0.024, "curve": -0.0020, "open": 0.0080, "wave": 0.0022}},
               # 동생 자랑: 아래 눈꺼풀을 올려 웃는 눈, 입을 벌리고 웃는다
               "proud": {"eye": {"lift": 0.026, "top": 0.022, "kbot": 2.5},
                         "brow": {"dz": 0.066, "ang": 6.0, "arch": 0.006},
                         "mouth": {"w": 0.026, "curve": 0.0070, "open": 0.0080, "top_arch": -0.0010}},
           })
c2.recolor_face(e, lambda c: c.x < 0, {"#f2a42c": "#e2463c", "#9a4a1e": "#86689e", "#ffe27a": "#ffa266",
                                        "#3a1810": "#3a0c16"})

# ---- 머리 (헤어 v2): 흰 긴 생머리, 왼쪽(+X) 가르마의 쓸린 앞머리, 가슴까지 오는 옆머리, 종아리까지 오는 뒷머리
HAIR, HAIR_D, HAIR_L = "#f4efeb", "#d8cdd0", "#ffffff"
HAIR_TIP, HAIR_TIP_D = "#f1dfa8", "#d8c08a"


def belita_locks(h, lk):
    if lk["region"] == "front":
        lk["p"] = 2.7                # 끝을 조금 뭉툭하게 (삐죽한 톱니 대신)
        lk["free"] *= 0.62
    elif lk["region"] in ("side", "back"):
        lk["p"] = 2.2
        lk["free"] *= 0.60


h = fairy.hair(e, HAIR, dark=HAIR_D, light=HAIR_L, volume=1.14, lock_fn=fairy.lock_edit(belita_locks))
h.cap(front=30, side=-6, back=-46, part=26, segs=16, rows=5)
h.bangs(n=6, spread=58, tip_el=-6, sweep=-30, part=26, jag=0.30, curl=1.1, seed=3.0)
h.sides(length=0.40, width=0.096, az=60, curl=0.3, thick=1.40, puff=1.2)
h.back(length=0.60, n=9, spread=98)
h.braid(side=1, az=96.0, el=-4.0, length=0.15, width=0.034, beads=7, tie=None, tuft=0.020)
h.shine(el=50, spread=74, n=2, size=1.2)
o = h.off

# ---- 뿔: 이마 왼쪽(+X) 가장자리에서 바깥으로 나와 위로 휜다
r0 = h.sp(36.0, 42.0, o * 0.2)


def horn(buf):
    w = {"head": 1.0}
    out = V((1.0, 0.12, 0.0)).normalized()
    ctrl = [r0 - out * 0.014 * k - V((0, 0, 0.008 * k)), r0 + out * 0.034 * k + V((0, 0, 0.010 * k)),
            r0 + out * 0.070 * k + V((0, 0.012 * k, 0.036 * k)), r0 + out * 0.082 * k + V((0, 0.024 * k, 0.078 * k)),
            r0 + out * 0.070 * k + V((0, 0.032 * k, 0.118 * k))]
    P = elf.catmull([V(p) for p in ctrl], 16)
    st = []
    for i, q in enumerate(P):
        t = i / (len(P) - 1)
        r = lerp(0.030, 0.0016, t ** 0.8) * k
        st.append({"c": q, "rx": r, "ry": r * 0.90, "w": w})
    loft(buf, st, segs=10, cap0="flat", cap1="round", mat=horn_m)


e.part("horn", "head", horn)


# ---- 가시 돋은 검은 가지 머리띠 + 붉은 마름모 보석
def circlet(buf):
    w = {"head": 1.0}

    def el_fn(az):
        # 앞(오른쪽 위)에서 높고, 왼쪽 뒤(땋은 머리 쪽)로 내려간다
        return lerp(48.0, 8.0, smoothstep(-40.0, 120.0, az))

    pts, nrm = [], []
    for i in range(21):
        az = lerp(-70.0, 125.0, i / 20)
        s = h.s_of_el(az, el_fn(az))
        p, nn = h.path(az, s, 0.004 * k)
        pts.append(p + V((0, 0, 0.004 * k * math.sin(i * 1.7))))
        nrm.append(nn)
    st = [{"c": q, "rx": 0.0055 * k, "ry": 0.0046 * k, "w": w} for q in pts]
    loft(buf, st, segs=5, cap0="round", cap1="round", mat=dark)
    # 가시: 바깥으로 비스듬히
    for i in range(2, 20, 3):
        q, nn = pts[i], nrm[i]
        T = (pts[i + 1] - pts[i - 1]).normalized()
        d = (nn * 0.8 + T * (0.6 if i % 2 else -0.6) + V((0, 0, 0.3))).normalized()
        loft(buf, [{"c": q, "rx": 0.0040 * k, "ry": 0.0030 * k, "w": w},
                   {"c": q + d * 0.012 * k, "rx": 0.0004 * k, "ry": 0.0004 * k, "w": w}],
             segs=4, cap0="flat", cap1="flat", mat=dark)
    # 앞(오른쪽 위) 마름모 셋: 가운데 큰 것이 아래로 길다
    az0 = -14.0
    p, nn = h.path(az0, h.s_of_el(az0, el_fn(az0) - 2.0), 0.007 * k)
    up = (h.path(az0, max(h.s_of_el(az0, el_fn(az0) - 2.0) - 0.02 * k, 0.0), 0.007 * k)[0] - p).normalized()
    Mc = Matrix.Translation(p) @ frame(nn, up)
    ec.gem(buf, Mc @ Matrix.Translation((0, 0, -0.010 * k)), 0.026 * k, 0.058 * k, gem_m, depth=0.006 * k,
           frame_mat=dark, frame_w=0.005 * k, wts=w)
    for sg in (1, -1):
        Ms = Mc @ Matrix.Translation((sg * 0.032 * k, 0.003 * k, 0.004 * k)) @ Matrix.Rotation(
            math.radians(-sg * 30), 4, "Y")
        ec.gem(buf, Ms, 0.017 * k, 0.034 * k, gem_m, depth=0.004 * k, frame_mat=dark, frame_w=0.003 * k, wts=w)
    # 왼쪽 뒤(땋은 머리 위) 마름모 둘
    for az, dz in ((104.0, 0.0), (116.0, -0.010)):
        s = h.s_of_el(az, el_fn(az) - 6.0)
        p, nn = h.path(az, s, 0.006 * k)
        Mx = Matrix.Translation(p + V((0, 0, dz * k))) @ frame(nn, (0, 0, 1))
        ec.gem(buf, Mx, 0.012 * k, 0.032 * k, gem_m, depth=0.004 * k, frame_mat=dark, frame_w=0.003 * k, wts=w)


e.part("circlet", "head", circlet)

# ---- 붉은 상의: 세운 깃 + 깃의 붉은 마름모 브로치
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(red, hem=wz - 0.006 * k, collar="stand", collar_mat=red_d, flare=0.006)
e.part("collar_trim", "body", lambda buf: band(buf, (0, 0.004 * k, e.torso_top + 0.028 * k), (0, 0, 1), (1, 0, 0),
                                               0.0545 * k, 0.0505 * k, 0.0050 * k, 0.0030 * k, segs=16, mat=dark,
                                               w={"neck": 0.5, "chest": 0.5}))
e.gear("brooch", ("torso", e.torso_top - 0.004 * k, 0.0, 0.014 * k),
       lambda b, Mx, w: ec.gem(b, Mx, 0.020 * k, 0.030 * k, gem_m, depth=0.005 * k, frame_mat=dark,
                               frame_w=0.004 * k, wts=w))
e.sleeves(red, length=0.46, off=0.010, flare=0.010, cuff=(red_d, 0.012, 0.004))
for sd in ("L", "R"):    # 짙은 회색 팔 토시 + 테
    c2.arm_tube(e, dark, sd, 0.64, 0.90, off=0.006, name=f"bracer_{sd}")
    e.ring(dark_d, f"arm_{sd}", 0.88, h=0.010, th=0.003, off=0.010, name=f"bracer_bot_{sd}")

# ---- 숄: 오른 어깨(-X)를 덮고 가슴을 가로질러 왼쪽 허리로
c2.arm_tube(e, shawl, "R", 0.0, 0.40, off=0.020, extra=lambda t: 0.010 * smoothstep(0.1, 0.4, t), name="shawl_arm")
e.ring(shawl_d, "arm_R", 0.40, h=0.010, th=0.003, off=0.031, name="shawl_arm_hem")


def strap_out(material, path, *, width, th, name):
    """e.strap과 같은 끈이지만 면이 바깥을 보게 감는다 (키트 _loop 끈은 폭 방향이 tan×n이라 면이 안쪽을 봐서
    넓은 끈에서 아웃라인이 사라진다)."""
    anchors = [e.anchor(a) for a in path]
    pts = elf.catmull([a.pos for a in anchors], max(8, len(anchors) * 4))
    nrm = elf.catmull([a.n for a in anchors], len(pts))

    def wf(t):
        f = t * (len(anchors) - 1)
        i = min(int(f), len(anchors) - 2)
        return elf.mixw(anchors[i].w, anchors[i + 1].w, f - i)
    ups = []
    for i in range(len(pts)):
        tan = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
        ups.append(nrm[i].cross(tan).normalized())
    e.part(name, "body", lambda buf: fairy.taper_strip(buf, pts, nrm, ups, [width * k] * len(pts), th * k,
                                                        mat=material, w=wf))


strap_out(shawl, [("torso", e.torso_top - 0.004 * k, -150, 0.024 * k), ("torso", e.shoulder_z + 0.010 * k, -96, 0.030 * k),
                  ("torso", e.shoulder_z - 0.020 * k, -48, 0.032 * k), ("torso", cz - 0.010 * k, 6, 0.034 * k),
                  ("torso", wz + 0.004 * k, 52, 0.032 * k), ("torso", wz - 0.010 * k, 92, 0.032 * k)],
          width=0.072, th=0.006, name="shawl")

# ---- 짧은 붉은 치마 + 허리띠
skirt = c2.Shell(e, red, wz + 0.006 * k, e.crotch_z - 0.030 * k, off=0.016, th=0.004, skirt=True, cols=24, rows=5,
                 flare=[(0.0, 0.0), (0.5, 0.008), (1.0, 0.022)], cover=True)
skirt.hem_trim(dark, width=0.010, th=0.0025)
skirt.done("skirt")
e.belt(dark, z=wz + 0.004 * k, h=0.012, th=0.004, off=0.020)

# ---- 앞자락: 깃에서 치마 밑단 아래까지 늘어진 붉은 판 + 짙은 테 + 문자 무늬 + 뾰족한 끝
def tabard(buf):
    pts, nrm, ups, wds = [], [], [], []
    zs = [e.torso_top - 0.016 * k, cz + 0.030 * k, cz - 0.020 * k, wz + 0.010 * k]
    for z in zs:
        p, n = e.torso_point(z, 0.0, 0.026 * k)
        pts.append(p)
        nrm.append(n)
    for u in (0.35, 0.75, 1.02):
        p, n = skirt.surface(u, 0.0, 0.010 * k)
        pts.append(p)
        nrm.append(n)
    P = elf.catmull(pts, 18)
    N = [nrm[min(int(i / (len(P) - 1) * (len(nrm) - 1) + 0.5), len(nrm) - 1)] for i in range(len(P))]
    U, S_ = [], []
    for i in range(len(P)):
        a = P[max(i - 1, 0)]
        b = P[min(i + 1, len(P) - 1)]
        U.append((a - b).normalized())
        S_.append((a - b).cross(N[i]).normalized())     # 폭 방향 (taper_strip의 ups)
    W_ = [lerp(0.032, 0.042, i / (len(P) - 1)) * k for i in range(len(P))]
    wts = [e._torso_wfn(q, 0) if q.z > e.hipj_z else c2.skirt_w(e, q) for q in P]
    nP = len(P)

    def wf(t):
        return wts[min(int(round(t * (nP - 1))), nP - 1)]
    fairy.taper_strip(buf, P, N, S_, W_, 0.003 * k, mat=red, w=wf)
    for sg in (1, -1):    # 짙은 테
        ed = [P[j] + S_[j] * sg * (W_[j] * 0.5 - 0.0015 * k) + N[j] * 0.0012 * k for j in range(nP)]
        fairy.taper_strip(buf, ed, N, S_, [0.0045 * k] * nP, 0.0025 * k, mat=dark, w=wf)
    # 끝: 아래로 뾰족한 짙은 쐐기
    q, n = P[-1], N[-1]
    Mx = Matrix.Translation(q + n * 0.002 * k) @ frame(n, U[-1])
    fairy.prism(buf, [(-0.022 * k, 0.004 * k), (0.022 * k, 0.004 * k), (0.0, -0.028 * k)], 0.004 * k, Mx, mat=dark,
                w=wts[-1], chamfer=0.0012 * k)
    # 문자 무늬 (짙은 기호 4개)
    for j, z in enumerate((cz - 0.044 * k, cz - 0.058 * k, wz + 0.024 * k, wz + 0.012 * k)):
        p, n = e.torso_point(z, 0.0, 0.0295 * k)
        Mg = Matrix.Translation(p) @ frame(n, (0, 0, 1))
        shapes = [[(-0.005, -0.0025), (0.005, -0.0025), (0.005, 0.0025), (-0.005, 0.0025)],
                  [(-0.005, -0.004), (-0.002, -0.004), (0.005, 0.004), (0.002, 0.004)],
                  [(-0.005, -0.004), (0.005, -0.004), (0.0, 0.004)],
                  [(-0.0018, -0.005), (0.0018, -0.005), (0.0018, 0.005), (-0.0018, 0.005)]]
        fairy.prism(buf, [(x * k, y * k) for x, y in shapes[j]], 0.0012 * k, Mg, mat=dark_d,
                    w=e._torso_wfn(p, 0))


e.part("tabard", "body", tabard)

# ---- 바닥까지 오는 겉자락 (허리에서, 앞이 트임) + 밑단 짙은 회색 털
train = c2.Shell(e, red_d, wz + 0.010 * k, 0.020 * k, gap=[(0.0, 34.0), (0.4, 44.0), (1.0, 58.0)], off=0.026,
                 th=0.005, skirt=True, cols=18, rows=9, flare=[(0.0, 0.0), (0.2, 0.016), (0.6, 0.060), (1.0, 0.110)])
train.edge_trim(red_dd, width=0.008, th=0.002)
hem = [train.surface(1.0, lerp(58.0, 302.0, i / 20), 0.008 * k)[0] for i in range(21)]
ec.bead_tube(train.buf, hem, 0.016 * k, 0.030 * k, 11, segs=6, n_per=3, mat=fur, wfn=lambda q: c2.skirt_w(e, q))
train.done("train")

# ---- 다리: 왼다리(+X) 가시덩굴 X자 감기, 크림색 단화 + 발목 띠
def vine(buf, side, chir, phase):
    sd = side
    st = []
    t0, t1 = 0.10, 0.92
    n = 26
    pts = []
    for i in range(n):
        t = lerp(t0, t1, i / (n - 1))
        ang = phase + chir * 360.0 * 2.2 * (i / (n - 1))
        a = e.anchor((f"leg_{sd}", t, ang, 0.006 * k))
        pts.append((a.pos, a.n, a.w))
        st.append({"c": a.pos, "rx": 0.0042 * k, "ry": 0.0042 * k, "w": a.w})
    loft(buf, st, segs=5, cap0="round", cap1="round", mat=dark)
    for i in range(2, n - 1, 3):
        q, nn, w = pts[i]
        T = (pts[i + 1][0] - pts[i - 1][0]).normalized()
        d = (nn * 0.85 + T * 0.5).normalized()
        loft(buf, [{"c": q, "rx": 0.0034 * k, "ry": 0.0026 * k, "w": w},
                   {"c": q + d * 0.010 * k, "rx": 0.0003 * k, "ry": 0.0003 * k, "w": w}],
             segs=4, cap0="flat", cap1="flat", mat=dark)


e.part("vine_a", "body", lambda b: vine(b, "L", 1, 30.0))
e.part("vine_b", "body", lambda b: vine(b, "L", -1, 150.0))
e.boots(cream, top=0.88, sole=(dark_d, 0.012), off=0.008, toe=0.002)
for sd in ("L", "R"):
    for t in (0.90, 0.955):
        e.ring(dark, f"leg_{sd}", t, h=0.008, th=0.003, off=0.012, name=f"ankle_{sd}{t}")

# ---- 날개: 짙은 회색 깃털 (요정 날개를 가진 유일한 마녀)
fairy.wings(e, span=0.30, height=0.19, sweep=14.0, raise_=16.0, prim=3, cov=2, color="#827a80", color2="#5b545c",
            th=0.015, z=e.chest_z + 0.040 * k)

# ---- 지팡이 (별도 노드 belita_staff, 오른손 본 강체)
grip = e._grip_point("R")
AX = V((-0.08, -0.05, 1.0)).normalized()        # 위로 세우고 살짝 바깥·앞으로
SIDE = AX.cross(V((0, -1, 0))).normalized()     # 머리 원판의 가로축 (+X 쪽)
FWD = SIDE.cross(AX).normalized()               # 원판 앞면이 보는 쪽 (-Y)
RF = Matrix((SIDE, -FWD, AX)).transposed().to_4x4()   # 로컬: X 옆, -Y 앞(바깥), Z 축 (prism·gem 규약)


def sp_(u, x=0.0, y=0.0):
    """지팡이 축 좌표 → 월드 (u: 손잡이에서 위로 m, x: 옆, y: 앞)."""
    return grip + AX * (u * k) + SIDE * (x * k) + FWD * (y * k)


def fr(u, x=0.0, y=0.0):
    M = RF.copy()
    M.translation = sp_(u, x, y)
    return M


staff = Buf()
U0, U1 = -0.36, 0.60          # 창끝 아래 ~ 머리 고리 아래
loft(staff, [{"c": sp_(u), "rx": 0.0105 * k, "ry": 0.0105 * k, "w": {}} for u in (U0, 0.0, U1)], segs=8,
     cap0="flat", cap1="flat", mat=dark)
for u in (-0.045, 0.045, 0.50, 0.56):     # 붉은 감은 끈
    band(staff, sp_(u), AX, SIDE, 0.0130 * k, 0.0130 * k, 0.012 * k, 0.003 * k, segs=8, mat=red)
# 창끝
loft(staff, [{"c": sp_(U0), "rx": 0.013 * k, "ry": 0.007 * k, "w": {}, "ref": tuple(SIDE)},
             {"c": sp_(U0 - 0.035), "rx": 0.020 * k, "ry": 0.009 * k, "w": {}, "ref": tuple(SIDE)},
             {"c": sp_(U0 - 0.10), "rx": 0.0008 * k, "ry": 0.0008 * k, "w": {}, "ref": tuple(SIDE)}],
     segs=4, cap0="flat", cap1="flat", mat=dark_d, p=1.0)
# 머리: 고리(안쪽 붉은 테) + 원판(금색 V 문장)
R_ = 0.080
RC = U1 + R_ + 0.004
NR = 16
ring_o = [{"c": sp_(RC - R_ * math.cos(2 * math.pi * i / NR), R_ * math.sin(2 * math.pi * i / NR)), "rx": 0.011 * k,
           "ry": 0.009 * k, "w": {}} for i in range(NR)]
loft(staff, ring_o + [dict(ring_o[0])], segs=6, cap0="flat", cap1="flat", mat=dark)
ring_r = [{"c": sp_(RC - (R_ - 0.014) * math.cos(2 * math.pi * i / NR), (R_ - 0.014) * math.sin(2 * math.pi * i / NR)),
           "rx": 0.0045 * k, "ry": 0.0045 * k, "w": {}} for i in range(NR)]
loft(staff, ring_r + [dict(ring_r[0])], segs=5, cap0="flat", cap1="flat", mat=red)
disc(staff, sp_(RC, 0, 0.0045), FWD, AX, 0.058 * k, 0.058 * k, 0.009 * k, segs=16, mat=red_d)
fairy.prism(staff, [(-0.030 * k, 0.022 * k), (-0.016 * k, 0.022 * k), (0.0, -0.006 * k), (0.016 * k, 0.022 * k),
                    (0.030 * k, 0.022 * k), (0.0, -0.030 * k)], 0.004 * k, fr(RC, 0, 0.0140), mat=gold,
            chamfer=0.001 * k)
# 위로 휜 두 갈래 (고리 옆에서 위로)
for sg in (1, -1):
    ctrl = [sp_(RC + 0.010, sg * R_ * 0.96), sp_(RC + 0.070, sg * R_ * 1.22), sp_(RC + 0.150, sg * R_ * 1.12),
            sp_(RC + 0.215, sg * R_ * 0.78)]
    P = elf.catmull(ctrl, 8)
    loft(staff, [{"c": q, "rx": lerp(0.010, 0.0012, i / (len(P) - 1)) * k, "ry": lerp(0.008, 0.0012, i / (len(P) - 1)) * k,
                  "w": {}} for i, q in enumerate(P)], segs=5, cap0="flat", cap1="round", mat=dark)
# 떠 있는 붉은 마름모 (고리 위 가운데 큰 것 + 옆 작은 것)
for x, u, s_ in ((0.0, RC + R_ + 0.055, 1.0), (-0.058, RC + R_ + 0.020, 0.55)):
    ec.gem(staff, fr(u, x, 0.0), 0.034 * k * s_, 0.064 * k * s_, gem_m, depth=0.008 * k * s_, frame_mat=gem_l,
           frame_w=0.002 * k)
# 늘어진 붉은 리본 두 가닥 + 끝 추
for sg, ln in ((1, 0.42), (-1, 0.34)):
    top = sp_(RC - R_ + 0.004, sg * 0.020, 0.0)
    pts = [top, top - AX * (ln * 0.3 * k) + SIDE * (sg * 0.012 * k), top - AX * (ln * 0.7 * k) + SIDE * (sg * 0.006 * k),
           top - AX * (ln * k)]
    P = elf.catmull(pts, 8)
    loft(staff, [{"c": q, "rx": 0.009 * k, "ry": 0.0018 * k, "w": {}, "ref": tuple(SIDE)} for q in P], segs=4,
         cap0="flat", cap1="flat", mat=red, p=1.0)
    Mx = RF.copy()
    Mx.translation = P[-1] - AX * 0.012 * k
    fairy.prism(staff, [(-0.010 * k, 0.012 * k), (0.010 * k, 0.012 * k), (0.0, -0.022 * k)], 0.005 * k, Mx,
                mat=dark_d, chamfer=0.0015 * k)
sob = staff.obj("belita_staff_geo", angle=35.0)
c2.prop(e, "staff", sob, "hand_R", outline=0.003)

e.finalize()

# 머리끝 크림빛 노랑 그라데이션 (정점색)
hob = e.result.get("hair")
zmin = min(v.co.z for v in hob.data.vertices)
for node, base, tip in (("hair", HAIR, HAIR_TIP), ("hair_in", HAIR_D, HAIR_TIP_D)):
    ob = e.result.get(node)
    if ob is not None:
        c2.vc_gradient(ob, base, [(zmin + 0.03 * k, tip), (zmin + 0.30 * k, base)])

e.export("characters/belita.glb")
