"""알레트·타이다·레이지(교주 차원 모나티엄 엘프 셋)가 같이 쓰는 도우미.

세 사람의 원작 전투복은 엘피니아 군 전투복 계열이다(reference-notes 5장, 프롤로그 캐시의 전투복 기준).
공통: 둥근 헬멧, 무채색 천, 검은 벨트 + 사각 은색 버클 + 벨트 고리, 군화 위에서 불룩하게 접힌 바지, 크고 뭉툭한 군화와
밝은 뒤 고리, 자줏빛 회색 장비. 여기에는 그 공통 장비와 세 사람의 무기(별도 노드)를 둔다. 근거: docs/art/characters-cameo3.md.

무기는 원작 무기의 형태 언어(docs/art/weapons-home.md 1장)만 가져와 3인칭 소품으로 다시 그렸다. 원점 = 파지점(무기 규약).
    riot_shield(e)  알레트: 모나티엄 진압 방패 (왼손, 로컬 -Y = 앞면, +Z = 위)
    rail_baton(e)   타이다: 두 갈래 전극 + 금색 안쪽 레일의 장봉형 전기충격기 (오른손, 로컬 +Y = 전극 쪽)
    xg_rifle(e)     레이지: 불펍 소총 (오른손, 로컬 +Y = 총구)
"""
from __future__ import annotations

import math

import bpy

import elf
import cameo2 as c2
import cameo3 as c3
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, frame

# 엘피니아 전투복 공통 색 (reference-notes 5.3)
BELT = "#4a4149"
METAL = "#cfcac4"
TAB = "#b9b2a8"
SOLE = "#2f2b31"
LINE = "#4a2229"


def base_gear(e, pre, *, pants, pants_d, boots, boots_d, glove=None, glove_cuff=None, blouse=0.020, bag=0.013,
              belt_z=None, boots_top=0.66):
    """공통: 통 넓은 바지(블라우징), 군화(목 패딩·끈판·뒤 고리·두꺼운 밑창), 검은 벨트 + 사각 은색 버클 + 벨트 고리, 장갑.
    반환: 머티리얼 사전."""
    M = elf.mat
    m = {"belt": M(f"{pre}_belt", BELT), "metal": M(f"{pre}_metal", METAL), "tab": M(f"{pre}_tab", TAB),
         "sole": M(f"{pre}_sole", SOLE)}
    e.pants(pants, bag=bag, blouse=blouse)
    e.boots(boots, top=boots_top, sole=(m["sole"], 0.016), cuff=boots_d, laces=boots_d, tab=m["tab"])
    if glove is not None:
        e.gloves(glove, cuff=glove_cuff or glove)
    kw = {"z": belt_z} if belt_z is not None else {}
    e.belt(m["belt"], buckle=m["metal"], loops=m["belt"], **kw)
    return m


# =========================================================================== 무기 (별도 노드)

