"""캐시 공용: 얼굴·머리카락·땋은 머리 (cathy_prologue.py, cathy.py가 같이 쓴다). 혼자 실행하는 모델 스크립트가 아니다.

원작 식별 요소 (docs/art/characters-cameo.md 1장)
- 회흑색 머리, 오른쪽(-X) 앞머리에 은회색 브릿지, 정수리 바보털 두 가닥
- 귀 뒤에서 무릎 위까지 늘어지는 양 갈래 땋은 머리. 끝으로 갈수록 밝은 회색이고 끝에 검은 리본
- 주황빛 붉은 눈, 살짝 처진 눈꼬리와 걱정스러운 눈썹(겁 많은 정찰병)
- 왼쪽(+X) 머리 위의 흰 해골 머리핀
"""
import math

import cameo
import elf
from elf import V, Matrix, Buf

HAIR = "#3e3c42"
HAIR_D = "#2a282e"
STREAK = "#b4b3b9"
BRAID_MID = "#6c6a71"
BRAID_TIP = "#9f9da4"
BRAID_END = "#c9c7cc"


def face(e):
    """주황빛 붉은 눈, 처진 눈꼬리. 교관 역할용 표정 3종을 더한다."""
    e.face(eye_color="#e0604c", iris_dark="#8a2833", iris_light="#ffb877", pupil="#4a1621",
           lash="#2c2428", brow="#3a3438", blush="#f7b0ad", blush_size=0.95,
           base={"eye": {"tilt_out": -0.004, "cout": 0.012}, "brow": {"ang": 5.0, "arch": 0.002}},
           expr={
               # 굳는 표정: 눈을 크게 뜨고 동공이 작아지며 입을 꾹 다문다 (프롤로그 끝 '대기 해제')
               "freeze": {"eye": {"top": 0.034, "bot": 0.056, "ktop": 2.5, "kbot": 2.0, "tilt_out": 0.0},
                          "iris": {"pupil": 0.55, "rx": 0.027, "ry": 0.038, "cz": 0.004},
                          "brow": {"dz": 0.071, "ang": 3.0, "arch": 0.0, "th": 0.0056},
                          "mouth": {"w": 0.016, "curve": -0.0014, "open": 0.0, "wave": 0.0005}},
           })
    # 능청 웃음: 반쯤 감은 눈, 왼쪽 눈썹만 올라가고 왼쪽 입꼬리가 올라간다
    cameo.face_expr(e, "smirk",
                    both={"eye": {"top": 0.020, "lift": 0.012, "ktop": 3.4, "tilt_out": -0.002},
                          "mouth": {"w": 0.030, "curve": 0.0062, "open": 0.0028, "top_arch": -0.0008}},
                    L={"brow": {"dz": 0.079, "ang": 2.0, "arch": 0.007}},
                    R={"brow": {"dz": 0.057, "ang": -12.0, "arch": 0.0}},
                    corner=(0.0068, -0.0012), mouth_dx=0.0030 * e.k)
    # 장난: 왼눈 윙크 + 메롱 (작게 벌린 입에 혀)
    cameo.face_expr(e, "tease",
                    both={"mouth": {"w": 0.024, "curve": 0.0052, "open": 0.0125, "top_arch": 0.0015}},
                    L={"eye": {"close": 1.0, "lift": 0.012}, "brow": {"dz": 0.060, "ang": -6.0}},
                    R={"eye": {"lift": 0.016, "top": 0.028}, "brow": {"dz": 0.071, "arch": 0.006}},
                    corner=(0.0020, 0.0))


