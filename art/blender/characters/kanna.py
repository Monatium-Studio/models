"""칸나: 모나티엄 진압반장. 1막 브리핑에서 리타의 상관이고, 시가전에서 흑뉴아에게 제압된다.

원작 칸나(트릭컬 리바이브)의 복장을 바탕으로 한 카메오 모델.
- 유지한 식별 요소: 연금발 + 뒤통수 위쪽에서 높게 묶은 포니테일(주황 머리끈, 끝이 왼쪽으로 쓸림), 정수리 바보털, 청록색 눈,
  반쯤 감은 자신만만한 눈매와 굵은 눈썹, 흰 탱크톱(넓은 U넥, 짧은 기장) 위에 앞을 열어 걸친 금색 테두리의 남보라 크롭
  재킷, 같은 색 바지, 허리에 느슨하게 걸친 금색 끈, 오른 허벅지 끈과 사각 은색 버클, 금색 테두리의 갈색 부츠와 흰 밑창.
  성인 체형 가슴 볼륨 bust 0.50 (docs/art/characters-cameo3.md '체형').
- 사용자 확정 (2026-11-02): "칸나는 탱크탑", 그리고 재킷은 원작 카드처럼 탱크톱 위에 걸친다. 재킷 앞이 열려 탱크톱의
  U넥과 짧은 기장이 보이고, 배는 원작보다 좁게(벨트 위 3cm 남짓) 드러낸다. 탱크톱 어깨끈은 재킷에 가려 만들지 않는다.
- 재해석: 진압반장 표식으로 금색 견장, 오른 어깨 금색 장식끈, 재킷 가슴 계급장, 바지 바깥 솔기의 금색 줄, 오른 허벅지의
  권총집, 왼쪽 허리 무전기. 금색은 지휘관에게만 쓴다(reference-notes 6장). 원작의 대포·금색 별은 옮기지 않았다.
- 예산(18k): 재킷에 가려지는 탱크톱은 성기게(7×22), 머리카락 셸은 몸보다 조금 성기게(0.70) 만든다.
- 표정: 키트 5종 + smug(한쪽 입꼬리), shout(지휘 외침) + blink 교정 키.
근거: docs/art/characters-cameo.md

npm run model -- art/blender/characters/kanna.py
npm run shot -- characters/kanna.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import cameo  # noqa: E402
import cameo2 as c2  # noqa: E402
from elf import V, Matrix, Buf, keys, lerp  # noqa: E402

cb.reset()
M_ = elf.mat
e = elf.Elf("kanna", height=1.24, leg=1.05, chest=0.30, bust=0.50, segs=0.78, hand_q=0.7, cheek=0.10)
k = e.k

# ---- 팔레트 (원작 실측 재킷·바지 #706478 계열을 조금 어둡게, 금색 테두리는 지휘관 표식)
jacket = M_("ka_jacket", "#655b76")
jacket_d = M_("ka_jacket_d", "#4d4459")
pants = M_("ka_pants", "#5c536b")
gold = M_("ka_gold", "#e3b04c")
gold_d = M_("ka_gold_d", "#b88a34")
white = M_("ka_white", "#eeecf2")      # 탱크톱 (원작 #f3efef, 맨살과 구분되게 아주 살짝 차갑게)
white_d = M_("ka_white_d", "#cdc7d6")
red = M_("ka_red", "#c4424a")
brown = M_("ka_brown", "#6a4240")
brown_d = M_("ka_brown_d", "#523231")
sole = M_("ka_sole", "#ece4dc")
metal = M_("ka_metal", "#d3cec8")
navy = M_("ka_navy", "#2f3644")
tie = M_("ka_tie", "#e8a03a")

# ---- 얼굴: 청록 눈, 반쯤 감은 자신만만한 눈매, 굵고 각진 눈썹
e.face(eye_color="#4fbcae", iris_dark="#1f5c58", iris_light="#c4f2e2", pupil="#173a3a",
       lash="#3a2a2c", brow="#7a5a44", brow_th=1.35, blush="#f6aaa6", blush_size=1.05,
       base={"eye": {"top": 0.015, "ktop": 5.0, "tilt_in": -0.004, "cout": 0.013, "bot": 0.050},
             "brow": {"ang": -14.0, "dz": 0.054, "arch": 0.0},
             "mouth": {"w": 0.020, "curve": 0.0040}},
       expr={
           # 지휘 외침: 눈을 뜨고 눈썹을 세게 내리며 입을 크게 벌린다 (브리핑, 돌격 명령)
           "shout": {"eye": {"top": 0.026, "ktop": 3.2, "tilt_in": -0.010},
                     "brow": {"ang": -20.0, "dz": 0.054, "th": 0.0075},
                     "mouth": {"w": 0.026, "open": 0.017, "curve": 0.0015, "top_arch": 0.003}},
       })
# 한쪽 입꼬리만 올린 자신만만한 웃음 (원작 칸나의 대표 표정)
cameo.face_expr(e, "smug",
                both={"eye": {"top": 0.013, "lift": 0.010, "ktop": 5.0},
                      "mouth": {"w": 0.026, "curve": 0.0055, "open": 0.0015}},
                L={"brow": {"dz": 0.066, "ang": -4.0}},
                R={"brow": {"dz": 0.058, "ang": -12.0}},
                corner=(0.0060, -0.0008), mouth_dx=0.0022 * k)

# ---- 머리 (헤어 v2): 연금발, 뒤통수 위 가운데 포니테일(사용자 확정), 옆으로 넘긴 앞머리, 바보털
# 원작 카드·3성 일러스트: 정수리 뒤 높은 곳(뒤에서 약 48°)에서 묶어 위·뒤로 부풀었다가 S자로 떨어지고,
# 끝은 어깨~가슴 높이에서 몇 갈래로 갈라진다. 굵기는 얼굴 폭의 1/3 정도.
def soft(h, lk):
    """옆으로 넘긴 앞머리: 끝만 모이는 매끈한 다발 (예전 jag 0.30은 톱니처럼 삐죽했다)."""
    if lk["region"] == "front":
        lk["p"] = 1.8
        lk["free"] *= 0.70
    elif lk["region"] == "side":
        lk["p"] = 1.9
        lk["curl"] = 0.006 * h.k     # 턱선에서 끝이 살짝 바깥으로


h = c2.hair(e, "#f2e1b4", dark="#d6bd88", light="#fffaf0", lock_fn=c2.lock_edit(soft))
h.cap(front=28, side=-8, back=-48, part=-18)
h.bangs(n=6, spread=58, tip_el=-4, sweep=-16, part=-22, jag=0.12, seed=2.0)
h.sides(length=0.11, width=0.078, curl=0.4, right=dict(length=0.14))   # 캐릭터 오른쪽(앞머리가 쓸리는 쪽)이 턱까지
h.back(length=0.0, n=7)
cameo.ahoge(h, az=-14, height=0.10, curl=1.6, width=0.022)
h.shine(el=50, spread=80, n=2, size=1.2)
# 포니테일: 뒤통수 위 가운데에서 묶고(주황 머리끈), 위·뒤로 부풀었다가 뒤통수 뒤로 떨어져 견갑골 위에서 끝난다.
# 끝은 캐릭터 왼쪽으로 살짝 쓸린다. 본 3개 (hair_tail_01..03), 흔들림용.
hc = e.head_c
TIE_EL = 48.0
base, nb = h.path(180.0, h.s_of_el(180.0, TIE_EL))
ctrl = [base - nb * 0.030 * k,                                   # 머리 덩어리 안에 묻힌 뿌리
        base + nb * 0.010 * k,                                   # 묶은 자리 (머리끈)
        hc + V((0.000, 0.244, 0.206)) * k,                       # 위·뒤로 살짝 솟음
        hc + V((0.004, 0.322, 0.112)) * k,                       # 둥글게 넘어가는 꼭대기
        hc + V((0.008, 0.336, -0.050)) * k,                      # 뒤통수 뒤로 가장 부푼 곳
        hc + V((0.018, 0.306, -0.195)) * k,                      # 뒷머리 바깥을 따라 내려옴
        V((0.034, hc.y / k + 0.258, e.chin / k - 0.070)) * k,     # 목 뒤로 살짝 들어옴
        V((0.058, hc.y / k + 0.222, e.shoulder_z / k - 0.080)) * k]   # 끝 (견갑골 위, 왼쪽으로 쓸림)
tl = cameo.Tail(e, h, "hair_tail", ctrl, width=0.150 * k, thick=0.108 * k, lat=(1, 0, 0), bones=3, tie_at=0.045,
                root=0.46, puff=0.14, hold=0.50, body_end=0.86, ends=3, split=0.62, spread=0.62, end_w=0.46,
                end_len=(0.96, 1.0, 0.90), tie=tie, tie_h=0.024, tie_th=0.008)
tl.done()


# ---- 흰 탱크톱: 넓은 U넥, 겨드랑이 아래로 파인 진동, 벨트 위 3cm 남짓에서 끝나는 기장.
# 윗단 높이를 방위마다 다르게 잡은 닫힌 셸(앞 U넥 → 어깨끈 자리 → 겨드랑이 → 뒷목)이고 가슴 볼륨(bust)을 따른다.
# 위에 재킷을 걸치므로 앞 트임과 재킷 밑단 아래만 보인다: 성기게 만들고 어깨끈은 생략한다(재킷에 가려짐).
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
sz = e.shoulder_z
Z_TANK = wz + 0.030 * k
# 윗단 높이(어깨 관절 높이 기준, m × k): 둥근 U넥(가운데 평평) → 끈 자리 → 겨드랑이 → 끈 자리 → 뒷목
TOP_TAB = [(0, -0.062), (8, -0.061), (16, -0.056), (24, -0.043), (30, -0.028), (35, -0.016), (42, -0.015),
           (50, -0.030), (60, -0.054), (90, -0.080), (120, -0.054), (130, -0.030), (138, -0.015), (145, -0.016),
           (152, -0.026), (164, -0.036), (180, -0.040)]


def tank_top_z(a):
    a = abs(((a + 180.0) % 360.0) - 180.0)
    return sz + keys(TOP_TAB, a) * k


class TankTop(cameo.Shell):
    """윗단 높이가 방위마다 다른 닫힌 몸판 (cameo.Shell의 격자·두께·테두리를 그대로 쓴다)."""

    def __init__(self, e, mat, z_hem, *, off=0.008, th=0.004, rows=7, cols=22):
        self.e, self.mat, self.buf, self.closed = e, mat, Buf(), True
        self.prm = dict(z_top=tank_top_z(0.0), z_hem=z_hem, off=off, flare=None, skirt=False, p=2.3, drop=None,
                        ruffle=None)
        self.rows, self.cols = rows, cols
        self.P, self.N, self.W = [], [], []
        for i in range(rows):
            u = i / (rows - 1)
            rowP, rowN, rowW = [], [], []
            for j in range(cols):
                a = 360.0 * j / cols
                z = lerp(tank_top_z(a), z_hem, u)
                rx, ry, cy = cameo.section(e, z)
                o = (off + 0.004 * u * u) * k            # 밑단 쪽이 살짝 여유
                q, n = cameo.ring_pt(rx + o, ry + o, cy, z, a, 2.3)
                bo = cameo.bust_off(e, z, a, o)
                if bo > 0.0:
                    q = q + n * bo
                rowP.append(q)
                rowN.append(n)
                rowW.append(e._torso_wfn(q, 0))
            self.P.append(rowP)
            self.N.append(rowN)
            self.W.append(rowW)
        self._build(th * k)
        lo = min(tank_top_z(a) for a in range(0, 360, 10))
        e.cover["torso"].append((z_hem, lo - 0.004 * k))


tk = TankTop(e, white, Z_TANK)
tk.top_trim(white_d, width=0.006, th=0.0018)      # U넥·진동 둘레 바이어스
tk.hem_trim(white_d, width=0.006, th=0.0018)
tk.done("tank_top")
# ---- 바지 + 벨트 + 느슨하게 걸친 금색 끈 + 허벅지 권총집
e.pants(pants, bag=0.015, blouse=0.0, length=0.80, off=0.018)
e.belt(brown, z=wz - 0.010 * k, h=0.024, buckle=gold, loops=brown_d, off=0.024)
cord = []
for i in range(10):
    a = -180 + 360 * i / 9
    t = 0.5 - 0.5 * math.cos(math.radians(a - 60))       # 왼쪽 위가 높고 오른쪽 아래로 처진다
    cord.append(("torso", wz - 0.030 * k - 0.085 * k * t, a, 0.022 * k + 0.006 * k * t))
e.strap(gold, cord, width=0.009, th=0.006, name="gold_cord")
# 허벅지 권총집·끈·사각 버클 (원작: 허벅지 위쪽 끈과 버클). 헐렁한 바지 통(bag) 바깥에 둔다
e.pouch(brown, ("leg_R", 0.26, -84, 0.034 * k), size=(0.040, 0.026, 0.070), flap=brown_d, button=metal, strap=brown_d,
        name="holster")
e.patch(metal, ("leg_R", 0.36, -22, 0.035 * k), size=(0.022, 0.018), name="thigh_buckle")
e.ring(brown_d, "leg_R", 0.36, h=0.014, th=0.004, off=0.031, name="thigh_strap")

# 바지 바깥 솔기의 금색 줄 (지휘관 정복 바지의 측장)
for side, sg in (("L", 1), ("R", -1)):
    e.strap(gold, [(f"leg_{side}", t, sg * 92, 0.017 * k + 0.015 * k * min(1.0, t / 0.3)) for t in
                   (0.02, 0.18, 0.36, 0.54, 0.66)], width=0.006, th=0.002, name=f"pants_stripe_{side}")



# ---- 남보라 크롭 재킷 (금색 테두리)
# 원작 카드: 탱크톱 위에 앞을 V로 열어 걸침, 세운 깃, 금색 견장·장식끈·계급장, 왼쪽 허리 무전기
jk = cameo.Shell(e, jacket, e.torso_top - 0.002 * k, cz - 0.030 * k, gap=[(0.0, 36.0), (0.45, 24.0), (1.0, 20.0)],
                 off=0.022, th=0.005, cols=22, flare=[(0.0, 0.0), (1.0, 0.004)])
jk.edge_trim(gold, width=0.008, th=0.003).hem_trim(gold, width=0.008, th=0.003).done("jacket")


# 세운 뒷깃: 목 뒤와 옆을 두르고 앞은 열림 (원작 카드: V로 열린 재킷 깃, 금색 테두리). 닫힌 고리는 목 앞을 가렸다
jc = cameo.Shell(e, jacket, e.torso_top + 0.030 * k, e.torso_top - 0.004 * k, gap=40.0, off=0.026, th=0.005, rows=3,
                 cols=16, flare=[(0.0, 0.008), (1.0, 0.0)])
jc.top_trim(gold, width=0.006, th=0.002).edge_trim(gold, width=0.006, th=0.002).done("jacket_collar")
e.sleeves(jacket, length=0.95, off=0.013, flare=0.008, cuff=(gold, 0.018, 0.005))
e.epaulet(gold_d, button=gold, width=0.030, th=0.005, off=0.028)
# 계급장 (재킷 왼쪽 가슴, 남색 바탕에 금색 막대 3)
e.patch(navy, ("torso", cz + 0.050 * k, 40, 0.027 * k), size=(0.026, 0.024), name="rank_bg")
e.patch(gold, ("torso", cz + 0.050 * k, 40, 0.0285 * k), size=(0.018, 0.016), shape="bars3", name="rank_fg")
# 오른 어깨 금색 장식끈 (지휘관 표식): 견장 끝 → 겨드랑이 앞 → 가슴 단추
sz = e.shoulder_z
for i, dz in enumerate((0.0, -0.020)):
    e.strap(gold, [("torso", sz + 0.010 * k, -80, 0.030 * k), ("torso", sz - 0.035 * k + dz * k, -66, 0.030 * k),
                   ("torso", cz + 0.010 * k + dz * k, -44, 0.028 * k), ("torso", cz + 0.045 * k, -26, 0.027 * k)],
            width=0.006, th=0.004, name=f"aiguillette_{i}")

# 왼쪽 허리 무전기 (진압반 지휘 무전)
def radio(buf, Mx, w):
    cameo.rrbox(buf, (0.034 * k, 0.020 * k, 0.052 * k), Mx @ Matrix.Translation((0, -0.010 * k, 0)), mat=navy, w=w,
                r=0.25, segs=1)
    cameo.rrbox(buf, (0.026 * k, 0.006 * k, 0.018 * k), Mx @ Matrix.Translation((0, -0.021 * k, 0.010 * k)),
                mat=jacket_d, w=w, r=0.3, segs=1)
    base = Mx @ V((0.010 * k, -0.010 * k, 0.026 * k))
    elf.loft(buf, [{"c": base, "rx": 0.0035 * k, "ry": 0.0035 * k, "w": w},
                   {"c": base + Mx.to_3x3() @ V((0, 0, 0.045 * k)), "rx": 0.0025 * k, "ry": 0.0025 * k, "w": w}],
             segs=6, cap0="flat", cap1="round", mat=navy)


e.gear("radio", ("torso", wz - 0.030 * k, 112, 0.030 * k), radio)


# ---- 금색 테두리 갈색 부츠, 흰 밑창
e.boots(brown, top=0.62, sole=(sole, 0.016), cuff=gold, tab=brown_d, toe=0.004, off=0.030)

# 머리카락 셸·속층은 몸보다 조금 성기게 (짧은 단발이라 0.70에서도 매끈하다, 18k 예산)
q0 = e.q
e.q = 0.70
h.done()
e.q = q0
e.finalize()
# holdFwd: 총을 가슴에 붙이는 공용 자세(train_drill, cb_aim)에서 오른 아래팔 소매가 가슴(bust)·탱크톱을 스치지 않게
# 쥔 자리를 앞으로 뺀다 (src/game/npc/Npc.ts). 예전 모델도 같은 자세에서 소매가 이너를 스쳤다.
e.export("characters/kanna.glb", props={"holdFwd": 0.035})