def riot_shield(e, *, body="#4e4852", rim="#2f2b33", window="#9fb3c4", mark="#d6b25e"):
    """모나티엄 진압 방패 [오리지널 디자인, 원작: 알레트의 진압 방패]. 키보다 조금 작은 세로 직사각형, 윗부분 시야창,
    가장자리 고무 테, 가운데 엘프 로고 휘장(ART_GUIDE 1장 예외: 교주 차원 병기 엠블럼 자리), 아래 발 받침 홈.
    로컬: 원점 = 손잡이(왼손 파지점), -Y = 앞면(바깥), +Z = 위. 반환: 오브젝트."""
    k = e.k
    M = elf.mat
    mb, mr, mw, mm = M(f"{e.name}_sh_body", body), M(f"{e.name}_sh_rim", rim), M(f"{e.name}_sh_win", window), \
        M(f"{e.name}_sh_mark", mark)
    mh = M(f"{e.name}_sh_handle", "#3a353e")
    W, H, T = 0.34 * k, 0.70 * k, 0.014 * k
    zc = 0.08 * k        # 손잡이에서 방패 중심까지 (손이 가운데보다 조금 아래)
    yf = -0.040 * k      # 손에서 방패 뒷면까지
    b = Buf()
    w = {}
    # 몸판: 앞으로 살짝 휜 판 (가로 7열)
    cols, rows = 9, 2
    R = []
    for i in range(rows + 1):
        z = zc - H / 2 + H * i / rows
        row = []
        for j in range(cols + 1):
            u = -1 + 2 * j / cols
            x = u * W / 2
            y = yf - 0.030 * k * (1 - u * u)
            row.append((x, y, z))
        R.append(row)
    fo = [[b.vert(V((x, y - T / 2, z)), w) for x, y, z in row] for row in R]
    bo = [[b.vert(V((x, y + T / 2, z)), w) for x, y, z in row] for row in R]
    for i in range(rows):
        for j in range(cols):
            b.face((fo[i][j], fo[i][j + 1], fo[i + 1][j + 1], fo[i + 1][j]), mb)
            b.face((bo[i][j], bo[i + 1][j], bo[i + 1][j + 1], bo[i][j + 1]), mb)
    for j in range(cols):
        b.face((fo[0][j], bo[0][j], bo[0][j + 1], fo[0][j + 1]), mr)
        b.face((fo[rows][j], fo[rows][j + 1], bo[rows][j + 1], bo[rows][j]), mr)
    for i in range(rows):
        b.face((fo[i][0], fo[i + 1][0], bo[i + 1][0], bo[i][0]), mr)
        b.face((fo[i][cols], bo[i][cols], bo[i + 1][cols], fo[i + 1][cols]), mr)

    def front_pt(u, z, lift=0.0):
        x = u * W / 2
        y = yf - 0.030 * k * (1 - u * u) - T / 2 - lift
        return V((x, y, z))

    def fnorm(u):
        return V((-0.12 * u, -1.0, 0.0)).normalized()
    # 고무 테두리 (앞면 가장자리 띠)
    for z in (zc - H / 2 + 0.010 * k, zc + H / 2 - 0.010 * k):
        pts = [front_pt(-1 + 2 * j / cols, z, 0.001 * k) for j in range(cols + 1)]
        elf._loop(b, pts, [fnorm(-1 + 2 * j / cols) for j in range(cols + 1)], [V((0, 0, 1))] * (cols + 1),
                  0.018 * k, 0.004 * k, mat=mr, w=w, closed=False)
    for u in (-0.97, 0.97):
        pts = [front_pt(u, zc - H / 2 + H * t, 0.001 * k) for t in (0.0, 1.0)]
        elf._loop(b, pts, [fnorm(u)] * 2, [V((1, 0, 0))] * 2, 0.018 * k, 0.004 * k, mat=mr, w=w, closed=False)
    # 시야창 (위쪽 가로 창)
    zw = zc + H / 2 - 0.090 * k
    for j in range(5):
        u0, u1 = -0.62 + 1.24 * j / 5, -0.62 + 1.24 * (j + 1) / 5
        p0, p1 = front_pt(u0, zw, 0.0015 * k), front_pt(u1, zw, 0.0015 * k)
        c = (p0 + p1) / 2
        Mx = Matrix.Translation(c) @ frame(fnorm((u0 + u1) / 2), (0, 0, 1))
        c3.box12(b, ((p1 - p0).length * 1.02, 0.003 * k, 0.050 * k), Mx, mw, w)
    # 가운데 휘장: 원판 + 엘프 로고 (오목 다각형이라 bmesh로 돌출)
    pc = front_pt(0.0, zc + 0.02 * k, 0.002 * k)
    disc(b, pc, (0, -1, 0), (0, 0, 1), 0.060 * k, 0.060 * k, 0.003 * k, segs=16, mat=mr, w=w)
    # 아래 받침 홈 두 개
    for u in (-0.45, 0.45):
        c3.box12(b, (0.050 * k, 0.006 * k, 0.020 * k),
                 Matrix.Translation(front_pt(u, zc - H / 2 + 0.040 * k, 0.003 * k)) @ frame(fnorm(u), (0, 0, 1)),
                 mr, w)
    # 손잡이 (뒷면): 세로 손잡이 + 팔뚝 띠
    loft(b, [{"c": V((0, yf + T / 2 + 0.002 * k, -0.035 * k)), "rx": 0.009 * k, "ry": 0.009 * k, "w": w},
             {"c": V((0, 0.0, -0.030 * k)), "rx": 0.009 * k, "ry": 0.009 * k, "w": w},
             {"c": V((0, 0.0, 0.030 * k)), "rx": 0.009 * k, "ry": 0.009 * k, "w": w},
             {"c": V((0, yf + T / 2 + 0.002 * k, 0.035 * k)), "rx": 0.009 * k, "ry": 0.009 * k, "w": w}],
         segs=6, cap0="flat", cap1="flat", mat=mh)
    ob = b.obj(f"{e.name}_shield_geo", angle=35.0)
    import r41  # noqa: WPS433 (엘프 로고 외곽선)
    logo = [(u * 0.080 * k, v * 0.080 * k) for u, v in r41.elf_logo_outline(0.006)]
    lg = c2.poly_object(f"{e.name}_shield_logo", logo, 0.003 * k,
                        Matrix.Translation(pc + V((0, -0.0035 * k, -0.004 * k))) @ frame((0, -1, 0), (0, 0, 1)), mm)
    import cb
    return cb.join([ob, lg], f"{e.name}_shield_src")


