"""엘레나 공용: 체격·얼굴·머리카락. elena.py(시장 복장)와 elena_prisoner.py(죄수복)가 같이 쓴다.
혼자 실행하는 모델 스크립트가 아니다. 얼굴·머리를 바꿀 때는 이 파일만 고치면 두 모델이 같이 바뀐다.

원작 식별 요소 (나무위키 「엘레나(트릭컬 리바이브)」 카드·소개 카드·SD 아이콘·코스튬, 2026-11-02 다시 확인):
- 머리: 장밋빛이 도는 차분한 분홍(연어색) 긴 생머리. 정수리는 둥글고 매끈하며, 어깨 아래부터 바깥으로 넓게 퍼지는
  A라인 실루엣이다. 끝은 넓적한 뭉치로 바깥으로 살짝 말린다. 앞머리는 눈썹 높이의 뭉툭한 일자 앞머리다.
  귀 높이 바깥 실루엣에서 한 가닥이 바깥으로 살짝 뻗친다. 정수리 좌우에 크림색 둥근 광택 두 개.
- 눈: 위는 옅은 하늘색, 아래는 크림빛 노랑. 윗눈꺼풀이 평평하게 내려온 반쯤 감은 능청스러운 눈매, 메롱.
- 체형: 다른 엘프보다 큰 성인 체형(실측 3.25등신). 원작 코스튬(검은 드레스)에서 성인 여성 체형이 분명하다.
  가슴 볼륨 bust=0.60 (docs/art/characters-cameo3.md '체형' 절).
표정: 키트 5종 + tongue(메롱), tired(지친 눈, 수용소), wink(윙크 메롱) + blink 교정 키.
근거: docs/art/characters-cameo.md 3장
"""
import math

import elf
import cameo
import cameo2 as c2
from elf import V, lerp, smoothstep

# 원작 실측 3.25등신. bust: 원작 성인 체형 (characters-cameo3.md '체형')
BODY = dict(height=1.36, head=0.44, leg=1.08, chest=0.40, bust=0.60, hips=1.06, cheek=0.09)
TRI = dict(segs=0.78, hand_q=0.7)

HAIR = "#d08782"       # 원작 실측 #d7928a(밝은 면) ~ #b2706c(그늘). 툰 3단에서 같은 인상이 나게 가운데 값
HAIR_D = "#a9625f"
HAIR_L = "#f6d6c2"     # 정수리 크림색 광택


def face(e):
    """옅은 하늘색-크림 노랑 눈, 반쯤 감은 능청스러운 눈매, 가는 눈썹, 분홍빛 속눈썹 그림자."""
    e.face(eye_color="#a5cbe6", iris_dark="#5a6f9c", iris_light="#f2e3a2", pupil="#2a3350",
           eye_size=1.06, lash="#4f2a2f", brow="#b46a64", brow_th=0.85, blush="#f6a9a6", blush_size=1.05,
           base={"eye": {"top": 0.018, "ktop": 4.6, "tilt_out": -0.002, "cout": 0.012},
                 "iris": {"cz": 0.0025},
                 "brow": {"ang": 3.0, "dz": 0.066, "arch": 0.004},
                 "mouth": {"w": 0.019, "curve": 0.0035}},
           expr={
               # 메롱: 작게 벌린 입에 혀
               "tongue": {"eye": {"top": 0.015, "lift": 0.008},
                          "mouth": {"w": 0.024, "curve": 0.0050, "open": 0.0125, "top_arch": 0.0015}},
               # 지친 눈 (수용소): 더 감긴 눈, 처진 눈썹, 시무룩한 입
               "tired": {"eye": {"top": 0.010, "tilt_out": -0.007, "ktop": 3.0},
                         "brow": {"ang": 14.0, "dz": 0.060},
                         "mouth": {"w": 0.018, "curve": -0.0020}},
           })
    cameo.face_expr(e, "wink",
                    both={"mouth": {"w": 0.024, "curve": 0.0055, "open": 0.0110, "top_arch": 0.0015}},
                    L={"eye": {"close": 1.0, "lift": 0.012}, "brow": {"dz": 0.060, "ang": -4.0}},
                    R={"eye": {"top": 0.021, "lift": 0.010}, "brow": {"dz": 0.070, "arch": 0.005}},
                    corner=(0.0025, 0.0))