def hair(e, helmet=False):
    """회흑색 단발 + 은회색 브릿지 + 바보털 (헤어 v2). helmet=True면 헬멧 아래로 보이는 부분만 성글게.
    원작: 머리 덩어리는 둥근 공 모양, 큰 앞머리 다발이 오른쪽 눈을 덮고, 끝이 턱 쪽으로 말리는 옆머리."""
    h = e.hair(HAIR, dark=HAIR_D, light="#77757e")
    streak = elf.mat(f"{e.name}_hair_streak", STREAK)
    if helmet:
        # 헬멧 아래: 성글게(v2 해상도 힌트), 덩어리를 얇게 해 헬멧 테 아래로 머리가 부풀어 나오지 않게
        h.cap(front=30, side=-8, back=-50, part=8, segs=16, rows=5, volume=0.78)
    else:
        h.cap(front=30, side=-8, back=-48, part=8, segs=16, rows=5)   # 예산: 셸을 조금 성글게
    h.bangs(n=7, spread=58, tip_el=-9, length=1.1, jag=0.45, sweep=-7, part=8, seed=1.0)
    # 오른쪽(-X) 눈 위로 늘어진 은회색 브릿지 한 다발 (원작 캐시의 가장 큰 식별 요소). 앞머리 셸 바깥에 얹는다.
    o = h.off
    cameo.strand(h, [h.sp(-14, 72, o * 0.5), h.sp(-26, 46, o * 1.30), h.sp(-36, 16, o * 1.40),
                     h.sp(-42, -4, o * 1.15), h.sp(-46, -14, o * 0.9)], 0.056 * e.k, 0.016 * e.k, n=12, segs=8,
                 mat=streak, taper=[(0, 0.7), (0.3, 1.0), (0.7, 0.8), (1, 0.0)])
    h.sides(length=0.035, width=0.066, curl=0.7)
    if helmet:
        h.back(length=0.03, n=5)
    else:
        h.back(length=0.025, n=7)
        cameo.ahoge(h, az=-8, height=0.095, curl=1.6, width=0.024)
        cameo.ahoge(h, az=8, height=0.065, curl=-1.2, width=0.018)
        h.shine(el=52, spread=84, n=2, size=1.1)
    return h


BRAID_STOPS = [(0.0, HAIR), (0.40, HAIR), (0.62, BRAID_MID), (0.80, BRAID_TIP), (0.95, BRAID_END)]


def braids(e, h, *, bow_mat=None, end_z=0.30, out=0.0, lobes=10, segs=10, rings=6):
    """귀 뒤에서 나와 어깨 뒤를 지나 허벅지 높이까지 늘어지는 양 갈래 땋은 머리 (원작: 옆으로 늘어지다 끝이 바깥으로 벌어짐).
    연속 볼륨(cameo.Braid: 마디가 반씩 겹쳐 틈이 없다). 뿌리 두 마디는 옆·뒷머리 덩어리 안에 묻고, 어깨 위에서
    몸과 팔 뒤로 살짝 떨어지게 휜다. 가닥마다 본 3개(hair_braid_L/R_01..03). <이름>_hair 노드에 합친다.
    색 그라데이션은 finalize 뒤 shade(e, bs)로 넣는다. 반환: Braid 목록."""
    k = e.k
    bow_mat = bow_mat or elf.mat(f"{e.name}_bow", "#2b282e")
    hm = elf.mat(f"{e.name}_braid", HAIR)
    out_ = []
    sz = e.shoulder_z
    for s in (1, -1):
        ctrl = [h.sp(s * 112, -2, h.off * 0.20),            # 귀 뒤 머리 덩어리 안 (묻힌 뿌리)
                h.sp(s * 120, -26, h.off * 0.95),           # 셸 바로 아래에서 나온다
                V((s * 0.184 * k, 0.118 * k, e.torso_top + 0.012 * k)),
                V((s * 0.205 * k, 0.114 * k, sz - 0.10 * k)),
                V((s * (0.234 + out) * k, 0.098 * k, sz - 0.22 * k)),
                V((s * (0.270 + out) * k, 0.074 * k, end_z * k))]
        b = cameo.Braid(e, f"hair_braid_{'L' if s > 0 else 'R'}", ctrl, w0=0.072 * k, w1=0.046 * k, lobes=lobes,
                        tilt=26, face=(s * 0.5, 0.86, 0.0), mat=hm, bones=3, tie=bow_mat, tie_at=0.90,
                        tuft=0.05 * k, bow=bow_mat, bow_size=0.095 * k, segs=segs, rings=rings)
        b.done()
        out_.append(b)
    return out_


def shade(e, bs):
    """finalize 뒤: 땋은 머리 끝으로 갈수록 밝아지는 정점색 그라데이션."""
    return cameo.shade_braids(cameo.hair_obj(e), bs, HAIR, BRAID_STOPS)


def skull_pin(e, h, *, az=58.0, el=44.0, size=0.058):
    """왼쪽 머리 위 해골 머리핀. 헤어 v2 셸 바깥 면에 얹는다(뜨지 않게 1.5 mm 묻음)."""
    k = e.k
    bone = elf.mat(f"{e.name}_skull", "#f4f0ec")
    hole = elf.mat(f"{e.name}_skull_d", "#3a3034")
    off = cameo.hair_surface_off(e, h, az, el) - 0.0015 * k
    e.gear("skull_pin", ("head", az, el, off),
           lambda buf, M, w: cameo.skull(buf, M @ Matrix.Rotation(math.radians(-15), 4, "Y"), size * k, bone, hole,
                                         w=w))