def rail_baton(e, *, body="#8e8a92", body_d="#5f5a64", rail="#e2b54c", grip="#3a353e", led="#7ff0ea"):
    """장봉형 전기충격기 [오리지널 디자인, 원작: 타이다의 두 갈래 막대(안쪽 금색 레일) + 몸통 창]. 모나티엄 MR-B 계열의
    큰 판(시청 경비용). 각진 몸통 + 표시창, 앞으로 뻗은 두 갈래 전극(안쪽 금색 레일), 뒤 손잡이와 개머리 받침.
    로컬: 원점 = 오른손 파지점, +Y = 전극 쪽(앞), +Z = 위. 반환: 오브젝트."""
    k = e.k
    M = elf.mat
    mb, md, mr, mg = M(f"{e.name}_rb_body", body), M(f"{e.name}_rb_body_d", body_d), M(f"{e.name}_rb_rail", rail), \
        M(f"{e.name}_rb_grip", grip)
    ml = M(f"{e.name}_rb_led", "#ffffff", emission=led, unlit=True)
    b = Buf()
    w = {}

    def box(size, c, m, r=0.25):
        rbox(b, tuple(s * k for s in size), Matrix.Translation(V(c) * k), mat=m, w=w, r=r, segs=1)
    box((0.050, 0.240, 0.060), (0, 0.080, 0.030), mb)          # 몸통
    box((0.054, 0.090, 0.030), (0, 0.040, 0.066), md)          # 위 덮개
    box((0.036, 0.120, 0.012), (0, 0.070, 0.064), md)
    c3.box12(b, (0.0545 * k, 0.070 * k, 0.018 * k), Matrix.Translation(V((0, 0.120, 0.036)) * k), ml, w)   # 표시창
    box((0.040, 0.050, 0.090), (0, -0.090, 0.010), md)         # 개머리 받침
    loft(b, [{"c": V((0, -0.010 * k, 0.000)), "rx": 0.014 * k, "ry": 0.016 * k, "w": w},
             {"c": V((0, -0.020 * k, -0.080 * k)), "rx": 0.014 * k, "ry": 0.016 * k, "w": w}], segs=6,
         cap0="flat", cap1="round", mat=mg)                    # 손잡이
    box((0.044, 0.040, 0.044), (0, 0.215, 0.030), md)          # 전극 뿌리
    for sx in (1, -1):                                          # 두 갈래 전극 + 안쪽 금색 레일
        box((0.014, 0.320, 0.044), (sx * 0.026, 0.390, 0.030), mb, r=0.2)
        box((0.006, 0.300, 0.026), (sx * 0.018, 0.395, 0.030), mr, r=0.2)
        box((0.016, 0.020, 0.050), (sx * 0.026, 0.550, 0.030), md, r=0.2)
    return b.obj(f"{e.name}_baton_src", angle=35.0)


