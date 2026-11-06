"""헤일리: 엘피니아 지구 침공 선봉대 지휘관. 프롤로그 오프닝에서 지구 침공 작전을 브리핑한다.

원작 헤일리(트릭컬 리바이브)의 '정복 차림'(헤일리(멀쩡) 테마극장·기억조각 「파라노이아 액티비티」 컷)을 바탕으로 한
카메오 모델. 전투복이 아니라 엘피니아 정복이다 (reference-notes 5.6).
- 유지한 식별 요소: 무릎까지 오는 붉은 생머리와 일자 앞머리, 분홍빛 눈, 왼쪽 귀의 은색 별 귀걸이,
  남색 정모(챙 + 높은 크라운)와 앞의 금색 톱니 휘장(엘프 로고), 남색 더블 브레스트 재킷과 금색 단추·견장·훈장,
  빨강-하양 줄무늬 허리띠, 남색 주름치마, 검은 니삭스와 부츠, 흰 장갑, 검은 망토.
- 재해석: 휘장은 원작 엘프 로고(ART_GUIDE 1장 예외)로 만들었다. 견장 술, 재킷 여밈선, 소매 금줄, 정모 턱끈,
  망토 고정 고리 같은 3차 디테일을 더했다. 원작의 소용돌이 눈은 옮기지 않았다(reference-notes 2장).
- 표정: 키트 5종 + confident(자신만만한 미소), briefing(브리핑 중 진지함), salute(경례), smirk(한쪽 입꼬리)
  + blink 교정 키.
근거: docs/art/characters-cameo2.md

npm run model -- art/blender/characters/haley.py
npm run shot -- characters/haley.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, smoothstep  # noqa: E402

cb.reset()
M_ = elf.mat
e = elf.Elf("haley", height=1.26, head=0.45, leg=1.04, chest=0.50, bust=0.60, hips=1.04, segs=0.74, hand_q=0.6, cheek=0.09)
k = e.k

# ---- 팔레트 (원작 실측: 머리 #c92a3f, 정복 #3b4566, 금색 #e7b23c, 망토 #26222c, 눈 #ee5d9a)
navy = M_("hl_navy", "#3a4466")
navy_d = M_("hl_navy_d", "#2a3150")
gold = M_("hl_gold", "#e9b440")
gold_d = M_("hl_gold_d", "#b98326")
red = M_("hl_red", "#c8323e")
white = M_("hl_white", "#f4f1ef")
cape_m = M_("hl_cape", "#2a2630")
cape_in = M_("hl_cape_in", "#3a3442")
black = M_("hl_black", "#25222b")
sole = M_("hl_sole", "#18161c")
glove = M_("hl_glove", "#f6f3f2")
silver = M_("hl_silver", "#d7d5e0")
visor_m = M_("hl_visor", "#1e1d26")

# ---- 얼굴: 분홍빛 눈, 굵은 붉은 갈색 눈썹, 기본은 여유 있는 표정
e.face(eye_color="#ee5d9a", iris_dark="#a01f5a", iris_light="#ffc2dc", pupil="#4e0d2c",
       lash="#5a1d2a", brow="#8e2a35", brow_th=1.25, blush="#f7a3a8", blush_size=1.05,
       base={"eye": {"top": 0.026, "ktop": 3.4},
             "brow": {"dz": 0.062, "ang": -2.0, "arch": 0.002},
             "mouth": {"w": 0.021, "curve": 0.0035}},
       expr={
           # 자신만만한 미소: 살짝 내리깐 눈, 올라간 입꼬리
           "confident": {"eye": {"top": 0.020, "lift": 0.012, "ktop": 3.8},
                         "brow": {"dz": 0.064, "ang": -5.0, "arch": 0.004},
                         "mouth": {"w": 0.032, "curve": 0.0085, "open": 0.0045, "top_arch": -0.0012}},
           # 브리핑 중 진지함: 눈썹을 모으고 입을 벌려 말하는 중
           "briefing": {"eye": {"top": 0.024, "tilt_in": -0.008, "ktop": 3.6},
                        "brow": {"ang": -12.0, "dz": 0.056, "th": 0.0072, "arch": 0.0},
                        "mouth": {"w": 0.021, "curve": -0.0010, "open": 0.0080, "top_arch": 0.0012}},
           # 경례: 크게 뜬 단호한 눈, 다문 입
           "salute": {"eye": {"top": 0.033, "ktop": 2.8, "tilt_in": -0.004},
                      "brow": {"ang": -8.0, "dz": 0.066, "th": 0.0070},
                      "mouth": {"w": 0.018, "curve": 0.0012}},
       })
c2.face_expr(e, "smirk",
             both={"eye": {"top": 0.021, "lift": 0.008}, "mouth": {"w": 0.030, "curve": 0.0035, "open": 0.0015}},
             L={"brow": {"dz": 0.068, "ang": 2.0, "arch": 0.004}},
             R={"brow": {"dz": 0.058, "ang": -10.0}},
             corner=(0.0095, -0.0015), mouth_dx=0.0025 * k)

# ---- 머리: 붉은 긴 생머리, 일자 앞머리, 무릎까지 오는 옆·뒷머리
HAIR = "#d4364a"


def blunt(h, lk):
    """일자 앞머리: 끝을 뭉툭하게(p↑), 갈라짐을 짧게."""
    if lk["region"] == "front":
        lk["p"] = 2.6
        lk["free"] *= 0.55


h = c2.hair(e, HAIR, dark="#9c1f33", light="#f58a8f", volume=1.05, lock_fn=c2.lock_edit(blunt))
h.cap(front=28, side=-8, back=-48)
h.bangs(n=7, spread=60, tip_el=-1, jag=0.05, sweep=0, curl=0.8, seed=2.0)
h.sides(length=0.16, width=0.070)
h.back(length=0.52, n=7, spread=100)
h.shine(el=46, spread=70, size=1.1)

# ---- 정모: 남색 크라운 + 짙은 띠 + 검은 챙 + 금색 턱끈 + 엘프 로고 휘장
OFF = 0.040 * k
TILT = math.radians(7.0)   # 뒤로 살짝 젖혀 씀


def rim_el(az):
    a = abs(((az + 180) % 360) - 180)
    return lerp(31.0, 20.0, smoothstep(0, 180, a))


BADGE = {}


def cap_geo(buf):
    w = {"head": 1.0}
    n = 28
    hc = e.head_c
    up = V((0, 0, 1))
    ring_b, ring_t = [], []
    for j in range(n):
        az = 360.0 * j / n
        ring_b.append(e.head_point(az, rim_el(az), OFF)[0])
        ring_t.append(e.head_point(az, rim_el(az) + 12.0, OFF * 1.05)[0])
    ct = sum(ring_t, V()) / n
    z_top = hc.z + e.hh / 2 + OFF * 0.85          # 크라운은 정수리(머리카락 포함)보다 높아야 한다
    prof = [(0.35, 0.30, 0.004), (0.80, 0.86, -0.010), (1.0, 1.0, 0.0)]   # (반경 비율, 높이 비율, 바깥 볼록)
    side, top = [], []
    for j in range(n):
        a = math.radians(360.0 * j / n)
        fr = 0.5 + 0.5 * math.cos(a)                      # 1=앞, 0=뒤
        p1 = ring_t[j]
        d = V((p1.x - ct.x, p1.y - ct.y, 0.0))
        rr = d.length
        d.normalize()
        R = rr * 1.30 + 0.024 * k
        zc = z_top + 0.048 * k * fr ** 1.6 - 0.006 * k * (1 - fr)
        col = []
        for rf, zf, bulge in prof:
            r_ = lerp(rr, R, rf) + bulge * k * 0
            q = V((ct.x, ct.y, 0)) + d * r_
            q.z = lerp(p1.z, zc, zf) + bulge * k
            col.append(q)
        side.append(col)
        top.append((d, R, zc))
    c_top = V((ct.x, ct.y - 0.004 * k, z_top + 0.028 * k))
    rings = [ring_b, ring_t] + [[side[j][i] for j in range(n)] for i in range(len(prof))]
    for s_ in (0.86, 0.58, 0.28):
        rings.append([V((c_top.x, c_top.y, 0)) + top[j][0] * (top[j][1] * s_) +
                      V((0, 0, lerp(c_top.z, top[j][2] + 0.004 * k, s_ ** 2))) for j in range(n)])
    crown = rings[4]
    # 휘장 자리: 크라운 앞면 가운데 (띠 윗단과 크라운 가장자리 사이)
    a0, a1 = rings[1][0], rings[3][0]
    pf = a0.lerp(a1, 0.52)
    tf = (a1 - a0).normalized()
    nf = tf.cross(V((1, 0, 0))).normalized()
    if nf.y > 0:
        nf = -nf
    BADGE["M"] = Matrix.Translation(pf + nf * 0.002 * k) @ elf.frame(nf, tf)
    ids = [[buf.vert(q, w) for q in r] for r in rings]
    mats = [navy_d] + [navy] * (len(rings) - 1)
    for r in range(len(ids) - 1):
        for j in range(n):
            j2 = (j + 1) % n
            buf.face((ids[r][j], ids[r][j2], ids[r + 1][j2], ids[r + 1][j]), mats[r])
    ci = buf.vert(c_top, w)
    for j in range(n):
        buf.face((ids[-1][j], ids[-1][(j + 1) % n], ci), navy)
    # 안쪽 면 (아래에서 보이지 않게 띠 안쪽을 막는다)
    inner = [buf.vert(q - (q - hc).normalized() * 0.006 * k, w) for q in ring_b]
    for j in range(n):
        j2 = (j + 1) % n
        buf.face((ids[0][j2], ids[0][j], inner[j], inner[j2]), navy_d)
    # 크라운 테두리 파이핑 (짙은 남색 끈)
    elf._loop(buf, [q + up * 0.002 * k for q in crown] + [crown[0] + up * 0.002 * k],
              [((q - ct) - up * (q - ct).dot(up)).normalized() for q in crown] + [
                  ((crown[0] - ct) - up * (crown[0] - ct).dot(up)).normalized()],
              [up] * (n + 1), 0.006 * k, 0.004 * k, mat=navy_d, w=w, closed=False)
    # 챙: 앞쪽 반원, 아래·앞으로 기운다
    vis = []
    m = 15
    for j in range(m):
        az = lerp(-78.0, 78.0, j / (m - 1))
        p0, n0 = e.head_point(az, rim_el(az) + 1.0, OFF + 0.002 * k)
        a = math.radians(az)
        out = V((math.sin(a), -math.cos(a), 0.0))
        reach = 0.064 * k * (math.cos(a) ** 0.7)
        vis.append((p0, p0 + out * reach + V((0, 0, -0.026 * k)) * (reach / (0.064 * k))))
    top_i = [buf.vert(a_, w) for a_, b_ in vis]
    out_i = [buf.vert(b_, w) for a_, b_ in vis]
    bot_i = [buf.vert(b_ + V((0, 0, -0.005 * k)), w) for a_, b_ in vis]
    bin_i = [buf.vert(a_ + V((0, 0, -0.005 * k)), w) for a_, b_ in vis]
    for j in range(m - 1):
        buf.face((top_i[j], top_i[j + 1], out_i[j + 1], out_i[j]), visor_m)
        buf.face((out_i[j], out_i[j + 1], bot_i[j + 1], bot_i[j]), visor_m)
        buf.face((bot_i[j], bot_i[j + 1], bin_i[j + 1], bin_i[j]), visor_m)
    for j in (0, m - 1):
        q = (top_i[j], out_i[j], bot_i[j], bin_i[j])
        buf.face(q if j == 0 else q[::-1], visor_m)
    # 금색 턱끈 (챙 바로 위로 띠 앞을 가로지르는 꼰 끈) + 양끝 단추
    cord = []
    for j in range(13):
        az = lerp(-82.0, 82.0, j / 12)
        p, nn = e.head_point(az, rim_el(az) + 3.5, OFF + 0.003 * k)
        cord.append({"c": p, "rx": 0.0042 * k, "ry": 0.0042 * k, "w": w})
    loft(buf, cord, segs=8, cap0="round", cap1="round", mat=gold)
    for sg in (1, -1):
        p, nn = e.head_point(sg * 84.0, rim_el(84.0) + 3.5, OFF + 0.004 * k)
        disc(buf, p, nn, (0, 0, 1), 0.0065 * k, 0.0065 * k, 0.003 * k, segs=10, mat=gold, w=w)


e.part("cap", "head", cap_geo)
e._hats = getattr(e, "_hats", []) + [(OFF, rim_el)]

# 휘장: 크라운 앞면 (띠 위, 솟은 앞면 가운데)
c2.elf_logo_badge(e, "cap_badge", BADGE["M"], 0.105 * k, gold, depth=0.006 * k, tol=0.006)

# 귀걸이: 왼쪽 귀 아래 은색 별 (네 갈래)
ear_base, ear_tip = e._ear_axis("L")


def earring(buf):
    w = {"head": 1.0}
    hook = ear_base.lerp(ear_tip, 0.64) + V((0.0, -0.002 * k, -0.012 * k))
    loft(buf, [{"c": hook, "rx": 0.0018 * k, "ry": 0.0018 * k, "w": w},
               {"c": hook + V((0, 0, -0.020 * k)), "rx": 0.0018 * k, "ry": 0.0018 * k, "w": w}], segs=6,
         cap0="round", cap1="round", mat=silver)
    Ms = Matrix.Translation(hook + V((0, 0, -0.040 * k))) @ elf.frame(V((0, -1, 0)), (0, 0, 1))
    c2.prism(buf, c2.star_poly(0.022 * k, 0.007 * k, n=4, rot=90), 0.006 * k,
             Ms @ Matrix.Translation((0, 0.003 * k, 0)), mat=silver, w=w, chamfer=0.002 * k)


e.part("earring", "head", earring)

# ---- 정복 재킷: 남색 더블 브레스트, 세운 깃, 금색 단추 2줄, 여밈선
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(navy, hem=hz - 0.010 * k, collar="stand", collar_mat=navy_d, flare=0.016)
e.sleeves(navy, length=0.95, flare=0.008, cuff=(navy_d, 0.026, 0.005))
for sd in ("L", "R"):
    e.ring(gold, f"arm_{sd}", 0.84, h=0.005, th=0.003, off=0.016, name=f"cuff_gold_{sd}")
e.gloves(glove, cuff=white)
# 여밈선 (캐릭터 왼쪽 위 → 가운데 아래로 겹친 앞판)
e.strap(navy_d, [("torso", e.torso_top - 0.012 * k, 18, 0.0125 * k), ("torso", cz, 14, 0.0128 * k),
                 ("torso", wz, 12, 0.0130 * k), ("torso", hz + 0.004 * k, 12, 0.0145 * k)],
        width=0.005, th=0.0018, name="placket")
for i, z in enumerate((cz + 0.040 * k, cz + 0.004 * k, wz + 0.010 * k)):
    for sg in (1, -1):
        a = e.anchor(("torso", z, sg * 22 + 4, 0.0135 * k))
        e.part(f"btn_{i}_{sg}", "body",
               lambda buf, a=a: disc(buf, a.pos, a.n, (0, 0, 1), 0.0072 * k, 0.0072 * k, 0.0032 * k, segs=10,
                                     mat=gold, w=a.w))
# 깃 금줄
e.part("collar_gold", "body", lambda buf: band(buf, (0, 0.004 * k, e.torso_top + 0.026 * k), (0, 0, 1), (1, 0, 0),
                                               0.0545 * k, 0.0505 * k, 0.0045 * k, 0.003 * k, segs=16, mat=gold,
                                               w={"neck": 0.5, "chest": 0.5}))
# 훈장: 왼쪽 가슴 (빨강-하양 약장 + 금색 메달)


def medal(buf, M, w):
    rbox(buf, (0.024 * k, 0.004 * k, 0.010 * k), M @ Matrix.Translation((0, -0.002 * k, 0.010 * k)), mat=red, w=w,
         r=0.2, segs=1)
    rbox(buf, (0.007 * k, 0.005 * k, 0.010 * k), M @ Matrix.Translation((0, -0.0025 * k, 0.010 * k)), mat=white,
         w=w, r=0.2, segs=1)
    c = M @ V((0, -0.005 * k, -0.008 * k))
    n = (M.to_3x3() @ V((0, -1, 0))).normalized()
    disc(buf, c, n, M.to_3x3() @ V((0, 0, 1)), 0.0105 * k, 0.0105 * k, 0.0035 * k, segs=14, mat=gold, w=w)
    disc(buf, c + n * 0.0036 * k, n, M.to_3x3() @ V((0, 0, 1)), 0.0062 * k, 0.0062 * k, 0.0012 * k, segs=10,
         mat=gold_d, w=w)


e.gear("medal", ("torso", cz + 0.030 * k, 46, 0.016 * k), medal)

# 견장: 어깨 위 금색 판 + 술


def epaulette(buf, s):
    sd = "L" if s > 0 else "R"
    S = e.S[sd]
    d = e.adir[sd]
    w = {f"shoulder_{sd}": 0.6, f"upperarm_{sd}": 0.4}
    up = V((-d.z * s * 0 + 0, 0, 1))
    c = S + V((-s * 0.004 * k, 0.0, 0.066 * k)) + d * 0.004 * k
    out = (V((s, 0, 0)) * 0.42 + V((0, 0, 1))).normalized()
    Mx = Matrix.Translation(c) @ elf.frame(out, V((0, -1, 0)))
    rbox(buf, (0.088 * k, 0.012 * k, 0.062 * k), Mx, mat=gold, w=w, r=0.45, segs=1)
    rbox(buf, (0.068 * k, 0.010 * k, 0.044 * k), Mx @ Matrix.Translation((0, -0.004 * k, 0)), mat=navy, w=w,
         r=0.45, segs=1)
    # 술: 판 바깥 끝에서 팔 쪽으로 늘어진 짧은 금실
    edge = c + (V((s, 0, 0)) - out * out.x * s).normalized() * 0.034 * k
    for i in range(6):
        y = lerp(-0.024, 0.024, i / 5) * k
        p0 = edge + V((0, y, 0))
        p1 = p0 + V((s * 0.012 * k, 0, -0.030 * k))
        loft(buf, [{"c": p0, "rx": 0.0042 * k, "ry": 0.0042 * k, "w": w},
                   {"c": p1, "rx": 0.0036 * k, "ry": 0.0036 * k, "w": {f"upperarm_{sd}": 1.0}}], segs=5,
             cap0="flat", cap1="round", mat=gold)
    _ = up


for s in (1, -1):
    e.part(f"epaulette_{'L' if s > 0 else 'R'}", "body", lambda buf, s=s: epaulette(buf, s))

# ---- 허리: 빨강-하양 줄무늬 띠
e.ring(red, "torso", wz - 0.005 * k, h=0.030, th=0.006, off=0.016, name="sash")
for dz in (0.009, -0.009):
    e.ring(white, "torso", wz - 0.005 * k + dz * k, h=0.0045, th=0.003, off=0.0215, name=f"sash_w{dz}")

# ---- 남색 주름치마 + 검은 니삭스 + 부츠
q0 = e.q
e.q = 0.45    # 치마 속 반바지는 거의 안 보이니 성글게
e.pants(navy_d, length=0.06, bag=0.0, blouse=0.0, off=0.006)
e.q = q0
skirt = c2.Shell(e, navy, hz + 0.020 * k, 0.250 * k, off=0.016, th=0.004, skirt=True, cols=36, rows=6,
                 flare=[(0.0, 0.0), (0.5, 0.016), (1.0, 0.036)], pleat=(0.012, 9, 0.0), pleat_mat=navy_d)
skirt.hem_trim(navy_d, width=0.008, th=0.002)
skirt.done("skirt", angle=30.0)
for sd in ("L", "R"):
    c2.leg_tube(e, black, sd, 0.36, 0.99, off=0.004, name=f"sock_{sd}")
    e.ring(black, f"leg_{sd}", 0.37, h=0.012, th=0.003, off=0.006, name=f"sock_top_{sd}")
e.boots(black, top=0.70, sole=(sole, 0.016), cuff=navy_d, toe=0.004, off=0.010)

# ---- 검은 망토: 어깨에서 종아리까지, 앞은 열림. 안감은 조금 밝은 보라 검정
cape = c2.Shell(e, cape_m, e.torso_top - 0.004 * k, 0.17 * k, gap=[(0.0, 62.0), (0.3, 70.0), (1.0, 88.0)], off=0.030,
                th=0.006, rows=11, cols=16, flare=[(0.0, 0.010), (0.25, 0.026), (1.0, 0.080)], shoulder=1.05,
                drop=[(0.0, 0.0), (1.0, 0.03)])
cape.hem_trim(cape_in, width=0.010, th=0.002, lift=-0.0055)
cape.done("cape")
# 망토 고정: 양 어깨 앞 금색 고리 단추
for sg in (1, -1):
    a = e.anchor(("torso", e.torso_top - 0.020 * k, sg * 58, 0.032 * k))
    e.part(f"cape_clasp_{sg}", "body",
           lambda buf, a=a: disc(buf, a.pos, a.n, (0, 0, 1), 0.010 * k, 0.010 * k, 0.004 * k, segs=12, mat=gold,
                                 w=a.w))

e.finalize()
e.export("characters/haley.glb")
