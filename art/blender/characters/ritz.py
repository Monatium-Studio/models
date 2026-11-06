"""리츠: 용족 사도 '만 번 담근 강철'. 엘리아스 침공전에서 모나티엄 방어 전력(교주 차원)으로 배치됐다가, 키디언·칸나와
함께 흑뉴아에게 힘으로 제압된다(1막 M2 「방어선」 시청 방어선).

원작 리츠(트릭컬 리바이브, 광기 성격 용족)의 기본 복장으로 만든 카메오 모델.
- 유지한 식별 요소: 검은 단발 + 오른눈(-X)을 덮는 긴 앞머리 + 바보털, 아래쪽이 붉게 물든 안쪽 머리, 왼쪽(+X) 귀 뒤의
  땋은 머리(붉은 끈), 뾰족 귀, 금속 가리개를 씌운 짧은 검은 뿔과 왼뿔의 붉은 리본, 반쯤 감긴 분홍빛 붉은 눈(아래 노란
  반달)과 물결 입, 직접 만든 회색 판금 갑옷(목가리개, 둥근 어깨받이, 흉갑, 손목 건틀릿), 검은 가죽끈과 징 박힌 벨트,
  검은 프릴 치마와 엉덩이 옆의 큰 방패꼴 판(네 갈래 별 문양), 무릎 판과 정강이·발 갑옷, 붉은 막의 검은 용 날개, 아랫면이
  붉은 검은 꼬리, 밧줄 감은 손잡이와 깔때기 폼멜의 거대한 무쇠 검(별도 노드).
- 재해석: 날개·꼬리에 본 사슬(wing_*, tail_*)을 넣었다. 붉은 안쪽 머리는 머리 덩어리 아래 띠(정점 색 구역)로,
  땋은 머리의 붉은 가닥은 아래쪽 물들임으로 단순화했다. 검은 원작 비율(키만 한 크기)보다 조금 줄였다(전장 약 1 m).
- 검 `ritz_sword`: 무기 규약(원점 = 오른손 파지점, 칼날 +Y, 칼등 +Z). 기본은 socket_hand_R 자식으로 오른손에 쥐고
  칼끝을 뒤 오른쪽 땅에 끌리게 둔다(원작 카드처럼 끌고 다니는 자세). 휘두를 때는 로컬 변환을 0으로 둔다.
- 표정: 키트 5종 + smug(능글맞게 벌린 입) + glare(노려봄) + grit(이 악문 전투) + dazed(제압된 뒤) + blink 교정 키.
근거: docs/art/characters-cameo3.md

npm run model -- art/blender/characters/ritz.py
npm run shot -- characters/ritz.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import cb  # noqa: E402
import elf  # noqa: E402
import cameo2 as c2  # noqa: E402
import dragon_common as dc  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, smoothstep  # noqa: E402

cb.reset()
M_ = elf.mat
e = elf.Elf("ritz", height=1.20, head=0.45, leg=1.0, chest=0.22, segs=0.64, hand_q=0.5, cheek=0.10,
            ear_len=0.072, ear_width=0.048, ear_angle=10.0, ear_sweep=16.0, skin="#fff1e6")
k = e.k

# ---- 팔레트 (원작 카드 실측: 머리 #333236, 붉은 머리 #c23a5c, 눈 #e8708f, 갑옷 #8e8a8f, 막 #b5395a)
plate = M_("rz_plate", "#9a979e")
plate_l = M_("rz_plate_l", "#bdbac0")
plate_d = M_("rz_plate_d", "#66636b")
black = M_("rz_black", "#2e2c32")
leather = M_("rz_leather", "#3b3438")
silver = M_("rz_silver", "#d4d3d9")
red = M_("rz_red", "#c43a5c")
red_d = M_("rz_red_d", "#8f2944")
horn_m = M_("rz_horn", "#242328")
mem = M_("rz_membrane", "#b7385a")
wbone = M_("rz_wingbone", "#2c2b31")
tail_m = M_("rz_tail", "#2e2d33")

# ---- 얼굴: 분홍빛 붉은 눈(아래 노란 반달), 무겁게 내려온 윗눈꺼풀, 물결 입 (뚱한 얼굴)
e.face(eye_color="#e46c8c", iris_dark="#9e2a4c", iris_light="#ffd98a", pupil="#4a0f22",
       lash="#26222a", brow="#2e2a32", brow_th=1.05, blush="#f6a6a8", blush_size=1.05,
       base={"eye": {"top": 0.011, "cin": 0.004, "cout": 0.010, "ktop": 4.6, "tilt_in": -0.003},
             "iris": {"cz": 0.0010},
             "brow": {"dz": 0.058, "ang": -4.0, "arch": 0.001},
             "mouth": {"w": 0.016, "curve": -0.0006, "wave": 0.0016}},
       expr={
           # 능글맞게 벌린 입 (원작 컷: 반쯤 감은 눈 + 벌린 입)
           "smug": {"eye": {"top": 0.008, "cin": 0.004, "cout": 0.012, "lift": 0.012, "ktop": 4.0},
                    "brow": {"dz": 0.062, "ang": -2.0},
                    "mouth": {"w": 0.026, "curve": 0.0070, "open": 0.0140, "top_arch": -0.0010}},
           # 노려봄: 눈썹을 세게 내리고 입을 다문다
           "glare": {"eye": {"top": 0.014, "ktop": 4.0, "tilt_in": -0.012, "cin": 0.002},
                     "iris": {"pupil": 0.80},
                     "brow": {"ang": -18.0, "dz": 0.052, "th": 0.0072},
                     "mouth": {"w": 0.018, "curve": -0.0020}},
           # 이 악문 전투: 노려보며 입을 옆으로 벌림
           "grit": {"eye": {"top": 0.018, "ktop": 3.4, "tilt_in": -0.012},
                    "iris": {"pupil": 0.70},
                    "brow": {"ang": -20.0, "dz": 0.054, "th": 0.0074},
                    "mouth": {"w": 0.030, "curve": -0.0030, "open": 0.0080, "wave": 0.0012}},
           # 제압된 뒤 (M2 시청 방어선): 초점 없는 반쯤 뜬 눈, 작은 동공, 벌린 입
           "dazed": {"eye": {"top": 0.012, "cin": 0.004, "cout": 0.004, "tilt_in": 0.006, "tilt_out": -0.004,
                             "ktop": 3.4},
                     "iris": {"pupil": 0.42, "cz": -0.0030},
                     "brow": {"ang": 16.0, "dz": 0.060},
                     "mouth": {"w": 0.020, "open": 0.0080, "curve": -0.0025, "wave": 0.0014}},
       })

# ---- 머리 (헤어 v2): 검은 단발, 오른눈을 덮는 앞머리, 바보털, 왼쪽 땋은 머리, 아래쪽 붉은 안쪽 머리
HAIR = "#333238"


def rz_locks(h, lk):
    if lk["region"] in ("side", "back"):
        lk["p"] = 1.8
        lk["curl"] = 0.004 * k
    if lk["region"] == "front":
        lk["p"] = 1.9


h = c2.hair(e, HAIR, dark="#1c1b20", light="#5c5a64", lock_fn=c2.lock_edit(rz_locks), volume=1.10)
h.cap(front=28, side=-8, back=-48, part=-16)
h.bangs(n=7, spread=58, tip_el=-6, jag=0.30, sweep=-8, part=-16, curl=0.9, seed=4.0)
h.sides(length=0.05, width=0.082, n=1)
h.back(length=0.045, n=9, spread=96)
h.ahoge(az=-12, height=0.072, curl=1.1, width=0.017)
h.shine(el=52, spread=70, size=1.0)
o = h.off
# 오른눈(-X)을 덮는 큰 다발: 가르마 쪽 머리선에서 눈을 지나 볼까지
h.strand([h.sp(-12, 24, o * 1.05), h.sp(-18, 8, o * 1.32), h.sp(-22, -8, o * 1.42) + V((0, -0.006, 0)) * k,
          h.sp(-24, -26, o * 1.12) + V((0, -0.010, 0)) * k],
         0.112 * k, 0.015 * k, n=12, segs=10, taper=[(0, 0.80), (0.2, 1.0), (0.65, 0.90), (1, 0.0)])
# 왼쪽(+X) 귀 뒤 땋은 머리 (가슴까지, 붉은 끈)
h.braid(side=1, az=100.0, el=-14.0, length=0.24, width=0.046, beads=8, tie=red, tuft=0.030)
# 아래쪽이 붉게 물든 안쪽 머리: 턱선 아래 머리끝 띠 (땋은 머리 아래쪽도 함께)
c2.stripe(h, red, -1.0, e.chin + 0.024 * k, mat_in=red_d, tilt=(0.0, -0.25))   # 오른쪽(-X)이 더 높이 물든다

# ---- 뿔: 짧고 뭉툭한 검은 뿔(바깥 위로 휨) + 각진 금속 가리개 + 리벳, 왼뿔에 붉은 리본
for side, s in (("L", 1), ("R", -1)):
    az = s * 52.0
    P, r_at, base, nrm = dc.horn(e, h, f"horn_{side}", az=az, el=42.0, r0=0.040, mat=horn_m, flat=0.86,
                                 taper=0.55, tip=0.011, segs=9,
                                 ctrl=[(s * 0.032, 0.008, 0.030), (s * 0.058, 0.014, 0.062),
                                       (s * 0.066, 0.024, 0.090)])

    def guard(buf, P=P, r_at=r_at, s=s, nrm=nrm):
        w = {"head": 1.0}
        dc.horn_sleeve(buf, P, r_at, 0.06, 0.56, plate, grow=0.0010, n=5, segs=4, rot=45.0, w=w, k=k)
        c, T = dc.path_at(P, 0.40)
        fwd = V((0, -1, 0))
        n2 = (fwd - T * fwd.dot(T)).normalized()
        dc.stud(buf, c + n2 * (r_at(0.40) + 0.006 * k), n2, 0.0052 * k, silver, w=w, depth=0.6, segs=6, rings=4)
    e.part(f"horn_guard_{side}", "head", guard)
    if side == "L":
        def ribbon(buf, P=P, r_at=r_at):
            w = {"head": 1.0}
            c, T = dc.path_at(P, 0.52)
            out = V((1.0, 0.25, 0.0)).normalized()
            Mx = Matrix.Translation(c + out * (r_at(0.52) + 0.002 * k)) @ elf.frame(out, T)
            for sg in (1, -1):     # 묶은 리본 꼬리 두 장 (뒤로 비스듬히 늘어짐)
                c2.prism(buf, [(0.0, 0.004 * k), (sg * 0.030 * k, -0.010 * k), (sg * 0.026 * k, -0.026 * k),
                               (sg * 0.016 * k, -0.018 * k), (0.0, -0.006 * k)][::sg], 0.003 * k,
                         Mx @ Matrix.Rotation(math.radians(sg * 18.0), 4, "Y"), mat=red, w=w)
            c2.ellipsoid(buf, Mx @ V((0, -0.004 * k, 0)), V(Mx.to_3x3() @ V((1, 0, 0))).normalized(),
                         V(Mx.to_3x3() @ V((0, 0, 1))).normalized(), V(Mx.to_3x3() @ V((0, -1, 0))).normalized(),
                         0.008 * k, 0.007 * k, 0.005 * k, segs=6, rings=4, mat=red_d, w=w)
        e.part("horn_ribbon", "head", ribbon)

# ---- 속옷: 검은 몸판(세운 깃) + 검은 소매 + 검은 반바지
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
e.shirt(black, hem=hz - 0.004 * k, collar="stand", collar_mat=black, flare=0.006)
e.sleeves(black, length=0.62, off=0.008, flare=0.004)
q0 = e.q
e.q = 0.35
e.pants(black, length=0.10, bag=0.0, blouse=0.0, off=0.006)
e.q = q0

# ---- 흉갑 (몸 앞뒤를 감싸는 판) + 가운데 능선 + 목가리개
st = e.torso_stations(wz + 0.004 * k, e.torso_top - 0.016 * k, off=0.022 * k, n=6,
                      flare=[(0.0, 0.004 * k), (0.5, 0.006 * k), (1.0, 0.0)])
st[0]["lip"] = 0.005 * k
st[-1]["lip"] = 0.005 * k
e.part("cuirass", "body", lambda buf: loft(buf, st, segs=int(22 * e.q), cap0="lip", cap1="lip", mat=plate,
                                           wfn=e._torso_wfn))
e.strap(plate_l, [("torso", wz + 0.024 * k, 0, 0.0370 * k), ("torso", cz, 0, 0.0370 * k),
                  ("torso", e.torso_top - 0.026 * k, 0, 0.0330 * k)], width=0.010, th=0.003, name="ridge")
e.part("gorget", "body", lambda buf: band(buf, (0, 0.004 * k, e.torso_top + 0.004 * k), (0, 0, 1), (1, 0, 0),
                                          0.070 * k, 0.064 * k, 0.026 * k, 0.007 * k, segs=16, mat=plate,
                                          w={"neck": 0.3, "chest": 0.7}, taper=0.10))
# 검은 가죽끈: 오른 어깨에서 왼쪽 옆구리로 + 은색 버클
e.strap(leather, [("torso", e.torso_top - 0.010 * k, -38, 0.0300 * k), ("torso", cz + 0.020 * k, -6, 0.0300 * k),
                  ("torso", cz - 0.040 * k, 40, 0.0300 * k), ("torso", wz + 0.010 * k, 80, 0.0300 * k)],
        width=0.020, th=0.004, name="baldric")
e.gear("baldric_buckle", ("torso", cz - 0.010 * k, 20, 0.034 * k),
       lambda b, Mx, w: (rbox(b, (0.024 * k, 0.005 * k, 0.026 * k), Mx, mat=silver, w=w, r=0.25, segs=1),
                         rbox(b, (0.012 * k, 0.006 * k, 0.014 * k), Mx, mat=leather, w=w, r=0.2, segs=1)))

# ---- 어깨받이: 둥근 돔 두 겹 + 리벳
for side, s in (("L", 1), ("R", -1)):
    S = e.S[side]
    d = e.adir[side]

    def pauldron(buf, S=S, d=d, s=s, side=side):
        w1 = {f"shoulder_{side}": 0.5, f"upperarm_{side}": 0.5}
        w2 = {f"upperarm_{side}": 1.0}
        up = V((0, 0, 1))
        A = d.normalized()
        F = V((0, -1, 0))
        Uu = A.cross(F).normalized()
        if Uu.z < 0:
            Uu = -Uu
        c1 = S + up * 0.020 * k + A * 0.004 * k
        c2.ellipsoid(buf, c1, A, F, Uu, 0.060 * k, 0.054 * k, 0.040 * k, segs=12, rings=6, mat=plate, w=w1)
        c3 = S + A * 0.044 * k + Uu * 0.012 * k
        c2.ellipsoid(buf, c3, A, F, Uu, 0.042 * k, 0.046 * k, 0.034 * k, segs=10, rings=5, mat=plate_d, w=w2)
        dc.stud(buf, c1 + Uu * 0.040 * k, Uu, 0.0060 * k, silver, w=w1, depth=0.6, segs=6, rings=4)
    e.part(f"pauldron_{side}", "arms", pauldron)

# ---- 건틀릿: 팔뚝 판 + 띠 + 회색 장갑
for side in ("L", "R"):
    c2.arm_tube(e, plate, side, 0.56, 0.95, off=0.014, name=f"vambrace_{side}",
                extra=lambda t: 0.006 * smoothstep(0.75, 1.0, t))
    e.ring(plate_d, f"arm_{side}", 0.70, h=0.008, th=0.003, off=0.018, name=f"vam_band_{side}")
e.gloves(plate_d, cuff=plate, inflate=0.0030)

# ---- 허리: 징 박힌 검은 벨트 + 검은 프릴 치마 + 엉덩이 옆 방패꼴 판
e.belt(leather, z=wz - 0.012 * k, h=0.026, th=0.006, off=0.030, buckle=silver, buckle_size=(0.032, 0.026))
for i, ang in enumerate((-56, -34, 34, 56, 160, 200)):
    a = e.anchor(("torso", wz - 0.012 * k, ang, 0.037 * k))
    e.part(f"belt_stud_{i}", "body", lambda buf, a=a: dc.stud(buf, a.pos, a.n, 0.0050 * k, silver, w=a.w, depth=0.6,
                                                              segs=6, rings=4))
sk = c2.Shell(e, black, wz - 0.016 * k, e.crotch_z - 0.030 * k, off=0.018, th=0.004, skirt=True, cols=22, rows=4,
              flare=[(0.0, 0.0), (0.5, 0.012), (1.0, 0.030)], ruffle=(0.004, 9, 0.5))
sk.hem_trim(plate_d, width=0.006, th=0.002)
sk.done("skirt")


def tasset(buf, s):
    """방패꼴 판: 위가 둥근 사각, 아래가 뾰족. 짙은 테 + 네 갈래 별."""
    ang = s * 74.0
    z_top = wz - 0.010 * k
    p0, n0 = e.torso_point(z_top, ang, 0.050 * k)
    out = V((n0.x, n0.y, 0.0)).normalized()
    up = V((0, 0, 1))
    tilt = math.radians(14.0)
    nn = (out * math.cos(tilt) + up * math.sin(tilt)).normalized()
    upv = (up * math.cos(tilt) - out * math.sin(tilt)).normalized()
    Mx = Matrix.Translation(p0) @ elf.frame(nn, upv)
    W_, H_ = 0.112 * k, 0.190 * k
    poly = []
    for i in range(7):     # 위: 둥근 모서리
        a = math.radians(180.0 - 180.0 * i / 6)
        poly.append((math.cos(a) * W_ / 2, -0.010 * k + math.sin(a) * 0.020 * k))
    poly += [(W_ / 2, -0.090 * k), (W_ * 0.30, -0.150 * k), (0.0, -H_), (-W_ * 0.30, -0.150 * k), (-W_ / 2, -0.090 * k)]
    poly = list(reversed(poly))
    wv = c2.skirt_w(e, Mx @ V((0, 0, -0.080 * k)))
    c2.prism(buf, poly, 0.007 * k, Mx, mat=plate_d, w=wv, chamfer=0.002 * k)
    inner = [(x * 0.80, (z + 0.090 * k) * 0.82 - 0.090 * k) for x, z in poly]
    c2.prism(buf, inner, 0.010 * k, Mx, mat=plate, w=wv, chamfer=0.002 * k)
    c2.prism(buf, c2.star_poly(0.034 * k, 0.008 * k, n=4, rot=90.0, cz=-0.080 * k), 0.013 * k, Mx, mat=plate_d,
             w=wv, chamfer=0.0015 * k)


for s in (1, -1):
    e.part(f"tasset_{'L' if s > 0 else 'R'}", "body", lambda buf, s=s: tasset(buf, s))

# ---- 다리: 맨 허벅지 + 무릎 판(리벳) + 정강이 판 + 발 갑옷
for sd in ("L", "R"):
    e.pad(plate, (f"leg_{sd}", 0.50, 0, 0.010 * k), size=(0.086, 0.020, 0.074), name=f"knee_{sd}")
    a = e.anchor((f"leg_{sd}", 0.50, 0, 0.034 * k))
    e.part(f"knee_rivet_{sd}", "body", lambda buf, a=a: dc.stud(buf, a.pos, a.n, 0.0060 * k, silver, w=a.w,
                                                                 depth=0.6, segs=6, rings=4))
    c2.leg_tube(e, plate, sd, 0.58, 0.86, off=0.012, name=f"greave_{sd}",
                extra=lambda t: 0.004 * smoothstep(0.0, 0.25, t))
    e.ring(plate_d, f"leg_{sd}", 0.66, h=0.008, th=0.003, off=0.016, name=f"greave_band_{sd}")
q0 = e.q
e.q = 0.5
e.boots(plate_d, top=0.84, sole=(black, 0.014), toe=0.006, off=0.012)
e.q = q0

# ---- 용 날개 (붉은 막, 검은 뼈대) + 꼬리 (아랫면 붉게, 왼쪽 뒤 땅으로)
dc.wings(e, span=0.36, height=0.34, mem=mem, bone=wbone, angle=138.0, sweep=20.0, raise_=10.0,
         z=e.chest_z + 0.070 * k)
bz = hz + 0.030 * k
bp, bn = e.torso_point(bz, 180.0, -0.012 * k)
ctrl = [bp,
        bp + V((0.0, 0.090 * k, -0.050 * k)),
        V((0.030 * k, bp.y + 0.180 * k, 0.180 * k)),
        V((0.100 * k, bp.y + 0.250 * k, 0.050 * k)),
        V((0.210 * k, bp.y + 0.260 * k, 0.030 * k)),
        V((0.320 * k, bp.y + 0.210 * k, 0.036 * k)),
        V((0.380 * k, bp.y + 0.140 * k, 0.050 * k))]
dc.tail(e, ctrl, 0.056, mat=tail_m, belly=red, bones=4, segs=10, n=20, belly_arc=120.0)

e.finalize()

# ---- 거대한 무쇠 검 (별도 노드 ritz_sword). 무기 규약: 원점 = 오른손 파지점, 칼날 +Y, 칼등 +Z, 두께 X
sw = Buf()
blade = M_("rz_blade", "#55555e")
edge = M_("rz_edge", "#d8d8de")
rope = M_("rz_rope", "#a8895f")
grip_m = M_("rz_grip", "#3a3439")
# 폼멜: 아래로 벌어지는 검은 깔때기
loft(sw, [{"c": (0, -0.064, 0), "rx": 0.016, "ry": 0.016, "w": {}},
          {"c": (0, -0.090, 0), "rx": 0.019, "ry": 0.019, "w": {}},
          {"c": (0, -0.112, 0), "rx": 0.028, "ry": 0.028, "w": {}},
          {"c": (0, -0.124, 0), "rx": 0.036, "ry": 0.036, "w": {}}],
     segs=12, cap0="flat", cap1="flat", mat=black, ref=(1, 0, 0))
# 손잡이 + 밧줄 감기 + 늘어진 밧줄 끝
loft(sw, [{"c": (0, -0.070, 0), "rx": 0.0135, "ry": 0.0135, "w": {}},
          {"c": (0, 0.050, 0), "rx": 0.0135, "ry": 0.0135, "w": {}}], segs=10, cap0="flat", cap1="flat", mat=grip_m)
for i in range(4):
    y = lerp(-0.048, 0.030, i / 3)
    band(sw, (0, y, 0), (0, 1, 0), (1, 0, 0), 0.0155, 0.0155, 0.016, 0.004, segs=7, mat=rope)
for dx, ln in ((0.006, 0.070), (-0.004, 0.090)):
    loft(sw, [{"c": (dx, -0.040, -0.016), "rx": 0.0042, "ry": 0.0042, "w": {}},
              {"c": (dx * 1.6, -0.050, -0.016 - ln * 0.6), "rx": 0.0040, "ry": 0.0040, "w": {}},
              {"c": (dx * 2.0, -0.070, -0.016 - ln), "rx": 0.0036, "ry": 0.0036, "w": {}}],
         segs=6, cap0="flat", cap1="round", mat=rope)
# 코등이: 검은 사각 덩어리
rbox(sw, (0.052, 0.036, 0.150), Matrix.Translation((0, 0.068, -0.004)), mat=black, r=0.18, segs=1)
# 칼날: 두꺼운 무쇠 판. 아래 날(-Z)이 밝고 들쭉날쭉(닳은 날), 끝은 날 쪽 모서리를 비스듬히 자름
Y0, Y1 = 0.086, 0.860
NS = 12
JAG = [0.0, 0.004, -0.003, 0.005, -0.002, 0.003, -0.004, 0.002, 0.005, -0.003, 0.002, 0.0]
secs = []
for i in range(NS):
    y = lerp(Y0, Y1, i / (NS - 1))
    ze = -0.078 + JAG[i]
    tip_cut = smoothstep(0.80, 1.0, i / (NS - 1))
    ye = y - 0.070 * tip_cut          # 날 쪽은 끝에서 짧다
    prof = [(0.013, 0.074, y), (0.013, -0.040, y), (0.0035, ze + 0.004, ye), (-0.0035, ze + 0.004, ye),
            (-0.013, -0.040, y), (-0.013, 0.074, y)]
    secs.append([sw.vert((x, yy, z), {}) for x, z, yy in prof])
mats_ring = [blade, edge, edge, edge, blade, blade]   # 면 j: 꼭짓점 j → j+1
for i in range(NS - 1):
    for j in range(6):
        j2 = (j + 1) % 6
        sw.face((secs[i][j], secs[i + 1][j], secs[i + 1][j2], secs[i][j2]), mats_ring[j])
sw.face(tuple(secs[0][::-1]), blade)
sw.face(tuple(secs[-1]), blade)
# 끝 근처 가로 쇠띠(양면 리벳 띠) + 칼등 쪽 덧댄 판
for xs in (1, -1):
    rbox(sw, (0.006, 0.030, 0.130), Matrix.Translation((xs * 0.0145, 0.760, 0.000)), mat=silver, r=0.2, segs=1)
rbox(sw, (0.032, 0.300, 0.016), Matrix.Translation((0, 0.250, 0.078)), mat=plate_d, r=0.25, segs=1)
sword = sw.obj("ritz_sword_geo", angle=35.0)
cb.apply_modifiers(sword)
vc = elf.vc_material("ritz_toon_vc", e.line)
elf.bake_vcol(sword)
elf.remap_to_vc(sword, vc)
elf.collapse_slots(sword)
sword.name = "ritz_sword"
sword["outline"] = 0.0035
sword["prop"] = "sword"
sword["blade_tip"] = "0,0.860,0.000"
sock = bpy.data.objects["socket_hand_R"]
sword.parent = sock
sword.matrix_parent_inverse = Matrix.Identity(4)
sword.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
# 기본 자세: 오른손에 쥐고 칼끝을 뒤 오른쪽 땅에 끌리게 (칼날 길이 0.86 m, 손 높이에서 땅까지)
mw = sock.matrix_world.copy()
hand = mw.translation
drop = hand.z - 0.030
dz = -drop / 0.86
hz_ = math.sqrt(max(1 - dz * dz, 0.0))
d = V((-0.30 * hz_, 0.954 * hz_, dz)).normalized()   # 칼날 방향: 뒤(+Y) 조금 바깥(-X), 아래
upw = V((0, 0, 1))
xw = d.cross(upw).normalized()
zw = xw.cross(d).normalized()                         # 칼등 = 위쪽
Mw = Matrix((xw, d, zw)).transposed().to_4x4()
Mw.translation = hand
sword.matrix_basis = mw.inverted() @ Mw

e.export("characters/ritz.glb")