def xg_rifle(e, *, body="#6f6a72", body_d="#4b464f", frame_c="#a69f9a", accent="#e9a24a", glass="#7ff0ea"):
    """불펍 소총 [오리지널 디자인, 원작: 레이지의 'XG-레이저' 불펍 소총의 형태 언어]. 긴 총열, 각진 몸통, 몸통 옆 긴
    둥근 창, 개머리 옆 둥근 구멍 세로줄, 표시창(시안 발광), 위 운반 손잡이 겸 조준기. 실루엣을 그대로 옮기지 않는다.
    로컬: 원점 = 오른손 파지점(권총 손잡이), +Y = 총구, +Z = 위. 반환: 오브젝트 (속성 muzzle은 부르는 쪽에서)."""
    k = e.k
    M = elf.mat
    mb, md, mf, ma = M(f"{e.name}_xg_body", body), M(f"{e.name}_xg_body_d", body_d), M(f"{e.name}_xg_frame", frame_c), \
        M(f"{e.name}_xg_accent", accent)
    ml = M(f"{e.name}_xg_led", "#ffffff", emission=glass, unlit=True)
    b = Buf()
    w = {}

    def box(size, c, m, r=0.22):
        rbox(b, tuple(s * k for s in size), Matrix.Translation(V(c) * k), mat=m, w=w, r=r, segs=1)
    box((0.046, 0.330, 0.090), (0, -0.040, 0.050), mf)         # 몸통 (불펍: 개머리까지)
    box((0.048, 0.220, 0.040), (0, -0.080, 0.012), md)         # 아래 몸통 (탄창 자리 뒤)
    box((0.036, 0.040, 0.080), (0, -0.090, -0.040), md)        # 탄창
    box((0.050, 0.120, 0.030), (0, 0.050, 0.110), md)          # 위 운반 손잡이 겸 조준기
    c3.box12(b, (0.052 * k, 0.040 * k, 0.012 * k), Matrix.Translation(V((0, 0.070, 0.112)) * k), ml, w)    # 표시창
    for x in (0.0242, -0.0242):                                 # 옆 긴 둥근 창 (짙은 홈)
        c3.box12(b, (0.003 * k, 0.140 * k, 0.020 * k), Matrix.Translation(V((x, 0.000, 0.060)) * k), md, w)
        for i in range(5):                                      # 개머리 옆 둥근 구멍 줄
            disc(b, V((x * 1.02, -0.170 + 0.000, 0.020 + 0.016 * i)) * k, (1 if x > 0 else -1, 0, 0), (0, 0, 1),
                 0.005 * k, 0.005 * k, 0.001 * k, segs=6, mat=md, w=w)
    box((0.040, 0.120, 0.050), (0, 0.180, 0.060), mb)          # 앞 덮개
    loft(b, [{"c": V((0, 0.240 * k, 0.062 * k)), "rx": 0.010 * k, "ry": 0.010 * k, "w": w},
             {"c": V((0, 0.500 * k, 0.062 * k)), "rx": 0.009 * k, "ry": 0.009 * k, "w": w}], segs=8,
         cap0="flat", cap1="flat", mat=md)                     # 총열
    loft(b, [{"c": V((0, 0.500 * k, 0.062 * k)), "rx": 0.014 * k, "ry": 0.014 * k, "w": w},
             {"c": V((0, 0.540 * k, 0.062 * k)), "rx": 0.014 * k, "ry": 0.014 * k, "w": w}], segs=8,
         cap0="flat", cap1="flat", mat=ma)                     # 총구 고리 (주황)
    box((0.050, 0.012, 0.070), (0, -0.204, 0.040), ma, r=0.2)  # 개머리 끝 주황 판
    loft(b, [{"c": V((0, 0.000, 0.010 * k)), "rx": 0.012 * k, "ry": 0.015 * k, "w": w},
             {"c": V((0, -0.016 * k, -0.060 * k)), "rx": 0.012 * k, "ry": 0.015 * k, "w": w}], segs=6,
         cap0="flat", cap1="round", mat=md)                    # 권총 손잡이
    return b.obj(f"{e.name}_rifle_src", angle=35.0)


def attach(e, ob, socket, Mw, name, props=None):
    """소품 노드를 소켓 자식으로 붙인다 (cameo3.socket_prop)."""
    return c3.socket_prop(e, ob, socket, Mw, name=name, outline=0.003, props=props)


def frame_world(fwd, up):
    """로컬 +Y = fwd, +Z = up 인 회전 행렬(4x4)."""
    Y = V(fwd).normalized()
    Z = V(up)
    Z = (Z - Y * Z.dot(Y)).normalized()
    X = Y.cross(Z).normalized()
    return Matrix((X, Y, Z)).transposed().to_4x4()