class FlowHair(c2.Hair2):
    """긴 생머리 A라인: 머리 덩어리가 가장 넓은 곳(s_break) 아래에서 바깥으로 점점 더 퍼진다.
    flare: 0.5 m 내려왔을 때 더 퍼지는 양에 가까운 배율(m 단위 계수), flare_fn(az): 방위별 배율.
    키트 v2는 수직으로 떨어지며 6%만 벌어진다(엘레나 원작의 종 모양 실루엣이 안 나온다)."""

    def __init__(self, e, color, *, flare=0.0, flare_fn=None, **kw):
        super().__init__(e, color, **kw)
        self.flare = flare
        self.flare_fn = flare_fn

    def _prep(self):
        if self._T is not None:
            return
        super()._prep()
        for i, L in enumerate(self._T):
            az = i * self._daz
            L["flare"] = self.flare * (self.flare_fn(az) if self.flare_fn else 1.0)

    def _eval(self, L, s):
        p, n = super()._eval(L, s)
        f = L.get("flare", 0.0)
        if f and s > L["sb"]:
            d = s - L["sb"]
            p = p + L["rad"] * (f * d * d / (d + 0.25 * self.k))
        return p, n


def _flare_fn(az):
    """옆과 옆뒤가 가장 많이 퍼지고, 팔이 지나가는 옆(85~115°)은 덜, 뒤 가운데는 중간."""
    a = abs(((az + 180.0) % 360.0) - 180.0)
    side = math.exp(-((a - 60.0) / 26.0) ** 2) + math.exp(-((a - 140.0) / 26.0) ** 2)
    return 0.45 + 0.75 * min(1.0, side)


def _locks(h, lk):
    """뭉툭한 일자 앞머리, 바깥으로 말리는 넓은 옆·뒷머리 끝."""
    k = h.k
    r = lk["region"]
    if r == "front":
        lk["p"] = 2.0             # 뾰족한 톱니 대신 끝만 살짝 모이는 뭉툭한 끝
        lk["free"] *= 0.55        # 갈라짐은 끝에서만
        lk["curl"] = -0.004 * k   # 이마 쪽으로 살짝 말림
        lk["th"] *= 1.15
    elif r == "side":
        lk["p"] = 1.9
        lk["free"] = min(lk["free"], 0.12 * k)
        lk["curl"] = 0.016 * k    # 끝이 바깥으로 뻗침
    elif r == "back":
        lk["p"] = 1.9
        lk["free"] = min(lk["free"], 0.13 * k)
        lk["curl"] = 0.014 * k
        lk["puff"] = 0.006 * k


def hair(e):
    """머리 (헤어 v2 + A라인): 매끈한 큰 돔, 뭉툭한 일자 앞머리, 허리까지 오는 두꺼운 옆 커튼, 엉덩이 아래까지 등 뒤로
    흐르며 바깥으로 퍼지는 긴 생머리(hair_back_01..03, chest 자식), 정수리 광택 2개."""
    k = e.k
    h = FlowHair(e, HAIR, dark=HAIR_D, light=HAIR_L, volume=1.14, flare=0.20, flare_fn=_flare_fn,
                 lock_fn=c2.lock_edit(_locks))
    e._hairs = getattr(e, "_hairs", []) + [h]
    h.cap(front=30, side=-6, back=-46)
    h.bangs(n=8, spread=50, tip_el=-2, jag=0.10, thick=1.15, seed=3.0, curl=0.6)
    # 옆 커튼: 관자놀이(48°)부터 귀 앞(78°)까지 한 덩어리. 두껍게(앞에서 봐도 덩어리로 읽힘), 끝에서만 두 갈래.
    # 귀(90°) 둘레는 키트의 짧은 채움 다발이라 원작처럼 뾰족한 귀가 머리 밖으로 나온다.
    h.sides(length=0.42, width=0.112, az=63, n=2, thick=2.4, curl=0.5, puff=1.6)
    h.back(length=0.52, n=9, spread=82)
    h.shine(el=52, spread=72, n=2, size=1.15)
    return h
