"""에필로그 「대관식」: 에르피엔 왕성 안뜰. 에르핀의 3차 대관식과 행사장 외곽 경계.

npm run model -- art/blender/levels/epilogue_coronation.py   → public/models/levels/epilogue_coronation.glb

원작: 침공전 종전 뒤 에르핀의 3차 대관식. 에르피엔 소상공회의 후원(골디·클로에)과 정령들이 되살린 왕관,
모두의 환호와 각 종족 수장들 앞에서 에르핀이 왕관을 다시 받는다. 엘레나가 참석하고 아멜리아가 비서로 동석한다.
오리지널: 행사장 배치(안뜰·서쪽 회랑·성문·단상 정자)와 모든 건축 형태. 원작 배경 그림을 옮기지 않았다.
원작: 깃발·현수막·탑 꼭대기와 가로등의 작은 깃발은 모두 에르피엔 군기(초록 바탕 + 노란 나비, lib/erpien_flag.py,
      사용자 결정 2026-11-02). 깃발 줄 삼각기는 군기의 초록·노랑. 바닥·단·아치·성문의 문장과 지붕 조형도 그 군기의 나비다.
리타는 모나티엄 대표단 경호 인원으로 서쪽 회랑(행사장 외곽)에 선다. 대본: docs/script/epilogue.md

배치 (Blender, -Y가 남쪽 = 정면)
  왕성        y 30..46. 정문 홀(x ±2.2, y 30..33.6, 바닥 0.9)과 앞 계단(y 27.8..30). 문짝은 런타임(epilogue/stage.ts)이 연다
  안뜰        x -16..16, y -16..28. 붉은 융단 통로가 왕성 계단 아래(y 27.8)에서 남쪽 단상까지 내려온다
  단상 정자   (0, -1) 3단 원형 단 + 기둥 6개 + 둥근 지붕. 남북이 열려 있다. 북쪽(통로 쪽)에서 오르고,
              네르의 제단은 단 남쪽(0, -2)에서 북쪽을 본다
  귀빈석      통로 머리 양쪽 낮은 단 (x ±2.6..6.8, y 4.8..8.6): 각 종족 수장
  의장대      통로 양쪽 (x ±1.9). 관람 줄(금 기둥 + 붉은 줄, x ±2.75) 뒤에 앞줄 주민(NPC), 그 뒤 군중(런타임 cinematic/crowd.ts)
  서쪽 회랑   x -21..-17, y -16..28. 안뜰 쪽 기둥(x -17, y -15 + 3k), 바깥 벽(x -21)의 아치 창과 현수막
              리타 (-20.45, -1.5) 동쪽(+X, 단상 쪽)을 보고 선다. 엘레나·아멜리아는 회랑 가운데(x -18.9)를 남→북으로 지나간다
  성문        남쪽 (y -17). 대관식 뒤 퍼레이드가 단 남쪽 융단을 따라 나가는 길

NPC 마커의 scene 속성 = 그 NPC가 보이는 컷 (없으면 모든 컷)
CAM: ep_a(전경) ep_b(초소의 리타) ep_c(회랑을 걸어오는 엘레나) co_a(정문 입장) co_g(만세: 에르핀 등 뒤에서 통로) co_h(단 위의 에르핀)
     pr_a pr_d(퍼레이드)
WP:  procession_nn(정문 홀 → 계단 → 통로 → 단), elena_walk_nn, amelia_walk_nn (회랑 남→북)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import monatium_city_kit as mk  # noqa: E402
import erpien_kit as ek  # noqa: E402
import erpien_flag as ef  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

cb.reset()

# ---------------------------------------------------------------- 요정 왕성 팔레트 (이 세트에서만 키트 팔레트에 더한다)
# 요정 경비대 초록·흰·금(docs/art/fairy-faction.md 2장 GUARD)과 에르핀(왕도) 대관식 복장의 붉은색·분홍을 바탕으로 했다.
mk.PAL.update({
    "marble": "#f8f4ee",      # 흰 석재 (왕성 벽)
    "marble_d": "#ddd4c8",    # 기단, 그림자 띠
    "marble_w": "#efe6da",    # 회랑 바닥
    "royal": "#bb3440",       # 융단·현수막 붉은색
    "royal_d": "#8c2633",
    "fairy_g": "#2f6a4f",     # 경비대 초록 (장식)
    "fairy_gd": "#21483a",
    "roof_f": "#4e8f87",      # 왕성 지붕 (청록 슬레이트)
    "roof_fd": "#3c716b",
    "rose": "#f3bccb",        # 정자 지붕, 장식
    "rose_d": "#dc93a8",
    "blossom": "#f5b8cf",     # 꽃나무
    "blossom_l": "#fbd6e3",
    "blossom_d": "#e597b6",
    "cream": "#f6e6cf",
    "hall_w": "#9b8c80",      # 정문 홀 안 벽 (그늘진 실내)
    "hall_c": "#5d524b",      # 정문 홀 천장
})
mk.GLOW.update({
    "sun_glass": "#ffe7c0",   # 노을 빛을 받은 창
    "spirit": "#fff3c4",      # 정령 빛 (단상 위 왕관 받침)
})

C = mk.City("epilogue_coronation")
EF = ef.city(C)                            # 에르피엔 군기 (깃발·현수막 공용 도안)
TREE = (0.0, 150.0)                        # 세계수 (에르피엔 한가운데)
ERP_H = 440.0                              # 세계수 높이
FAIRY_A = "characters/fairy_guard.glb"
FAIRY_B = "characters/fairy_guard_b.glb"
OFFICER = "characters/fairy_guard_officer.glb"
MUSKET = "weapons/fairy/fairy_guard_musket.glb"
CIV = "characters/_kit_base.glb"
SQ = {k: f"characters/squad_{k}.glb" for k in ("rona", "sabre", "jesty", "karen")}

DAIS = Vector((0.0, -1.0, 0.75))          # 단상 윗면 가운데 (에르핀이 무릎 꿇는 자리 근처, 네르는 남쪽 제단)
FY = 30.0                                  # 왕성 정면 벽
HX, HY, HZ = 2.2, FY + 3.6, 0.9 + 6.4      # 정문 홀: 반폭, 안쪽 벽, 천장
AISLE0, AISLE1 = DAIS.y + 4.4, FY - 2.2    # 융단 통로: 단 북쪽 끝 → 왕성 계단 아래
PLAT = (2.6, 6.8, 4.8, 8.6, 0.3)           # 귀빈석 (|x| 안·밖, y 남·북, 높이)
COL_X = -17.0                              # 회랑 기둥 줄
WALL_X = -21.0                             # 회랑 바깥 벽 안쪽 면
WALK_X = -18.9                             # 회랑 가운데 (걷는 길)
POST_X = -20.45                            # 바깥 벽 앞 초소
Y0, Y1 = -16.4, 28.0                       # 회랑 남·북 끝
COLS_Y = [-15.0 + 3.0 * k for k in range(15)]   # -15 .. 27
RITA = (POST_X, -1.5)


# ================================================================ 도형 도우미

def arch_pts(w, h, n=10):
    """아치 외곽선 (밑변 가운데가 원점, 위가 반원)."""
    r = w / 2
    pts = [(-r, 0.0), (r, 0.0)]
    for i in range(n + 1):
        a = math.pi * i / n
        pts.append((r * math.cos(a), h - r + r * math.sin(a)))
    pts.append((-r, 0.0))
    # 마지막 점은 첫 점과 같으니 뺀다
    return pts[:-1]


def ellipse(cx, cy, rx, ry, rot=0.0, n=14):
    c, s = math.cos(rot), math.sin(rot)
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def butterfly(C, center, size, normal, *, lift=0.012, up=(0, 0, 1), on_detail=False, sculpt=False):
    """요정 문장 = 에르피엔 군기의 나비 (lib/erpien_flag, 원작 도안: 노란 바탕 + 금 윤곽선 + 말린 선, 사용자 결정 2026-11-02).
    바닥·벽·아치의 문장은 emblem()(면에 그림), 지붕 꼭대기 조형은 앞뒤 대칭 badge(both, 두께 2 × lift).
    on_detail: 바탕 면이 detail 등급(융단·붉은 원·휘장)이면 나비 바탕도 강한 편향(fine)으로 (말린 선은 lift × 2.2)."""
    M = face_matrix(center, normal, up)
    if sculpt:
        ef.badge(ef.city(C), M, size, depth=lift, res=1, both=True)
    else:
        ef.emblem(ef.city(C), M, size, res=1, lift=lift, layers={"under": "fine"} if on_detail else None)


def face_matrix(p, normal, up=(0, 0, 1)):
    """로컬 (X = 면의 오른쪽, -Y = normal, Z = 위)를 p에 놓는 행렬 (erpien_flag 로컬 규약: 앞면 -Y)."""
    N = Vector(normal).normalized()
    R, U, _ = mk.frame(N, up)
    M = Matrix((R, -N, U)).transposed().to_4x4()
    M.translation = Vector(p)
    return M


def flag_banner(C, top, normal, w, h, *, pole=True, both=False, low=False):
    """세로 현수막 = 에르피엔 군기 (lib/erpien_flag.banner): 금 봉 + 초록 천 + 노란 나비 + 위 금 줄 + 아래 금 술.
    top = 봉 가운데(벽 면 위 점), normal = 바깥. both = 뒤에서도 보이는 자리(기둥에 건 현수막), low = 멀리 보는 자리."""
    ef.banner(EF, face_matrix(Vector(top) + Vector(normal).normalized() * 0.1, normal), W=w, H=h, rod=pole,
              both=both, low=low, strokes=not low)


def cone_roof(C, x, y, z0, r, h, *, key="roof_f", finial=True, pennant=False, kind="main"):
    C.cyl(key, (x, y, z0), (x, y, z0 + h), r, r2=0.04, segs=18, kind=kind)
    C.cyl("gold", (x, y, z0 - 0.02), (x, y, z0 + 0.18), r + 0.06, segs=18, kind="detail", cap=False)
    if finial:
        C.cyl("gold", (x, y, z0 + h - 0.1), (x, y, z0 + h + (1.6 if pennant else 0.9)), 0.05, segs=6, kind="detail")
        C.blob("gold", (x, y, z0 + h + 0.25), 0.16, segs=8, rings=5, kind="detail")
    if pennant:
        # 꼭지 깃대 끝의 작은 에르피엔 군기 (동쪽으로 날림, 앞면 남쪽)
        ef.far_flag(EF, Matrix.Translation((x, y, z0 + h + 1.55)), W=1.3, layers={"cloth": "detail"})


def tower(C, x, y, r, h, roof_h, *, windows=3, face=(0, -1), pennant=True, kind="main"):
    """둥근 탑: 흰 몸통 + 금 띠 + 아치 창 + 청록 원뿔 지붕."""
    C.cyl("marble_d", (x, y, 0), (x, y, 0.6), r + 0.2, segs=20, kind=kind)
    C.cyl("marble", (x, y, 0.6), (x, y, h), r, segs=20, kind=kind)
    C.cyl("gold", (x, y, h - 0.55), (x, y, h - 0.4), r + 0.05, segs=20, kind="detail", cap=False)
    C.cyl("marble_d", (x, y, h - 0.4), (x, y, h), r + 0.3, segs=20, kind=kind)
    a0 = math.atan2(face[1], face[0])
    for i in range(windows):
        a = a0 + (i - (windows - 1) / 2) * 0.75
        N = Vector((math.cos(a), math.sin(a), 0))
        for k, zz in enumerate((h * 0.35, h * 0.62)):
            c = Vector((x, y, zz)) + N * (r - 0.02)
            C.decal("gold", arch_pts(0.9, 1.6, 8), tuple(c), tuple(N), lift=0.02)
            C.decal("glass_d", arch_pts(0.7, 1.45, 8), tuple(c + Vector((0, 0, 0.07))), tuple(N), lift=0.03)
    cone_roof(C, x, y, h, r + 0.45, roof_h, pennant=pennant, kind=kind)


def blossom_tree(C, x, y, *, h=4.2, seed=0, z=0.0, scale=1.0):
    mk.tree(C, x, y, h=h, seed=seed, z=z, scale=scale, leaf=("blossom", "blossom_l", "blossom_d"))


def bunting(C, p0, p1, *, sag=0.9, n=16, keys=ef.BUNTING):
    """장식 깃발 줄: 늘어진 줄 + 삼각 깃발 (에르피엔 군기의 초록·노랑)."""
    P0, P1 = Vector(p0), Vector(p1)
    pts = []
    for i in range(n + 1):
        t = i / n
        p = P0.lerp(P1, t)
        p.z -= sag * 4 * t * (1 - t)
        pts.append(p)
    for i in range(n):
        C.cyl("dark", tuple(pts[i]), tuple(pts[i + 1]), 0.012, segs=4, kind="fine", smooth=False)
    d = (P1 - P0).normalized()
    nb = d.cross(Vector((0, 0, 1))).normalized() * 0.004
    for i in range(1, n):
        a, b = pts[i] - d * 0.2, pts[i] + d * 0.2
        tip = pts[i] + Vector((0, 0, -0.42))
        key = keys[i % len(keys)]
        # 앞뒤 면을 4 mm씩 띄운다: 같은 자리에 맞붙은 두 면은 외곽선 헐의 평균 법선이 0이 되어 헐이 천을 덮어 검게 보였다
        for sg, q in ((1, (a, b, tip)), (-1, (b, a, tip))):
            f = C.poly(key, [tuple(v + nb * sg) for v in q], kind="detail")
            f.normal_update()
            if f.normal.dot(nb * sg) < 0:
                f.normal_flip()


def house(C, x, y, w, d, h, *, roof="roof_f", wall="marble", seed=0, kind="far"):
    """에르피엔 시가지 집 (원경): 흰 벽 + 박공 지붕."""
    mk.lod_gable(C, wall, roof, x - w / 2, x + w / 2, y - d / 2, y + d / 2, 0.0, h, h + min(w, d) * 0.55,
                 axis="x" if w >= d else "y", kind=kind)


# ================================================================ 땅과 원경: 에르피엔 한가운데의 세계수, 밑동을 두른 왕궁, 둘레의 시가
# [원작] 왕국 한가운데 세계수를 모셨다. 왕궁 주변과 도시에 성곽이 있는 이중 성벽 (erpien_kit 머리말).
# 이 세트의 왕성 정문 홀·안뜰·남쪽 성문·퍼레이드 대로는 세계수 남쪽 왕궁 고리의 정면이고, 대로는 남쪽으로 뻗은 방사형 큰길이다.
#   세계수 TREE (0, 150): 밑동 반지름 약 35 m, 수관 밑 158 m, 꼭대기 440 m. 정문 홀 바로 뒤에서 솟는다
#   왕궁 고리 75~106 m(남쪽은 이 세트의 왕성), 안쪽 성벽 123 m, 시가 139~290 m, 바깥 성벽 317 m(남문 y -167)
C.group("land")
hgt = ek.ground(C, TREE[0], TREE[1], r_flat=ERP_H * 0.78, r_out=1500.0, amp=26.0, seed=4, z=-0.06)   # 판석(윗면 0)과 겹쳐 깜빡이지 않게 조금 낮춘다
C.group("worldtree", outline=0.55, bake=1)       # bake: 불러올 때 정점 색으로 합친다 (LevelLoader)
WT = ek.world_tree(C, TREE[0], TREE[1], 0.0, ERP_H, detail=1, kind="main", seed=8)


def near_set(x, y):
    """이 세트가 이미 지은 자리 (왕성·안뜰·회랑·성문·퍼레이드 대로와 그 끝)와 그 둘레 왕궁 정원: 왕국 키트가 비운다."""
    if -32.0 < x < 28.0 and -160.0 < y < 58.0:
        return True
    return -62.0 < x < 62.0 and -40.0 < y < 72.0


C.group("kingdom", outline=0.14, bake=1)
ERP = ek.kingdom(C, TREE[0], TREE[1], 0.0, ERP_H, hfun=hgt, face=(0.0, -1.0), kind="main", seed=11, skip=near_set,
                 palace_scale=0.5, density=1.0)
# 왕궁 정원 (안뜰 동서, 왕궁 고리 앞): 꽃나무와 둥근 나무 숲
C.group("palace_garden", bake=1)
rng = random.Random(33)
for i in range(46):
    sx = -1 if i % 2 else 1
    x = sx * rng.uniform(26.0, 58.0)
    y = rng.uniform(-30.0, 66.0)
    if math.hypot(x - TREE[0], y - TREE[1]) < ERP_H * 0.29:
        continue
    if sx < 0 and x > -34.0:
        continue                       # 서쪽 회랑 바깥 벽에 붙지 않게
    if i % 3:
        mk.tree(C, x, y, h=rng.uniform(6.0, 9.0), seed=300 + i, z=hgt(x, y) - 0.1, lod=1, kind="far")
    else:
        mk.tree(C, x, y, h=rng.uniform(5.0, 7.0), seed=300 + i, z=hgt(x, y) - 0.1, lod=1, kind="far",
                leaf=("blossom", "blossom_l", "blossom_d"))
C.group("far", bake=1)
mk.mountains(C, TREE[0], TREE[1], count=8, dist=1150, spread=80, h=(160, 300), seed=3, arc=(20, 170))
mk.mountains(C, TREE[0], TREE[1], count=6, dist=1200, spread=80, h=(140, 260), seed=11, arc=(190, 350))
for i, (x, y, z, s) in enumerate(((-420, 620, 280, 70), (380, 700, 320, 80), (640, 220, 250, 60),
                                  (-660, 120, 260, 64), (420, -380, 240, 60), (-460, -300, 230, 56))):
    mk.cloud(C, x, y, z, size=s, seed=i + 40)
C.group("woods", bake=1)
for i in range(11):
    a = 2 * math.pi * (i + 0.3) / 11
    d = 420.0 + (i % 3) * 60.0
    x, y = TREE[0] + math.cos(a) * d, TREE[1] + math.sin(a) * d
    mk.forest(C, x, y, r=34, n=9, seed=i + 61, hfun=hgt, hmin=7.0, hmax=11.0)

# ================================================================ 안뜰 바닥
C.group("court", bake=1, step="concrete")
mk.paving(C, -16.6, 16.6, -16.4, 29.0, key="pave", grout="pave_d", tile=1.8)
# 단상을 두른 장식 고리 (붉은 벽돌 톤 원)
C.ring("pave_r", hw.circle(6.0, 48, 0, DAIS.y), hw.circle(5.5, 48, 0, DAIS.y), (0, 0, 0.0), (0, 0, 1), lift=0.012)
# 붉은 융단: 왕성 계단 아래 → 단 북쪽 (입장 통로), 단 남쪽 → 성문 (퍼레이드가 나가는 길)
for ya, yb in ((AISLE0 - 0.4, AISLE1), (-18.6, DAIS.y - 4.4)):
    C.box("royal", -1.15, 1.15, ya, yb, 0.0, 0.025, kind="detail")
    for sx in (-1, 1):
        C.box("gold", sx * 1.15 - 0.08, sx * 1.15 + 0.08, ya - 0.01, yb + 0.01, 0.0, 0.03, kind="detail")   # 끝면을 융단과 어긋나게
for k in range(6):
    butterfly(C, (0, AISLE0 + 2.4 + k * 3.7, 0.025), 0.9, (0, 0, 1), lift=0.006, up=(0, -1, 0), on_detail=True)


def rope_line(x, y0, y1, step=2.4):
    """관람 경계: 금 기둥 + 늘어진 붉은 줄."""
    n = max(1, int(round(abs(y1 - y0) / step)))
    prev = None
    for i in range(n + 1):
        p = (x, y0 + (y1 - y0) * i / n, 0.0)
        C.cyl("gold", p, (p[0], p[1], 0.62), 0.035, segs=8, kind="detail")
        C.blob("gold", (p[0], p[1], 0.66), 0.05, segs=6, rings=4, kind="detail")
        if prev:
            mid = ((prev[0] + p[0]) / 2, (prev[1] + p[1]) / 2, 0.42)
            C.cyl("royal", (prev[0], prev[1], 0.58), mid, 0.018, segs=5, kind="detail", smooth=False)
            C.cyl("royal", mid, (p[0], p[1], 0.58), 0.018, segs=5, kind="detail", smooth=False)
        prev = p


# 통로 양쪽 관람 줄 (의장대 뒤, 앞줄 주민 앞)
for sx in (-1, 1):
    rope_line(sx * 2.75, PLAT[3] + 0.6, AISLE1 - 0.5)

# 귀빈석: 통로 머리 양쪽 낮은 단. 각 종족 수장이 선다 [오리지널 배치, 원작: 각 종족 지도자들이 대관식에 참석]
for sx in (-1, 1):
    xa, xb = sorted((sx * PLAT[0], sx * PLAT[1]))
    ya, yb, h = PLAT[2], PLAT[3], PLAT[4]
    C.box("marble_d", xa, xb, ya, yb, 0.0, h)
    C.col(xa, xb, ya, yb, 0.0, h)
    C.box("royal", xa + 0.1, xb - 0.1, ya + 0.1, yb - 0.1, h, h + 0.02, kind="detail")
    # 앞(남쪽)과 통로 쪽 면의 금 띠
    C.strip("gold", (xa, ya, h - 0.07), (xb, ya, h - 0.07), 0.05, normal=(0, -1, 0), lift=0.004)
    xi = sx * PLAT[0]
    C.strip("gold", (xi, ya, h - 0.07), (xi, yb, h - 0.07), 0.05, normal=(-sx, 0, 0), lift=0.004)
    # 뒤쪽 금 깃대 둘 (에르피엔 군기 현수막이 단상을 본다)
    for j, xx in enumerate((xa + 0.3, xb - 0.3)):
        C.cyl("gold", (xx, yb - 0.3, h), (xx, yb - 0.3, h + 3.2), 0.045, segs=8, kind="detail")
        C.blob("gold", (xx, yb - 0.3, h + 3.28), 0.09, segs=8, rings=5, kind="detail")
        flag_banner(C, (xx, yb - 0.36, h + 3.0), (0, -1, 0), 0.75, 1.9, pole=False, both=True)

# ================================================================ 단상 정자 (에르핀이 왕관을 받는 자리)
C.group("dais", bake=1, step="concrete")
cx, cy = DAIS.x, DAIS.y
for i, (r, z0, z1, key) in enumerate(((4.7, 0.0, 0.25, "marble_d"), (4.1, 0.25, 0.5, "marble"),
                                      (3.5, 0.5, 0.75, "marble"))):
    C.cyl(key, (cx, cy, z0), (cx, cy, z1), r, segs=40)
    C.cyl("gold", (cx, cy, z1 - 0.05), (cx, cy, z1 + 0.005), r + 0.02, segs=40, kind="detail", cap=False)
C.col(cx - 4.7, cx + 4.7, cy - 4.7, cy + 4.7, 0, 0.75)
# 단 윗면 붉은 원 + 에르피엔 나비
C.cyl("royal", (cx, cy, 0.75), (cx, cy, 0.77), 2.6, segs=36, kind="detail")
butterfly(C, (cx, cy + 0.2, 0.77), 1.6, (0, 0, 1), lift=0.006, up=(0, -1, 0), on_detail=True)
# 융단이 단 북쪽(통로 쪽)을 타고 올라간다 (단마다 얇은 판)
for (ya, yb, z) in ((cy + 4.1, cy + 4.75, 0.25), (cy + 3.5, cy + 4.15, 0.5), (cy + 2.4, cy + 3.55, 0.75)):
    C.box("royal", -1.15, 1.15, ya, yb, z - 0.01, z + 0.02, kind="detail")
# 기둥 6개 (각도 0, 60, 120, 180, 240, 300 → 남북(90, 270)이 열림)
PR = 3.05
TOP = 0.75 + 3.6
for i in range(6):
    a = math.radians(60 * i)
    px, py = cx + math.cos(a) * PR, cy + math.sin(a) * PR
    C.cyl("marble_d", (px, py, 0.75), (px, py, 0.95), 0.3, segs=12, kind="detail")
    C.cyl("marble", (px, py, 0.95), (px, py, TOP - 0.25), 0.17, segs=12)
    C.cyl("gold", (px, py, 1.15), (px, py, 1.25), 0.2, segs=12, kind="detail", cap=False)
    C.cyl("gold", (px, py, TOP - 0.25), (px, py, TOP), 0.2, r2=0.3, segs=12, kind="detail")
    # 기둥을 감는 꽃줄 (분홍 리본 나선 + 작은 꽃)
    prev = None
    for k in range(25):
        z = 1.3 + k * 0.11
        b = a + k * 0.55
        p = (px + math.cos(b) * 0.18, py + math.sin(b) * 0.18, z)
        if prev:
            C.cyl("rose_d", prev, p, 0.02, segs=5, kind="detail", smooth=False)
        if k % 4 == 2:
            C.blob(("blossom_l", "flower_y", "white")[(i + k) % 3], p, 0.045, segs=6, rings=4, kind="detail")
        prev = p
mk._bm_torus(C.bm("gold", "main"), (cx, cy, TOP + 0.08), PR, 0.16, seg=40, rseg=6)
C.cyl("marble", (cx, cy, TOP + 0.08), (cx, cy, TOP + 0.4), PR + 0.25, segs=40)
C.blob("rose", (cx, cy, TOP + 0.4), PR + 0.2, (1, 1, 0.52), segs=28, rings=10)
C.cyl("gold", (cx, cy, TOP + 0.36), (cx, cy, TOP + 0.48), PR + 0.32, segs=40, kind="detail", cap=False)
# 지붕 꼭대기: 에르피엔 나비 조형 (앞뒤 대칭)
top = Vector((cx, cy, TOP + 0.4 + (PR + 0.2) * 0.52))
C.cyl("gold", tuple(top), tuple(top + Vector((0, 0, 0.9))), 0.06, segs=8, kind="detail")
butterfly(C, tuple(top + Vector((0, 0.0, 1.25))), 1.1, (0, -1, 0), lift=0.02, sculpt=True)
# 지붕 가장자리에 늘어진 천 (붉은 띠, 금 술)
for i in range(18):
    a = 2 * math.pi * (i + 0.5) / 18
    p = Vector((cx + math.cos(a) * (PR + 0.3), cy + math.sin(a) * (PR + 0.3), TOP + 0.36))
    N = Vector((math.cos(a), math.sin(a), 0))
    C.plate("royal", [(-0.5, 0), (0.5, 0), (0.0, -0.45)], tuple(p), tuple(N), 0.02, kind="detail")
    C.blob("gold", tuple(p + Vector((0, 0, -0.5))), 0.05, segs=5, rings=3, kind="detail")
# 사제장(네르)이 서는 낮은 제단 단 (단 남쪽, 북쪽 통로를 본다): 무릎 꿇은 여왕에게 왕관을 씌울 수 있는 높이 (SD 체형은 팔이 짧다)
ALTAR = Vector((cx, cy - 1.0, 0.75 + 0.3))
C.cyl("marble", (cx, cy - 1.0, 0.75), (cx, cy - 1.0, ALTAR.z), 0.42, segs=28)
C.cyl("gold", (cx, cy - 1.0, ALTAR.z - 0.04), (cx, cy - 1.0, ALTAR.z + 0.005), 0.43, segs=28, kind="detail", cap=False)
C.cyl("royal", (cx, cy - 1.0, ALTAR.z), (cx, cy - 1.0, ALTAR.z + 0.012), 0.34, segs=28, kind="detail")
C.marker("MARK_crown", (cx, cy, 0.75 + 1.75))
C.marker("MARK_dais", (cx, cy, 0.75))
# 정자 뒤 양옆 큰 현수막 기둥 (통로에서 보면 단상을 감싼다)
for sx in (-1, 1):
    x = sx * 6.2
    C.cyl("gold", (x, cy - 1.0, 0), (x, cy - 1.0, 7.2), 0.09, segs=10, kind="detail")
    C.blob("gold", (x, cy - 1.0, 7.3), 0.2, segs=8, rings=5, kind="detail")
    flag_banner(C, (x, cy - 0.9, 6.9), (0, 1, 0), 1.5, 4.4, both=True)
    mk.flowers(C, x, cy - 1.0, r=0.9, n=12, seed=sx + 5, z=0.0)

# ================================================================ 왕성 (북쪽)
C.group("palace", bake=1, step="concrete")
C.box("marble_d", -18.0, 18.0, FY, 46.0, 0.0, 0.9)
# 몸체: 가운데 정문 홀(x ±HX, y FY..HY, 높이 0.9..HZ)을 비우고 둘러 쌓는다
C.box("marble", -16.0, -HX, FY, 44.0, 0.9, 10.0)
C.box("marble", HX, 16.0, FY, 44.0, 0.9, 10.0)
C.box("marble", -HX, HX, HY, 44.0, 0.9, 10.0)
C.box("marble", -HX, HX, FY, HY, HZ, 10.0)
C.box("gold", -16.05, 16.05, FY - 0.05, FY + 0.05, 9.0, 9.2, kind="detail")
C.box("marble_d", -16.4, 16.4, FY - 0.4, 44.4, 10.0, 10.5)
# 지붕 (박공): 앞뒤로 기운 판 두 장
for ye, ny in ((FY - 0.6, -1), (44.6, 1)):
    C.poly("roof_f", [(-16.6, ye, 10.5), (16.6, ye, 10.5), (16.6, 37.0, 15.5), (-16.6, 37.0, 15.5)],
           normal=(0, ny, 1.5), kind="main")
C.poly("roof_fd", [(-16.6, FY - 0.6, 10.5), (-16.6, 37.0, 15.5), (-16.6, 44.6, 10.5)], normal=(-1, 0, 0), kind="main")
C.poly("roof_fd", [(16.6, FY - 0.6, 10.5), (16.6, 44.6, 10.5), (16.6, 37.0, 15.5)], normal=(1, 0, 0), kind="main")
# 정면: 큰 정문 (열린 아치, 안은 정문 홀) + 창 두 줄 + 현수막
# 아치 윗부분(어깨)을 채우는 판: 홀 입구 안쪽 FY..FY+0.4. 아치 = 폭 2HX, 어깨 3.6, 꼭대기 3.6 + HX
SPRING = 3.6
SPAN = [(-HX, HZ - 0.9), (HX, HZ - 0.9)] + [(HX * math.cos(math.pi * i / 14), SPRING + HX * math.sin(math.pi * i / 14))
                                          for i in range(15)]
C.plate("marble", SPAN, (0, FY + 0.4, 0.9), (0, -1, 0), 0.4, kind="main")
# 아치 둘레: 짙은 돌 테 + 금 테 (정면에 붙인 띠)
C.ring("marble_d", arch_pts(2 * HX + 1.1, SPRING + HX + 0.55, 16), arch_pts(2 * HX, SPRING + HX, 16), (0, FY, 0.9),
       (0, -1, 0), lift=0.006)
C.ring("gold", arch_pts(2 * HX + 0.36, SPRING + HX + 0.18, 16), arch_pts(2 * HX + 0.12, SPRING + HX + 0.06, 16),
       (0, FY, 0.9), (0, -1, 0), lift=0.012)
butterfly(C, (0, FY, 0.9 + SPRING + HX + 1.25), 1.5, (0, -1, 0), lift=0.012)
# 정문 홀 안 (그늘진 실내로 보이게 짙은 벽·천장, 안쪽 벽의 붉은 휘장, 금 샹들리에와 벽등)
for sx in (-1, 1):
    xa, xb = sorted((sx * HX, sx * (HX - 0.02)))
    C.box("hall_w", xa, xb, FY + 0.4, HY, 0.9, HZ - 0.02, kind="detail")
    for yy in (FY + 1.3, FY + 2.9):
        C.box("gold", min(sx * (HX - 0.02), sx * (HX - 0.1)), max(sx * (HX - 0.02), sx * (HX - 0.1)), yy - 0.07,
              yy + 0.07, 3.5, 3.8, kind="detail")
        C.blob("lamp", (sx * (HX - 0.2), yy, 3.95), 0.12, (1, 1, 1.3), segs=8, rings=5, kind="detail")
C.box("hall_c", -HX, HX, FY + 0.4, HY, HZ - 0.02, HZ, kind="detail")
C.box("royal_d", -HX + 0.02, HX - 0.02, HY - 0.05, HY, 0.9, HZ - 0.02, kind="detail")
C.box("royal", -1.3, 1.3, HY - 0.08, HY - 0.05, 0.9, HZ - 0.5, kind="detail")
C.strip("gold", (-1.3, HY - 0.08, HZ - 0.5), (1.3, HY - 0.08, HZ - 0.5), 0.08, normal=(0, -1, 0), lift=0.004)
butterfly(C, (0, HY - 0.08, 4.2), 1.5, (0, -1, 0), lift=0.006, on_detail=True)
CH = Vector((0, FY + 1.9, HZ - 1.5))
C.cyl("gold", tuple(CH), (CH.x, CH.y, HZ - 0.02), 0.025, segs=6, kind="detail")
mk._bm_torus(C.bm("gold", "detail"), tuple(CH), 0.55, 0.035, seg=24, rseg=5)
for i in range(8):
    a = 2 * math.pi * i / 8
    C.blob("lamp", (CH.x + math.cos(a) * 0.55, CH.y + math.sin(a) * 0.55, CH.z + 0.1), 0.07, (1, 1, 1.4), segs=6,
           rings=4, kind="detail")
C.marker("MARK_portal", (0, FY + 0.45, 0.9), props={"halfWidth": HX, "height": SPRING + HX})
for x in (-13.0, -9.0, -5.0, 5.0, 9.0, 13.0):
    for z in (2.0, 6.0):
        C.decal("gold", arch_pts(1.4, 2.6, 10), (x, FY, z), (0, -1, 0), lift=0.02)
        C.decal("sun_glass" if z > 3 else "glass_d", arch_pts(1.15, 2.4, 10), (x, FY, z + 0.1), (0, -1, 0),
                lift=0.03)
for x in (-11.0, -7.0, 7.0, 11.0):
    flag_banner(C, (x, FY - 0.02, 9.0), (0, -1, 0), 1.3, 4.6)
# 가운데 큰 탑과 모서리 탑
tower(C, 0.0, 38.6, 4.2, 22.0, 10.0, windows=3)     # 정문 홀(y ..HY) 뒤
for sx in (-1, 1):
    tower(C, sx * 16.0, FY + 0.5, 2.7, 14.0, 6.5, windows=2, face=(0, -1))
    tower(C, sx * 16.0, 44.5, 2.4, 12.5, 5.5, windows=1, face=(sx, 0))
# 왕성 앞 계단: 나팔수가 서는 층계참(y FY-1.4..FY, 높이 0.9)과 두 단. 융단이 홀 안쪽 벽부터 계단을 타고 내려온다
for k, (y0, z) in enumerate(((FY - 1.4, 0.9), (FY - 1.8, 0.6), (FY - 2.2, 0.3))):
    y1 = FY if k == 0 else y0 + 0.4          # 단끼리 겹치지 않게 (옆면이 같은 평면이면 깜빡인다)
    C.box("marble_d", -5.0, 5.0, y0, y1, 0.0, z, kind="detail")
    C.box("royal", -1.15, 1.15, y0 - 0.012, y1, z - 0.01, z + 0.02, kind="detail")   # 단 앞 모서리를 덮는다
C.box("royal", -1.15, 1.15, FY, HY - 0.3, 0.89, 0.92, kind="detail")
C.col(-5.0, 5.0, FY - 2.2, FY, 0.0, 0.9)

# ================================================================ 성벽과 남쪽 성문
C.group("walls", bake=1)
WALL_H = 4.2


def merlons(x0, x1, y0, y1, z, *, axis="x", pitch=1.6):
    if axis == "x":
        n = max(1, int((x1 - x0) / pitch))
        for i in range(n):
            x = x0 + (i + 0.5) * (x1 - x0) / n
            C.box("marble", x - 0.4, x + 0.4, y0, y1, z, z + 0.55, kind="detail")
            C.blob("marble", (x, (y0 + y1) / 2, z + 0.55), 0.4, (1, (y1 - y0) / 0.8, 0.5), segs=8, rings=4,
                   kind="detail")
    else:
        n = max(1, int((y1 - y0) / pitch))
        for i in range(n):
            y = y0 + (i + 0.5) * (y1 - y0) / n
            C.box("marble", x0, x1, y - 0.4, y + 0.4, z, z + 0.55, kind="detail")
            C.blob("marble", ((x0 + x1) / 2, y, z + 0.55), 0.4, ((x1 - x0) / 0.8, 1, 0.5), segs=8, rings=4,
                   kind="detail")


# 동쪽 벽
C.box("marble", 16.6, 17.8, -17.6, 30.0, 0.0, WALL_H)
C.box("gold", 16.55, 16.6, -17.6, 30.0, WALL_H - 0.5, WALL_H - 0.38, kind="detail")
merlons(16.6, 17.8, -17.6, 30.0, WALL_H, axis="y")
for y in (-10.0, 0.0, 10.0, 20.0):
    flag_banner(C, (16.6, y, 3.8), (-1, 0, 0), 1.0, 2.8, low=True)
# 남쪽 성벽 (성문 아치 + 회랑 남쪽 출입구)
GY0, GY1 = -17.8, -16.6
C.box("marble", -21.6, -3.0, GY0, GY1, 0.0, WALL_H)
C.box("marble", 3.0, 17.8, GY0, GY1, 0.0, WALL_H)
C.box("marble", -3.0, 3.0, GY0, GY1, 5.4, 7.2)
GATE = ([(-3.0, 5.4), (3.0, 5.4), (3.0, 0.0), (2.2, 0.0)]
        + [(2.2 * math.cos(math.pi * i / 10), 3.2 + 2.2 * math.sin(math.pi * i / 10)) for i in range(11)]
        + [(-2.2, 0.0), (-3.0, 0.0)])
C.plate("marble", GATE, (0, GY1, 0), (0, -1, 0), GY1 - GY0, kind="main")
C.ring("gold", arch_pts(4.6, 5.6, 12), arch_pts(4.4, 5.5, 12), (0, GY0, 0.0), (0, -1, 0), lift=0.02)
C.ring("gold", arch_pts(4.6, 5.6, 12), arch_pts(4.4, 5.5, 12), (0, GY1, 0.0), (0, 1, 0), lift=0.02)
merlons(-21.6, 17.8, GY0, GY1, WALL_H, axis="x")
butterfly(C, (0, GY0, 6.3), 1.3, (0, -1, 0), lift=0.02)     # 아치 금테(5.6 m) 위로 꼬리가 뜬다
butterfly(C, (0, GY1, 6.3), 1.3, (0, 1, 0), lift=0.02)
for sx in (-1, 1):
    tower(C, sx * 4.4, -17.2, 1.9, 8.0, 4.2, windows=1, face=(0, -1))
# 성문 열린 문짝 (안쪽으로 젖혀 둠)
for sx in (-1, 1):
    C.rbox("wood_d", (sx * 2.25, -15.4, 2.4), (0.12, 2.2, 4.4), (0, 0, sx * 12))
    C.rbox("gold", (sx * 2.25 + sx * 0.07, -15.4, 2.4), (0.02, 1.6, 0.12), (0, 0, sx * 12), kind="detail")

# ================================================================ 서쪽 회랑 (행사장 외곽, 리타의 초소)
C.group("colonnade", bake=1, step="concrete")
C.box("marble_w", -21.6, -16.6, Y0, Y1, -0.3, 0.004)
for k in range(int((Y1 - Y0) / 1.5)):
    y = Y0 + k * 1.5
    C.strip("marble_d", (-21.0, y, 0.0), (-16.6, y, 0.0), 0.05, lift=0.006)
# 바닥 층: 대리석 판(0.004) → 줄눈(0.006) → 융단(0.009) → 금 테(0.012). 겹치는 띠끼리 같은 높이면 깜빡인다
C.strip("gold", (-16.75, Y0, 0.0), (-16.75, Y1, 0.0), 0.08, lift=0.009)
C.strip("royal", (-19.5, Y0, 0.0), (-19.5, Y1, 0.0), 1.2, lift=0.009)   # 회랑 가운데 붉은 띠 융단
C.strip("gold", (-20.12, Y0, 0.0), (-20.12, Y1, 0.0), 0.05, lift=0.012)
C.strip("gold", (-18.88, Y0, 0.0), (-18.88, Y1, 0.0), 0.05, lift=0.012)
# 바깥 벽 (바닥 판 윗면 0.004 위에서 시작: 바깥 옆면이 바닥 판 옆면과 겹치지 않게)
C.box("marble", -21.6, WALL_X, Y0, Y1, 0.004, 5.2)
C.box("marble_d", WALL_X, WALL_X + 0.12, Y0, Y1, 0.0, 0.35, kind="detail")
C.box("gold", WALL_X, WALL_X + 0.03, Y0, Y1, 3.25, 3.32, kind="detail")
for i, y in enumerate(COLS_Y[:-1]):
    yc = y + 1.5
    # 아치 창 (바깥 벽 안쪽 면)
    C.decal("gold", arch_pts(1.35, 2.5, 10), (WALL_X, yc, 0.75), (1, 0, 0), lift=0.02)
    C.decal("sun_glass", arch_pts(1.1, 2.32, 10), (WALL_X, yc, 0.84), (1, 0, 0), lift=0.03)
    C.strip("gold", (WALL_X + 0.035, yc, 0.84), (WALL_X + 0.035, yc, 2.6), 0.04, normal=(1, 0, 0), lift=0.0)
    C.box("marble_d", WALL_X, WALL_X + 0.22, yc - 0.75, yc + 0.75, 0.62, 0.75, kind="detail")
# 기둥 사이 벽면(기둥 맞은편)에 현수막
for i, y in enumerate(COLS_Y):
    if i % 2:
        flag_banner(C, (WALL_X, y, 4.4), (1, 0, 0), 0.9, 2.5)
    else:
        # 벽등 (금 받침 + 크림 갓)
        C.box("gold", WALL_X, WALL_X + 0.1, y - 0.08, y + 0.08, 2.9, 3.2, kind="detail")
        C.blob("lamp", (WALL_X + 0.2, y, 3.3), 0.13, (1, 1, 1.3), segs=8, rings=5, kind="detail")
# 기둥 줄 (안뜰 쪽)
for y in COLS_Y:
    C.box("marble_d", COL_X - 0.36, COL_X + 0.36, y - 0.36, y + 0.36, 0.0, 0.28, kind="detail")
    C.cyl("marble", (COL_X, y, 0.28), (COL_X, y, 3.3), 0.24, r2=0.21, segs=12)
    C.cyl("gold", (COL_X, y, 0.36), (COL_X, y, 0.46), 0.27, segs=12, kind="detail", cap=False)
    C.cyl("gold", (COL_X, y, 3.2), (COL_X, y, 3.45), 0.24, r2=0.34, segs=12, kind="detail")
    C.box("marble_d", COL_X - 0.4, COL_X + 0.4, y - 0.4, y + 0.4, 3.45, 3.6, kind="detail")
    C.col(COL_X - 0.25, COL_X + 0.25, y - 0.25, y + 0.25, 0, 3.6)
# 아치 (기둥 사이 위쪽 벽: 안뜰 쪽과 회랑 쪽 두 면)
for y in COLS_Y[:-1]:
    ya, yb = y + 0.28, y + 3.0 - 0.28
    w = yb - ya
    zs, rise = 2.35, 0.95
    pts = [(-w / 2, 1.25)]
    pts.append((-w / 2, 0.0))
    for i in range(1, 12):
        a = math.pi * (1 - i / 12)
        pts.append(((w / 2) * math.cos(a), rise * math.sin(a)))
    pts.append((w / 2, 0.0))
    pts.append((w / 2, 1.25))
    C.plate("marble", pts, (COL_X - 0.3, (ya + yb) / 2, zs), (1, 0, 0), 0.6, kind="main")
    C.strip("gold", (COL_X + 0.305, ya, zs + rise + 0.18), (COL_X + 0.305, yb, zs + rise + 0.18), 0.06,
            normal=(1, 0, 0), lift=0.0)
# 들보·천장·지붕
C.box("marble", COL_X - 0.42, COL_X + 0.42, Y0, Y1, 3.6, 4.25)
C.box("gold", COL_X + 0.42, COL_X + 0.45, Y0, Y1, 3.95, 4.05, kind="detail")
C.box("marble_d", WALL_X, COL_X - 0.42, Y0, Y1, 4.05, 4.25)
for y in COLS_Y:
    C.box("marble_d", WALL_X, COL_X - 0.42, y - 0.12, y + 0.12, 3.82, 4.05, kind="detail")
C.rbox("roof_f", (-19.05, (Y0 + Y1) / 2, 4.75), (5.6, Y1 - Y0 + 0.6, 0.22), (0, 10.5, 0))
C.box("roof_fd", -16.4, -16.2, Y0, Y1, 4.0, 4.3, kind="detail")
# 회랑 남·북 끝벽
C.box("marble", -21.6, COL_X - 0.4, Y1, Y1 + 0.6, 0.0, 5.2)
C.plate("wood_d", arch_pts(1.6, 2.4, 10), (WALK_X, Y1 - 0.02, 0.0), (0, -1, 0), 0.05, kind="detail")
C.ring("gold", arch_pts(1.8, 2.55, 10), arch_pts(1.6, 2.4, 10), (WALK_X, Y1 - 0.07, 0.0), (0, -1, 0), lift=0.004)

# ================================================================ 안뜰 꾸밈: 꽃나무, 화단, 가로등, 깃발 줄
C.group("garden", bake=1)
for k, y in enumerate((-12.0, -5.0, 2.0, 9.0, 16.0, 23.0)):
    for sx in (-1, 1):
        x = sx * 14.2 if sx > 0 else -14.6
        if sx < 0 and y in (-5.0, 2.0, 16.0, 23.0):
            continue          # 서쪽: 리타 초소 앞(기둥 사이 시야)과 북쪽 망원 시야를 비운다
        mk.planter(C, x - 1.1, x + 1.1, y - 1.1, y + 1.1, h=0.45, hedge=False)
        blossom_tree(C, x, y, h=4.4, seed=k * 3 + sx + 7, z=0.45)
        mk.flowers(C, x, y, r=0.9, n=8, seed=k + sx * 13, z=0.47)
# 가로등은 단 남쪽 융단(퍼레이드가 나가는 길) 양옆에만 (통로·단상 시야를 막지 않게)
for y in (-14.0, -9.5):
    for sx in (-1, 1):
        mk.lamp(C, sx * 2.6, y, h=3.2)
# 깃발 줄: 성문 안쪽 하나, 입장 통로 위를 가로지르는 셋
for y in (-12.0, 12.5, 18.5, 24.5):
    bunting(C, (COL_X + 0.4, y, 4.1), (16.6, y, 4.0), sag=1.2, n=26)
# 뒤쪽 군중은 epilogue.ts가 런타임에 만든다 (cinematic/crowd.ts: 실제 주민 모델 인스턴싱, 환호·손 흔들기·박수·깃발·만세)

# ================================================================ NPC
# 컷 이름 묶음 (NPC 마커 scene 속성): 안뜰 컷 / 퍼레이드 컷
COURT = "ep_a,ep_b,ep_c,co_a,co_b,co_c,co_d,co_e,co_f,co_g,co_m,co_h"
CORO = "co_a,co_b,co_c,co_d,co_e,co_f,co_g,co_m,co_h"
PARADE = "pr_a,pr_b,pr_c,pr_d,pr_e,pr_log"

# 대관식 [오리지널 연출, 원작: 에르핀은 모두의 환호와 각 종족 수장들 앞에서 네르에게서 왕관을 다시 받는다]
#   에르핀: 왕성 정문 홀에서 나와(문이 열린다) 계단을 내려와 융단 통로를 걸어 단 북쪽으로 오른다 → 남쪽(네르)을 보고 무릎 꿇음
#          → 왕관 → 일어나 북쪽(통로의 백성)으로 돈다
#   네르(대관식 복장): 단 남쪽 낮은 제단(ALTAR) 위에서 북쪽을 본다. ner.glb(엘다인 각성 판)는 M9 전용
#   폴랑(경비대장): 왕관 방석을 받쳐 들고 에르핀 뒤를 따라 나와, 네르 곁에서 방석을 내민다. 뒤에 만세삼창을 이끈다 [오리지널]
C.group("npc_dais")
C.npc("erpin", (0.0, FY + 2.2, 0.9), "characters/erpin_royal.glb", pose="attention", face=(0.0, 0.0), name="에르핀",
      props={"expr": "regal", "scene": COURT})
C.npc("ner", tuple(ALTAR), "characters/ner_coronation.glb", pose="attention", face=(ALTAR.x, ALTAR.y + 10), name="네르",
      props={"fallback": "characters/_kit_base.glb", "scene": COURT})
C.npc("polan", (0.0, FY + 3.4, 0.9), "characters/polan.glb", pose="carry_box", face=(0.0, 0.0), name="폴랑",
      props={"expr": "serious", "scene": COURT})
C.npc("officer", (2.35, AISLE1 - 1.0, 0.0), OFFICER, pose="hold_rifle_ready", face=(2.35, 0.0), name="요정 경비대 지휘관",
      props={"hold_R": MUSKET, "scene": COURT})
# 정문 계단 층계참의 나팔수 둘 (나팔은 런타임 소품)
for sx in (-1, 1):
    C.npc(f"herald_{'L' if sx < 0 else 'R'}", (sx * 3.7, FY - 0.75, 0.9), FAIRY_B if sx < 0 else FAIRY_A, pose="attention",
          face=(sx * 3.7, 0.0), name="요정 경비대 나팔수", props={"scene": COURT})
# 행렬 경로: 정문 홀 → 층계참 → 두 단 → 융단 통로 → 단 북쪽 세 층 → 무릎 꿇을 자리 앞
for i, (y, z) in enumerate(((FY + 2.2, 0.9), (FY - 1.3, 0.9), (FY - 1.6, 0.6), (FY - 2.0, 0.3), (FY - 2.45, 0.0),
                            (DAIS.y + 4.95, 0.0), (DAIS.y + 4.4, 0.25), (DAIS.y + 3.8, 0.5), (DAIS.y + 3.1, 0.75),
                            (DAIS.y + 0.65, 0.75))):
    C.marker(f"WP_procession_{i + 1:02d}", (0.0, y, z))
# 융단을 따라 선 의장대 (서로 마주 본다)
C.group("npc_honor")
for k, y in enumerate((PLAT[3] + 1.9, PLAT[3] + 5.3, PLAT[3] + 8.7, PLAT[3] + 12.1, PLAT[3] + 15.5)):
    for sx in (-1, 1):
        C.npc(f"honor_{k + 1:02d}{'L' if sx < 0 else 'R'}", (sx * 1.9, y, 0.0), FAIRY_A if (k + (sx > 0)) % 2 else FAIRY_B,
              pose="hold_rifle_ready", face=(0.0, y), name="요정 경비대", props={"hold_R": MUSKET, "scene": COURT})

# 귀빈석의 각 종족 수장 (2026-11-02 사용자 확정 명단). 단 위(높이 PLAT[4] + 0.02)에서 단상 쪽을 본다
#   서쪽: 엘레나(엘프, 모나티엄 시장)와 비서 아멜리아, 벨리타(마녀), 실라(정령)
#   동쪽: 디아나(수인), 다야(용족), 셰이디(유령). 뒷줄에 후원자 골디(서)·클로에(동)
# 모델이 아직 없으면 fallback(키트 기본 인물)으로 서고 epilogue.ts가 'PLACEHOLDER' 표찰을 단다
C.group("npc_leaders")
LZ = PLAT[4] + 0.02
LEAD_FACE = (0.0, DAIS.y + 3.0)
C.npc("elena_front", (-3.3, PLAT[2] + 1.0, LZ), "characters/elena.glb", pose="attention", face=LEAD_FACE, name="엘레나",
      props={"scene": CORO})
C.npc("amelia_front", (-3.55, PLAT[2] + 2.25, LZ), "characters/amelia.glb", pose="attention", face=LEAD_FACE,
      name="아멜리아", props={"scene": CORO})
for nid, x, dy, model, name in (("belita", -4.55, 0.85, "characters/belita.glb", "벨리타"),
                                ("sila", -5.85, 0.75, "characters/sila.glb", "실라"),
                                ("diana", 3.3, 1.0, "characters/diana.glb", "디아나"),
                                ("daya", 4.55, 0.85, "characters/daya.glb", "다야"),
                                ("shady", 5.85, 0.75, "characters/shady.glb", "셰이디")):
    C.npc(nid, (x, PLAT[2] + dy, LZ), model, pose="attention", face=LEAD_FACE, name=name,
          props={"fallback": CIV, "scene": COURT})
# 대관식 후원자 (원작: 에르피엔 소상공회의 골디·클로에가 대관식을 후원했다). 귀빈석 뒷줄
for nid, x, model, name in (("goldie", -5.4, "characters/goldie.glb", "골디"), ("chloe", 5.4, "characters/chloe.glb", "클로에")):
    C.npc(nid, (x, PLAT[2] + 2.2, LZ), model, pose="attention", face=LEAD_FACE, name=name,
          props={"fallback": CIV, "scene": COURT})

# 관람 줄 뒤 앞줄 주민 (요정 왕국 주민·엘프·수인, 군중 키트 crowd_*.glb, g·h는 아이). 그 뒤는 런타임 군중
# (cinematic/crowd.ts: 같은 주민 모델 인스턴싱, 가까운 사람은 본 모델·먼 사람은 crowd_lod)
C.group("npc_crowd")
CROWD_KIT = ["fairy_a", "fairy_g", "fairy_b", "elf_a", "fairy_c", "beast_b", "fairy_d", "elf_b", "fairy_e",
             "beast_c", "fairy_h", "elf_g", "beast_d", "fairy_b", "elf_d", "beast_e", "fairy_e", "beast_g"]
rng = random.Random(9)
k = 0
for side in (-1, 1):
    for row in range(9):
        y = PLAT[3] + 1.6 + row * 1.85 + rng.uniform(-0.2, 0.2)
        x = side * (3.3 + rng.uniform(-0.1, 0.15))
        kit = CROWD_KIT[k % len(CROWD_KIT)]
        pose = ("wave", "clap", "attention", "cheer", "clap", "attention", "wave")[(k * 3 + row) % 7]
        C.npc(f"front_{k + 1:02d}", (x, y, 0.0), f"characters/crowd_{kit}.glb", pose=pose,
              face=(0.0, y - 2.5), name="주민", props={"fallback": CIV, "scene": COURT})
        k += 1
# 모나티엄 대표단 경호 (특수작전부): 서쪽 회랑의 초소들 (대관식 동안은 행사장 외곽에 그대로)
C.group("npc_posts")
C.npc("rita", (RITA[0], RITA[1], 0.0), "characters/rita.glb", pose="at_ease", face=(RITA[0] + 5, RITA[1]),
      name="리타", props={"expr": "serious", "scene": COURT})
C.npc("sabre", (POST_X, -13.5, 0.0), SQ["sabre"], pose="at_ease", face=(POST_X + 5, -13.5), name="사브르",
      props={"scene": COURT})
C.npc("fairy_post", (POST_X, -7.5, 0.0), FAIRY_A, pose="hold_rifle_ready", face=(POST_X + 5, -7.5), name="요정 경비대",
      props={"hold_R": MUSKET, "scene": COURT})
C.npc("jesty", (POST_X, 13.5, 0.0), SQ["jesty"], pose="at_ease", face=(POST_X + 5, 13.5), name="제스티",
      props={"scene": COURT})
# 회랑을 지나가는 엘레나와 아멜리아 (ep_c): 남쪽 출입구 밖에서 걸어 들어온다. 걷는 길은 WP_
C.npc("elena", (WALK_X + 0.15, -19.4, 0.0), "characters/elena.glb", pose="walk", face=(WALK_X, 0), name="엘레나",
      props={"scene": "ep_c"})
C.npc("amelia", (WALK_X - 0.2, -18.0, 0.0), "characters/amelia.glb", pose="walk", face=(WALK_X, 0), name="아멜리아",
      props={"scene": "ep_c"})
for i, y in enumerate((-19.4, -16.0, -6.0, 0.0, 6.0, 14.0, 26.5)):
    C.marker(f"WP_elena_walk_{i + 1:02d}", (WALK_X + 0.15, y, 0.0))
for i, y in enumerate((-18.0, -15.0, -5.0, 1.0, 7.0, 15.0, 26.5)):
    C.marker(f"WP_amelia_walk_{i + 1:02d}", (WALK_X - 0.2, y, 0.0))

# ================================================================ 퍼레이드 대로 (성문 남쪽) [오리지널]
# 성문(y -17)에서 남쪽으로 곧은 대로. 차도 x -6..6, 보도 6..9.5, 양쪽 흰 벽 상가(박공이 길을 본다), 길을 가로지르는 깃발 줄,
# 금 기둥과 붉은 줄의 관람 경계, 가로등 깃발, 끝의 개선문(y -118). 특수작전부 경계 초소는 동쪽 보도 y -100.
C.group("boulevard", bake=1, step="concrete")
BY0, BY1 = -18.6, -134.0
mk.paving(C, -6.0, 6.0, BY1, BY0, key="pave", grout="pave_d", tile=1.4)
for sx in (-1, 1):
    x0, x1 = sorted((sx * 6.0, sx * 9.6))
    mk.paving(C, x0, x1, BY1, BY0, key="pave_r", grout="pave_d", tile=1.2)
    C.strip("gold", (sx * 6.0, BY0, 0.0), (sx * 6.0, BY1, 0.0), 0.08, lift=0.008)
# 가운데 꽃잎 띠 (분홍 데칼 점선)
for k in range(int((BY0 - BY1) / 3.0)):
    y = BY0 - 1.5 - k * 3.0
    C.decal("blossom_l", ellipse(0, 0, 0.5, 0.3, 0, 10), (0.0, y, 0.0), (0, 0, 1), up=(0, 1, 0), lift=0.013)  # 줄눈(0.01) 위
# 양쪽 상가
rng = random.Random(77)
y = BY0 - 0.6
bi = 0
while y > BY1 + 4:
    w = rng.uniform(7.0, 9.5)
    for sx in (-1, 1):
        floors = rng.choice((2, 2, 3))
        h = 2.9 * floors + 0.4
        xa, xb = sorted((sx * 9.6, sx * 16.5))
        wall = ("marble", "cream", "marble", "warm")[(bi + (sx > 0)) % 4]
        roof = ("roof_f", "royal_d", "roof_fd", "rose_d")[(bi * 3 + (sx > 0)) % 4]
        mk.lod_gable(C, wall, roof, xa, xb, y - w + 0.15, y - 0.15, 0.0, h, h + 2.6, axis="x", kind="main")
        C.col(xa, xb, y - w + 0.15, y - 0.15, 0.0, h)
        N = (-sx, 0, 0)
        fx = sx * 9.6
        yc = y - w / 2
        # 문 (1층 가운데) + 창 (층마다 둘) + 금 띠
        C.plate("wood_d", arch_pts(1.3, 2.1, 10), (fx, yc, 0.0), N, 0.05, up=(0, 0, 1), kind="detail")
        C.ring("gold", arch_pts(1.5, 2.25, 10), arch_pts(1.3, 2.1, 10), (fx - sx * 0.05, yc, 0.0), N, lift=0.004)
        for f in range(floors):
            z = 0.9 + f * 2.9 + (0.0 if f else 0.0)
            for dy in ((-2.3, 2.3) if f else (-2.6, 2.6)):
                C.decal("gold", arch_pts(1.0, 1.7, 8), (fx, yc + dy, z + (0.2 if f else 0.4)), N, lift=0.02)
                C.decal("sun_glass" if (bi + f) % 2 else "glass_d", arch_pts(0.82, 1.55, 8),
                        (fx, yc + dy, z + (0.27 if f else 0.47)), N, lift=0.03)
            C.box("gold", min(fx, fx - sx * 0.04), max(fx, fx - sx * 0.04), y - w + 0.2, y - 0.2, z + 2.55, z + 2.65,
                  kind="detail")
        # 2층 발코니 + 꽃 상자
        bz = 2.9 + 0.1
        C.box("marble_d", min(fx, fx - sx * 0.7), max(fx, fx - sx * 0.7), yc - 1.3, yc + 1.3, bz - 0.12, bz, kind="detail")
        C.box("gold", min(fx - sx * 0.66, fx - sx * 0.7), max(fx - sx * 0.66, fx - sx * 0.7), yc - 1.3, yc + 1.3, bz,
              bz + 0.55, kind="detail")
        mk.flowers(C, fx - sx * 0.45, yc, r=0.9, n=10, seed=bi * 7 + (sx > 0), z=bz)
        # 현수막 (건물 둘에 하나)
        if (bi + (sx > 0)) % 2 == 0:
            flag_banner(C, (fx, yc + (w / 2 - 1.2) * (1 if sx > 0 else -1), h - 0.3), N, 1.0, 3.0, low=True)
    y -= w
    bi += 1
# 길을 가로지르는 깃발 줄, 관람 경계(금 기둥 + 붉은 줄), 가로등
for k in range(12):
    yy = BY0 - 6.0 - k * 9.5
    if yy < BY1 + 6:
        break
    bunting(C, (-9.6, yy, 5.4), (9.6, yy, 5.4), sag=0.9, n=22)
    bunting(C, (-9.6, yy - 3.0, 4.6), (9.6, yy + 3.0, 4.6), sag=0.7, n=22, keys=ef.BUNTING[::-1])
for sx in (-1, 1):
    prev = None
    yy = BY0 - 2.0
    while yy > BY1 + 4:
        p = (sx * 6.25, yy, 0.0)
        C.cyl("gold", p, (p[0], p[1], 0.62), 0.035, segs=8, kind="detail")
        C.blob("gold", (p[0], p[1], 0.66), 0.05, segs=6, rings=4, kind="detail")
        if prev:
            mid = ((prev[0] + p[0]) / 2, (prev[1] + p[1]) / 2, 0.42)
            C.cyl("royal", (prev[0], prev[1], 0.58), mid, 0.018, segs=5, kind="detail", smooth=False)
            C.cyl("royal", mid, (p[0], p[1], 0.58), 0.018, segs=5, kind="detail", smooth=False)
        prev = p
        yy -= 2.5
    for k in range(12):
        yy = BY0 - 4.0 - k * 9.5
        if yy < BY1 + 4:
            break
        mk.lamp(C, sx * 6.6, yy, h=3.4)
        # 가로등 기둥의 작은 에르피엔 군기 (차도 쪽으로)
        ef.far_flag(EF, Matrix.Translation((sx * 6.6, yy, 3.05)) @ Matrix.Rotation(math.pi if sx > 0 else 0.0, 4, "Z"),
                    W=0.62, layers={"cloth": "detail"})
# 개선문 (차가 지나가는 큰 아치) y -118
AY = -118.0
C.box("marble", -9.6, -3.6, AY - 1.2, AY + 1.2, 0.0, 7.6)
C.box("marble", 3.6, 9.6, AY - 1.2, AY + 1.2, 0.0, 7.6)
C.box("marble", -3.6, 3.6, AY - 1.2, AY + 1.2, 6.0, 7.6)
C.plate("marble", [(-3.6, 6.0), (3.6, 6.0), (3.6, 4.2)] + [(3.6 * math.cos(math.pi * i / 12), 4.2 + 1.8 * math.sin(math.pi * i / 12)) for i in range(13)] + [(-3.6, 4.2)],
        (0, AY + 1.2, 0.0), (0, -1, 0), 2.4, kind="main")
C.box("marble_d", -10.0, 10.0, AY - 1.4, AY + 1.4, 7.6, 8.2)
C.box("gold", -10.05, 10.05, AY - 1.45, AY + 1.45, 7.45, 7.55, kind="detail")
for ny in (-1, 1):
    butterfly(C, (0, AY + ny * 1.21, 6.75), 1.35, (0, ny, 0), lift=0.02)     # 아치 꼭대기(6.0)와 금 띠(7.45) 사이
    for sx in (-1, 1):
        flag_banner(C, (sx * 6.6, AY + ny * 1.21, 7.2), (0, ny, 0), 1.4, 4.2, low=True)
C.col(-9.6, -3.6, AY - 1.2, AY + 1.2, 0.0, 7.6)
C.col(3.6, 9.6, AY - 1.2, AY + 1.2, 0.0, 7.6)
# 대로 끝 광장 너머 (왕성으로 돌아오는 길의 원경 집들)
for i in range(8):
    x = -24 + i * 7.0
    house(C, x, -142.0 - (i % 3) * 3.0, 6.5, 6.0, 4.5 + (i % 2) * 1.5, roof=("roof_f", "royal_d", "rose_d")[i % 3], seed=i)

# 퍼레이드 인물 (차에 태우고 행진시키는 것은 epilogue.ts)
C.group("npc_parade")
PR_Y = -40.0
C.npc("erpin_car", (0.0, PR_Y, 0.0), "characters/erpin_royal.glb", pose="wave", face=(0.0, PR_Y - 10), name="에르핀",
      props={"expr": "cheer", "scene": PARADE})
C.npc("ner_car", (0.6, PR_Y, 0.0), "characters/ner_coronation.glb", pose="attention", face=(0.6, PR_Y - 10),
      name="네르", props={"fallback": "characters/_kit_base.glb", "scene": PARADE})
C.npc("elena_car", (0.0, PR_Y + 9, 0.0), "characters/elena.glb", pose="wave", face=(0.0, PR_Y), name="엘레나",
      props={"expr": "smile", "scene": PARADE})
C.npc("amelia_car", (0.6, PR_Y + 9, 0.0), "characters/amelia.glb", pose="attention", face=(0.6, PR_Y), name="아멜리아",
      props={"scene": PARADE})
C.npc("driver_1", (0.0, PR_Y - 1.5, 0.0), OFFICER, pose="sit", face=(0.0, PR_Y - 10), name="요정 경비대",
      props={"scene": PARADE})
C.npc("driver_2", (0.0, PR_Y + 7.5, 0.0), FAIRY_B, pose="sit", face=(0.0, PR_Y), name="요정 경비대",
      props={"scene": PARADE})
# 차 앞에서 행진하는 요정 경비대 (두 줄 넷)
for i in range(8):
    sx = -1 if i % 2 == 0 else 1
    yy = -24.0 - (i // 2) * 2.0
    C.npc(f"escort_{i + 1:02d}", (sx * 1.25, yy, 0.0), FAIRY_A if (i // 2) % 2 else FAIRY_B, pose="hold_rifle_ready",
          face=(sx * 1.25, yy - 10), name="요정 경비대", props={"hold_R": MUSKET, "scene": PARADE})
# 특수작전부 경계 초소 (동쪽 보도, 길을 본다). 리타는 그중 하나
POST_Y = -100.0
for i, (nid, model) in enumerate((("jesty_post", SQ["jesty"]), ("sabre_post", SQ["sabre"]), ("rita_post", "characters/rita.glb"),
                                   ("rona_post", SQ["rona"]), ("karen_post", SQ["karen"]))):
    yy = POST_Y + 4.4 - i * 2.2
    C.npc(nid, (6.75, yy, 0.0), model, pose="attention", face=(0.0, yy), name=nid.split("_")[0],
          props={"scene": PARADE})
C.npc("fairy_post2", (-6.75, POST_Y, 0.0), FAIRY_A, pose="hold_rifle_ready", face=(0.0, POST_Y), name="요정 경비대",
      props={"hold_R": MUSKET, "scene": PARADE})
# 길가 관람객 (군중 시점 컷 pr_c의 어깨 너머 앞쪽): 서쪽 보도 y -61. 주민 모델(군중 키트), 맨 앞은 아이
for i, (dx, dy, pose, kit) in enumerate(((-7.0, -59.6, "cheer", "fairy_a"), (-7.3, -60.8, "wave", "beast_c"),
                                         (-6.95, -62.1, "clap", "fairy_g"), (-8.2, -60.2, "cheer", "elf_b"),
                                         (-8.4, -61.6, "wave", "fairy_e"))):
    C.npc(f"pov_civ_{i + 1}", (dx, dy, 0.0), f"characters/crowd_{kit}.glb", pose=pose, face=(0.0, dy),
          name="주민", props={"fallback": CIV, "scene": PARADE})

# ================================================================ 카메라
C.group("cams")
# ep_a 전경: 남쪽 하늘 높은 곳에서 에르피엔 전체(가운데 세계수, 밑동을 두른 왕궁, 둘레의 시가 고리) → 퍼레이드 대로 위로
#      내려와 왕성 안뜰 → 회랑 쪽으로 내려와 기둥 사이로 초소의 리타
C.cam("ep_a", [
    (0.0, (0.0, -640.0, 260.0), (0.0, TREE[1], 215.0), 40),
    (5.0, (22.0, -120.0, 46.0), (-1.0, 40.0, 30.0), 46),
    (8.5, (-9.5, -24.0, 9.5), (-12.0, 2.0, 2.0), 44),
    (12.0, (-13.6, -3.4, 1.9), (-20.3, -1.5, 0.85), 28),
])
# ep_b 초소의 리타: 회랑 안, 리타 앞 비스듬히 (얼굴과 뒤쪽 창·현수막)
C.cam("ep_b", [
    (0.0, (-18.0, 1.6, 1.05), (RITA[0], RITA[1], 0.88), 36),
    (8.0, (-18.3, 0.8, 0.98), (RITA[0], RITA[1], 0.9), 32),
])
# ep_c 회랑: 리타 북쪽 어깨 옆에서 남쪽을 본다. 엘레나·아멜리아가 멀리서 걸어온다
C.cam("ep_c", [
    (0.0, (-20.05, 1.6, 1.12), (WALK_X, -14.0, 0.75), 42),
    (10.0, (-20.0, 1.3, 1.1), (WALK_X, -10.0, 0.8), 40),
])
# co_a 정문 입장: 단상 북쪽 위에서 왕성 바로 뒤로 솟은 세계수(줄기와 수관)를 올려다보다가, 나팔과 함께 정문으로 내려온다.
#      문이 열리고 에르핀이 홀에서 나온다 (내려오며 다가간다)
C.cam("co_a", [
    (0.0, (2.2, 3.4, 8.6), (0.0, TREE[1], 130.0), 52),
    (2.3, (2.0, 4.0, 7.8), (0.0, FY - 0.5, 3.4), 40),
    (7.5, (1.1, 7.2, 5.0), (0.0, FY - 1.5, 2.2), 34),
])
# co_g 셋째 만세: 통로 머리(단 북쪽 층계 아래)에서 통로 전체와 왕성. 선창하는 폴랑의 등, 두 팔을 든 백성과 의장대.
#      예포와 함께 왕성 뒤 세계수까지 천천히 올려다본다 (4초 컷)
C.cam("co_g", [
    (0.0, (-0.95, DAIS.y + 3.6, 1.55), (0.6, 16.0, 3.2), 50),
    (1.4, (-0.95, DAIS.y + 3.65, 1.58), (0.6, 18.0, 4.6), 50),
    (4.0, (-0.9, DAIS.y + 3.8, 1.7), (0.0, TREE[1], 72.0), 56),
])
# co_h 단 위의 에르핀 (통로 머리 낮은 곳에서 올려다본다): 네르의 선포, 에르핀의 한마디
C.cam("co_h", [
    (0.0, (-1.2, DAIS.y + 6.6, 1.3), (DAIS.x, DAIS.y + 1.25, 1.62), 24),
    (8.0, (-0.95, DAIS.y + 6.0, 1.34), (DAIS.x, DAIS.y + 1.25, 1.74), 20),
])
# pr_a 대로 위 크레인: 행렬 앞(남쪽)에서 북쪽을 본다. 성문을 빠져나오는 행렬, 그 뒤로 왕성과 세계수 (세계수에서 뻗어 나온 큰길)
C.cam("pr_a", [
    (0.0, (2.6, -47.0, 4.6), (0.0, -16.0, 9.5), 54),
    (7.0, (2.2, -53.0, 4.2), (0.0, -20.0, 11.0), 54),
])
# pr_d 대로 위 높은 크레인: 행렬 앞쪽에서 대로를 거슬러 본다. 호위, 두 차, 양쪽 군중, 깃발 줄, 끝에 왕성과 세계수
C.cam("pr_d", [
    (0.0, (-3.0, -106.0, 10.5), (0.0, -40.0, 15.0), 56),
    (6.0, (-2.4, -103.0, 9.5), (0.0, -42.0, 17.0), 54),
])
C.marker("SPAWN_player", (RITA[0], RITA[1], 0.0), face=(0, DAIS.y))
# 세계수 줄기 위쪽 (연출이 '세계수 쪽으로' 시선을 돌릴 때 보는 점: epilogue/coronation.ts, title/scenes/coronation.ts)
C.marker("MARK_worldtree", (TREE[0], TREE[1], 90.0))

ROOT = {
    "sky": "#bfe2f2",
    "fog": "380,2800",
    "sun": "-0.55,0.62,0.75",
    "ambient": 1.5,
    "near": 0.08,
    "far": 3200,
    "music": "epilogue",
    "sunIntensity": 2.3,
    "sunColor": "#ffe6c4",
    "hemiSky": "#f2f6ff",
    "hemiGround": "#9a8b78",
    "timeOfDay": "late_afternoon",
    "scene": "EP_CORONATION",
    "shots": "ep_a,ep_b,ep_c,co_a,co_g,co_h,pr_a,pr_d",
    "physics": 0,
}
C.finish("levels/epilogue_coronation.glb", root_props=ROOT, outline=0.022)
