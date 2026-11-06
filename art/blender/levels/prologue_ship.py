"""프롤로그 함내 레벨: 헤일리의 기함 (선봉대 기함, 병력 수송 겸용).

npm run model -- art/blender/levels/prologue_ship.py                 → public/models/levels/prologue_ship.glb
PREVIEW=1 npm run model -- art/blender/levels/prologue_ship.py       → public/models/_tmp/prologue_ship_preview.glb
PREVIEW=col npm run model -- art/blender/levels/prologue_ship.py     → 충돌 박스를 붉게 보이는 미리보기
npm run shot -- _tmp/prologue_ship_preview.glb --views top

오프닝 컷신 → 튜토리얼 순서로 구역이 이어진다 (docs/scenario.md '프롤로그', docs/script/prologue.md,
docs/art/level-prologue.md).
  1. bridge   함교·브리핑 (상갑판 z=4.4): 헤일리 브리핑, 홀로 테이블, 지구 망원 영상 화면
  2. atrium   승강 구간: 상갑판 통로에서 주갑판으로. 큰 창 너머 함대, 중력 승강기 빛기둥, 계단
  3. troop    병력 구획 B: 정찰 침투조 대기. 침상, 사물함, 장비 거치대, 브리핑 보드
  4. range    사격장: 대기실, 사로 5개, 옆 통로(달리기·점프·앉기). 튜토리얼 T01~T10
  5. course   훈련 구획: 홀로그램 장애물 시뮬레이션 코스. 타임 어택 T11~T13
  6. space    창밖 별 배경 판과 함대 실루엣

좌표: Blender Z-up, 1 BU = 1 m. 뱃머리는 -Y. 주갑판 z=0, 상갑판 z=4.4.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import home_weapons as hw  # noqa: E402
import level_kit as lk  # noqa: E402
from mathutils import Euler, Vector  # noqa: E402

cb.reset()
PREVIEW = os.environ.get("PREVIEW", "")
L = lk.Level("prologue_ship")

ZU = 4.4            # 상갑판 바닥
SOLDIER = "characters/_kit_elfinia_soldier.glb"
UP_Y = (0, 1, 0)

# ---------------------------------------------------------------- 공용 조각
HOLO_COURSE = "HOLO_course"
HOLO_RANGE = "HOLO_range"


def main_lights(n, where):
    """평상 조명 그룹 LIGHT_main_<n> (천장 조명판 메시 하나). 미션이 꺼서 비상등으로 바꾼다."""
    name = f"LIGHT_main_{n:02d}"
    L.group(name, mode="mesh", emissiveToggle=1, group="main", on=1, color=lk.GLOW["lamp"], room=where)
    L.group(None)
    return name



def alert_light(lid, wall_pt, normal, group="alert"):
    """경고등: 벽 받침 + 어두운 렌즈(항상 보임) + LIGHT_ 발광 렌즈(미션이 켜고 끔)."""
    N = Vector(normal).normalized()
    p = Vector(wall_pt)
    tip = p + N * 0.16
    if abs(N.x) > 0.5:
        L.box("navy", min(p.x, tip.x), max(p.x, tip.x), p.y - 0.08, p.y + 0.08, p.z - 0.05, p.z, kind="detail")
    else:
        L.box("navy", p.x - 0.08, p.x + 0.08, min(p.y, tip.y), max(p.y, tip.y), p.z - 0.05, p.z, kind="detail")
    base = p + N * 0.09
    L.cyl("metal", tuple(base), tuple(base + Vector((0, 0, 0.04))), 0.07, verts=12, kind="detail")
    L.cyl("red_d", tuple(base + Vector((0, 0, 0.04))), tuple(base + Vector((0, 0, 0.13))), 0.058, verts=12,
          r2=0.036, kind="detail")
    L.cyl("gold", tuple(base + Vector((0, 0, 0.13))), tuple(base + Vector((0, 0, 0.15))), 0.03, verts=8,
          kind="detail")
    L.special(f"LIGHT_{lid}", lambda b: lk.bm_cone(b, tuple(base + Vector((0, 0, 0.038))), (0, 0, 1), 0.066, 0.042,
                                                    0.1, segs=12),
              "alert", {"emissiveToggle": 1, "group": group, "on": 0, "blink": 1.2, "color": lk.GLOW["alert"]})


def speaker(sid, wall_pt, normal, up=(0, 0, 1)):
    """무전 스피커: 남색 함 + 둥근 그릴 + LIGHT_ 시안 고리 + SPEAKER_ 마커(소리 위치)."""
    N = Vector(normal).normalized()
    L.extrude("navy", hw.rrect(0.5, 0.34, 0.06, n=2), wall_pt, normal, 0.16, up=up, kind="detail")
    fc = Vector(wall_pt) + N * 0.16
    L.decal("navy_d", hw.circle(0.12, 20), tuple(fc), normal, up=up, lift=0.003)
    R, U = lk.frame(normal, up)
    for i in range(3):
        for j in range(3):
            q = fc + Vector(R) * ((i - 1) * 0.055) + Vector(U) * ((j - 1) * 0.055)
            L.decal("metal", lk.octagon(0.013), tuple(q), normal, up=up, lift=0.009)   # 그릴(0.003)보다 6 mm 앞
    L.decal("gold", lk.octagon(0.02), tuple(fc + Vector(R) * 0.19 - Vector(U) * 0.1), normal, up=up, lift=0.004)
    L.special(f"LIGHT_{sid}", lambda b: lk.bm_ring(b, hw.circle(0.15, 24), hw.circle(0.128, 24),
                                                   tuple(fc + N * 0.004), normal, up),
              "glow", {"emissiveToggle": 1, "group": "radio", "on": 0, "color": lk.GLOW["glow"]})
    L.marker(f"SPEAKER_{sid}", tuple(fc + N * 0.05), look=tuple(fc + N * 2), props={"group": "radio"})


def holo_wall(x0, x1, y0, y1, h, *, z0=0.0, post=2.4, col=True, number=None):
    """홀로그램 벽(하드 라이트): 건메탈 기둥 + 반투명 시안 판 + 발광 위 테. 충돌 있음. number: 벽 번호 표시.
    판·발광은 HOLO_course 그룹 (엔딩에서 꺼진다. 기둥·받침은 남는다)."""
    with L.in_group(HOLO_COURSE):
        L.box("holo", x0, x1, y0, y1, z0 + 0.1, z0 + h - 0.06, kind="fine")
        L.box("glow", x0 - 0.01, x1 + 0.01, y0 - 0.01, y1 + 0.01, z0 + h - 0.06, z0 + h)
    L.box("navy", x0 - 0.02, x1 + 0.02, y0 - 0.02, y1 + 0.02, z0 - 0.003, z0 + 0.1)
    along_x = (x1 - x0) > (y1 - y0)
    length = (x1 - x0) if along_x else (y1 - y0)
    n = max(1, math.ceil(length / post))
    for i in range(n + 1):
        t = i / n
        if along_x:
            x = x0 + (x1 - x0) * t
            L.box("metal", x - 0.082, x + 0.082, y0 - 0.05, y1 + 0.05, z0 - 0.005, z0 + h + 0.05)   # 벽 턱 앞면(0.07)보다 12 mm 앞
            with L.in_group(HOLO_COURSE):
                L.box("glow", x - 0.075, x + 0.075, y0 - 0.055, y1 + 0.055, z0 + h + 0.05, z0 + h + 0.09)
        else:
            y = y0 + (y1 - y0) * t
            L.box("metal", x0 - 0.05, x1 + 0.05, y - 0.082, y + 0.082, z0 - 0.005, z0 + h + 0.05)
            with L.in_group(HOLO_COURSE):
                L.box("glow", x0 - 0.055, x1 + 0.055, y - 0.075, y + 0.075, z0 + h + 0.05, z0 + h + 0.09)
    if number is not None:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        for sgn in (1, -1):
            if along_x:
                c, nrm = (cx, (y0 if sgn < 0 else y1) + sgn * 0.002, z0 + h * 0.55), (0, sgn, 0)
            else:
                c, nrm = ((x0 if sgn < 0 else x1) + sgn * 0.002, cy, z0 + h * 0.55), (sgn, 0, 0)
            with L.in_group(HOLO_COURSE):
                # 남색 원판은 금테 안쪽까지만 (금테와 겹치지 않게), 숫자는 원판보다 6 mm 앞
                L.decal("navy", hw.circle(0.22, 20), c, nrm, lift=0.004)
                L.ring("gold", hw.circle(0.26, 20), hw.circle(0.22, 20), c, nrm, lift=0.006)
                L.text("glow", str(number), 0.3, c, nrm, lift=0.010)
    if col:
        L.col(x0, x1, y0, y1, z0, z0 + h)


def pad_block(x0, x1, y0, y1, h, *, col=True):
    """훈련용 쿠션 블록 (점프 상자, 낮은 엄폐물): 남청 쿠션 + 남색 뚜껑 + 금색 테 + 발광 윗면 테두리."""
    L.box("pad", x0, x1, y0, y1, 0.0, h - 0.05, col=False)
    L.box("navy", x0 - 0.015, x1 + 0.015, y0 - 0.015, y1 + 0.015, h - 0.05, h)
    L.box("gold", x0 - 0.02, x1 + 0.02, y0 - 0.02, y1 + 0.02, h - 0.075, h - 0.05, kind="detail")
    w, d = x1 - x0, y1 - y0
    if w > 0.2 and d > 0.2:
        L.ring("glow", hw.rrect(w - 0.06, d - 0.06, 0.05, n=1), hw.rrect(w - 0.12, d - 0.12, 0.03, n=1),
               ((x0 + x1) / 2, (y0 + y1) / 2, h), (0, 0, 1), up=UP_Y, lift=0.004)
    if col:
        L.col(x0, x1, y0, y1, 0.0, h)


def crouch_bar(x0, x1, y0, y1, gap=0.88, top=2.6):
    """앉아서 통과하는 홀로 차단막: 아래 틈 gap. 아래 테에 경고 띠. 양끝 기둥."""
    with L.in_group(HOLO_COURSE):
        L.box("holo", x0, x1, y0, y1, gap + 0.08, top - 0.05, kind="fine")
        L.box("glow", x0 - 0.01, x1 + 0.01, y0 - 0.01, y1 + 0.01, top - 0.05, top)
    L.box("navy", x0 - 0.02, x1 + 0.02, y0 - 0.02, y1 + 0.02, gap, gap + 0.08)
    L.box("hazard", x0 - 0.025, x1 + 0.025, y0 - 0.025, y1 + 0.025, gap + 0.02, gap + 0.06, kind="detail")
    if (x1 - x0) > (y1 - y0):
        for x in (x0, x1):
            L.box("metal", x - 0.08, x + 0.08, y0 - 0.06, y1 + 0.06, -0.005, top + 0.05)
            L.col(x - 0.08, x + 0.08, y0 - 0.06, y1 + 0.06, 0.0, top)
    else:
        for y in (y0, y1):
            L.box("metal", x0 - 0.06, x1 + 0.06, y - 0.08, y + 0.08, -0.005, top + 0.05)
            L.col(x0 - 0.06, x1 + 0.06, y - 0.08, y + 0.08, 0.0, top)
    L.col(x0, x1, y0, y1, gap, top)


def crawl_tunnel(x0, x1, y0, y1, gap=0.88, top=2.6):
    """기어서 지나는 낮은 굴 (X 방향 길이): 쿠션 지붕(틈 위) + 입구·출구의 홀로 막 + 양끝 기둥."""
    L.box("pad", x0, x1, y0, y1, gap, gap + 0.34)
    L.box("navy", x0 - 0.02, x1 + 0.02, y0 - 0.02, y1 + 0.02, gap + 0.34, gap + 0.4)
    L.box("hazard", x0 - 0.025, x1 + 0.025, y0 - 0.005, y1, gap + 0.02, gap + 0.07, kind="detail")
    L.ring("glow", hw.rrect(x1 - x0 - 0.1, y1 - y0 - 0.1, 0.05, n=1), hw.rrect(x1 - x0 - 0.16, y1 - y0 - 0.16, 0.03, n=1),
           ((x0 + x1) / 2, (y0 + y1) / 2, gap + 0.4), (0, 0, 1), up=UP_Y, lift=0.004)
    for x in (x0, x1):
        with L.in_group(HOLO_COURSE):
            L.box("holo", x - 0.03, x + 0.03, y0, y1, gap + 0.4, top - 0.05, kind="fine")
            L.box("glow", x - 0.04, x + 0.04, y0, y1, top - 0.05, top)
        for y in (y0, y1):
            L.box("metal", x - 0.08, x + 0.08, y - 0.08, y + 0.08, -0.005, top + 0.05)
            L.col(x - 0.08, x + 0.08, y - 0.08, y + 0.08, 0.0, top)
    for k in range(1, 4):
        y = y0 + (y1 - y0) * k / 4
        L.box("metal", x0 + 0.1, x1 - 0.1, y - 0.04, y + 0.04, gap - 0.02, gap + 0.02, kind="detail")
    L.col(x0, x1, y0, y1, gap, top)


def floor_chevrons(p, d, n=3, key="glow", w=0.5, gap=0.42, z=0.0, group=None):
    """바닥 진행 방향 화살(V자). group을 주면 그 그룹(HOLO_)에 넣는다."""
    if group:
        with L.in_group(group):
            return floor_chevrons(p, d, n, key, w, gap, z)
    D = Vector((d[0], d[1], 0)).normalized()
    S = Vector((-D.y, D.x, 0))
    for i in range(n):
        c = Vector((p[0], p[1], z)) + D * (i * gap)
        a = c + D * 0.12
        pts = [a, c - D * 0.08 + S * w / 2, c - D * 0.08 + S * (w / 2 - 0.1), a - D * 0.12,
               c - D * 0.08 - S * (w / 2 - 0.1), c - D * 0.08 - S * w / 2]
        L.poly(key, [tuple(q + Vector((0, 0, 0.007))) for q in pts], normal=(0, 0, 1))


def gate(axis, c, a0, a1, h, label, *, z0=0.0, key="navy"):
    """출발·결승 문 (홀로 아치): 기둥 두 개 + 위 보 + 글자판 + 바닥 선. axis 'x'면 X로 걸침(면 y=c)."""
    prev_g = L.grp
    if axis == "x":
        for x in (a0, a1):
            L.box("metal", x - 0.1, x + 0.1, c - 0.1, c + 0.1, z0, z0 + h)
            with L.in_group(HOLO_COURSE):
                L.box("glow", x - 0.105, x + 0.105, c - 0.105, c + 0.105, z0 + h - 0.6, z0 + h - 0.55, kind="fine")
            L.col(x - 0.1, x + 0.1, c - 0.1, c + 0.1, z0, z0 + h)
        L.box(key, a0 - 0.12, a1 + 0.12, c - 0.12, c + 0.12, z0 + h, z0 + h + 0.36)
        L.box("gold", a0 - 0.13, a1 + 0.13, c - 0.13, c + 0.13, z0 + h + 0.36, z0 + h + 0.4, kind="detail")
        L.group(HOLO_COURSE)
        for sgn in (1, -1):
            L.text("glow", label, 0.24, ((a0 + a1) / 2, c + sgn * 0.125, z0 + h + 0.18), (0, sgn, 0))
        L.strip("glow", (a0, c, z0), (a1, c, z0), 0.12, (0, 0, 1), lift=0.008)
        L.grp = prev_g
    else:
        for y in (a0, a1):
            L.box("metal", c - 0.1, c + 0.1, y - 0.1, y + 0.1, z0, z0 + h)
            with L.in_group(HOLO_COURSE):
                L.box("glow", c - 0.105, c + 0.105, y - 0.105, y + 0.105, z0 + h - 0.6, z0 + h - 0.55, kind="fine")
            L.col(c - 0.1, c + 0.1, y - 0.1, y + 0.1, z0, z0 + h)
        L.box(key, c - 0.12, c + 0.12, a0 - 0.12, a1 + 0.12, z0 + h, z0 + h + 0.36)
        L.box("gold", c - 0.13, c + 0.13, a0 - 0.13, a1 + 0.13, z0 + h + 0.36, z0 + h + 0.4, kind="detail")
        L.group(HOLO_COURSE)
        for sgn in (1, -1):
            L.text("glow", label, 0.24, (c + sgn * 0.125, (a0 + a1) / 2, z0 + h + 0.18), (sgn, 0, 0))
        L.strip("glow", (c, a0, z0), (c, a1, z0), 0.12, (0, 0, 1), lift=0.008)
        L.grp = prev_g


def screen(center, normal, w, h, *, up=(0, 0, 1), frame_key="navy_l", depth=0.06, layer=None):
    """화면 틀(남색) + 금테 + 화면 바탕(UNLIT). 반환: 화면 면 중심(내용을 올릴 곳)."""
    N = Vector(normal).normalized()
    L.extrude(frame_key, hw.rrect(w + 0.12, h + 0.12, 0.08, n=2), center, normal, depth, up=up, kind="detail",
              layer=layer)
    fc = Vector(center) + N * depth
    L.ring("gold", hw.rrect(w + 0.1, h + 0.1, 0.07, n=2), hw.rrect(w + 0.05, h + 0.05, 0.05, n=2), tuple(fc), normal,
           up=up, lift=0.003, layer=layer)
    L.decal("screen", hw.rrect(w, h, 0.04, n=2), tuple(fc), normal, up=up, lift=0.004, layer=layer)
    return fc


def on_screen(fc, normal, u, v, *, up=(0, 0, 1)):
    R, U = lk.frame(normal, up)
    return tuple(Vector(fc) + Vector(R) * u + Vector(U) * v)


def broadcast_screen(center, normal, w=1.0, h=0.6):
    """헤일리 브리핑 중계 모니터 (복도·병력 구획). 로고 + '브리핑 중계' + 진행 막대."""
    fc = screen(center, normal, w, h, depth=0.05)
    L.logo(on_screen(fc, normal, -w * 0.28, 0.02), h * 0.62, normal, disc=None, lift=0.008)
    L.text("glow", "선봉대 브리핑", h * 0.13, on_screen(fc, normal, w * 0.18, h * 0.12), normal, lift=0.008)
    L.text("amber", "중계 중", h * 0.11, on_screen(fc, normal, w * 0.18, -h * 0.08), normal, lift=0.008)
    L.decal("glow_d", hw.rrect(w * 0.8, 0.025, 0.01, n=1, cy=-h * 0.36), fc, normal, lift=0.007)
    L.decal("glow", hw.rrect(w * 0.5, 0.025, 0.01, n=1, cx=-w * 0.15, cy=-h * 0.36), fc, normal, lift=0.009)


def fleet_ship(cx, cy, cz, length):
    """창밖 엘피니아 함선 실루엣 (뱃머리 -Y). length = 겉보기 길이."""
    s = length / 10.0
    side_pts = [(-5.0, 0.0), (-4.6, -0.45), (-3.2, -0.75), (3.4, -0.8), (4.6, -0.55), (5.0, -0.1), (5.0, 0.55),
                (4.2, 0.85), (1.6, 0.95), (0.9, 1.6), (-0.4, 1.65), (-0.9, 1.0), (-3.4, 0.7), (-4.6, 0.45)]
    pts = [(cy + y * s, cz + z * s) for y, z in side_pts]
    L.obj("navy_l", cb.profile_extrude("ship", pts, 1.5 * s, axis="X", loc=(cx, 0, 0)))
    top = [(cy + y * s, cz + z * s) for y, z in [(-4.0, 0.55), (4.0, 0.75), (4.2, 0.9), (-3.6, 0.75)]]
    L.obj("olive", cb.profile_extrude("deck", top, 1.1 * s, axis="X", loc=(cx, 0, 0)))
    L.box("gold", cx - 0.77 * s, cx + 0.77 * s, cy - 2.2 * s, cy - 1.95 * s, cz - 0.7 * s, cz + 0.65 * s)
    L.box("gold", cx - 0.77 * s, cx + 0.77 * s, cy + 1.2 * s, cy + 1.35 * s, cz - 0.75 * s, cz + 0.8 * s)
    for ex, ez in ((-0.45, 0.1), (0.45, 0.1), (0.0, -0.4)):
        L.cyl("metal", (cx + ex * s, cy + 4.6 * s, cz + ez * s), (cx + ex * s, cy + 5.5 * s, cz + ez * s),
              0.28 * s, verts=10)
        L.decal("engine", hw.circle(0.22 * s, 10), (cx + ex * s, cy + 5.5 * s, cz + ez * s), (0, 1, 0), lift=0.02)
    for i in range(7):
        y = cy + (-3.0 + i * 0.9) * s
        for sx in (-1, 1):
            L.decal("glow", hw.circle(0.07 * s, 6), (cx + sx * 0.75 * s, y, cz + 0.2 * s), (sx, 0, 0), lift=0.02)


def stair_rail(x, y0, z0, y1, z1, h=0.78):
    """계단 옆 경사 난간 + 충돌 벽(계단 높이 + 1.1 m)."""
    n = max(2, math.ceil(abs(y1 - y0) / 1.0))
    for i in range(n + 1):
        t = i / n
        y, z = y0 + (y1 - y0) * t, z0 + (z1 - z0) * t
        L.cyl("metal", (x, y, z), (x, y, z + h - 0.03), 0.022, verts=8, kind="detail")
        L.cyl("gold", (x, y, z + h - 0.05), (x, y, z + h + 0.025), 0.032, verts=8, kind="detail")
    L.cyl("steel", (x, y0, z0 + h), (x, y1, z1 + h), 0.026, verts=8, kind="detail")
    L.cyl("metal", (x, y0, z0 + h * 0.5), (x, y1, z1 + h * 0.5), 0.014, verts=6, kind="detail")
    L.col(x - 0.06, x + 0.06, min(y0, y1), max(y0, y1), 0.0, max(z0, z1) + 1.1)


def wall_cap(x0, x1, y0, y1, z1):
    """벽 끝 마감 기둥 (건메탈 + 금색 고리)."""
    L.box("metal", x0, x1, y0, y1, -0.004, z1 + 0.004)        # 바닥·천장 속으로 4 mm (벽 위·아래 면과 겹치지 않게)
    L.box("gold", x0 - 0.015, x1 + 0.015, y0 - 0.015, y1 + 0.015, 0.945, 1.025, kind="detail")   # 벽 턱·징두리보다 5 mm 크게


# ================================================================ 1. 함교 (bridge)
L.zone("bridge")
BX0, BX1, BY0, BY1 = -7.0, 7.0, -29.0, -16.4
ZB = ZU + 3.6
L.floor(BX0, BX1, BY0, BY1, ZU, key="floor", grid=1.4)
# 앞 창 (5칸)
WIN = [(-5.3, 2.0), (-2.65, 2.0), (0.0, 2.0), (2.65, 2.0), (5.3, 2.0)]
WZ0, WZ1 = ZU + 1.0, ZU + 3.15
# BRIDGE_intact: 직격 때 숨길 부분 (앞 벽·창, 떠 있는 화면, 홀로그램, 옆 화면). BRIDGE_damaged가 그 자리를 대신한다
L.group("BRIDGE_intact", state="intact", on=1)
L.wall("x", BY0, BX0, BX1, +1, ZU, ZB, openings=[(x - w / 2, x + w / 2, WZ0, WZ1) for x, w in WIN], pitch=2.65,
       insets=False)
for i, (x, w) in enumerate(WIN):
    L.portal("x", BY0 - 0.1, x, w, WZ1 - WZ0, WZ0, 0.2, window=True, rad=0.45, border=0.12, faces=(1,))
    with L.in_group(f"WINDOW_bridge_{i + 1}", mode="mesh", parent="BRIDGE_intact", outward="0,0,1",
                    size=f"{w},{WZ1 - WZ0:.2f}"):
        L.decal("glass", hw.rrect(w, WZ1 - WZ0, 0.45, n=4), (x, BY0 - 0.1, (WZ0 + WZ1) / 2), (0, 1, 0), lift=0)
    L.col(x - w / 2, x + w / 2, BY0 - 0.12, BY0 - 0.08, WZ0, WZ1)
L.group(None)
# 뒤 벽 (함교 문)
DOOR_X = 4.0
L.wall("x", BY1, BX0, BX1, -1, ZU, ZB, openings=[(DOOR_X - 0.5, DOOR_X + 0.5, ZU, ZU + 2.0)])
L.portal("x", BY1 + 0.1, DOOR_X, 1.0, 2.0, ZU, 0.2, faces=(-1, 1))
# 옆 벽
L.wall("y", BX0, BY0, BY1, +1, ZU, ZB, pipes=True)
L.wall("y", BX1, BY0, BY1, -1, ZU, ZB, pipes=True)
L.ceiling(BX0, BX1, BY0, BY1, ZB, rib_axis="x", pitch=2.1, lamp_rows=[-4.2, 4.2], lamp_group=main_lights(1, "bridge"))


def _door_leaf(b):
    lk._bm_box(b, DOOR_X - 0.52, DOOR_X + 0.52, BY1 + 0.04, BY1 + 0.16, ZU, ZU + 2.02)


# 함교 문 (DOOR_bridge): 한 짝, 벽 속으로 +X 방향 미닫이. 기본 닫힘 → 플레이어는 함교에 못 들어간다
L.special("DOOR_bridge", _door_leaf, "navy_l", {"move": "1.05,0,0"})
for sgn, yy in ((-1, BY1 + 0.04), (1, BY1 + 0.16)):
    nrm = (0, sgn, 0)
    L.decal("gold", hw.stadium(0.5, 0.12), (DOOR_X, yy, ZU + 1.55), nrm, lift=0.004)
    L.decal("glow", hw.stadium(0.42, 0.05), (DOOR_X, yy, ZU + 1.55), nrm, lift=0.008)
    L.decal("navy", hw.rrect(0.84, 1.2, 0.08, n=2), (DOOR_X, yy, ZU + 0.75), nrm, lift=0.004)
    L.logo((DOOR_X, yy, ZU + 0.85), 0.34, nrm, disc=None, lift=0.008)

# 홀로 테이블 + 지구 홀로그램
HT = (0.0, -23.0)
L.cyl("metal", (HT[0], HT[1], ZU), (HT[0], HT[1], ZU + 0.5), 0.55, verts=24, r2=0.42)
L.cyl("navy", (HT[0], HT[1], ZU + 0.48), (HT[0], HT[1], ZU + 0.62), 1.15, verts=36)
L.obj("gold", hw.torus("rim", 1.15, 0.035, loc=(HT[0], HT[1], ZU + 0.6), seg=36, rseg=6), kind="detail")
L.group("BRIDGE_intact")
L.decal("glow_d", hw.circle(1.02, 36), (HT[0], HT[1], ZU + 0.62), (0, 0, 1), up=UP_Y, lift=0.004)
L.ring("glow", hw.circle(0.98, 36), hw.circle(0.93, 36), (HT[0], HT[1], ZU + 0.62), (0, 0, 1), up=UP_Y, lift=0.007)
L.ring("glow", hw.circle(0.5, 24), hw.circle(0.47, 24), (HT[0], HT[1], ZU + 0.62), (0, 0, 1), up=UP_Y, lift=0.007)
L.group(None)
L.ccyl(HT[0], HT[1], 1.16, ZU, ZU + 0.62, n=24)      # 둥근 탁자 (예전 2.3 m 정사각형은 모서리 0.45 m가 빈 벽이었다)
HZ = ZU + 1.5
# 홀로그램: 지구(기본 켜짐, 천천히 돈다), 골든 레코드(브리핑 02, 기본 꺼짐), 표적 표시(브리핑 05, 기본 꺼짐)
L.group("HOLO_bridge_earth", parent="BRIDGE_intact", pivot=(HT[0], HT[1], HZ), holo=1, on=1, spin="0,12,0")
L.cyl("holo_l", (HT[0], HT[1], ZU + 0.63), (HT[0], HT[1], HZ - 0.2), 0.9, verts=28, r2=0.5, cap=False, kind="fine")
L.obj("holo", cb.sphere("earth_holo", radius=0.42, loc=(HT[0], HT[1], HZ), segments=20, rings=10), kind="fine")
for rot in ((0, 0, 0), (90, 0, 0), (90, 0, 60), (90, 0, 120)):
    L.obj("glow", hw.torus("lat", 0.43, 0.006, loc=(HT[0], HT[1], HZ), rot=rot, seg=28, rseg=4), kind="fine")
ORB = Euler((math.radians(18), math.radians(8), 0))
L.obj("glow", hw.torus("orbit", 0.78, 0.008, loc=(HT[0], HT[1], HZ), rot=(18, 8, 0), seg=40, rseg=4), kind="fine")
for i in range(5):
    a = math.radians(200 + i * 14)
    p = Vector((math.cos(a) * 0.78, math.sin(a) * 0.78, 0))
    p.rotate(ORB)
    L.cyl("amber", (HT[0] + p.x, HT[1] + p.y, HZ + p.z - 0.03), (HT[0] + p.x, HT[1] + p.y, HZ + p.z + 0.03),
          0.03, verts=4, r2=0.0, kind="fine")
# 북미 위 표적 표시 (한 나라가 붉게)
L.group("HOLO_bridge_target", parent="HOLO_bridge_earth", holo=1, on=0)
TGT = Vector((HT[0] - 0.2, HT[1] + 0.3, HZ + 0.22))
TGN = (TGT - Vector((HT[0], HT[1], HZ))).normalized()
L.obj("holo_red", hw.torus("tgt", 0.11, 0.008, loc=tuple(TGT + TGN * 0.02), seg=16, rseg=4,
                           rot=tuple(math.degrees(a) for a in TGN.to_track_quat("Z", "Y").to_euler())), kind="fine")
L.decal("holo_red", hw.circle(0.085, 14), tuple(TGT), tuple(TGN), lift=0.012)
L.group(None)
# 골든 레코드 홀로그램 (금빛 원반, 테이블 위에서 돈다)
L.group("HOLO_bridge_record", parent="BRIDGE_intact", pivot=(HT[0], HT[1], HZ), holo=1, on=0, spin="0,40,0")
RN = Vector((0, -0.34, 0.94)).normalized()
L.decal("holo_gold", hw.circle(0.4, 40), (HT[0], HT[1], HZ), tuple(RN), up=(0, 1, 0), lift=0.0)
for r0 in (0.36, 0.3, 0.24, 0.18):
    L.ring("amber", hw.circle(r0, 40), hw.circle(r0 - 0.008, 40), (HT[0], HT[1], HZ), tuple(RN), up=(0, 1, 0), lift=0.004)
L.decal("holo_gold", hw.circle(0.1, 20), (HT[0], HT[1], HZ), tuple(RN), up=(0, 1, 0), lift=0.006)
L.decal("holo_gold", hw.circle(0.4, 40), (HT[0], HT[1], HZ), tuple(-RN), up=(0, 1, 0), lift=0.0)
L.group(None)
# 바닥 금색 고리
for r0, r1 in ((1.62, 1.67), (2.45, 2.49)):
    L.ring("gold", hw.circle(r1, 40), hw.circle(r0, 40), (HT[0], HT[1], ZU), (0, 0, 1), up=UP_Y, lift=0.009)
for k in range(8):
    a = math.radians(22.5 + k * 45)
    L.strip("gold", (HT[0] + math.cos(a) * 1.7, HT[1] + math.sin(a) * 1.7, ZU),
            (HT[0] + math.cos(a) * 2.4, HT[1] + math.sin(a) * 2.4, ZU), 0.04, (0, 0, 1), lift=0.009)   # 바닥 줄(0.006) 위
# 천장 고리 조명 (테이블 위)
L.cyl("navy", (HT[0], HT[1], ZB - 0.18), (HT[0], HT[1], ZB), 1.5, verts=36, layer="ceil")
with L.in_group("LIGHT_main_01"):
    L.ring("lamp", hw.circle(1.4, 36), hw.circle(1.1, 36), (HT[0], HT[1], ZB - 0.18), (0, 0, -1), up=UP_Y, lift=0.004,
           layer="ceil")

# 떠 있는 지구 망원 영상 화면 (테이블 너머, 창 앞)
SC = (0.0, -27.2, ZU + 2.15)
L.group("BRIDGE_intact")
L.box("metal", -0.06, 0.06, -27.35, -27.25, ZU + 3.3, ZB, layer="ceil")
L.box("metal", -1.9, 1.9, -27.35, -27.25, ZU + 3.25, ZU + 3.33)
fc = screen(SC, (0, 1, 0), 3.8, 2.1, depth=0.08)
N_SC = (0, 1, 0)
EC = (-0.75, -0.02)
L.decal("ocean", hw.circle(0.86, 40, *EC), fc, N_SC, lift=0.006)
L.ring("glow", hw.circle(0.92, 40, *EC), hw.circle(0.87, 40, *EC), fc, N_SC, lift=0.006)
LAND = [
    [(-0.62, 0.62), (-0.40, 0.70), (-0.18, 0.62), (-0.08, 0.48), (-0.16, 0.36), (-0.10, 0.22), (-0.22, 0.10),
     (-0.34, 0.12), (-0.40, 0.02), (-0.50, 0.12), (-0.62, 0.24), (-0.70, 0.40)],
    [(-0.36, -0.02), (-0.24, -0.08), (-0.14, -0.20), (-0.18, -0.40), (-0.30, -0.62), (-0.38, -0.50),
     (-0.42, -0.30), (-0.44, -0.12)],
    [(-0.06, 0.70), (0.06, 0.74), (0.10, 0.64), (0.0, 0.58)],
    [(0.42, 0.40), (0.56, 0.44), (0.70, 0.30), (0.76, 0.06), (0.68, -0.22), (0.56, -0.30), (0.50, -0.06),
     (0.40, 0.10), (0.46, 0.26)],
]
for poly in LAND:
    L.decal("land", [(EC[0] + u, EC[1] + v) for u, v in poly], fc, N_SC, lift=0.009)
for (u, v, ln, a) in ((0.05, 0.18, 0.42, 12), (0.20, -0.35, 0.5, -8), (0.30, 0.55, 0.3, 20), (-0.55, -0.40, 0.3, 5)):
    L.decal("cloud", hw.stadium(ln, 0.05, cx=EC[0] + u, cy=EC[1] + v, angle=a), fc, N_SC, lift=0.012)
cres = hw.arc_pts(EC[0], EC[1], 0.86, -70, 70, 14) + list(reversed(hw.arc_pts(EC[0] - 0.22, EC[1], 0.8, -60, 60, 14)))
L.decal("screen", cres, fc, N_SC, lift=0.013)
TG = (EC[0] - 0.36, EC[1] + 0.40)
L.ring("amber", hw.circle(0.17, 24, *TG), hw.circle(0.15, 24, *TG), fc, N_SC, lift=0.016)
for (du, dv) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    L.strip("amber", on_screen(fc, N_SC, TG[0] + du * 0.19, TG[1] + dv * 0.19),
            on_screen(fc, N_SC, TG[0] + du * 0.31, TG[1] + dv * 0.31), 0.012, N_SC, lift=0.016)
for k in range(-4, 5):
    v = k * 0.22
    L.strip("glow_d", on_screen(fc, N_SC, -1.8, v), on_screen(fc, N_SC, 1.8, v), 0.006, N_SC, lift=0.005)
for k in range(-8, 9):
    u = k * 0.22
    L.strip("glow_d", on_screen(fc, N_SC, u, -0.98), on_screen(fc, N_SC, u, 0.98), 0.006, N_SC, lift=0.005)
L.text("glow", "망원 관측", 0.13, on_screen(fc, N_SC, 0.85, 0.78), N_SC, lift=0.012)
L.text("paper", "목표: 제3 행성", 0.085, on_screen(fc, N_SC, 0.85, 0.52), N_SC, lift=0.012)
L.text("amber", "50개 별의 왕국", 0.085, on_screen(fc, N_SC, 0.85, 0.36), N_SC, lift=0.012)
for i, ln in enumerate((0.9, 0.55, 0.75, 0.35, 0.62)):
    L.decal("glow", hw.rrect(ln, 0.045, 0.02, n=1, cx=0.42 + ln / 2, cy=0.12 - i * 0.12), fc, N_SC, lift=0.012)
L.decal("amber", hw.circle(0.035, 10, 1.62, 0.86), fc, N_SC, lift=0.012)
L.text("amber", "LIVE", 0.06, on_screen(fc, N_SC, 1.46, 0.86), N_SC, lift=0.012)
L.decal("glow", hw.rrect(1.2, 0.18, 0.04, n=1, cx=1.05, cy=-0.72), fc, N_SC, lift=0.010)
L.text("screen", "평화적 접촉 가능", 0.075, on_screen(fc, N_SC, 1.05, -0.72), N_SC, lift=0.016)
L.decal("navy_d", hw.rrect(3.9, 2.2, 0.08, n=2), SC, (0, -1, 0), lift=0.002)
L.group(None)

# 지휘 단상 (뒤쪽, 계단 2단 0.18)
DX0, DX1, DY0 = -2.6, 2.6, -19.7
L.box("navy", DX0, DX1, DY0 - 0.32, DY0, ZU, ZU + 0.18, col=True)
L.box("floor", DX0, DX1, DY0, BY1, ZU, ZU + 0.36, col=True)
L.strip("hazard", (DX0 + 0.1, DY0 - 0.27, ZU + 0.18), (DX1 - 0.1, DY0 - 0.27, ZU + 0.18), 0.05, (0, 0, 1), lift=0.004)
L.box("gold", DX0 - 0.004, DX1 + 0.004, DY0 - 0.02, DY0 + 0.02, ZU + 0.33, ZU + 0.37, kind="detail")
L.railing([(DX0 + 0.08, DY0 + 0.2), (DX0 + 0.08, BY1 - 0.3)], ZU + 0.36, h=0.6)
L.railing([(DX1 - 0.08, DY0 + 0.2), (DX1 - 0.08, BY1 - 0.3)], ZU + 0.36, h=0.6)
CSx, CSy, CSz = 0.0, -17.7, ZU + 0.36
L.cyl("metal", (CSx, CSy, CSz), (CSx, CSy, CSz + 0.3), 0.16, verts=12, r2=0.1)
L.obj("seat", hw.box("seat_c", (0.62, 0.52, 0.12), (CSx, CSy - 0.02, CSz + 0.34), bevel=0.04, seg=2))
L.obj("seat", hw.box("seat_b", (0.62, 0.14, 0.78), (CSx, CSy + 0.26, CSz + 0.74), rot=(-8, 0, 0), bevel=0.05, seg=2))
L.obj("gold", hw.box("seat_bg", (0.66, 0.06, 0.1), (CSx, CSy + 0.31, CSz + 1.12), rot=(-8, 0, 0), bevel=0.02),
      kind="detail")
for sx in (-1, 1):
    L.obj("navy", hw.box(f"arm{sx}", (0.1, 0.5, 0.08), (CSx + sx * 0.36, CSy - 0.02, CSz + 0.5), bevel=0.025))
    L.decal("glow", hw.rrect(0.07, 0.22, 0.02, n=1), (CSx + sx * 0.36, CSy - 0.08, CSz + 0.54), (0, 0, 1),
            up=UP_Y, lift=0.004)
L.logo((CSx, CSy + 0.3, CSz + 0.92), 0.2, (0, -1, 0), disc="navy", lift=0.01)
L.col(CSx - 0.41, CSx + 0.41, CSy - 0.28, CSy + 0.33, CSz, CSz + 0.55)       # 좌판·팔걸이
L.col(CSx - 0.33, CSx + 0.33, CSy + 0.19, CSy + 0.36, CSz, CSz + 1.17)       # 등받이
L.logo_plate((0.0, BY1, ZU + 2.35), 1.15, (0, -1, 0), thick=0.08)
# 옆 벽 대형 화면: 함대 진형 (왼쪽), 함 상태 (오른쪽)
L.group("BRIDGE_intact")
fcL = screen((BX0 + 0.05, -24.3, ZU + 2.05), (1, 0, 0), 3.4, 1.1)
NL_ = (1, 0, 0)
for i in range(7):
    u = -1.4 + i * 0.45
    v = 0.1 * math.sin(i * 1.3)
    L.decal("glow", [(u - 0.08, v - 0.05), (u + 0.1, v), (u - 0.08, v + 0.05)], fcL, NL_, lift=0.008)
L.decal("amber", [(1.5, 0.0), (1.38, 0.07), (1.38, -0.07)], fcL, NL_, lift=0.008)
L.strip("glow_d", on_screen(fcL, NL_, -1.6, -0.3), on_screen(fcL, NL_, 1.6, -0.3), 0.01, NL_, lift=0.006)
L.text("glow", "선봉 함대 진형", 0.09, on_screen(fcL, NL_, -1.05, 0.4), NL_, lift=0.008)
fcR = screen((BX1 - 0.05, -24.3, ZU + 2.05), (-1, 0, 0), 3.4, 1.1)
NR_ = (-1, 0, 0)
ship_pts = [(-1.3, 0.0), (-1.1, -0.18), (1.0, -0.2), (1.3, -0.08), (1.3, 0.12), (0.2, 0.2), (0.0, 0.35), (-0.4, 0.35),
            (-0.5, 0.16), (-1.1, 0.16)]
L.ring("glow", ship_pts, [(u * 0.95, v * 0.85) for u, v in ship_pts], fcR, NR_, lift=0.008)
for i, ok in enumerate((1, 1, 1, 0, 1)):
    L.decal("glow" if ok else "amber", hw.rrect(0.16, 0.08, 0.02, n=1, cx=-0.8 + i * 0.4, cy=-0.38), fcR, NR_,
            lift=0.008)
L.text("glow", "기함 상태 정상", 0.09, on_screen(fcR, NR_, 1.0, 0.4), NR_, lift=0.008)
L.group(None)
# 함교 승무원 콘솔
for i, y in enumerate((-26.4, -22.6)):
    L.prop(f"console_port_{i + 1}", (BX0 + 0.55, y, ZU), "props/ship_console.glb", face=(BX0, y))
    L.col(BX0 + 0.29, BX0 + 0.84, y - 0.37, y + 0.37, ZU, ZU + 1.28)      # 콘솔 실제 크기 (예전 상자는 0.3 m 컸다)
    L.prop(f"console_stbd_{i + 1}", (BX1 - 0.55, y, ZU), "props/ship_console.glb", face=(BX1, y))
    L.col(BX1 - 0.84, BX1 - 0.29, y - 0.37, y + 0.37, ZU, ZU + 1.28)
for i, x in enumerate((-4.6, 4.6)):
    L.prop(f"console_front_{i + 1}", (x, BY0 + 0.6, ZU), "props/ship_console.glb", face=(x, BY0))
    L.col(x - 0.37, x + 0.37, BY0 + 0.34, BY0 + 0.89, ZU, ZU + 1.28)

# NPC: 헤일리와 승무원
HALEY = (1.6, -22.05, ZU)           # 홀로 테이블 오른쪽 앞 (단상 쪽 청중을 향함)
L.npc("haley", HALEY, "characters/haley.glb", face=(-0.4, -19.2),
      props={"pose": "at_ease", "look": "none", "name": "헤일리", "fallback": SOLDIER})
L.npc("crew_01", (BX0 + 1.2, -26.4, ZU), SOLDIER, face=(BX0, -26.4), props={"pose": "idle", "look": "none"})
L.npc("crew_02", (BX1 - 1.2, -22.6, ZU), SOLDIER, face=(BX1, -22.6), props={"pose": "idle", "look": "none"})
L.npc("crew_03", (-4.6, BY0 + 1.25, ZU), SOLDIER, face=(-4.6, BY0), props={"pose": "idle", "look": "none"})
L.npc("bridge_01", (-2.5, -20.7, ZU), SOLDIER, face=HALEY, props={"pose": "at_ease", "look": "haley"})
L.npc("bridge_02", (-3.0, -21.9, ZU), SOLDIER, face=HALEY, props={"pose": "at_ease", "look": "haley"})
L.npc("bridge_03", (-1.9, -24.3, ZU), SOLDIER, face=HALEY, props={"pose": "attention", "look": "haley"})
L.mark("bridge", (0.0, -21.0, ZU))

# 카메라: 헤일리 브리핑 컷 4개 (미션이 대사마다 골라 자른다: a 넓게, b 헤일리, c 홀로그램·지구 화면, d 역방향)
HF = (HALEY[0], HALEY[1], ZU + 0.95)
L.cam_rail("brief_a", [
    (0.0, (-4.4, -17.4, ZU + 2.3), (0.4, -23.4, ZU + 1.3), 48),
    (7.0, (-3.2, -18.4, ZU + 1.9), (0.6, -23.2, ZU + 1.2), 44),
])
L.cam_rail("brief_b", [
    (0.0, (0.8, -20.25, ZU + 1.02), HF, 30),
    (6.0, (0.95, -20.5, ZU + 1.0), HF, 27),
])
L.cam_rail("brief_c", [
    (0.0, (-1.2, -20.2, ZU + 1.55), (-0.6, -27.2, ZU + 2.15), 36),
    (6.0, (-1.45, -21.5, ZU + 1.75), (-0.75, -27.2, ZU + 2.15), 30),
])
L.cam_rail("brief_d", [
    (0.0, (2.9, -24.2, ZU + 1.35), (-2.4, -20.6, ZU + 0.9), 42),
    (6.0, (2.6, -24.5, ZU + 1.3), (-2.6, -20.9, ZU + 0.9), 40),
])

# ================================================================ 2. 승강 구간 (atrium) + 상갑판 통로
L.zone("atrium")
AX0, AX1, AY0, AY1 = -7.0, 4.8, -12.6, -2.6
ZA = 8.8
CX0, CX1 = 3.2, 4.8
L.floor(CX0, CX1, BY1 + 0.2, AY0 - 0.2, ZU, grid=0.8)
L.box("metal", CX0, CX1, BY1, BY1 + 0.2, ZU - 0.12, ZU, col=True)
# 문턱: 벽 개구부 밑면(ZU)보다 5 mm 위. 층계참 쪽으로 8.4 cm 더 내밀어, 문 구멍에 잘려 윗면이 층계참 바닥(ZU)과
# 같은 높이로 남은 갑판선 띠(깊이 8 cm)를 덮는다
L.box("metal", CX0 + 0.004, CX1 - 0.004, AY0 - 0.2, AY0 + 0.084, ZU - 0.12, ZU + 0.005)
L.col(CX0, CX1, AY0 - 0.2, AY0, ZU - 0.12, ZU)
L.wall("y", CX0, BY1 + 0.2, AY0 - 0.2, +1, ZU, ZU + 2.4, pitch=1.7, cornice=False, insets=False)
L.wall("y", CX1, BY1 + 0.2, AY0 - 0.2, -1, ZU, ZU + 2.4, pitch=1.7, cornice=False, insets=False)
L.ceiling(CX0, CX1, BY1 + 0.2, AY0 - 0.2, ZU + 2.4, rib_axis="x", pitch=1.2, lamp_w=0.8, lamp_len=0.4,
          lamp_group=main_lights(2, "corridor"))
L.sign((CX0 + 0.02, -14.9, ZU + 1.6), (1, 0, 0), 1.1, 0.34, "함교", size=0.16, logo=True)
broadcast_screen((CX1 - 0.02, -14.6, ZU + 1.55), (-1, 0, 0))

L.floor(AX0, AX1, AY0, AY1, 0.0, grid=1.2)
AWIN = [(-10.6, 2.2), (-7.6, 2.2), (-4.6, 2.2)]
AWZ0, AWZ1 = 0.9, 7.9
L.wall("y", AX0, AY0, AY1, +1, 0.0, ZA, openings=[(y - w / 2, y + w / 2, AWZ0, AWZ1) for y, w in AWIN],
       band=[ZU - 0.1], pitch=3.0)
for y, w in AWIN:
    L.portal("y", AX0 - 0.1, y, w, AWZ1 - AWZ0, AWZ0, 0.2, window=True, rad=0.9, border=0.16, faces=(1,))
    with L.in_group(f"WINDOW_atrium_{AWIN.index((y, w)) + 1}", mode="mesh", outward="-1,0,0",
                    size=f"{w},{AWZ1 - AWZ0:.2f}"):
        L.decal("glass", hw.rrect(w, AWZ1 - AWZ0, 0.9, n=4), (AX0 - 0.1, y, (AWZ0 + AWZ1) / 2), (1, 0, 0), lift=0)
    L.col(AX0 - 0.12, AX0 - 0.08, y - w / 2, y + w / 2, AWZ0, AWZ1)
    L.box("metal", AX0 - 0.12, AX0 + 0.02, y - w / 2, y + w / 2, ZU - 0.12, ZU + 0.02)
    L.box("gold", AX0 - 0.13, AX0 + 0.03, y - w / 2, y + w / 2, ZU + 0.02, ZU + 0.05, kind="detail")
L.wall("x", AY0, AX0, AX1, +1, 0.0, ZA, openings=[(CX0 + 0.1, CX1 - 0.1, ZU, ZU + 2.2)], band=[ZU - 0.1])
L.portal("x", AY0 - 0.1, (CX0 + CX1) / 2, 1.4, 2.2, ZU, 0.2, faces=(1,))
L.wall("y", AX1, AY0, AY1, -1, 0.0, ZA, band=[ZU - 0.1])
L.logo_plate((AX1, -7.6, 6.4), 1.3, (-1, 0, 0), thick=0.08)
TD_X0, TD_X1 = 0.6, 2.4
L.wall("x", AY1, AX0, AX1, -1, 0.0, ZA, openings=[(TD_X0, TD_X1, 0.0, 2.1)], band=[ZU - 0.1])
L.ceiling(AX0, AX1, AY0, AY1, ZA, rib_axis="y", pitch=2.4, lamp_rows=[-11.4, -3.8], lamp_group=main_lights(3, "atrium"))
# 위 층계참 (z=ZU)
LND_Y1 = -11.2
L.box("floor", -4.8, AX1, AY0, LND_Y1, ZU - 0.3, ZU, col=True)
L.box("gold", -4.82, CX0, LND_Y1 - 0.02, LND_Y1 + 0.02, ZU - 0.06, ZU - 0.02, kind="detail")
for x in (-4.5, -0.6):
    L.cyl("metal", (x, -11.5, 0), (x, -11.5, ZU - 0.3), 0.15, verts=12)
    L.col(x - 0.15, x + 0.15, -11.65, -11.35, 0.0, ZU - 0.3)
L.railing([(CX0, LND_Y1), (-4.8, LND_Y1), (-4.8, AY0 + 0.05)], ZU)
# 계단 두 단 (단 높이 0.22, 디딤 0.32): 층계참(z 4.4) → 중간 층계참(z 2.2) → 바닥
T_ = 0.32
MID_Y0 = LND_Y1 + 9 * T_            # 중간 층계참 시작 (-8.32)
MID_Y1 = MID_Y0 + 1.2
STAIR_LOW = MID_Y1 + 9 * T_         # 계단 아래 끝 (-4.24)
L.stairs("y", CX0, CX1, MID_Y0, -1, ZU / 2, ZU, 10, T_, solid_to=0.0)
L.box("metal", CX0, CX1, MID_Y0, MID_Y1, 0.0, ZU / 2 - 0.05, col=False)
L.box("floor", CX0, CX1, MID_Y0, MID_Y1, ZU / 2 - 0.05, ZU / 2, kind="detail")
L.col(CX0, CX1, MID_Y0, MID_Y1, 0.0, ZU / 2)
L.stairs("y", CX0, CX1, STAIR_LOW, -1, 0.0, ZU / 2, 10, T_)
stair_rail(CX0, LND_Y1, ZU, MID_Y0, ZU / 2)
stair_rail(CX0, MID_Y0, ZU / 2, MID_Y1, ZU / 2)
stair_rail(CX0, MID_Y1, ZU / 2, STAIR_LOW, 0.0)
# 중력 승강기 (빛기둥)
LF = (-3.2, -9.5)
L.cyl("navy", (LF[0], LF[1], 0), (LF[0], LF[1], 0.12), 1.3, verts=32)
L.obj("gold", hw.torus("lf_base", 1.25, 0.04, loc=(LF[0], LF[1], 0.12), seg=32, rseg=6), kind="detail")
L.decal("glow", hw.circle(1.0, 32), (LF[0], LF[1], 0.12), (0, 0, 1), up=UP_Y, lift=0.004)
L.ring("navy_d", hw.circle(0.8, 32), hw.circle(0.74, 32), (LF[0], LF[1], 0.12), (0, 0, 1), up=UP_Y, lift=0.008)
L.logo((LF[0], LF[1], 0.12), 0.9, (0, 0, 1), up=UP_Y, disc=None, key="navy_d", lift=0.01)
L.ccyl(LF[0], LF[1], 1.3, 0.0, 0.12, n=24)
L.ccyl(LF[0], LF[1], 1.2, 0.12, 1.0, n=24)          # 허리 높이 고리(0.9 m) 안: 빛기둥 승강대에는 들어가지 않는다
for z in (0.9, 2.6, ZU - 0.2, 6.4, ZA - 0.5):
    L.obj("gold", hw.torus("lf_ring", 1.18, 0.05, loc=(LF[0], LF[1], z), seg=32, rseg=6), kind="detail")
    L.obj("glow", hw.torus("lf_glow", 1.08, 0.022, loc=(LF[0], LF[1], z), seg=32, rseg=4), kind="fine")
for k in range(4):
    a = math.radians(45 + k * 90)
    x, y = LF[0] + math.cos(a) * 1.22, LF[1] + math.sin(a) * 1.22
    L.cyl("metal", (x, y, 0.12), (x, y, ZA), 0.06, verts=8)
    L.col(x - 0.07, x + 0.07, y - 0.07, y + 0.07, 0.0, ZA)
L.cyl("beam", (LF[0], LF[1], 0.13), (LF[0], LF[1], ZA - 0.2), 1.0, verts=28, cap=False, kind="fine")
L.cyl("navy", (LF[0], LF[1], ZA - 0.25), (LF[0], LF[1], ZA), 1.35, verts=32, layer="ceil")
with L.in_group("LIGHT_main_03"):
    L.decal("lamp", hw.circle(1.0, 32), (LF[0], LF[1], ZA - 0.25), (0, 0, -1), up=UP_Y, lift=0.004, layer="ceil")
L.box("hazard", LF[0] - 0.6, LF[0] + 0.6, LND_Y1 - 0.03, LND_Y1 + 0.03, ZU + 0.38, ZU + 0.44, kind="detail")
L.sign((-1.0, AY1, 2.45), (0, -1, 0), 1.6, 0.42, "병력 구획 B", size=0.17, logo=True, sub="정찰 침투조 대기")
L.sign((0.8, AY0, ZU + 1.4), (0, 1, 0), 1.3, 0.4, "함교", size=0.18, logo=True)
broadcast_screen((AX1 - 0.02, -5.6, 1.55), (-1, 0, 0), w=1.2, h=0.7)
# 하선 갑판으로 뛰어 올라가는 돌격대원 (카메라와 엇갈림)
for i, (x, y) in enumerate(((4.0, -3.4), (3.6, -2.95), (2.9, -3.7))):
    L.npc(f"runner_{i + 1:02d}", (x, y, 0.0), SOLDIER, face=(4.0, -6.0), props={"pose": "idle", "look": "none", "path": f"runner_{i + 1}"})
for i in range(1, 4):
    for j, p in enumerate(((4.0, -4.5, 0.0), (4.0, -7.6, ZU / 2), (4.0, -11.9, ZU), (4.0, -15.6, ZU))):
        L.wp(f"runner_{i}_{j + 1:02d}", p)

# ================================================================ 6. 창밖 (space)
L.zone("space")
L.stars((-40.0, -8.0, 4.0), (1, 0, 0), 110, 80, 420, seed=3)
L.stars((0.0, -64.0, 8.0), (0, 1, 0), 110, 70, 340, seed=7)
for (x, y, z, ln) in ((-16.0, -14.0, 2.5, 9.0), (-24.0, -30.0, 7.5, 12.0), (-21.0, 4.0, -3.0, 8.0),
                      (-30.0, -2.0, 11.0, 6.0), (-13.0, -36.0, -5.0, 5.0)):
    fleet_ship(x, y, z, ln)
for (x, y, z, ln) in ((-9.0, -48.0, 9.0, 7.0), (12.0, -52.0, 3.0, 9.0), (3.0, -58.0, 14.0, 4.0)):
    fleet_ship(x, y, z, ln)
EP = (7.5, -62.5, 15.0)                 # 뱃머리 창 오른쪽 위에 보이는 목적지 행성
L.decal("ocean", hw.circle(1.1, 28), EP, (0, 1, 0), lift=0.05)
L.decal("land", [(-0.5, 0.5), (-0.1, 0.65), (0.1, 0.3), (-0.2, 0.0), (-0.55, 0.15)], EP, (0, 1, 0), lift=0.07)
L.decal("space", hw.arc_pts(0, 0, 1.1, -80, 80, 12) + list(reversed(hw.arc_pts(-0.35, 0, 1.0, -70, 70, 12))), EP,
        (0, 1, 0), lift=0.09)
L.ring("beam", hw.circle(1.3, 28), hw.circle(1.1, 28), EP, (0, 1, 0), lift=0.04)

# ================================================================ 3. 병력 구획 B (troop)
L.zone("troop")
TX0, TX1, TY0, TY1 = -7.0, 7.0, -2.2, 10.6
ZT = 2.9
L.floor(TX0, TX1, TY0, TY1, 0.0, grid=1.2)
L.portal("x", (AY1 + TY0) / 2, (TD_X0 + TD_X1) / 2, TD_X1 - TD_X0, 2.1, 0.0, 0.4)
L.box("metal", TD_X0, TD_X1, AY1, TY0, -0.12, 0.0, col=True)


def _hatch(b):
    lk._bm_box(b, TD_X0 - 0.04, TD_X1 + 0.04, -2.47, -2.33, -0.004, 2.14)   # 밑면은 문턱 속 (벽 밑면과 겹치지 않게)


# 병력 구획 ↔ 승강 구간 문 (DOOR_bay_hatch): 벽 속으로 위로 열린다. 미션이 함내 이동 컷 동안 열고 뒤에 닫는다
L.special("DOOR_bay_hatch", _hatch, "navy_l", {"move": "0,2.2,0"})
for sgn, yy in ((-1, -2.47), (1, -2.33)):
    nrm = (0, sgn, 0)
    hc = ((TD_X0 + TD_X1) / 2, yy, 1.05)
    L.decal("hazard", hw.rrect(1.7, 0.1, 0.02, n=1, cy=-0.95), hc, nrm, lift=0.004)
    L.decal("navy", hw.rrect(1.24, 0.84, 0.06, n=2, cy=0.15), hc, nrm, lift=0.004)   # 금테 안쪽까지만 (금테와 겹치지 않게)
    L.ring("gold", hw.rrect(1.3, 0.9, 0.08, n=2, cy=0.15), hw.rrect(1.24, 0.84, 0.06, n=2, cy=0.15), hc, nrm, lift=0.006)
    L.logo((hc[0], yy, 1.2), 0.42, nrm, disc=None, lift=0.008)
    L.decal("glow", hw.stadium(0.6, 0.05, cy=0.75), hc, nrm, lift=0.006)
PORTS = [0.05, 1.95, 3.85, 5.75, 7.65]
L.wall("y", TX0, TY0, TY1, +1, 0.0, ZT, openings=[(y - 0.3, y + 0.3, 1.05, 1.65) for y in PORTS], pitch=1.9,
       insets=False)
for y in PORTS:
    L.porthole("y", TX0 - 0.1, y, 1.35, 0.3, 0.2, side=1, glass_group=f"WINDOW_troop_{PORTS.index(y) + 1}",
               outward="-1,0,0", size="0.6,0.6")
    L.col(TX0 - 0.12, TX0 - 0.08, y - 0.3, y + 0.3, 1.05, 1.65)
L.wall("x", TY0, TX0, TX1, +1, 0.0, ZT, openings=[(TD_X0, TD_X1, 0.0, 2.1)])
L.wall("y", TX1, TY0, TY1, -1, 0.0, ZT, pipes=True)
RD_X0, RD_X1 = -3.0, -1.0           # 사격장 문
L.wall("x", TY1, TX0, TX1, -1, 0.0, ZT, openings=[(RD_X0, RD_X1, 0.0, 2.1)])
L.ceiling(TX0, TX1, TY0, TY1, ZT, rib_axis="x", pitch=1.9, lamp_rows=[-3.2, 3.4], lamp_w=0.45, lamp_len=1.0,
          lamp_group=main_lights(4, "troop"))
L.logo((0.6, 4.4, 0.0), 1.5, (0, 0, 1), up=UP_Y, disc="navy", disc_scale=0.7, ring="gold", lift=0.008)
# 침상 (좌현, 머리가 벽 쪽) + 사물함 + 장비 거치대 + 벤치 + 보급 상자
BUNKS = [(PORTS[i] + PORTS[i + 1]) / 2 for i in range(len(PORTS) - 1)] + [9.5]
for i, y in enumerate(BUNKS):
    L.prop(f"bunk_{i + 1:02d}", (TX0 + 0.85, y, 0.0), "props/ship_bunk.glb", yaw=0)
    L.col(TX0 + 0.06, TX0 + 1.64, y - 0.45, y + 0.45, 0.0, 1.75)
for i, y in enumerate((-1.2, 0.15, 1.5, 2.85)):
    L.prop(f"locker_{i + 1:02d}", (TX1 - 0.3, y, 0.0), "props/ship_locker.glb", face=(TX1, y))
    L.col(TX1 - 0.55, TX1 - 0.06, y - 0.62, y + 0.62, 0.0, 1.8)
for i, y in enumerate((4.6, 6.4)):
    L.prop(f"gear_rack_{i + 1:02d}", (TX1 - 0.22, y, 0.0), "props/ship_gear_rack.glb", face=(TX1, y))
    L.col(TX1 - 0.48, TX1 - 0.06, y - 0.75, y + 0.75, 0.0, 1.6)
for i, (x, y) in enumerate(((0.6, 1.2), (0.6, 7.6))):
    L.prop(f"bench_{i + 1:02d}", (x, y, 0.0), "props/ship_bench.glb", yaw=0)
    L.col(x - 0.75, x + 0.75, y - 0.2, y + 0.2, 0.0, 0.34)
for i, (x, y, z, yaw) in enumerate(((5.45, 8.9, 0.0, 10), (5.5, 8.92, 0.42, -5), (4.55, 9.5, 0.0, 85))):
    L.prop(f"crate_{i + 1:02d}", (x, y, z), "props/ship_crate.glb", yaw=yaw)
    L.ocol((x, y, z), (0.6, 0.45, 0.42), yaw)        # 상자마다 돌린 COL (예전: 세 상자를 덮는 축 정렬 상자)
fcB = screen((2.9, TY1, 1.75), (0, -1, 0), 3.6, 1.25)
NB = (0, -1, 0)
L.decal("glow_d", hw.arc_pts(0.0, -2.2, 2.0, 60, 120, 20) + [(-1.0, -0.6), (1.0, -0.6)], fcB, NB, lift=0.006)
L.decal("ocean", hw.arc_pts(0.0, -2.2, 1.95, 62, 118, 20) + [(-0.92, -0.6), (0.92, -0.6)], fcB, NB, lift=0.008)
for (u, v) in ((-0.45, 0.02), (0.1, -0.12), (0.55, 0.0)):
    L.decal("amber", [(u, v + 0.07), (u - 0.06, v - 0.04), (u + 0.06, v - 0.04)], fcB, NB, lift=0.012)
for k in range(9):
    L.decal("glow", hw.circle(0.012, 6, -1.5 + k * 0.12, 0.45 - k * 0.05), fcB, NB, lift=0.012)
L.text("glow", "정찰 침투조", 0.13, on_screen(fcB, NB, 1.05, 0.42), NB, lift=0.012)
L.text("amber", "함내 대기", 0.11, on_screen(fcB, NB, 1.05, 0.22), NB, lift=0.012)
L.logo(on_screen(fcB, NB, -1.45, 0.38), 0.28, NB, disc=None, lift=0.012)
broadcast_screen((-5.6, TY1, 2.0), (0, -1, 0), w=1.1, h=0.62)
L.sign((-3.6, TY0, 2.2), (0, 1, 0), 2.0, 0.42, "병력 구획 B", size=0.16, logo=True, sub="정찰 침투조")
L.sign((RD_X0 - 0.95, TY1, 1.65), (0, -1, 0), 1.0, 0.32, "사격장", size=0.15)
# 정찰 침투조: 장비를 메고 벽 쪽에서 대기, 브리핑 보드 앞에서 수다
L.npc("bay_01", (-4.6, TY0 + 0.45, 0.0), SOLDIER, face=(-4.6, 3.0), props={"pose": "cross_arms", "look": "none"})
L.npc("bay_02", (-3.4, TY0 + 0.5, 0.0), SOLDIER, face=(-3.0, 3.0), props={"pose": "idle", "look": "none"})
L.npc("bay_03", (TX1 - 0.95, 3.75, 0.0), SOLDIER, face=(0.0, 3.75), props={"pose": "hands_hips", "look": "none"})
L.npc("bay_04", (2.3, 9.2, 0.0), SOLDIER, face=(3.5, 9.3), props={"pose": "idle", "look": "bay_05"})
L.npc("bay_05", (3.5, 9.3, 0.0), SOLDIER, face=(2.3, 9.2), props={"pose": "cross_arms", "look": "bay_04"})
L.npc("bay_06", (0.3, 0.75, 0.0), SOLDIER, face=(0.3, -2.0), props={"pose": "at_ease", "look": "none"})

# ================================================================ 4. 사격장 (range)
L.zone("range")
RX0, RX1, RY0, RY1 = -7.0, 5.9, 11.0, 60.0      # 대기실 폭 (X), 사로 끝 (Y)
ZR = 3.2
LANE_X1 = 2.0                                   # 사로 구역 오른쪽 벽 면
LANES = [-6.1, -4.3, -2.5, -0.7, 1.1]           # 사로 1~5 중심
PARTS = [-5.2, -3.4, -1.6, 0.2]                 # 칸막이
BOOTH_Y = 15.0                                  # 칸막이 시작 (대기실 끝)
CNT_Y0 = 16.1                                   # 사대 턱 뒤쪽 면
FIRE_Y = 16.6                                   # 사로 앞선 (거리 기준)
STAND_Y = 15.45                                 # 사대 노란 선
PA0, PA1 = 2.3, 3.9                             # 옆 통로 A (달리기, 나가는 길)
PB0, PB1 = 4.1, 5.9                             # 옆 통로 B (점프·앉기, 돌아오는 길)
PY1 = 38.2                                      # 옆 통로 끝 벽
DIV_Y1 = 36.6                                   # 가운데 벽 끝 (U자 돌기)
ZP = 2.6                                        # 옆 통로 천장
RITA_LANE = 2                                   # 리타 사로 (0부터: 3번 사로)
RL = LANES[RITA_LANE]

L.floor(RX0, RX1, RY0, BOOTH_Y, 0.0, grid=1.0)
L.floor(RX0, LANE_X1, BOOTH_Y, FIRE_Y, 0.0, grid=1.0)
L.floor(RX0, LANE_X1, FIRE_Y, RY1, 0.0, key="floor_d", lines=False)
L.floor(PA0, PB1, BOOTH_Y, PY1, 0.0, grid=0.8)
L.portal("x", (TY1 + RY0) / 2, (RD_X0 + RD_X1) / 2, RD_X1 - RD_X0, 2.1, 0.0, 0.4)
L.box("metal", RD_X0, RD_X1, TY1, RY0, -0.12, 0.0, col=True)
CD_Y0, CD_Y1 = 11.8, 13.4                       # 훈련 구획 문
# 벽: 대기실
L.wall("x", RY0, RX0, RX1, +1, 0.0, ZR, openings=[(RD_X0, RD_X1, 0.0, 2.1)])
L.wall("y", RX1, RY0, BOOTH_Y, -1, 0.0, ZR, openings=[(CD_Y0, CD_Y1, 0.0, 2.1)], pitch=2.0)
L.wall("y", RX0, RY0, RY1, +1, 0.0, ZR, pitch=2.5)
# 사로 오른쪽 안전벽 (사로 쪽 면)과 옆 통로 벽들
L.wall("y", LANE_X1, BOOTH_Y, RY1, -1, 0.0, ZR, pitch=2.5, t=0.15)
L.wall("y", PA0, BOOTH_Y, PY1, +1, 0.0, ZP, pitch=2.0, t=0.15, cornice=False, insets=False)
L.wall("y", PB1, BOOTH_Y, PY1, -1, 0.0, ZP, pitch=2.0, cornice=False, insets=False)
L.wall("y", PA1, BOOTH_Y, DIV_Y1, -1, 0.0, ZP, pitch=2.0, t=0.1, cornice=False, insets=False)
L.wall("y", PB0, BOOTH_Y, DIV_Y1, +1, 0.0, ZP, pitch=2.0, t=0.1, cornice=False, insets=False)
L.wall("x", PY1, PA0, PB1, -1, 0.0, ZP, cornice=False, insets=False, pillars=False)
wall_cap(PA1 - 0.04, PB0 + 0.04, DIV_Y1 - 0.08, DIV_Y1 + 0.08, ZP)
wall_cap(PA1 - 0.04, PB0 + 0.04, BOOTH_Y - 0.08, BOOTH_Y + 0.08, ZP)
wall_cap(LANE_X1 - 0.02, PA0 + 0.02, BOOTH_Y - 0.08, BOOTH_Y + 0.08, ZR)
# 옆 통로 입구 위 보: 사로 쪽 끝면은 안전벽 면(LANE_X1)보다 2 cm 안 (벽 속), 윗면은 벽 윗면보다 1 cm 위
L.box("navy", LANE_X1 + 0.02, RX1, BOOTH_Y - 0.1, BOOTH_Y + 0.1, ZP, ZR + 0.01)
L.col(LANE_X1, RX1, BOOTH_Y - 0.1, BOOTH_Y + 0.1, ZP, ZR)
L.box("gold", LANE_X1 + 0.02, RX1, BOOTH_Y - 0.11, BOOTH_Y + 0.11, ZP - 0.04, ZP, kind="detail")
L.wall("x", RY1, RX0, LANE_X1, -1, 0.0, ZR, pillars=False, insets=False, strip=False)
L.ceiling(RX0, RX1, RY0, BOOTH_Y, ZR, rib_axis="y", pitch=2.15, lamp_rows=[13.0], lamp_group=main_lights(5, "range"))
L.ceiling(RX0, LANE_X1, BOOTH_Y, RY1, ZR, rib_axis="x", pitch=4.0, lamp_rows=LANES, lamp_w=0.3, lamp_len=0.9,
          lamp_group=main_lights(6, "range_lanes"))
L.ceiling(PA0, PB1, BOOTH_Y, PY1, ZP, rib_axis="x", pitch=2.0, lamp_rows=[(PA0 + PA1) / 2, (PB0 + PB1) / 2],
          lamp_w=0.25, lamp_len=0.8, lamp_group=main_lights(7, "range_passage"))
# 사로 바닥: 구분선, 5 m 눈금, 거리선 10/20/40, 거리 숫자
for x in PARTS:
    L.strip("paper", (x, FIRE_Y + 0.1, 0.0), (x, RY1 - 2.4, 0.0), 0.05, (0, 0, 1), lift=0.01)
    for k in range(1, 9):
        y = FIRE_Y + k * 5
        L.strip("paper", (x - 0.15, y, 0.0), (x + 0.15, y, 0.0), 0.04, (0, 0, 1), lift=0.011)
DIST = {10: FIRE_Y + 10, 20: FIRE_Y + 20, 40: FIRE_Y + 40}
for d, y in DIST.items():
    with L.in_group(HOLO_RANGE, holo=1, on=1):
        L.strip("glow", (RX0 + 0.1, y, 0.0), (LANE_X1 - 0.1, y, 0.0), 0.08, (0, 0, 1), lift=0.012)
    for x in LANES:
        L.text("paper", f"{d}", 0.5, (x, y - 0.5, 0.0), (0, 0, 1), up=UP_Y, lift=0.012)
    for xw, nrm in ((RX0, (1, 0, 0)), (LANE_X1, (-1, 0, 0))):
        L.sign((xw, y, 1.75), nrm, 0.9, 0.5, f"{d} m", size=0.3, depth=0.1)
    L.box("metal", -2.54, -2.46, y - 0.04, y + 0.04, 2.95, ZR, layer="ceil")
    L.box("navy", -2.7, -2.3, y - 0.06, y + 0.06, 2.93, 2.97, layer="ceil")            # 홀로 투사기
    with L.in_group(HOLO_RANGE):                                                       # 매달린 거리 표지 (홀로)
        L.box("holo", -3.7, -1.3, y - 0.01, y + 0.01, 2.5, 2.92, layer="ceil")
        L.box("glow", -3.72, -1.28, y - 0.015, y + 0.015, 2.48, 2.5, layer="ceil")
        for sgn in (-1, 1):
            L.text("glow", f"{d} m", 0.28, (-2.5, y + sgn * 0.012, 2.71), (0, sgn, 0), lift=0.004, layer="ceil")
# 사대: 턱(0.75 m, 엘프 눈높이 0.9 m 아래), 칸막이(1.45 m), 노란 선, 사로 번호
L.box("navy", RX0, LANE_X1, CNT_Y0, FIRE_Y, 0.0, 0.68, col=False)
L.box("floor", RX0, LANE_X1, CNT_Y0 - 0.04, FIRE_Y + 0.04, 0.68, 0.75)
L.box("gold", RX0, LANE_X1, CNT_Y0 - 0.06, CNT_Y0 - 0.03, 0.70, 0.74, kind="detail")
L.col(RX0, LANE_X1, CNT_Y0, FIRE_Y, 0.0, 0.75)
edges = [RX0] + PARTS + [LANE_X1]
for i, x in enumerate(LANES):
    L.logo_plate((x - 0.5, CNT_Y0, 0.42), 0.24, (0, -1, 0), thick=0.03)
    L.sign((x + 0.32, CNT_Y0, 0.42), (0, -1, 0), 0.4, 0.3, f"{i + 1}", size=0.22, depth=0.03)
    L.box("metal", x - 0.32, x + 0.32, CNT_Y0 + 0.05, CNT_Y0 + 0.4, 0.75, 0.8, kind="detail")
    with L.in_group(HOLO_RANGE):
        L.decal("glow", hw.rrect(0.46, 0.06, 0.02, n=1), (x, CNT_Y0 + 0.08, 0.8), (0, 0, 1), up=UP_Y, lift=0.003)
    x0, x1 = edges[i] + 0.1, edges[i + 1] - 0.1
    L.strip("hazard", (x0, STAND_Y, 0.0), (x1, STAND_Y, 0.0), 0.08, (0, 0, 1), lift=0.01)
    L.decal("navy_d", hw.rrect(x1 - x0 - 0.1, 0.55, 0.06, n=2), (x, (STAND_Y + CNT_Y0) / 2 + 0.06, 0.0), (0, 0, 1),
            up=UP_Y, lift=0.008)
    L.text("hazard", f"{i + 1}", 0.32, (x, BOOTH_Y - 0.45, 0.0), (0, 0, 1), up=UP_Y, lift=0.01)
for x in PARTS:
    L.box("navy_l", x - 0.04, x + 0.04, BOOTH_Y, FIRE_Y - 0.005, 0.0, 1.45)   # 끝면은 사대 턱 앞면보다 5 mm 안
    L.col(x - 0.04, x + 0.04, BOOTH_Y, FIRE_Y, 0.0, 1.45)
    L.box("metal", x - 0.06, x + 0.06, BOOTH_Y, FIRE_Y, 1.45, 1.52)
    L.box("gold", x - 0.065, x + 0.065, BOOTH_Y - 0.005, BOOTH_Y + 0.08, 0.0, 1.525, kind="detail")
    for sgn in (-1, 1):
        L.decal("hull_d", hw.rrect(1.2, 0.9, 0.08, n=2), (x + sgn * 0.04, 15.85, 0.75), (sgn, 0, 0), lift=0.003)
# 사로 끝 방탄 경사판, 천장 방음판, 표적 레일
LC = (RX0 + LANE_X1) / 2
L.rbox("navy_d", (LC, RY1 - 1.0, 1.2), (LANE_X1 - RX0 + 0.1, 0.25, 3.0), rot=(-35, 0, 0))   # 양 끝은 벽 속 (바닥 옆면과 겹치지 않게)
L.box("metal", RX0, LANE_X1, RY1 - 2.3, RY1 - 0.2, 0.0, 0.3)
L.logo_plate((LC, RY1, 2.55), 0.8, (0, -1, 0), thick=0.06)
for y in (21.0, 31.0, 41.0, 51.0):
    L.rbox("navy", (LC, y, ZR - 0.35), (LANE_X1 - RX0 - 0.1, 0.06, 0.7), rot=(40, 0, 0), layer="ceil")
for x in LANES:
    L.box("metal", x - 0.04, x + 0.04, FIRE_Y, RY1 - 1.5, ZR - 0.1, ZR, layer="ceil")
# 옆 통로 A (T03 달리기): 진행 화살, 끝 표시선
A_MID = (PA0 + PA1) / 2
B_MID = (PB0 + PB1) / 2
SPRINT_END = 35.0
for y in (16.5, 21.0, 25.5, 30.0):
    floor_chevrons((A_MID, y), (0, 1), n=3, w=0.45, group=HOLO_RANGE)
L.strip("hazard", (PA0 + 0.08, SPRINT_END, 0.0), (PA1 - 0.08, SPRINT_END, 0.0), 0.14, (0, 0, 1), lift=0.01)
L.strip("glow", (PA0 + 0.08, SPRINT_END + 0.12, 0.0), (PA1 - 0.08, SPRINT_END + 0.12, 0.0), 0.04, (0, 0, 1),
        lift=0.01)
L.sign((A_MID, PY1, 1.7), (0, -1, 0), 1.2, 0.36, "달리기 끝", size=0.15)
L.sign((A_MID, BOOTH_Y + 0.1, 2.3), (0, 1, 0), 1.3, 0.3, "기동 훈련로", size=0.13, layer=None)
# 옆 통로 B (T04 점프: 탄약 상자 0.42 m + 옆에 못 넘는 높은 더미, T05 앉기: 낮은 배관 아래 0.88 m)
CR_Y = 31.4
for i, x in enumerate((PB0 + 0.37, PB0 + 0.97)):
    L.prop(f"jump_crate_{i + 1:02d}", (x, CR_Y, 0.0), "props/ship_crate.glb", yaw=0)
L.col(PB0 + 0.07, PB0 + 1.27, CR_Y - 0.225, CR_Y + 0.225, 0.0, 0.42)
for k in range(3):
    L.prop(f"tall_crate_{k + 1:02d}", (PB1 - 0.29, CR_Y, k * 0.42), "props/ship_crate.glb", yaw=90 + (k - 1) * 4)
L.col(PB0 + 1.27, PB1, CR_Y - 0.3, CR_Y + 0.3, 0.0, 1.26)
for y in (CR_Y + 1.6, CR_Y - 1.9):
    floor_chevrons((B_MID, y), (0, -1), n=2, key="hazard", w=0.5)
PIPE_Y = 24.9
PIPE_GAP = 0.88
L.cyl("metal", (PB0 - 0.05, PIPE_Y, PIPE_GAP + 0.13), (PB1 + 0.05, PIPE_Y, PIPE_GAP + 0.13), 0.13, verts=16)
L.cyl("navy", (PB0 - 0.05, PIPE_Y + 0.2, PIPE_GAP + 0.42), (PB1 + 0.05, PIPE_Y + 0.2, PIPE_GAP + 0.42), 0.1, verts=14)
L.cyl("metal", (PB0 - 0.05, PIPE_Y - 0.18, PIPE_GAP + 0.46), (PB1 + 0.05, PIPE_Y - 0.18, PIPE_GAP + 0.46), 0.08,
      verts=12)
for x in (PB0 + 0.45, PB1 - 0.45):
    L.cyl("hazard", (x - 0.05, PIPE_Y, PIPE_GAP + 0.13), (x + 0.05, PIPE_Y, PIPE_GAP + 0.13), 0.135, verts=16,
          kind="detail")
L.cyl("gold", (B_MID - 0.04, PIPE_Y, PIPE_GAP + 0.13), (B_MID + 0.04, PIPE_Y, PIPE_GAP + 0.13), 0.145, verts=16,
      kind="detail")
L.cyl("steel", (B_MID, PIPE_Y, PIPE_GAP + 0.26), (B_MID, PIPE_Y, PIPE_GAP + 0.36), 0.03, verts=8, kind="detail")
L.obj("hazard", hw.torus("valve", 0.08, 0.012, loc=(B_MID, PIPE_Y, PIPE_GAP + 0.37), seg=14, rseg=4), kind="detail")
for x in (PB0 + 0.03, PB1 - 0.03):
    L.box("navy", x - 0.03, x + 0.03, PIPE_Y - 0.3, PIPE_Y + 0.35, PIPE_GAP - 0.05, PIPE_GAP + 0.6, kind="detail")
L.col(PB0, PB1, PIPE_Y - 0.3, PIPE_Y + 0.32, PIPE_GAP, ZP)
for y in (PIPE_Y + 1.4, PIPE_Y - 1.6):
    floor_chevrons((B_MID, y), (0, -1), n=2, key="hazard", w=0.5)
L.text("hazard", "0.88", 0.12, (B_MID, PIPE_Y - 0.14, PIPE_GAP + 0.13), (0, -1, 0), lift=0.14)
# 대기실: 장비 거치대, 기록판(캐시가 기대는 곳), 소화기, 탄약 상자, 벤치, 바닥 로고
for i, x in enumerate((-6.15, -4.55)):
    L.prop(f"range_rack_{i + 1:02d}", (x, RY0 + 0.22, 0.0), "props/ship_gear_rack.glb", face=(x, RY0))
    L.col(x - 0.75, x + 0.75, RY0 + 0.06, RY0 + 0.48, 0.0, 1.6)
BOARD = (-0.15, 14.6)               # 기록판 (사대 옆, 4번 사로 칸 뒤). 미션이 MARK_record_board 앞에 기록 화면을 띄운다
# 4번 사로 칸 입구(칸막이 x -1.6 끝 ↔ 판 서쪽 끝, 대각선 0.77 m): 예전 x -0.55에서는 0.47 m라 캡슐(반지름 0.22 + 둘레 틈 0.02)이
# 못 지나가고 V자 틈에 끼었다. 내비 침식(0.22 m, 0.11 m 칸)은 대각선 틈이 0.7 m 안팎은 되어야 이어진다(0.68 m 끊김, 0.77 m 이어짐).
# 동쪽(칸막이 x 0.2 끝 ↔ 판 뒷면 0.28 m)은 캡슐·내비 모두 막힌다
BW, BH, BZ = 1.26, 0.96, 1.45       # 화면 크기·중심 높이 (미션 화면 1.2 x 0.9, 높이 1.45와 맞춤)
MK_Y = BOARD[1] - 0.065             # 마커 면 (미션 화면은 마커 앞 0.03 m)
for sx in (-1, 1):
    L.box("metal", BOARD[0] + sx * 0.45 - 0.03, BOARD[0] + sx * 0.45 + 0.03, MK_Y - 0.03, MK_Y + 0.03, 0.0, BZ - 0.4)
    L.box("navy", BOARD[0] + sx * 0.45 - 0.12, BOARD[0] + sx * 0.45 + 0.12, MK_Y - 0.2, MK_Y + 0.2, 0.0, 0.05)
NK = (0, -1, 0)
L.group("record_board_face", mode="node")
fcK = screen((BOARD[0], BOARD[1], BZ), NK, BW, BH, depth=0.06)
L.decal("navy_l", hw.rrect(BW + 0.12, BH + 0.12, 0.08, n=2), (BOARD[0], BOARD[1], BZ), (0, 1, 0), lift=0.002)
L.text("glow", "훈련 코스 기록", 0.085, on_screen(fcK, NK, 0.0, 0.36), NK, lift=0.01)
L.strip("gold", on_screen(fcK, NK, -0.58, 0.28), on_screen(fcK, NK, 0.58, 0.28), 0.012, NK, lift=0.01)
L.text("amber", "1. 캐시", 0.09, on_screen(fcK, NK, -0.55, 0.16), NK, lift=0.01, align="LEFT")
L.text("amber", "33.70", 0.1, on_screen(fcK, NK, 0.55, 0.16), NK, lift=0.01, align="RIGHT")
for k in range(3):
    L.strip("glow_d", on_screen(fcK, NK, -0.55, 0.0 - k * 0.13), on_screen(fcK, NK, 0.55, 0.0 - k * 0.13),
            0.008, NK, lift=0.008)
L.group(None)
for sx in (-1, 1):                                                      # 기둥 (받침 0.24)
    L.col(BOARD[0] + sx * 0.45 - 0.12, BOARD[0] + sx * 0.45 + 0.12, MK_Y - 0.2, MK_Y + 0.2, 0.0, BZ - 0.4)
L.col(BOARD[0] - BW / 2 - 0.06, BOARD[0] + BW / 2 + 0.06, BOARD[1] - 0.12, BOARD[1] + 0.12, BZ - BH / 2 - 0.06, BZ + 0.55)   # 판 (틀 1.38 x 1.08)
L.mark("record_board", (BOARD[0], MK_Y, 0.0), face=(BOARD[0], MK_Y - 5))
L.attach("record_board_face", "MARK_record_board")
EXT = (RX0 + 0.12, 14.3, 0.0)       # 소화기 (T01 재시도 '불 꺼진 물체')
L.prop("extinguisher_01", EXT, "props/ship_extinguisher.glb", face=(EXT[0] + 1, EXT[1]))
L.mark("extinguisher", (EXT[0] + 0.12, EXT[1], 0.62))
L.col(RX0, RX0 + 0.3, EXT[1] - 0.15, EXT[1] + 0.15, 0.0, 0.9)
for i, (x, y, z, yaw) in enumerate(((RX1 - 0.4, 14.0, 0.0, 90), (RX1 - 0.4, 14.05, 0.42, 84),
                                     (RX1 - 0.35, RY0 + 0.4, 0.0, 0))):
    L.prop(f"range_crate_{i + 1:02d}", (x, y, z), "props/ship_crate.glb", yaw=yaw)
    L.ocol((x, y, z), (0.6, 0.45, 0.42), yaw)
L.prop("range_bench_01", (-5.2, 13.2, 0.0), "props/ship_bench.glb", yaw=0)
L.col(-5.95, -4.45, 13.0, 13.4, 0.0, 0.34)
L.logo((-2.5, 12.9, 0.0), 0.9, (0, 0, 1), up=UP_Y, disc="navy", disc_scale=0.7, ring="gold", lift=0.008)
broadcast_screen((2.6, RY0, 2.05), (0, 1, 0), w=1.1, h=0.62)
L.sign((RX1, 12.6, 2.5), (-1, 0, 0), 1.6, 0.36, "훈련 구획", size=0.15, logo=True)
# 무전 스피커와 경고등
speaker("radio_01", (RX0, 12.0, 2.45), (1, 0, 0))
alert_light("alert_01", (RX0, 13.3, 2.62), (1, 0, 0))
alert_light("alert_02", (LANE_X1, 17.5, 2.62), (-1, 0, 0))
alert_light("alert_03", (RX0, 31.0, 2.62), (1, 0, 0))
alert_light("alert_04", (LANE_X1, 31.0, 2.62), (-1, 0, 0))

# 리타 시작 (대기실, 사대 3.1 m 뒤), 캐시 (기록판 옆에서 팔짱)
SPAWN = (RL + 0.3, 12.6, 0.0)
L.spawn("player", SPAWN, face=(SPAWN[0], SPAWN[1] + 10))
L.npc("rita", SPAWN, "characters/rita_prologue.glb", face=(SPAWN[0], SPAWN[1] + 10),
      props={"pose": "idle", "role": "cinematic", "name": "리타", "look": "none"})
CATHY = (BOARD[0] + BW / 2 + 0.3, BOARD[1] - 0.25, 0.0)
L.npc("cathy", CATHY, "characters/cathy_prologue.glb", face=(SPAWN[0], SPAWN[1]),
      props={"pose": "cross_arms", "look": "player", "name": "캐시"})
L.wp("cathy_board", CATHY, face=SPAWN)
L.wp("cathy_booth", (RL + 1.05, 14.7, 0.0), face=(RL, 15.8))
L.wp("cathy_passage", (A_MID + 0.6, 14.2, 0.0), face=(A_MID, 20.0))
L.wp("cathy_door", (RX1 - 1.0, 12.6, 0.0), face=(RX1 + 1.0, 12.6))
L.wp("cathy_course", (7.4, 12.2, 0.0), face=(8.0, 20.0))
# 다른 사로의 병사들
L.npc("range_01", (LANES[0], STAND_Y - 0.1, 0.0), SOLDIER, face=(LANES[0], 40.0), props={"pose": "idle", "look": "none"})
L.npc("range_02", (-5.4, 13.6, 0.0), SOLDIER, face=(-4.3, 13.2), props={"pose": "hands_hips", "look": "range_03"})
L.npc("range_03", (-4.3, 13.2, 0.0), SOLDIER, face=(-5.4, 13.6), props={"pose": "idle", "look": "range_02"})
# 표적 (리타 사로 x -3.3..-1.7). 미션 그룹: ads(불 들어오는 고정 표적, T01 찾기·T07 정조준), hip(T06 5~8 m),
# pistol(T10 11~15 m), decor(옆 사로 고정 표적, 불 꺼짐: T01 재시도 판정)
for i, (dx, d) in enumerate(((-0.5, 25.0), (0.45, 29.5), (-0.1, 33.5))):
    L.target(f"ads_{i + 1}", (RL + dx, FIRE_Y + d, 0.0), "ads", kind="static", face=(RL + dx, 0.0), props={"lamp": 1})
for i, (dx, d) in enumerate(((-0.5, 5.5), (0.4, 7.0), (-0.1, 8.2))):
    L.target(f"hip_{i + 1}", (RL + dx, FIRE_Y + d, 0.0), "hip", face=(RL, STAND_Y))
for i, (dx, d) in enumerate(((-0.55, 11.0), (0.5, 13.0), (0.0, 15.0))):
    L.target(f"pistol_{i + 1}", (RL + dx, FIRE_Y + d, 0.0), "pistol", face=(RL, STAND_Y))
for i, (ln, d) in enumerate(((1, 27.0), (3, 30.0), (1, 20.0), (3, 17.0), (0, 24.0), (4, 26.0))):
    L.target(f"decor_{i + 1}", (LANES[ln], FIRE_Y + d, 0.0), "decor", kind="static", face=(LANES[ln], 0.0))
# 카메라: 리타와 캐시 클로즈업 → 기록판 → 리타의 눈 (마지막 점 = SPAWN_player 눈높이 0.9 m)
EYE = (SPAWN[0], SPAWN[1], 0.9)
CF = (CATHY[0], CATHY[1], 0.92)
L.cam_rail("closeup", [
    (0.0, (SPAWN[0] - 0.5, RY0 + 0.35, 1.55), (BOARD[0] + 0.3, BOARD[1], 1.0), 45),
    (2.5, (SPAWN[0] + 0.85, 13.25, 1.02), CF, 30),
    (4.5, (BOARD[0] + 0.1, 13.65, 1.22), (BOARD[0], BOARD[1], 1.42), 30),
    (6.5, (SPAWN[0] + 0.1, 13.55, 0.97), (EYE[0], EYE[1] + 0.02, 0.9), 28),
    (8.3, (SPAWN[0] - 0.8, 12.95, 0.96), (EYE[0], EYE[1] + 0.25, 0.9), 34),
    (9.8, (SPAWN[0], 12.05, 0.93), (EYE[0], EYE[1] + 2.0, 0.9), 50),
    (11.0, EYE, (EYE[0], EYE[1] + 10.0, 0.9), 70),
])

# ================================================================ 5. 훈련 구획 (course)
L.zone("course")
KX0, KX1, KY0, KY1 = 6.3, 22.3, 11.0, 41.0
ZK = 4.6


def K(rx):
    return KX0 + rx


L.group(HOLO_COURSE, holo=1, on=1)
L.group(None)
L.floor(KX0, KX1, KY0, KY1, 0.0, key="navy_d", line="glow_d", grid=2.0, line_group=HOLO_COURSE)
L.portal("y", (RX1 + KX0) / 2, (CD_Y0 + CD_Y1) / 2, CD_Y1 - CD_Y0, 2.1, 0.0, 0.4)
L.box("metal", RX1, KX0, CD_Y0, CD_Y1, -0.12, 0.0, col=True)
L.wall("y", KX0, KY0, KY1, +1, 0.0, ZK, openings=[(CD_Y0, CD_Y1, 0.0, 2.1)], style="holo", pitch=3.0,
       inset_group=HOLO_COURSE)
L.wall("y", KX1, KY0, KY1, -1, 0.0, ZK, style="holo", pitch=3.0, inset_group=HOLO_COURSE)
L.wall("x", KY0, KX0, KX1, +1, 0.0, ZK, style="holo", pitch=3.2, inset_group=HOLO_COURSE)
L.wall("x", KY1, KX0, KX1, -1, 0.0, ZK, style="holo", pitch=3.2, inset_group=HOLO_COURSE)
L.ceiling(KX0, KX1, KY0, KY1, ZK, key="navy_d", rib_axis="x", pitch=3.0, lamp_rows=[K(1.6), K(8.0), K(14.1)],
          lamp_w=0.35, lamp_len=1.6, rib_key="navy", lamp_group=main_lights(8, "course"))
# 섬 (표적 구역): 서·북 벽 2.0 m, 남 벽 2.7 m(위 통로 옆), 동쪽은 넘겨 쏘는 0.7 m 엄폐벽
IX0, IX1, IY0, IY1 = K(3.2), K(12.2), 15.1, 34.4
holo_wall(IX0, IX0 + 0.2, IY0, IY1, 2.0)
holo_wall(IX0, IX1, IY1 - 0.2, IY1, 2.0, number=3)
holo_wall(IX0, IX1, IY0 - 0.2, IY0, 2.7)
pad_block(IX1 - 0.2, IX1, IY0, IY1 - 0.2, 0.7)
# 달리기 직선로의 지그재그 벽 1·2
holo_wall(KX0, K(2.0), 21.0, 21.2, 1.6, number=1)
holo_wall(K(1.2), IX0, 27.0, 27.2, 1.6, number=2)
# 위 통로 (z 1.08): 동쪽 계단으로 올라 서쪽 끝 결승선을 지나 대기실로 뛰어내린다 (한 방향)
PZ = 1.08
PX0, PYN = K(4.0), 14.9
L.box("pad", PX0, KX1, KY0, PYN, 0.0, PZ - 0.06)
L.box("floor", PX0, KX1, KY0, PYN, PZ - 0.06, PZ, col=False)
L.col(PX0, KX1, KY0, PYN, 0.0, PZ)
L.box("gold", PX0 - 0.02, PX0 + 0.02, KY0, PYN + 0.004, PZ - 0.065, PZ - 0.02, kind="detail")   # 판 끝면보다 4 mm 앞
L.strip("hazard", (PX0 + 0.08, KY0 + 0.05, PZ), (PX0 + 0.08, PYN - 0.05, PZ), 0.12, (0, 0, 1), lift=0.006)
for k in range(1, 10):
    L.strip("glow_d", (PX0 + k * 1.2, KY0, PZ), (PX0 + k * 1.2, PYN, PZ), 0.02, (0, 0, 1), lift=0.005)
for y in (11.9, 12.9, 13.9):
    floor_chevrons((PX0 - 0.35, y), (-1, 0), n=1, key="hazard", w=0.5, z=0.0)
    floor_chevrons((K(10.0), y), (-1, 0), n=3, z=PZ, group=HOLO_COURSE)
ST_LOW = PYN + 5 * 0.32
L.stairs("y", IX1, KX1, ST_LOW, -1, 0.0, PZ, 6, 0.32, key="pad", top_key="floor")
L.railing([(IX1 - 0.1, PYN - 0.12), (PX0 + 0.3, PYN - 0.12)], PZ, h=0.7)
# 출발선 (대기실 → 직선로), 결승선 (위 통로 서쪽 끝)
gate("x", IY0 - 0.1, KX0 + 0.12, IX0 - 0.02, 2.3, "출발")
gate("y", PX0 + 0.75, KY0 + 0.15, PYN - 0.15, 2.2, "결승", z0=PZ)
for y in (16.4, 23.6, 30.0):
    floor_chevrons((K(1.6), y), (0, 1), n=3, group=HOLO_COURSE)
# 북쪽 통로: 점프 상자 0.45 → 0.90, 앉기 굴(틈 0.88 m, 길이 3 m). 3번 벽 옆 0.55 m 틈은 지름길(이스터 에그)
NY0, NY1 = IY1, KY1
pad_block(K(5.0), K(5.8), NY0, NY1, 0.45)
pad_block(K(5.8), K(6.8), NY0, NY1, 0.90)
for y in (35.6, 37.7, 39.8):
    L.strip("hazard", (K(5.02), y - 0.3, 0.45), (K(5.02), y + 0.3, 0.45), 0.05, (0, 0, 1), lift=0.005)
SHORTCUT = 0.55
crawl_tunnel(K(8.6), K(11.6), NY0 + SHORTCUT + 0.08, NY1)
for y in (35.9, 37.9, 39.9):
    floor_chevrons((K(1.6), y), (1, 0), n=2, group=HOLO_COURSE)
    floor_chevrons((K(7.7), y), (1, 0), n=2, group=HOLO_COURSE)
    floor_chevrons((K(12.6), y), (1, 0), n=2, group=HOLO_COURSE)
L.sign((K(8.0), KY1, 2.9), (0, -1, 0), 4.2, 0.6, "모의 전투 훈련 구획", size=0.3, logo=True, depth=0.06)
# 동쪽 통로 (사격 구간): 엄폐벽 너머 섬 안 표적, 앉기 차단막, 점프 상자
crouch_bar(IX1, KX1, 22.6, 23.4)
pad_block(IX1, KX1, 18.8, 19.8, 0.45)
for y in (37.0, 30.5, 26.0, 21.2, 17.6):
    floor_chevrons((K(14.1), y), (0, -1), n=2, group=HOLO_COURSE)
# 섬 가운데 홀로 투사기 (장식) + 바닥 로고
HP = (K(7.7), 24.6)
L.cyl("metal", (HP[0], HP[1], 0.0), (HP[0], HP[1], 0.5), 0.45, verts=20, r2=0.32)
L.cyl("navy", (HP[0], HP[1], 0.5), (HP[0], HP[1], 0.6), 0.5, verts=20)
with L.in_group(HOLO_COURSE):
    L.cyl("beam", (HP[0], HP[1], 0.6), (HP[0], HP[1], 3.4), 0.3, verts=16, cap=False, kind="fine")
    for z in (1.2, 2.0, 2.8):
        L.obj("glow", hw.torus("emit", 0.42, 0.015, loc=(HP[0], HP[1], z), seg=20, rseg=4), kind="fine")
L.col(HP[0] - 0.45, HP[0] + 0.45, HP[1] - 0.45, HP[1] + 0.45, 0.0, 0.6)
L.logo((K(7.7), 29.6, 0.0), 1.6, (0, 0, 1), up=(1, 0, 0), disc="navy", disc_scale=0.7, ring="glow", lift=0.008)
L.logo((K(1.6), 12.9, 0.0), 0.9, (0, 0, 1), up=UP_Y, disc="navy", disc_scale=0.7, ring="gold", lift=0.008)
# 타임 어택 팝업 표적 10개 (섬 안 8 + 직선로 끝 1 + 북동 모퉁이 1)
COURSE_T = [(K(1.6), 40.4, (K(1.6), 30.0)), (K(15.0), 40.4, (K(9.0), 37.6)),
            (K(10.4), 33.0, None), (K(6.9), 31.4, None), (K(5.0), 27.0, None), (K(9.4), 25.6, None),
            (K(9.2), 21.8, None), (K(6.3), 19.6, None), (K(10.6), 17.4, None), (K(5.0), 16.6, None)]
for i, (x, y, f) in enumerate(COURSE_T):
    L.target(f"course_{i + 1:02d}", (x, y, 0.0), "course", face=f or (K(14.1), y + (1.5 if y < 28 else -1.5)))
# 섬 안을 오가는 이동 표적 (경로 WP_course_mv_*)
L.target("course_mv", (K(8.0), 28.8, 0.0), "course", kind="moving", face=(K(14.1), 28.8),
         props={"path": "course_mv", "speed": 1.3})
L.wp("course_mv_01", (K(8.0), 32.4, 0.0))
L.wp("course_mv_02", (K(8.0), 22.6, 0.0))
speaker("radio_02", (K(2.6), KY0, 3.35), (0, 1, 0))
alert_light("alert_05", (KX0, 30.0, 3.4), (1, 0, 0))
alert_light("alert_06", (KX1, 26.0, 3.4), (-1, 0, 0))
L.zone("troop")
alert_light("alert_07", (TX1, 8.6, 2.45), (-1, 0, 0))

# ================================================================ 튜토리얼 목표·트리거 (이름: 미션 prologue.ts 규약)
L.zone("range")
BX = [(edges[i] + 0.05, edges[i + 1] - 0.05) for i in range(5)]
L.mark("range_line", (RL, STAND_Y, 0.0))                          # T02·T06: 사대 노란 선
L.trig("range_line", BX[RITA_LANE][0], BX[RITA_LANE][1], STAND_Y - 0.35, CNT_Y0, 0.0, 2.2)
L.trig("lane_left", BX[RITA_LANE - 1][0], BX[RITA_LANE - 1][1], BOOTH_Y, CNT_Y0, 0.0, 2.2)
L.trig("lane_right", BX[RITA_LANE + 1][0], BX[RITA_LANE + 1][1], BOOTH_Y, CNT_Y0, 0.0, 2.2)
L.mark("sprint_start", (A_MID, BOOTH_Y + 0.4, 0.0))               # T03: 옆 통로 A 입구 → 끝 표시선
L.trig("sprint_start", PA0, PA1, BOOTH_Y - 0.6, BOOTH_Y + 1.0, 0.0, 2.2)
L.mark("sprint_end", (A_MID, SPRINT_END, 0.0))
L.trig("sprint_end", PA0, PA1, SPRINT_END, SPRINT_END + 0.8, 0.0, 2.2)
L.mark("jump", (B_MID, CR_Y, 0.42))                               # T04: 탄약 상자 (0.42 m)
L.trig("jump_zone", PB0, PB1, CR_Y - 0.5, CR_Y + 1.2, 0.0, 2.2)
L.trig("jump_done", PB0, PB1, CR_Y - 2.4, CR_Y - 0.6, 0.0, 2.2)
L.mark("crouch", (B_MID, PIPE_Y, 0.0))                            # T05: 배관 밑 (틈 0.88 m)
L.trig("crouch_zone", PB0, PB1, PIPE_Y - 0.35, PIPE_Y + 0.4, 0.0, 0.88)
L.trig("crouch_done", PB0, PB1, PIPE_Y - 2.4, PIPE_Y - 0.8, 0.0, 2.2)
L.zone("course")
L.mark("course_start", (K(1.6), IY0 - 0.7, 0.0))                  # T11: 출발선
L.trig("course_start", KX0, IX0, IY0 - 1.3, IY0 + 0.4, 0.0, 2.2)
L.mark("course_cp1", (K(14.1), 37.7, 0.0))                        # T12: 반환점 1 (북동 모퉁이)
L.trig("course_cp1", IX1, KX1, 35.0, KY1, 0.0, 2.2)
L.mark("course_cp2", (K(14.1), ST_LOW + 0.6, 0.0))                # 반환점 2 (동쪽 계단 아래)
L.trig("course_cp2", IX1, KX1, ST_LOW, ST_LOW + 1.4, 0.0, 2.2)
L.mark("course_end", (PX0 + 0.75, 12.95, PZ))                     # 결승
L.trig("course_end", PX0, PX0 + 1.4, KY0, PYN, PZ, PZ + 2.2)
L.wp("cathy_finish", (K(0.8), 13.6, 0.0), face=(PX0, 13.0))

# 카메라: 함내 이동 (함교 문 → 통로 → 승강 구간 → 병력 구획 → 사격장 문)
L.zone("atrium")
L.cam_rail("descent", [
    (0.0, (DOOR_X, BY1 + 0.6, ZU + 1.05), (DOOR_X, AY0, ZU + 1.0), 55),
    (2.4, (DOOR_X, AY0 + 0.6, ZU + 1.2), (-6.5, -7.6, ZU + 1.0), 55),
    (4.8, (0.2, -11.6, ZU + 1.9), (-7.5, -6.0, 3.6), 55),
    (7.2, (LF[0], LF[1], ZU + 1.3), (-4.4, -4.5, 1.6), 55),
    (9.8, (LF[0] + 0.2, LF[1] + 0.6, 1.3), ((TD_X0 + TD_X1) / 2, AY1, 1.1), 55),
    (11.8, ((TD_X0 + TD_X1) / 2, -1.3, 1.35), (-3.6, 1.5, 0.7), 55),
    (14.0, (-0.6, 5.8, 1.45), ((RD_X0 + RD_X1) / 2, TY1, 1.05), 55),
    (16.0, ((RD_X0 + RD_X1) / 2, TY1 - 0.4, 1.4), (BOARD[0], BOARD[1], 1.1), 50),
])

# ================================================================ 엔딩: 함대 피격 (운동에너지 탄두가 함교를 직격)
# 비상등(LIGHT_emergency_*), 평상 조명(LIGHT_main_*), 피탄 연출 마커(FX_spark/smoke/debris_*), 떨어지는 천장 패널(DEBRIS_*),
# 홀로 그룹(HOLO_*), 창(WINDOW_*), 함교 상태(BRIDGE_intact / BRIDGE_damaged). 규칙: docs/LEVELS.md, docs/art/level-prologue.md 7장
IMPACT = Vector((0.0, BY0 - 0.5, ZU + 1.8))     # 직격 지점 (함교 앞 창 가운데)
WAVE = 35.0                                      # 충격이 함내로 퍼지는 속도(m/s) → FX delay(초)
_n = {"spark": 0, "smoke": 0, "debris": 0, "emergency": 0}


def three(v):
    """Blender 방향 → three.js 문자열 "x,y,z"."""
    return f"{v[0]:g},{v[2]:g},{-v[1]:g}"


def fx(kind, pos, d=(0, 0, -1), **props):
    """FX_<kind>_<nn> 마커. -Y(three.js +Z)가 d 방향. delay = 직격 지점에서 떨어진 거리 / WAVE."""
    _n[kind] += 1
    n = _n[kind]
    P = Vector(pos)
    p = {"kind": kind, "delay": round((P - IMPACT).length / WAVE, 2), "dir": three(d)}
    p.update(props)
    L.marker(f"FX_{kind}_{n:02d}", tuple(P), look=tuple(P + Vector(d)), props=p)
    return n


def emergency_lamp(wall_pt, normal):
    """적색 비상등: 남색 함 + 어두운 렌즈(항상 보임) + LIGHT_emergency_<nn>(UNLIT, 평소 꺼짐)."""
    _n["emergency"] += 1
    n = _n["emergency"]
    N, P = Vector(normal), Vector(wall_pt)
    L.extrude("navy", hw.rrect(0.46, 0.14, 0.04, n=1), tuple(P), normal, 0.08, kind="detail")
    fc = P + N * 0.08
    L.decal("red_d", hw.rrect(0.38, 0.075, 0.03, n=1), tuple(fc), normal, lift=0.003)
    R = Vector(lk.frame(normal)[0])
    for sgn in (-1, 1):
        L.decal("steel", lk.octagon(0.012), tuple(fc + R * (sgn * 0.205)), normal, lift=0.003)

    def build(b):
        a = fc + N * 0.004
        c = fc + N * 0.022
        half = R * 0.195
        lo = Vector((min(a.x, c.x, (a - half).x, (a + half).x), min(a.y, c.y, (a - half).y, (a + half).y), fc.z - 0.04))
        hi = Vector((max(a.x, c.x, (a - half).x, (a + half).x), max(a.y, c.y, (a - half).y, (a + half).y), fc.z + 0.04))
        lk._bm_box(b, lo.x, hi.x, lo.y, hi.y, lo.z, hi.z)

    L.special(f"LIGHT_emergency_{n:02d}", build, "alert",
              {"emissiveToggle": 1, "group": "emergency", "on": 0, "color": "#ff3a2e", "room": L.zname})


def junction(wall_pt, normal, top, h=0.42):
    """배선함 (불꽃이 튀는 자리): 남색 함 + 경고 띠 + 천장까지 배관. 반환: 불꽃 점."""
    N, P = Vector(normal), Vector(wall_pt)
    L.extrude("navy", hw.rrect(0.32, h, 0.03, n=1), tuple(P), normal, 0.12, kind="detail")
    fc = P + N * 0.12
    L.decal("hazard", hw.rrect(0.22, 0.05, 0.01, n=1, cy=h / 2 - 0.07), tuple(fc), normal, lift=0.003)
    L.decal("navy_d", hw.stadium(0.18, 0.03, cy=-0.06), tuple(fc), normal, lift=0.003)
    L.decal("navy_d", hw.stadium(0.18, 0.03, cy=-0.12), tuple(fc), normal, lift=0.003)
    q = P + N * 0.06
    L.cyl("metal", tuple(q + Vector((0, 0, h / 2))), (q.x, q.y, top), 0.03, verts=8, kind="detail")
    return tuple(fc + Vector((0, 0, h / 2 - 0.02)) + N * 0.02)


def spark_at(wall_pt, normal, top, **props):
    p = junction(wall_pt, normal, top)
    d = Vector(normal) * 0.7 + Vector((0, 0, -0.7))
    return fx("spark", p, tuple(d.normalized()), **props)


def debris_panel(cx, cy, zc, sx, sy, floor_z, *, key="navy_l"):
    """떨어지는 천장 패널 DEBRIS_<nn> (FX_debris_<nn>의 자식, fall=1). zc = 천장 아랫면."""
    n = _n["debris"] + 1
    name = f"DEBRIS_{n:02d}"

    def build(b):
        lk._bm_box(b, cx - sx / 2, cx + sx / 2, cy - sy / 2, cy + sy / 2, zc - 0.045, zc - 0.01)
        for k in (-1, 1):
            lk._bm_box(b, cx - sx / 2 + 0.06, cx + sx / 2 - 0.06, cy + k * (sy / 2 - 0.08) - 0.025,
                       cy + k * (sy / 2 - 0.08) + 0.025, zc - 0.06, zc - 0.045)

    L.special(name, build, key, {"fall": 1, "floor": round(floor_z, 3), "collider": 0})
    fx("debris", (cx, cy, zc - 0.05), (0, 0, -1), debris=name)
    L.attach(name, f"FX_debris_{n:02d}")


# ---- 비상등
for zn, pts in (
    ("bridge", [((BX0, -20.0, ZB - 0.45), (1, 0, 0)), ((BX0, -27.0, ZB - 0.45), (1, 0, 0)),
                ((BX1, -20.0, ZB - 0.45), (-1, 0, 0)), ((BX1, -27.0, ZB - 0.45), (-1, 0, 0))]),
    ("atrium", [((CX0, -14.0, ZU + 2.05), (1, 0, 0)), ((AX1, -10.0, ZA - 1.2), (-1, 0, 0)),
                ((AX1, -5.0, 3.2), (-1, 0, 0)), ((-4.0, AY0, ZA - 1.6), (0, 1, 0))]),
    ("troop", [((-5.5, TY0, ZT - 0.35), (0, 1, 0)), ((4.5, TY0, ZT - 0.35), (0, 1, 0)), ((TX0, 2.9, ZT - 0.35), (1, 0, 0)),
               ((TX1, 5.5, ZT - 0.35), (-1, 0, 0)), ((5.8, TY1, ZT - 0.35), (0, -1, 0))]),
    ("range", [((-5.5, RY0, ZR - 0.4), (0, 1, 0)), ((1.6, RY0, ZR - 0.4), (0, 1, 0)), ((4.6, RY0, ZR - 0.4), (0, 1, 0)),
               ((RX0, 22.0, ZR - 0.4), (1, 0, 0)), ((RX0, 40.0, ZR - 0.4), (1, 0, 0)), ((RX0, 52.0, ZR - 0.4), (1, 0, 0)),
               ((LANE_X1, 24.0, ZR - 0.4), (-1, 0, 0)), ((LANE_X1, 44.0, ZR - 0.4), (-1, 0, 0)),
               ((PA0, 26.0, ZP - 0.3), (1, 0, 0)), ((PB1, 20.0, ZP - 0.3), (-1, 0, 0)), ((PB1, 33.0, ZP - 0.3), (-1, 0, 0))]),
    ("course", [((KX0, 22.0, ZK - 0.4), (1, 0, 0)), ((KX0, 36.0, ZK - 0.4), (1, 0, 0)), ((KX1, 18.0, ZK - 0.4), (-1, 0, 0)),
                ((KX1, 34.0, ZK - 0.4), (-1, 0, 0)), ((K(5.0), KY1, ZK - 0.4), (0, -1, 0))]),
):
    L.zone(zn)
    for wp, nrm in pts:
        emergency_lamp(wp, nrm)

# ---- 함교 쪽 통로 (충격이 가장 먼저, 가장 세게 온다): 불꽃 4, 떨어지는 패널 3, 연기 2
L.zone("atrium")
spark_at((CX0, -15.5, ZU + 1.55), (1, 0, 0), ZU + 2.4, strength=1.0)
spark_at((CX1, -13.7, ZU + 1.55), (-1, 0, 0), ZU + 2.4, strength=1.0)
fx("spark", (DOOR_X, BY1 + 0.25, ZU + 2.18), (0, 0.6, -0.8), strength=1.0)          # 함교 문틀 위
spark_at((AX1, -12.0, ZU + 1.4), (-1, 0, 0), ZA, strength=0.8)                       # 위 층계참
debris_panel(DOOR_X, -15.07, ZU + 2.4 - 0.14, 1.2, 0.5, ZU)
debris_panel(DOOR_X, -13.93, ZU + 2.4 - 0.14, 1.2, 0.5, ZU)
debris_panel(0.0, -12.0, ZA, 1.4, 0.9, ZU)
fx("smoke", (DOOR_X, -15.2, ZU + 2.1), (0, 1, 0), strength=1.0)
fx("smoke", (-1.0, -11.8, ZU + 0.4), (0, 0, 1), strength=0.7)
# ---- 병력 구획: 불꽃 3, 패널 2, 연기 2
L.zone("troop")
spark_at((TX1, 2.2, 2.0), (-1, 0, 0), ZT)
spark_at((-1.0, TY0, 1.5), (0, 1, 0), ZT)
spark_at((TX0, 9.0, 1.95), (1, 0, 0), ZT)
debris_panel(0.2, 2.4, ZT, 1.0, 0.8, 0.0)
debris_panel(-1.6, 7.85, ZT, 1.0, 0.8, 0.0)
fx("smoke", (0.2, 2.4, ZT - 0.2), (0, 0, -1))
fx("smoke", (-6.2, 9.0, 1.8), (1, 0, 0))
# ---- 사격장: 불꽃 5, 패널 3, 연기 3
L.zone("range")
spark_at((-0.3, RY0, 1.6), (0, 1, 0), ZR)
spark_at((RX0, 15.9, 2.0), (1, 0, 0), ZR)
spark_at((RX1, 14.6, 1.8), (-1, 0, 0), ZR)
spark_at((LANE_X1, 20.0, 2.2), (-1, 0, 0), ZR)
spark_at((PB1, 28.0, 1.7), (-1, 0, 0), ZP)
debris_panel(-1.625, 11.75, ZR, 1.0, 0.8, 0.0)
debris_panel(2.675, 14.4, ZR, 1.0, 0.7, 0.0)
debris_panel(RL, 18.4, ZR, 0.8, 0.5, 0.0)                                             # 리타 사로 바로 앞
fx("smoke", (-1.6, 11.8, ZR - 0.2), (0, 0, -1))
fx("smoke", (RL, 18.4, ZR - 0.2), (0, 0, -1))
fx("smoke", (RX1 - 0.3, 14.6, 1.9), (-1, 0, 0))
# ---- 훈련 구획: 불꽃 2, 연기 1 (홀로그램이 꺼진다)
L.zone("course")
spark_at((KX0, 18.0, 2.6), (1, 0, 0), ZK)
spark_at((KX1, 30.0, 2.6), (-1, 0, 0), ZK)
fx("smoke", (K(8.0), 12.6, 3.6), (0, 0, -1))

# ---- 함교 직격 뒤 (BRIDGE_damaged, 평소 숨김): 찢긴 앞 벽, 꺼진 화면, 쓰러진 망원 화면, 잔해, 그을림, 늘어진 배선
L.zone("bridge")
import random as _r  # noqa: E402
RND = _r.Random(41)
BR0, BR1 = -3.9, 3.7                                  # 뚫린 구멍 X 범위
L.group("BRIDGE_damaged", state="damaged", on=0)
L.wall("x", BY0, BX0, BX1, +1, ZU, ZB, openings=[(-6.3, -4.3, WZ0, WZ1), (4.3, 6.3, WZ0, WZ1), (BR0, BR1, ZU + 0.45, ZB)],
       pitch=2.65, insets=False, col=False, strip=False)
for x in (-5.3, 5.3):
    L.portal("x", BY0 - 0.1, x, 2.0, WZ1 - WZ0, WZ0, 0.2, window=True, rad=0.45, border=0.12, faces=(1,))
# 구멍 가장자리: 안쪽으로 휜 선체 판과 부러진 늑골
edge = ([(BR0 + 0.05, BY0 + 0.1, ZU + 0.6 + k * 0.55) for k in range(6)] +
        [(BR1 - 0.05, BY0 + 0.1, ZU + 0.7 + k * 0.5) for k in range(6)] +
        [(BR0 + 0.4 + k * 0.62, BY0 + 0.1, ZU + 0.5) for k in range(12)] +
        [(BR0 + 0.3 + k * 0.7, BY0 + 0.1, ZB - 0.15) for k in range(11)])
for i, (x, y, z) in enumerate(edge):
    key = ("hull", "hull_d", "metal", "navy")[i % 4]
    L.rbox(key, (x, y + RND.uniform(0.05, 0.35), z), (RND.uniform(0.25, 0.6), 0.05, RND.uniform(0.2, 0.5)),
           rot=(RND.uniform(-70, -20), RND.uniform(-35, 35), RND.uniform(-40, 40)))
    if i % 3 == 0:
        L.rbox("amber", (x, y + 0.02, z), (0.12, 0.03, 0.03), rot=(0, RND.uniform(0, 180), RND.uniform(0, 180)), kind="fine")
for x in (-2.6, 0.0, 2.6):
    L.rbox("metal", (x, BY0 + 0.6, ZU + 2.6), (0.18, 1.3, 0.18), rot=(RND.uniform(25, 50), RND.uniform(-20, 20), 0))
# 그을림 (앞 벽 안쪽, 바닥, 천장)
for (u, v, r) in ((-4.6, ZU + 1.4, 0.9), (4.4, ZU + 1.6, 0.8), (-4.2, ZU + 3.0, 0.7), (4.0, ZU + 3.1, 0.6)):
    pts = [(math.cos(2 * math.pi * k / 11) * r * RND.uniform(0.6, 1.1), math.sin(2 * math.pi * k / 11) * r * RND.uniform(0.6, 1.1))
           for k in range(11)]
    L.decal("scorch", pts, (u, BY0 + 0.075, v), (0, 1, 0), lift=0.004)
for (cx, cy, r) in ((0.0, -27.4, 2.6), (-1.6, -25.2, 1.1), (2.1, -25.6, 1.0)):
    pts = [(math.cos(2 * math.pi * k / 14) * r * RND.uniform(0.6, 1.05), math.sin(2 * math.pi * k / 14) * r * RND.uniform(0.6, 1.05))
           for k in range(14)]
    L.decal("scorch", pts, (cx, cy, ZU), (0, 0, 1), up=UP_Y, lift=0.012)
pts = [(math.cos(2 * math.pi * k / 12) * 2.4 * RND.uniform(0.6, 1.0), math.sin(2 * math.pi * k / 12) * 1.6 * RND.uniform(0.6, 1.0))
       for k in range(12)]
L.decal("scorch", pts, (0.0, -27.6, ZB - 0.15), (0, 0, -1), up=UP_Y, lift=0.004, layer="ceil")
# 바닥 잔해
for i in range(16):
    x, y = RND.uniform(-4.5, 4.5), RND.uniform(-28.6, -24.6)
    sx, sy, sz = RND.uniform(0.15, 0.6), RND.uniform(0.15, 0.5), RND.uniform(0.04, 0.18)
    L.rbox(("hull", "metal", "navy", "hull_d")[i % 4], (x, y, ZU + sz / 2 + 0.02), (sx, sy, sz),
           rot=(RND.uniform(-12, 12), RND.uniform(-12, 12), RND.uniform(0, 180)))
# 쓰러진 망원 화면 (홀로 테이블에 기댐, 꺼짐, 금 감)
L.rbox("navy_l", (0.25, -25.05, ZU + 0.98), (3.9, 0.1, 2.2), rot=(-58, 0, 6))
L.rbox("navy_d", (0.25, -24.99, ZU + 1.01), (3.7, 0.04, 2.0), rot=(-58, 0, 6))
L.rbox("steel", (0.0, -24.9, ZU + 1.1), (1.6, 0.05, 0.02), rot=(-58, 25, 6), kind="fine")
L.rbox("steel", (0.9, -24.95, ZU + 1.05), (0.9, 0.05, 0.02), rot=(-58, -40, 6), kind="fine")
# 꺼진 홀로 테이블
L.decal("navy_d", hw.circle(1.02, 36), (HT[0], HT[1], ZU + 0.62), (0, 0, 1), up=UP_Y, lift=0.004)
for a0 in (20, 140, 250):
    L.strip("steel", (HT[0], HT[1], ZU + 0.62),
            (HT[0] + math.cos(math.radians(a0)) * 0.95, HT[1] + math.sin(math.radians(a0)) * 0.95, ZU + 0.62),
            0.015, (0, 0, 1), lift=0.008)
# 꺼진 옆 화면 (틀 + 어두운 판 + 금)
for (cx, nx) in ((BX0 + 0.05, 1), (BX1 - 0.05, -1)):
    fcD = screen((cx, -24.3, ZU + 2.05), (nx, 0, 0), 3.4, 1.1)
    L.decal("navy_d", hw.rrect(3.4, 1.1, 0.04, n=2), fcD, (nx, 0, 0), lift=0.008)
    L.strip("steel", on_screen(fcD, (nx, 0, 0), -0.6, 0.4), on_screen(fcD, (nx, 0, 0), 0.3, -0.45), 0.01, (nx, 0, 0),
            lift=0.01)
# 늘어진 천장 판과 배선
L.rbox("navy_l", (-2.2, -26.3, ZB - 0.75), (1.4, 0.05, 1.4), rot=(-62, 0, 12), layer="ceil")
for (x0, y0, x1, y1, z1) in ((1.6, -26.0, 1.9, -26.3, ZU + 1.6), (-0.8, -25.4, -0.6, -25.6, ZU + 2.0),
                             (2.8, -27.8, 3.0, -27.4, ZU + 1.3)):
    L.obj("rubber", hw.sweep("cable", [(x0, y0, ZB - 0.02), ((x0 + x1) / 2, (y0 + y1) / 2, (ZB + z1) / 2 - 0.3), (x1, y1, z1)],
                             hw.circle(0.018, 6)), kind="detail", layer="ceil")
L.group(None)
for (pos, d) in (((1.9, -26.3, ZU + 1.6), (0, 0, -1)), ((-0.6, -25.6, ZU + 2.0), (0, 0, -1)),
                 ((3.0, -27.4, ZU + 1.3), (0, 0, -1)), ((BR0 + 0.1, BY0 + 0.3, ZU + 2.0), (0.6, 0.6, -0.5))):
    fx("spark", pos, d, state="damaged", strength=0.8)
for pos in ((0.0, BY0 + 0.4, ZU + 1.4), (HT[0], HT[1], ZU + 0.7), (-2.2, -26.3, ZB - 0.4)):
    fx("smoke", pos, (0, 0, 1), state="damaged")
# 직격 뒤 함교를 다시 보여 주는 카메라 (단상에서 뚫린 앞 벽 쪽으로 천천히)
L.cam_rail("bridge_hit", [
    (0.0, (-1.6, -17.6, ZU + 1.9), (0.0, BY0, ZU + 1.9), 52),
    (4.0, (-1.1, -19.4, ZU + 1.6), (0.2, BY0, ZU + 1.8), 46),
    (8.0, (-0.6, -21.0, ZU + 1.45), (0.4, BY0, ZU + 1.9), 40),
])

# ================================================================ finish
ROOT = {
    "sky": "#0d1428",
    "fog": "30,160",
    "sun": "0.35,1,0.25",
    "ambient": 1.3,
    "music": "prologue_ship",
}


def _preview_extra(root):
    lk.import_props(root)


out = "levels/prologue_ship.glb" if not PREVIEW else (
    "_tmp/prologue_ship_preview.glb" if PREVIEW != "col" else "_tmp/prologue_ship_col.glb")
L.finish(out, root_props=ROOT, outline=0.009, extra_preview=_preview_extra,
         preview_skip=() if "space" in PREVIEW else ("space",))
