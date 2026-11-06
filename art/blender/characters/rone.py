"""로네(갑옷): 모나티엄 첩보원. 지금은 인터루드 모나티엄 건설 회상(interlude_construction)에만 쓴다.
본편(1막~에필로그)의 로네는 이미 로네(시장)이라 rone_mayor.py(rone_mayor.glb)를 쓴다. 레벨 glb에 남은
characters/rone.glb 경로는 런타임에서 바꿔 끼운다(src/game/npc/NpcSet.ts MODEL_SWAP, docs/art/characters-cameo2.md 3.1절).

원작 로네(트릭컬 리바이브, '최고의 스파이??')의 복장을 바탕으로 한 카메오 모델.
- 유지한 식별 요소: 긴 갈색 생머리, 크림빛 금색 머리띠, 옆으로 쓸린 앞머리, 오른쪽 가슴까지 오는 옆머리,
  왼쪽 가슴 높이에서 묶어 종아리까지 늘어뜨린 낮은 사이드테일, 회갈색 졸린 눈, 은색 판금 흉갑·어깨받이·건틀릿과
  금색 테두리, 흰 감비슨 치마와 금색 테두리 앞뒤 자락, 허벅지까지 오는 은색 정강이 갑옷과 금색 띠,
  왼쪽 허리 뒤로 비스듬히 찬 갈색 칼집의 검. 헬름은 쓰지 않는다(원작 설정).
- 재해석: 판금은 SD 덩어리로 단순화하고 리벳과 금색 테 줄을 3차 디테일로 넣었다. 허리띠에 첩보반 표식
  (짙은 남색 원판 + 은색 열쇠 구멍)을 달았다.
- 분대원 '로나'와의 구분: 로나는 민트색 트윈테일·정글모·금빛 눈이다. 로네는 갈색 생머리·머리띠·한쪽 꼬리·
  은색 갑옷·회갈색 눈으로 색과 실루엣이 모두 다르다 (docs/art/characters-rita-squad.md 4.2).
- 표정: 키트 5종 + fluster(허둥지둥), cry(오열), dreamy(돈까스 상상), smug(마스터 스파이) + blink 교정 키.
근거: docs/art/characters-cameo2.md

npm run model -- art/blender/characters/rone.py
npm run shot -- characters/rone.glb
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
e = elf.Elf("rone", height=1.20, head=0.45, leg=1.02, chest=0.15, segs=0.76, hand_q=0.6, cheek=0.10)
k = e.k

# ---- 팔레트 (원작 실측: 머리 #8a6455, 머리띠 #f0d9a0, 갑옷 #d4d6de, 금색 #d9a54a, 감비슨 #f3eee8, 칼집 #6e4a3c)
plate = M_("rn_plate", "#b9bccb")
plate_d = M_("rn_plate_d", "#8d90a1")
gold = M_("rn_gold", "#dca54c")
white = M_("rn_white", "#f4efe9")
white_d = M_("rn_white_d", "#ddd5cc")
leather = M_("rn_leather", "#6f4b3d")
leather_d = M_("rn_leather_d", "#4f3429")
band_m = M_("rn_band", "#f1dba3")
navy = M_("rn_navy", "#2f3650")
steel = M_("rn_steel", "#bfc2cc")

# ---- 얼굴: 회갈색 졸린 눈 (윗눈꺼풀이 무겁게 내려옴), 살짝 벌린 입, 걱정 많은 눈썹
e.face(eye_color="#8c7d77", iris_dark="#4a3c38", iris_light="#e0d6cf", pupil="#2a2020",
       lash="#4a2e2a", brow="#6e4c40", blush="#f7a7a4", blush_size=1.1,
       base={"eye": {"top": 0.016, "ktop": 3.8, "tilt_out": -0.004, "cout": 0.012},
             "iris": {"cz": 0.0020},
             "brow": {"dz": 0.062, "ang": 7.0, "arch": 0.002},
             "mouth": {"w": 0.018, "curve": 0.0020, "open": 0.0035, "top_arch": 0.0010}},
       expr={
           # 허둥지둥: 동그래진 눈, 작은 동공, 올라간 눈썹, 물결 입
           "fluster": {"eye": {"top": 0.034, "ktop": 2.4, "bot": 0.056},
                       "iris": {"pupil": 0.55, "rx": 0.026, "ry": 0.034},
                       "brow": {"ang": 18.0, "dz": 0.074, "arch": 0.004},
                       "mouth": {"w": 0.024, "curve": -0.0020, "open": 0.0080, "wave": 0.0018}},
           # 오열 (돈까스가 날아갔을 때): 처진 눈썹, 가늘게 젖은 눈, 크게 벌린 입
           "cry": {"eye": {"top": 0.008, "tilt_in": 0.012, "tilt_out": -0.012, "lift": 0.016},
                   "brow": {"ang": 26.0, "dz": 0.062},
                   "mouth": {"w": 0.032, "curve": -0.0070, "open": 0.020, "wave": 0.0020}},
           # 돈까스 상상: 반달 눈웃음, 벌린 입
           "dreamy": {"eye": {"top": 0.014, "lift": 0.026, "kbot": 2.6},
                      "brow": {"ang": 10.0, "dz": 0.068, "arch": 0.006},
                      "mouth": {"w": 0.030, "curve": 0.0070, "open": 0.012, "top_arch": -0.001}},
       })
c2.face_expr(e, "smug",
             both={"eye": {"top": 0.013, "lift": 0.010}, "mouth": {"w": 0.026, "curve": 0.0035, "open": 0.0}},
             L={"brow": {"dz": 0.066, "ang": -2.0}}, R={"brow": {"dz": 0.060, "ang": -8.0}},
             corner=(0.0070, -0.0005), mouth_dx=0.0020 * k)


# ---- 머리: 갈색 생머리, 옆으로 쓸린 앞머리, 오른쪽 긴 옆머리, 머리띠, 왼쪽 낮은 사이드테일
HAIR = "#8b6456"


def rone_locks(h, lk):
    if lk["region"] == "side" and lk.get("side") == "R":
        lk["L"] += 0.14 * k          # 오른쪽 옆머리는 가슴까지
        lk["free"] += 0.06 * k
    if lk["region"] == "front":
        lk["p"] = 1.7


h = c2.hair(e, HAIR, dark="#664539", light="#b48d7c", lock_fn=c2.lock_edit(rone_locks))
h.cap(front=30, side=-8, back=-48, part=16)
h.bangs(n=6, spread=60, tip_el=0, jag=0.25, sweep=-12, seed=3.0)
h.sides(length=0.10, width=0.080)
h.back(length=0.10, n=7, spread=96)
h.shine(el=50, spread=70, size=1.1)
c2.on_hair_band(e, h, band_m, az0=-104, az1=104, el_fn=lambda az: 56.0 - 46.0 * (abs(az) / 104.0) ** 1.8,
                width=0.022, th=0.005, lift=-0.003)

# 낮은 사이드테일 (왼쪽): 귀 뒤 아래에서 모아 가슴 높이에서 묶고 종아리까지
o = h.vol
root, rn = h.path(124.0, h.s_of_el(124.0, -16.0), -o * 0.3)
sz, wz, hz, cz = e.shoulder_z, e.waist_z, e.hipj_z, e.chest_z
ctrl = [root,
        V((0.168 * k, 0.034 * k, e.chin - 0.010 * k)),
        V((0.178 * k, -0.018 * k, sz + 0.010 * k)),
        V((0.196 * k, -0.040 * k, cz - 0.020 * k)),
        V((0.208 * k, -0.026 * k, wz - 0.030 * k)),
        V((0.220 * k, -0.004 * k, hz - 0.040 * k)),
        V((0.232 * k, 0.020 * k, e.knee_z + 0.010 * k)),
        V((0.248 * k, 0.050 * k, 0.150 * k))]
tl = c2.Tail(h, "hair_tail_L", ctrl, 0.108 * k, 0.060 * k, bones=3, parent="chest", root_bone="head", t_hold=0.62,
             root_w=1.0,
             clumps=((0.32, 0.55, 0.92), (-0.30, 0.55, 0.88)),
             ref_fn=lambda t, q: V((1.0, 0.25, 0.0)))
tl.tie(leather_d, t=0.30, size=1.0, h_=0.026, th=0.008)

# ---- 감비슨(흰 누빔 옷): 상체 + 치마, 흰 소매
e.shirt(white, hem=hz - 0.004 * k, collar="stand", collar_mat=white_d, flare=0.010)
e.sleeves(white, length=0.60, off=0.012, flare=0.010, puff=0.010)
q0 = e.q
e.q = 0.5     # 치마 속 바지는 정강이 갑옷 위 허벅지만 보인다
e.pants(white_d, length=0.42, bag=0.004, blouse=0.0, off=0.006)
e.q = q0
sk = c2.Shell(e, white, wz - 0.020 * k, hz - 0.135 * k, off=0.018, th=0.004, skirt=True, cols=24, rows=7,
              flare=[(0.0, 0.0), (0.5, 0.016), (1.0, 0.036)], ruffle=(0.004, 8, 0.4))
sk.done("gambeson")

# 앞뒤 자락 (금색 테두리의 흰 판, 아래가 뾰족): 원작의 V자 금색 테
def tabard(buf, front=True):
    a0 = 0 if front else 180
    rows = []
    for i in range(6):
        u = i / 5
        z = lerp(wz - 0.012 * k, hz - 0.150 * k, u)
        half = lerp(0.085, 0.020, u ** 1.4) * k
        row = []
        for j in range(5):
            x = lerp(-half, half, j / 4)
            a = a0 + math.degrees(x / (0.15 * k)) * (1 if front else -1)
            rx, ry, cy = c2.section(e, z, True)
            q, n = c2.ring_pt(rx + 0.024 * k + 0.030 * k * u, ry + 0.024 * k + 0.030 * k * u, cy, z, a)
            row.append((q, n))
        rows.append(row)
    ids = [[buf.vert(q, c2.skirt_w(e, q)) for q, n in r] for r in rows]
    for i in range(len(rows) - 1):
        for j in range(4):
            buf.face((ids[i][j], ids[i + 1][j], ids[i + 1][j + 1], ids[i][j + 1]) if front else
                     (ids[i][j + 1], ids[i + 1][j + 1], ids[i + 1][j], ids[i][j]), white)
    # 금색 테: 좌우 가장자리 + 아래 끝
    for jj in (0, 4):
        pts = [rows[i][jj][0] + rows[i][jj][1] * 0.002 * k for i in range(len(rows))]
        loft(buf, [{"c": p, "rx": 0.0042 * k, "ry": 0.0030 * k, "w": c2.skirt_w(e, p), "ref": tuple(rows[i][jj][1])}
                   for i, p in enumerate(pts)], segs=6, cap0="round", cap1="round", mat=gold)


e.part("tabard_f", "body", lambda buf: tabard(buf, True))
e.part("tabard_b", "body", lambda buf: tabard(buf, False))

# ---- 판금: 흉갑(금색 테 + 가운데 능선), 어깨받이, 건틀릿, 정강이 갑옷
bp = c2.Shell(e, plate, e.torso_top - 0.012 * k, wz - 0.010 * k, off=0.022, th=0.006, rows=8, cols=24,
              flare=[(0.0, 0.004), (0.5, 0.006), (1.0, 0.0)], cover=True)
bp.top_trim(gold, width=0.010, th=0.003)
bp.hem_trim(gold, width=0.010, th=0.003)
bp.done("breastplate", angle=60.0)
e.strap(plate_d, [("torso", e.torso_top - 0.016 * k, 0, 0.026 * k), ("torso", cz, 0, 0.030 * k),
                  ("torso", wz + 0.004 * k, 0, 0.027 * k)], width=0.008, th=0.003, name="ridge")
e.belt(leather, z=wz - 0.016 * k, h=0.026, off=0.030, buckle=gold, buckle_size=(0.034, 0.028))
# 첩보반 표식 (허리띠 왼쪽 원판)
e.gear("spy_badge", ("torso", wz - 0.016 * k, 36, 0.036 * k),
       lambda buf, Mx, w: (disc(buf, Mx @ V((0, -0.002 * k, 0)), (Mx.to_3x3() @ V((0, -1, 0))).normalized(), (0, 0, 1),
                                0.016 * k, 0.016 * k, 0.004 * k, segs=14, mat=navy, w=w),
                           c2.prism(buf, [(0, 0.008 * k), (-0.004 * k, 0.002 * k), (-0.0025 * k, -0.008 * k),
                                          (0.0025 * k, -0.008 * k), (0.004 * k, 0.002 * k)], 0.002 * k,
                                    Mx @ Matrix.Translation((0, -0.006 * k, 0)), mat=steel, w=w)))


def pauldron(buf, s):
    sd = "L" if s > 0 else "R"
    S = e.S[sd]
    d = e.adir[sd]
    w = {f"shoulder_{sd}": 0.5, f"upperarm_{sd}": 0.5}
    for i, (sc, m) in enumerate(((1.0, plate), (0.78, plate))):
        c = S + d * (0.010 + 0.022 * i) * k + V((0, 0, (0.050 - 0.018 * i) * k))
        out = (V((s, 0, 0)) * 0.6 + V((0, 0, 1))).normalized()
        M = Matrix.Translation(c) @ elf.frame(out, V((0, -1, 0)))
        c2.ellipsoid(buf, c, (M.to_3x3() @ V((1, 0, 0))).normalized(), (M.to_3x3() @ V((0, 0, 1))).normalized(),
                     (M.to_3x3() @ V((0, -1, 0))).normalized(), 0.050 * k * sc, 0.050 * k * sc, 0.022 * k * sc,
                     segs=12, rings=6, mat=m, w=w)
    # 금색 테두리 (어깨받이 아랫단)
    c = S + d * 0.034 * k + V((0, 0, 0.026 * k))
    band(buf, c, d, V((0, -1, 0)), 0.046 * k, 0.044 * k, 0.007 * k, 0.003 * k, segs=14, mat=gold, w=w)


for s in (1, -1):
    e.part(f"pauldron_{'L' if s > 0 else 'R'}", "arms", lambda buf, s=s: pauldron(buf, s))

for sd in ("L", "R"):
    c2.arm_tube(e, plate, sd, 0.56, 0.99, off=0.012, extra=lambda t: 0.006 * smoothstep(0.56, 0.75, t),
                name=f"gauntlet_{sd}")
    e.ring(gold, f"arm_{sd}", 0.58, h=0.008, th=0.003, off=0.020, name=f"gauntlet_gold_{sd}")
e.gloves(plate, cuff=plate_d, inflate=0.0035)

for sd in ("L", "R"):
    c2.leg_tube(e, plate, sd, 0.40, 0.99, off=0.012, extra=lambda t: 0.008 * math.exp(-((t - 0.55) / 0.08) ** 2),
                name=f"greave_{sd}")
    e.ring(gold, f"leg_{sd}", 0.41, h=0.014, th=0.004, off=0.016, name=f"greave_top_{sd}")
    e.ring(gold, f"leg_{sd}", 0.47, h=0.006, th=0.003, off=0.016, name=f"greave_band_{sd}")
    e.pad(plate_d, (f"leg_{sd}", 0.55, 0, 0.020 * k), size=(0.054, 0.016, 0.050), name=f"knee_{sd}")
e.boots(plate, top=0.82, sole=(leather_d, 0.014), cuff=plate_d, toe=0.004, off=0.014)

# ---- 검: 왼쪽 허리에 비스듬히 찬 갈색 칼집 + 금색 장식, 자루와 코등이는 앞쪽 위
def sword(buf):
    hip = V((0.150 * k, 0.050 * k, wz - 0.030 * k))
    axis = V((0.25, 0.55, -1.0)).normalized()        # 칼끝이 뒤·아래로
    w = {"hips": 1.0}
    L = 0.46 * k
    st = []
    for i in range(7):
        t = i / 6
        c = hip + axis * (L * t)
        r = lerp(0.020, 0.014, t) * k
        st.append({"c": c, "rx": r, "ry": r * 0.55, "w": w, "ref": (0.4, -0.2, 0.2)})
    loft(buf, st, segs=10, cap0="flat", cap1="round", mat=leather)
    for t in (0.05, 0.55):
        c = hip + axis * (L * t)
        band(buf, c, axis, V((0.4, -0.2, 0.2)).normalized(), 0.022 * k, 0.013 * k, 0.012 * k, 0.003 * k, segs=10,
             mat=gold, w=w)
    tip = hip + axis * L
    band(buf, tip - axis * 0.012 * k, axis, V((0.4, -0.2, 0.2)).normalized(), 0.016 * k, 0.010 * k, 0.018 * k,
         0.003 * k, segs=10, mat=gold, w=w)
    # 코등이 + 자루 + 폼멜
    g = hip - axis * 0.006 * k
    side = axis.cross(V((0, -1, 0))).normalized()
    rbox(buf, (0.070 * k, 0.014 * k, 0.012 * k), Matrix.Translation(g) @ elf.frame(axis.cross(side), side), mat=gold,
         w=w, r=0.4, segs=1)
    grip = [{"c": g - axis * 0.004 * k, "rx": 0.009 * k, "ry": 0.009 * k, "w": w},
            {"c": g - axis * 0.060 * k, "rx": 0.009 * k, "ry": 0.009 * k, "w": w}]
    loft(buf, grip, segs=8, cap0="flat", cap1="flat", mat=leather_d)
    pm = g - axis * 0.070 * k
    c2.ellipsoid(buf, pm, axis, side, axis.cross(side).normalized(), 0.012 * k, 0.012 * k, 0.012 * k, segs=8,
                 rings=5, mat=gold, w=w)


e.part("sword", "body", sword)

e.finalize()
e.export("characters/rone.glb")
