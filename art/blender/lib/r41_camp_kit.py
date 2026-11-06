"""R41 야전 수용소 키트 (r41_camp_kit).

2막 M5 「수용소」·M6 초반이 쓰는 R41 수용 시설 모듈. 도시 키트(monatium_city_kit)의 City 조립기 위에 쌓는다.
문서: docs/art/r41-camp.md, R41 형태 언어: docs/art/r41-style.md (45° 모따기 판, 밝은 회색 + 제국 흑, 앰버 띠, 마젠타 기계 발광)

설정 [오리지널]: 둠스데이 정전으로 네트워크에 묶인 전자 장비와 R41 차원 기술 장비가 모두 죽었다. 그래서 수용소는 '멍청한' 장비로
돌아간다. 철조망 밖 서쪽의 디젤 발전기가 케이블로 백열 투광등과 감시탑 탐조등을 켜고, 초소끼리는 전봇대에 건 유선 야전 전화로
교신한다. 리타가 전화선을 끊고 발전기를 세우면 순찰이 직접 걸어서 확인하러 다녀야 한다 = 원작의 '길어진 순찰 주기'.
"""
from __future__ import annotations

import math
import random

import bmesh
import bpy
import mathutils
from mathutils import Vector

import cb
import monatium_city_kit as mk
import monatium_ruins_kit as rk

mk.PAL.update({
    "r41_grey": "#b9b5c0",     # 밝은 회색 판 (R41 전투복 색과 같은 계열)
    "r41_band": "#d88a3a",     # 앰버 띠
    "fence_post": "#56525e",
    "olive_d": "#4d5644",
    "canvas_r": "#8f8a7c",     # R41 천막 (회갈색)
    "drum_r41": "#3e4a3c",
    "cable": "#1d1b20",
    "pole": "#6e5642",
    "plywood": "#b99d74",
})
mk.ALPHA.update({
    "mesh_a": ("#7c7887", 0.38),   # 철망 (반투명)
    "beam_w": ("#fff2c8", 0.09),   # 탐조등 빛줄기
})


def _named(C, name, key, build, loc, props=None, *, no_outline=True):
    """원점을 loc에 둔 이름 있는 메시 (build(bm)은 loc 기준 로컬 좌표로 쌓는다)."""
    b = bmesh.new()
    build(b)
    me = bpy.data.meshes.new(name)
    b.to_mesh(me)
    b.free()
    o = bpy.data.objects.new(name, me)
    cb.link(o)
    cb.assign(o, mk.M(key))
    o.location = loc
    o["collider"] = 0
    if no_outline:
        o["noOutline"] = 1
    for k, v in (props or {}).items():
        o[k] = v
    C.add_node(o)
    return o


# ================================================================== 철조망

def fence_run(C, p0, p1, *, h=2.6, pitch=3.0, col=True, coil=True, z=0.0):
    """R41 철망 울타리: 모따기 기둥 + 위아래 가로대 + 반투명 철망 + 위쪽 윤형 철조망. COL은 두께 0.3 박스."""
    a, b = Vector((p0[0], p0[1], z)), Vector((p1[0], p1[1], z))
    d = b - a
    L = d.length
    if L < 0.05:
        return
    u = d.normalized()
    n = max(1, int(round(L / pitch)))
    for k in range(n + 1):
        p = a + d * (k / n)
        C.rbox("fence_post", (p.x, p.y, z + h / 2), (0.12, 0.12, h), (0, 0, math.degrees(math.atan2(u.y, u.x))))
        C.rbox("r41_band", (p.x, p.y, z + h - 0.25), (0.14, 0.14, 0.08), (0, 0, math.degrees(math.atan2(u.y, u.x))),
               kind="detail")
    for zz in (0.15, h - 0.12):
        C.beam("fence_post", tuple(a + Vector((0, 0, zz))), tuple(b + Vector((0, 0, zz))), 0.05, 0.05, kind="detail")
    # 철망 판 (양면이 보이게 얇은 상자)
    side = Vector((-u.y, u.x, 0)) * 0.01
    pts = [a + Vector((0, 0, 0.12)) - side, b + Vector((0, 0, 0.12)) - side, b + Vector((0, 0, h - 0.1)) - side,
           a + Vector((0, 0, h - 0.1)) - side]
    C.poly("mesh_a", [tuple(p) for p in pts])
    C.poly("mesh_a", [tuple(p + side * 2) for p in reversed(pts)])
    if coil:
        steps = max(4, int(L / 0.45))
        prev = None
        for i in range(steps + 1):
            t = i / steps
            p = a + d * t
            ang = i * 1.9
            q = p + Vector((0, 0, h + 0.22)) + Vector((-u.y, u.x, 0)) * math.cos(ang) * 0.2 + Vector((0, 0, math.sin(ang) * 0.2))
            if prev is not None:
                C.beam("steel", tuple(prev), tuple(q), 0.018, 0.018, kind="detail")
            prev = q
    if col:
        x0, x1 = sorted((a.x, b.x))
        y0, y1 = sorted((a.y, b.y))
        C.col(x0 - 0.15, x1 + 0.15, y0 - 0.15, y1 + 0.15, z, z + h + 0.5)


def fence_loop(C, pts, *, gaps=(), h=2.6):
    """닫힌 울타리. gaps=[(i, t0, t1)]: i번째 변의 t0..t1 구간을 비운다 (문, 찢긴 틈)."""
    for i in range(len(pts)):
        p0, p1 = Vector(pts[i]), Vector(pts[(i + 1) % len(pts)])
        cuts = sorted([(t0, t1) for (j, t0, t1) in gaps if j == i])
        t = 0.0
        for (t0, t1) in cuts:
            if t0 > t:
                fence_run(C, tuple(p0.lerp(p1, t)), tuple(p0.lerp(p1, t0)), h=h)
            t = t1
        if t < 1.0:
            fence_run(C, tuple(p0.lerp(p1, t)), tuple(p1), h=h)


def gate_posts(C, x, y, w, *, axis="x", h=3.2, sign=("외래종 수용소", "R41 · ALIEN SPECIES HOLDING")):
    """문 기둥 둘 + 위 가로 간판."""
    for s in (-1, 1):
        px, py = (x + s * w / 2, y) if axis == "x" else (x, y + s * w / 2)
        C.rbox("r41_shell", (px, py, h / 2), (0.32, 0.32, h), (0, 0, 45))
        C.col(px - 0.2, px + 0.2, py - 0.2, py + 0.2, 0, h)
    if sign:
        if axis == "x":
            C.box("r41_shell", x - w / 2, x + w / 2, y - 0.08, y + 0.08, h - 0.7, h - 0.05)
            C.rect("r41_band", (x, y - 0.09, h - 0.62), (0, -1, 0), w - 0.3, 0.08, lift=0.01)
            C.text("r41_light", sign[0], 0.34, (x, y - 0.09, h - 0.32), (0, -1, 0), lift=0.012)
            C.text("r41_band", sign[1], 0.14, (x, y - 0.09, h - 0.55), (0, -1, 0), lift=0.012)


# ================================================================== 건물

def window_spots(x0, x1, y0, y1, doors=()):
    """막사 창 자리 [(side, u)]: 벽마다 3 m에 하나, 문 둘레(문 반폭 + 0.6 m)는 비운다. u = 벽을 따른 가운데 좌표."""
    out = []
    for side in ("-y", "+y", "-x", "+x"):
        a0, a1 = (x0, x1) if side in ("-y", "+y") else (y0, y1)
        n = int((a1 - a0) / 3.0)
        for k in range(n):
            u = a0 + (k + 0.5) * (a1 - a0) / n
            if any(abs(u - cc) < w / 2 + 0.6 for (s, cc, w) in doors if s == side):
                continue
            out.append((side, u))
    return out


def barrack(C, x0, x1, y0, y1, *, h=2.6, doors=(), wall=0.18, key="r41_grey", roof="r41_shell", floor_z=0.0,
            windows=True, inner=False, trims=True):
    """조립식 막사. doors=[(side, center, width)], side in '-y','+y','-x','+x'. 안을 걸을 수 있다(벽마다 COL).
    inner=True: 실내 마감(널마루·천장·서까래·안쪽 창·문틀)까지. 돌려주는 Room으로 가구를 놓는다 (fit_out)."""
    z0 = floor_z
    C.box("concrete_d", x0 - 0.2, x1 + 0.2, y0 - 0.2, y1 + 0.2, z0 - 0.3, z0)
    C.col(x0 - 0.2, x1 + 0.2, y0 - 0.2, y1 + 0.2, z0 - 0.3, z0)

    def wall_run(side):
        horiz = side in ("-y", "+y")
        a0, a1 = (x0, x1) if horiz else (y0, y1)
        c = (y0 if side == "-y" else y1) if horiz else (x0 if side == "-x" else x1)
        cuts = sorted([(cc - w / 2, cc + w / 2) for (s, cc, w) in doors if s == side])
        t = a0
        segs = []
        for (u0, u1) in cuts:
            segs.append((t, u0, False))
            segs.append((u0, u1, True))
            t = u1
        segs.append((t, a1, False))
        for (u0, u1, is_door) in segs:
            if u1 - u0 < 0.02:
                continue
            zz0 = z0 + (2.0 if is_door else 0.0)
            if horiz:
                C.box(key, u0, u1, c - wall / 2, c + wall / 2, zz0, z0 + h, col=True)
            else:
                C.box(key, c - wall / 2, c + wall / 2, u0, u1, zz0, z0 + h, col=True)
        # 앰버 띠 (아래): 벽보다 1 cm 나오고 모서리를 감싼다 (끝면이 이웃 벽 끝면과 같은 평면에 오지 않게)
        e = wall / 2 + 0.01
        if horiz:
            C.box("r41_band", a0 - e, a1 + e, c - e, c + e, z0 + 0.25, z0 + 0.33, kind="detail")
        else:
            C.box("r41_band", c - e, c + e, a0 - e, a1 + e, z0 + 0.25, z0 + 0.33, kind="detail")
        if windows:
            for (s, u) in window_spots(x0, x1, y0, y1, doors):
                if s != side:
                    continue
                N = mk.FRONT[side]
                pc = Vector((u, c, z0 + 1.55)) if horiz else Vector((c, u, z0 + 1.55))
                C.rect("char", tuple(pc + N * (wall / 2 + 0.005)), tuple(N), 0.9, 0.5, lift=0.01)
                C.rect("steel", tuple(pc + N * (wall / 2 + 0.01) + Vector((0, 0, 0))), tuple(N), 0.9, 0.04, lift=0.012)
    for sd in ("-y", "+y", "-x", "+x"):
        wall_run(sd)
    # 지붕: 낮은 박공 + 처마
    cx = (x0 + x1) / 2
    C.prism(roof, [(x0 - 0.3, y0 - 0.3), (x1 + 0.3, y0 - 0.3), (x1 + 0.3, y1 + 0.3), (x0 - 0.3, y1 + 0.3)],
            z0 + h, z0 + h + 0.18, bottom=True)
    C.prism(roof, [(x0 - 0.3, y0 - 0.3), (x1 + 0.3, y0 - 0.3), (cx, (y0 + y1) / 2)], z0 + h + 0.18, z0 + h + 0.2)
    C.box(roof, x0 - 0.3, x1 + 0.3, (y0 + y1) / 2 - 0.3, (y0 + y1) / 2 + 0.3, z0 + h + 0.18, z0 + h + 0.7)
    if inner:
        return fit_out(C, x0, x1, y0, y1, h=h, doors=doors, wall=wall, z=z0, windows=windows, trims=trims)
    return None


def watchtower(C, tid, x, y, *, h=4.0, face=(0, 0), search=True):
    """감시탑: 다리 넷 + 발판(z=h) + 난간 + 지붕 + 사다리 + 탐조등(LIGHT_search_<tid>, BEAM_<tid>)."""
    s = 1.3
    for sx in (-1, 1):
        for sy in (-1, 1):
            leg = ((x + sx * s * 1.1, y + sy * s * 1.1, 0), (x + sx * s * 0.85, y + sy * s * 0.85, h))
            C.beam("fence_post", *leg, 0.16, 0.16)
            rk.col_beam(C, *leg, 0.16, 0.16)          # 기운 다리 그대로 (곧은 상자는 밑동이 6 cm 모자랐다)
    for k in range(2):
        z = h * (0.35 + 0.3 * k)
        C.beam("fence_post", (x - s, y - s, z), (x + s, y + s, z + 0.6), 0.06, 0.06, kind="detail")
        C.beam("fence_post", (x + s, y - s, z), (x - s, y + s, z + 0.6), 0.06, 0.06, kind="detail")
    C.box("r41_shell", x - s - 0.2, x + s + 0.2, y - s - 0.2, y + s + 0.2, h - 0.15, h, col=True)
    for (ax, ay, bx, by) in ((-1, -1, 1, -1), (1, -1, 1, 1), (1, 1, -1, 1), (-1, 1, -1, -1)):
        # 초소 난간 벽 (발판 위 보초가 걸어 나가 떨어지지 않게 COL)
        C.box("r41_grey", min(x + ax * s, x + bx * s) - 0.05, max(x + ax * s, x + bx * s) + 0.05,
              min(y + ay * s, y + by * s) - 0.05, max(y + ay * s, y + by * s) + 0.05, h, h + 0.9, col=True)
    # 앰버 띠: 난간 벽을 두른 고리 (예전에는 초소를 가로지르는 통판이라 발판 위 0.72 m에 보초 허리를 지나는 판이 있었다)
    C.ring_prism("r41_band", [(x - s - 0.06, y - s - 0.06), (x + s + 0.06, y - s - 0.06), (x + s + 0.06, y + s + 0.06),
                              (x - s - 0.06, y + s + 0.06)],
                 [(x - s + 0.03, y - s + 0.03), (x + s - 0.03, y - s + 0.03), (x + s - 0.03, y + s - 0.03),
                  (x - s + 0.03, y + s - 0.03)], h + 0.72, h + 0.8, kind="detail")
    for sx in (-1, 1):
        for sy in (-1, 1):
            C.beam("fence_post", (x + sx * s, y + sy * s, h + 0.9), (x + sx * s, y + sy * s, h + 2.2), 0.08, 0.08,
                   kind="detail")
    C.prism("r41_shell", [(x - s - 0.4, y - s - 0.4), (x + s + 0.4, y - s - 0.4), (x + s + 0.4, y + s + 0.4),
                          (x - s - 0.4, y + s + 0.4)], h + 2.2, h + 2.4, bottom=True)
    # 사다리
    lx = x - s - 0.3
    for k in range(int(h / 0.32)):
        C.beam("steel", (lx, y - 0.25, 0.3 + k * 0.32), (lx, y + 0.25, 0.3 + k * 0.32), 0.03, 0.03, kind="detail")
    for sy in (-0.25, 0.25):
        C.beam("steel", (lx, y + sy, 0), (lx, y + sy, h + 0.9), 0.04, 0.04, kind="detail")
    C.col(lx - 0.03, lx + 0.03, y - 0.27, y + 0.27, 0, h + 0.9)     # 사다리 (오르지는 않는다: 막는 판)
    if search:
        searchlight(C, tid, (x, y, h + 1.15), face)


def searchlight(C, lid, pos, face, *, length=20.0, spread=3.2):
    """탐조등 몸통 + 렌즈(LIGHT_search_<lid>) + 빛줄기(BEAM_<lid>, 원점 = 렌즈, 미션이 Z축으로 돌린다)."""
    px, py, pz = pos
    yaw = math.atan2(face[1] - py, face[0] - px)
    d = Vector((math.cos(yaw), math.sin(yaw), -0.18)).normalized()
    C.cyl("r41_shell", (px, py, pz - 0.45), (px, py, pz - 0.05), 0.08, segs=8)
    C.cyl("r41_shell", tuple(Vector(pos) - d * 0.25), tuple(Vector(pos) + d * 0.18), 0.24, r2=0.28, segs=12)
    lens_c = Vector(pos) + d * 0.19

    def lens(b):
        mk._bm_cyl(b, Vector((0, 0, 0)), d * 0.03, 0.24, segs=12)
    o = _named(C, f"LIGHT_search_{lid}", "lamp", lens, tuple(lens_c),
               {"emissiveToggle": 1, "group": "flood", "on": 1, "color": "#fff2c8"})
    C.cyl("lamp_off", tuple(lens_c - d * 0.005), tuple(lens_c + d * 0.02), 0.235, segs=12, kind="detail")

    def beam(b):
        n = 10
        tip = b.verts.new((0, 0, 0))
        R = Vector((-d.y, d.x, 0)).normalized()
        U = d.cross(R).normalized()
        ring = []
        for i in range(n):
            a = i / n * math.tau
            ring.append(b.verts.new(tuple(d * length + R * math.cos(a) * spread + U * math.sin(a) * spread)))
        for i in range(n):
            b.faces.new((tip, ring[i], ring[(i + 1) % n]))
    _named(C, f"BEAM_{lid}", "beam_w", beam, tuple(lens_c + d * 0.03), {"beam": 1, "yaw0": round(math.degrees(yaw), 2)})
    return o


def flood_pole(C, lid, x, y, *, h=5.0, face=(0, 0)):
    """투광등 기둥 (백열등, 발전기 전원). LIGHT_flood_<lid>."""
    C.cyl("fence_post", (x, y, 0), (x, y, h), 0.09, segs=8)
    C.cyl("concrete_d", (x, y, 0), (x, y, 0.3), 0.22, segs=8, kind="detail")
    C.col(x - 0.12, x + 0.12, y - 0.12, y + 0.12, 0, h)
    yaw = math.atan2(face[1] - y, face[0] - x)
    d = Vector((math.cos(yaw), math.sin(yaw), -0.6)).normalized()
    head = Vector((x, y, h)) + Vector((math.cos(yaw), math.sin(yaw), 0)) * 0.3
    C.beam("fence_post", (x, y, h - 0.1), tuple(head), 0.06, 0.06, kind="detail")
    C.cyl("r41_shell", tuple(head - d * 0.12), tuple(head + d * 0.08), 0.2, segs=10)

    def lens(b):
        mk._bm_cyl(b, Vector((0, 0, 0)), d * 0.02, 0.18, segs=10)
    _named(C, f"LIGHT_flood_{lid}", "lamp", lens, tuple(head + d * 0.09),
           {"emissiveToggle": 1, "group": "flood", "on": 1, "color": "#fff2c8"})
    C.cyl("lamp_off", tuple(head + d * 0.085), tuple(head + d * 0.1), 0.175, segs=10, kind="detail")


def generator(C, x, y, *, yaw=0.0):
    """디젤 발전기 (R41 야전형: 모따기 상자 + 라디에이터 + 배기관 + 조작판). 엔진이 멈추면 백열등이 모두 꺼진다."""
    C.rbox("r41_shell", (x, y, 0.65), (2.6, 1.3, 1.2), (0, 0, yaw))
    C.rbox("r41_grey", (x, y, 1.3), (2.4, 1.1, 0.12), (0, 0, yaw))
    a = math.radians(yaw)
    fwd = Vector((math.cos(a), math.sin(a), 0))
    side = Vector((-math.sin(a), math.cos(a), 0))
    rad = Vector((x, y, 0.7)) + fwd * 1.31
    for k in range(6):
        C.rbox("cable", tuple(rad + side * ((k - 2.5) * 0.17)), (0.04, 0.06, 0.9), (0, 0, yaw), kind="detail")
    ex = Vector((x, y, 1.3)) - fwd * 0.8 + side * 0.4
    C.cyl("dark", tuple(ex), tuple(ex + Vector((0, 0, 0.9))), 0.07, segs=8)
    panel = Vector((x, y, 0.95)) - side * 0.66
    C.rbox("r41_band", tuple(panel), (0.7, 0.04, 0.5), (0, 0, yaw), kind="detail")
    C.rbox("dark", tuple(panel - side * 0.03 + Vector((0.1, 0, 0.05))), (0.08, 0.04, 0.16), (0, 0, yaw), kind="detail")
    for k in range(3):
        p = Vector((x, y, 0)) + fwd * (-1.8 - 0.65 * (k % 2)) + side * (0.7 - k * 0.6)
        drum(C, p.x, p.y)
    # 몸통(라디에이터·조작판 포함)을 발전기와 같이 돌린 상자로 (예전 2.9 m 정사각 상자는 좁은 쪽을 0.8 m씩 넘쳤다)
    C.lcol(x, y, 0, yaw, -1.3, 1.35, -0.7, 0.7, 0, 1.36)


def drum(C, x, y, *, key="drum_r41", z=0.0):
    C.cyl(key, (x, y, z), (x, y, z + 0.85), 0.29, segs=12)
    for zz in (0.25, 0.6):
        C.cyl("dark", (x, y, z + zz), (x, y, z + zz + 0.03), 0.295, segs=12, kind="detail", cap=False)
    rk.col_cyl(C, (x, y, z), (x, y, z + 0.85), 0.295, segs=12)


def phone_pole(C, x, y, *, h=4.4):
    C.cyl("pole", (x, y, 0), (x, y, h), 0.11, r2=0.08, segs=8)
    C.beam("pole", (x - 0.6, y, h - 0.3), (x + 0.6, y, h - 0.3), 0.08, 0.08, kind="detail")
    C.col(x - 0.12, x + 0.12, y - 0.12, y + 0.12, 0, h)
    return Vector((x, y, h - 0.25))


def wire(C, a, b, *, sag=0.4, segs=6, key="cable", w=0.02):
    A, B = Vector(a), Vector(b)
    prev = A
    for i in range(1, segs + 1):
        t = i / segs
        p = A.lerp(B, t) - Vector((0, 0, sag * 4 * t * (1 - t)))
        C.beam(key, tuple(prev), tuple(p), w, w, kind="detail")
        prev = p


def junction_box(C, x, y, *, face=(0, -1)):
    """야전 전화 분선함 (전봇대에 단 상자). 리타가 여기서 선을 끊는다."""
    C.box("olive_d", x - 0.22, x + 0.22, y - 0.08, y + 0.08, 1.05, 1.5)
    C.rect("r41_band", (x, y + face[1] * 0.085, 1.42), (face[0], face[1], 0), 0.4, 0.05, lift=0.005)
    C.text("r41_light", "TEL-07", 0.06, (x, y + face[1] * 0.085, 1.25), (face[0], face[1], 0), lift=0.006)


def mess_tent(C, x0, x1, y0, y1, *, h=2.4):
    for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        C.cyl("fence_post", (x, y, 0), (x, y, h), 0.05, segs=6)
        C.col(x - 0.05, x + 0.05, y - 0.05, y + 0.05, 0, h)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    C.prism("canvas_r", [(x0 - 0.3, y0 - 0.3), (x1 + 0.3, y0 - 0.3), (x1 + 0.3, y1 + 0.3), (x0 - 0.3, y1 + 0.3)],
            h, h + 0.08, bottom=True)
    C.box("canvas_r", x0 - 0.3, x1 + 0.3, cy - 0.2, cy + 0.2, h + 0.08, h + 0.45)
    # 식탁·벤치 (엘프 높이: 식탁 0.62, 벤치 0.34)
    C.box("plywood", cx - 1.6, cx + 1.6, cy - 0.45, cy + 0.45, 0.58, 0.62, col=True)
    for sx in (-1.3, 1.3):
        C.box("fence_post", cx + sx - 0.05, cx + sx + 0.05, cy - 0.4, cy + 0.4, 0, 0.58)
    # 벤치: 판 + 양 끝 다리. COL은 바닥부터 (2026-11-03 floatcheck: 다리 없이 판만 0.3 m에 떠 있었다)
    for sy in (-0.85, 0.85):
        C.box("plywood", cx - 1.5, cx + 1.5, cy + sy - 0.15, cy + sy + 0.15, 0.3, 0.34)
        for sx in (-1.25, 1.25):
            C.box("fence_post", cx + sx - 0.04, cx + sx + 0.04, cy + sy - 0.12, cy + sy + 0.12, 0, 0.3)
        C.col(cx - 1.5, cx + 1.5, cy + sy - 0.15, cy + sy + 0.15, 0, 0.34)
    return Vector((cx, cy, 0.62))


def bunk(C, x, y, *, yaw=0.0, bedding=False, seed=0):
    """2층 침상. bedding=True: 칸마다 갠 담요 + 베개 (막사·B동 안, 사람이 쓰는 침상)."""
    a = math.radians(yaw)
    C.rbox("fence_post", (x, y, 0.35), (1.6, 0.7, 0.06), (0, 0, yaw))
    C.rbox("canvas_r", (x, y, 0.42), (1.5, 0.62, 0.1), (0, 0, yaw))  # 기둥(±0.28..0.32) 면과 겹치지 않게
    C.rbox("fence_post", (x, y, 1.25), (1.6, 0.7, 0.06), (0, 0, yaw))
    C.rbox("canvas_r", (x, y, 1.32), (1.5, 0.62, 0.1), (0, 0, yaw))
    for sx in (-0.75, 0.75):
        for sy in (-0.3, 0.3):
            p = Vector((x, y, 0)) + Vector((math.cos(a), math.sin(a), 0)) * sx + Vector((-math.sin(a), math.cos(a), 0)) * sy
            C.beam("fence_post", (p.x, p.y, 0), (p.x, p.y, 1.4), 0.04, 0.04, kind="detail")
    if bedding:
        rng = random.Random(seed * 31 + int(x * 7) + int(y * 3))
        P = _lf(x, y, 0, yaw)
        for zz in (0.47, 1.37):
            if rng.random() < 0.8:          # 담요: 발치 쪽에 갬 (가끔 펼쳐 둔 칸)
                if rng.random() < 0.7:
                    C.rbox("drum_r41", P(0.42, 0, zz + 0.04), (0.5, 0.56, 0.08), (0, 0, yaw))
                else:
                    C.rbox("drum_r41", P(0.15, 0, zz + 0.012), (1.1, 0.6, 0.024), (0, 0, yaw))
            C.blob("canvas_r", P(-0.58, 0, zz + 0.05), 0.15, (0.9, 1.6, 0.45), segs=8, rings=4, rot_z=a)
    # 침상 크기 그대로 돌린 상자 (예전 1.6 m 정사각 상자는 침상 폭 0.7 m 양옆을 0.45 m씩 막았다)
    C.lcol(x, y, 0, yaw, -0.82, 0.82, -0.37, 0.37, 0, 1.4)


def r41_crate(C, x, y, *, s=0.7, yaw=0.0, z=0.0, stack=1):
    for k in range(stack):
        C.rbox("r41_shell", (x, y, z + s / 2 + k * s), (s * 1.2, s, s), (0, 0, yaw))
        C.rbox("r41_band", (x, y, z + s * 0.75 + k * s), (s * 1.22, s * 1.02, 0.05), (0, 0, yaw), kind="detail")
    C.lcol(x, y, z, yaw, -s * 0.61, s * 0.61, -s * 0.51, s * 0.51, 0, s * stack)    # 상자와 같이 돌린 상자


def sign(C, x, y, text_ko, text_en, *, face=(0, -1), h=1.6):
    C.cyl("fence_post", (x, y, 0), (x, y, h), 0.04, segs=6)
    C.col(x - 0.05, x + 0.05, y - 0.05, y + 0.05, 0, h)
    N = Vector((face[0], face[1], 0))
    # 판은 기둥(반지름 0.04) 앞면에 붙인다: 기둥이 판 앞으로 4 mm 비집고 나와 깜빡이지 않게
    C.plate("r41_shell", [(-0.5, -0.25), (0.5, -0.25), (0.5, 0.25), (-0.5, 0.25)], tuple(Vector((x, y, h)) + N * 0.04),
            tuple(N), 0.03)
    C.text("r41_band", text_ko, 0.12, tuple(Vector((x, y, h + 0.07)) + N * 0.075), tuple(N), lift=0.004)
    C.text("r41_light", text_en, 0.06, tuple(Vector((x, y, h - 0.1)) + N * 0.075), tuple(N), lift=0.004)


# ================================================================== 실내 (막사·초소·보급창·천막 안)
# 2026-11-05 사용자: "수용소 건물들은 여전히 못들어가게 대충 모델링해놓은걸로 퉁칠거냐?" 막사는 빈 상자(검은 천장, 아스팔트 바닥),
# 천막은 문을 그린 통짜 덩어리였다. 이제 들어가면 쓰임새대로 꾸민 방이다. 정전 뒤라 전기 장비는 죽었다: 불은 석유 남포등,
# 난방은 무쇠 난로, 교신은 수동 야전 전화(교환대)이고 R41 무전기에는 「먹통」 쪽지가 붙었다.
# 끼임 규약 (docs/DO-NOT-REVIVE.md '들어가면 못 나오는 틈 금지'): 가구 COL은 벽·다른 가구에 붙이거나(틈 0) 0.6 m 넘게 띄운다.
# 문에서 방 가운데까지(진입점이 있으면 거기까지) 1.2 m 넘는 통로를 비운다.

mk.PAL.update({
    "floor_w": "#7a644d",     # 널마루
    "paper": "#e6dcc2",       # 종이 (지도·근무표·쪽지)
    "ink": "#3b3542",         # 먹 (지도 선, 글씨)
    "tin": "#9b9aa2",         # 양철 (양동이·주전자·남포등 갓)
    "cork": "#9a7350",        # 게시판
    "pin": "#c8423a",         # 지도 핀
})
mk.GLOW.update({
    "lantern": "#ffd88a",     # 남포등 유리 (석유: 발전기가 서도 켜져 있다)
})
FLOOR = 0.035                 # 널마루 윗면 (바닥 COL도 이 높이: 문턱 3.5 cm)


def _lf(x, y, z, yaw):
    """로컬 (u, v, w) → 월드. 로컬 -Y가 정면, yaw는 Z축 도."""
    a = math.radians(yaw)
    c, s = math.cos(a), math.sin(a)
    return lambda u, v, w=0.0: (x + u * c - v * s, y + u * s + v * c, z + w)


def face_yaw(face):
    """face = 정면이 보는 수평 방향 (fx, fy) → yaw (도, 로컬 -Y를 그쪽으로)."""
    return math.degrees(math.atan2(face[1], face[0])) + 90.0


class Room:
    """막사 안 (벽 안쪽 면 기준). wbox: 벽에 붙인 상자 (side = 등을 댄 벽, a = 벽을 따른 월드 좌표, d = 벽에서 안으로 거리)."""

    def __init__(self, C, x0, x1, y0, y1, *, h, doors=(), wall=0.18, z=0.0):
        self.C, self.h, self.z, self.doors, self.wall = C, h, z, tuple(doors), wall
        self.ox = (x0, x1, y0, y1)
        self.x0, self.x1, self.y0, self.y1 = x0 + wall / 2, x1 - wall / 2, y0 + wall / 2, y1 - wall / 2
        self.cx, self.cy = (x0 + x1) / 2, (y0 + y1) / 2

    def face(self, side):
        return {"-y": self.y0, "+y": self.y1, "-x": self.x0, "+x": self.x1}[side]

    def inward(self, side):
        return -mk.FRONT[side]

    def rect_of(self, side, a0, a1, d0, d1):
        """벽 기준 (a, d) 범위 → 월드 (x0, x1, y0, y1)."""
        f = self.face(side)
        if side == "-y":
            return (a0, a1, f + d0, f + d1)
        if side == "+y":
            return (a0, a1, f - d1, f - d0)
        if side == "-x":
            return (f + d0, f + d1, a0, a1)
        return (f - d1, f - d0, a0, a1)

    def wbox(self, key, side, a0, a1, d0, d1, z0, z1, *, col=False, kind="main"):
        r = self.rect_of(side, a0, a1, d0, d1)
        self.C.box(key, *r, self.z + z0, self.z + z1, kind=kind, col=col)
        return r

    def wcol(self, side, a0, a1, d0, d1, z0, z1):
        r = self.rect_of(side, a0, a1, d0, d1)
        self.C.col(*r, self.z + z0, self.z + z1)

    def wpoint(self, side, a, d, z):
        """벽 기준 점 → 월드 Vector."""
        f = self.face(side)
        if side in ("-y", "+y"):
            return Vector((a, f + (d if side == "-y" else -d), self.z + z))
        return Vector((f + (d if side == "-x" else -d), a, self.z + z))


def fit_out(C, x0, x1, y0, y1, *, h, doors=(), wall=0.18, z=0.0, windows=True, trims=True):
    """막사 실내 마감: 널마루(+바닥 COL), 합판 천장 + 서까래, 안쪽 창(유리·창살·창턱), 문틀(trims: 미닫이 문짝이
    벽 안쪽 면을 미끄러지는 B동은 끈다). Room을 돌려준다."""
    R = Room(C, x0, x1, y0, y1, h=h, doors=doors, wall=wall, z=z)
    # 널마루: 벽 가운데 선까지 깔아(벽 안쪽 면과 같은 평면이 생기지 않게) 문 자리에는 3.5 cm 문턱이 보인다
    C.box("floor_w", x0, x1, y0, y1, z, z + FLOOR, kind="detail", col=True)
    long_x = (R.x1 - R.x0) >= (R.y1 - R.y0)
    k = 0.32
    if long_x:
        yy = R.y0 + k
        while yy < R.y1 - 0.1:
            C.strip("ink", (R.x0, yy, z + FLOOR), (R.x1, yy, z + FLOOR), 0.012, lift=0.002)
            yy += k
    else:
        xx = R.x0 + k
        while xx < R.x1 - 0.1:
            C.strip("ink", (xx, R.y0, z + FLOOR), (xx, R.y1, z + FLOOR), 0.012, lift=0.002)
            xx += k
    # 천장: 합판 + 짧은 쪽으로 건너지른 서까래
    C.box("plywood", x0, x1, y0, y1, z + h - 0.04, z + h - 0.005)
    if long_x:
        n = max(2, int((R.x1 - R.x0) / 1.5))
        for i in range(1, n):
            xx = R.x0 + (R.x1 - R.x0) * i / n
            C.box("wood_d", xx - 0.05, xx + 0.05, R.y0 - 0.02, R.y1 + 0.02, z + h - 0.16, z + h - 0.04, kind="detail")
    else:
        n = max(2, int((R.y1 - R.y0) / 1.5))
        for i in range(1, n):
            yy = R.y0 + (R.y1 - R.y0) * i / n
            C.box("wood_d", R.x0 - 0.02, R.x1 + 0.02, yy - 0.05, yy + 0.05, z + h - 0.16, z + h - 0.04, kind="detail")
    # 안쪽 창 (바깥 창과 같은 자리·크기): 어두운 유리 + 창살 + 창턱
    if windows:
        for (side, u) in window_spots(x0, x1, y0, y1, doors):
            n_in = R.inward(side)
            c = R.wpoint(side, u, 0.0, 1.55)
            C.rect("char", tuple(c + n_in * 0.005), tuple(n_in), 0.9, 0.5, lift=0.01)
            C.rect("steel", tuple(c + n_in * 0.01), tuple(n_in), 0.9, 0.04, lift=0.012)
            C.rect("steel", tuple(c + n_in * 0.01), tuple(n_in), 0.04, 0.5, lift=0.012)
            if trims or not any(s_ == side for (s_, _, _) in doors):      # 미닫이 문짝이 지나가는 벽에는 창턱을 내지 않는다
                R.wbox("plywood", side, u - 0.52, u + 0.52, -0.01, 0.07, 1.26, 1.3, kind="detail")
    # 문틀 (안쪽 면): 양 옆 기둥 + 위 가로대. 벽에서 2 cm 나온 판
    for (side, cc, w) in (doors if trims else ()):
        for s in (-1, 1):
            a = cc + s * (w / 2 + 0.03)
            R.wbox("fence_post", side, a - 0.03, a + 0.03, -0.01, 0.02, FLOOR, 2.06, kind="detail")
        R.wbox("fence_post", side, cc - w / 2 - 0.06, cc + w / 2 + 0.06, -0.01, 0.02, 2.0, 2.06, kind="detail")
    return R


# ------------------------------------------------------------------ 가구 (엘프 체격: 탁자 0.62, 의자 0.34, 사물함 1.3)

def table(C, x0, x1, y0, y1, *, h=0.62, key="plywood"):
    """탁자: 판 + 네 다리, COL은 바닥부터 판 크기 그대로."""
    C.box(key, x0, x1, y0, y1, h - 0.04, h)
    for (lx, ly) in ((x0 + 0.08, y0 + 0.08), (x1 - 0.08, y0 + 0.08), (x0 + 0.08, y1 - 0.08), (x1 - 0.08, y1 - 0.08)):
        C.box("fence_post", lx - 0.035, lx + 0.035, ly - 0.035, ly + 0.035, 0, h - 0.04)
    C.col(x0, x1, y0, y1, 0, h)


def bench_pair(C, x0, x1, y0, y1, *, axis="x", gap=0.18, w=0.3, h=0.34):
    """탁자(x0..x1, y0..y1) 양 긴 변에 벤치. 벤치와 탁자 사이 틈(gap)은 COL로 메운다 (캡슐보다 좁은 틈 금지)."""
    for s in (-1, 1):
        if axis == "x":
            e = y0 if s < 0 else y1
            b0, b1 = sorted((e + s * gap, e + s * (gap + w)))
            C.box("plywood", x0 + 0.05, x1 - 0.05, b0, b1, h - 0.04, h)
            for lx in (x0 + 0.2, x1 - 0.2):
                C.box("fence_post", lx - 0.03, lx + 0.03, b0 + 0.04, b1 - 0.04, 0, h - 0.04)
            c0, c1 = sorted((e, e + s * (gap + w)))
            C.col(x0 + 0.05, x1 - 0.05, c0, c1, 0, h)
        else:
            e = x0 if s < 0 else x1
            b0, b1 = sorted((e + s * gap, e + s * (gap + w)))
            C.box("plywood", b0, b1, y0 + 0.05, y1 - 0.05, h - 0.04, h)
            for ly in (y0 + 0.2, y1 - 0.2):
                C.box("fence_post", b0 + 0.04, b1 - 0.04, ly - 0.03, ly + 0.03, 0, h - 0.04)
            c0, c1 = sorted((e, e + s * (gap + w)))
            C.col(c0, c1, y0 + 0.05, y1 - 0.05, 0, h)


def chair(C, x, y, *, face=(0, -1), key="plywood"):
    """접이 의자: 앉는 판 0.34 + 등판(정면 반대쪽). face = 앉은 사람이 보는 쪽. COL은 앉는 판 + 등판."""
    yaw = face_yaw(face)
    P = _lf(x, y, 0, yaw)
    C.rbox(key, P(0, 0, 0.32), (0.4, 0.38, 0.04), (0, 0, yaw))
    C.rbox(key, P(0, 0.17, 0.62), (0.4, 0.035, 0.26), (0, 0, yaw))
    for (u, v) in ((-0.17, -0.15), (0.17, -0.15), (-0.17, 0.17), (0.17, 0.17)):
        C.beam("fence_post", P(u, v, 0), P(u, v, 0.3 if v < 0 else 0.76), 0.03, 0.03, kind="detail")
    C.lcol(x, y, 0, yaw, -0.2, 0.2, -0.19, 0.19, 0, 0.34)
    C.lcol(x, y, 0, yaw, -0.2, 0.2, 0.15, 0.19, 0, 0.76)


def stool(C, x, y, *, key="plywood"):
    C.cyl(key, (x, y, 0.3), (x, y, 0.34), 0.17, segs=10)
    for k in range(3):
        a = k * math.tau / 3
        C.beam("fence_post", (x + math.cos(a) * 0.15, y + math.sin(a) * 0.15, 0), (x + math.cos(a) * 0.1, y + math.sin(a) * 0.1, 0.3),
               0.03, 0.03, kind="detail")
    C.ccyl(x, y, 0.17, 0, 0.34, n=10)


def desk(R, side, a0, a1, *, d=0.62, h=0.62, drawers=+1):
    """벽에 붙인 책상 (side 벽, a0..a1, 깊이 d). 서랍 칸은 drawers 쪽(+1 = a1 끝). COL은 바닥부터 책상 크기."""
    C = R.C
    R.wbox("plywood", side, a0, a1, 0.0, d, h - 0.04, h)
    da = (a1 - 0.42, a1 - 0.02) if drawers > 0 else (a0 + 0.02, a0 + 0.42)
    R.wbox("r41_metal", side, da[0], da[1], 0.03, d - 0.03, 0, h - 0.04)
    for k in range(3):
        zz = 0.12 + k * 0.17
        R.wbox("steel", side, (da[0] + da[1]) / 2 - 0.07, (da[0] + da[1]) / 2 + 0.07, d - 0.03, d - 0.01, zz, zz + 0.025,
               kind="detail")
    for a in ((a0 + 0.05) if drawers > 0 else (a1 - 0.05),):
        for dd in (0.06, d - 0.06):
            R.wbox("fence_post", side, a - 0.03, a + 0.03, dd - 0.03, dd + 0.03, 0, h - 0.04, kind="detail")
    R.wcol(side, a0, a1, 0.0, d, 0, h)
    return R.wpoint(side, (a0 + a1) / 2, d / 2, h)


def lockers(R, side, a0, n, *, w=0.5, d=0.45, h=1.3, seed=0):
    """사물함 줄 (side 벽에 등, a0부터 +a 쪽으로 n칸). 칸마다 통풍 줄·손잡이·이름표. COL은 한 상자."""
    rng = random.Random(seed)
    a1 = a0 + n * w
    R.wbox("r41_metal", side, a0, a1, 0.0, d, 0, h)
    R.wbox("r41_shell", side, a0 - 0.01, a1 + 0.01, -0.01, d + 0.01, h, h + 0.03, kind="detail")
    n_in = R.inward(side)
    for i in range(n):
        u = a0 + (i + 0.5) * w
        c = R.wpoint(side, u, d, 0)
        R.wbox("r41_shell", side, a0 + i * w - 0.01, a0 + i * w + 0.01, d - 0.005, d + 0.004, 0.05, h - 0.02, kind="detail")
        for k in range(3):
            C = R.C
            C.rect("r41_shell", tuple(c + Vector((0, 0, h - 0.18 - k * 0.06))), tuple(n_in), w * 0.6, 0.02, lift=0.006)
        R.C.rect("steel", tuple(c + Vector((0, 0, 0.7))), tuple(n_in), 0.04, 0.14, lift=0.008)
        R.C.rect("paper", tuple(c + Vector((0, 0, h - 0.36))), tuple(n_in), 0.16, 0.06, lift=0.008)
        if rng.random() < 0.3:          # 덜 닫힌 문: 어두운 틈
            R.C.rect("char", tuple(c + Vector((0, 0, h / 2))), tuple(n_in), 0.03, h * 0.8, lift=0.007)
    R.wcol(side, a0, a1, 0.0, d, 0, h + 0.03)


def footlocker(C, x, y, *, face=(0, -1), key="olive_d"):
    """침상 발치 관물 상자 (0.6 x 0.36 x 0.34). COL은 상자 그대로."""
    yaw = face_yaw(face)
    P = _lf(x, y, 0, yaw)
    C.rbox(key, P(0, 0, 0.17), (0.6, 0.36, 0.34), (0, 0, yaw))
    C.rbox("r41_band", P(0, 0, 0.27), (0.61, 0.37, 0.04), (0, 0, yaw), kind="detail")
    C.rbox("steel", P(0, -0.185, 0.22), (0.08, 0.012, 0.06), (0, 0, yaw), kind="detail")
    C.lcol(x, y, 0, yaw, -0.3, 0.3, -0.18, 0.18, 0, 0.34)


def stove(C, x, y, *, ceil, r=0.26):
    """무쇠 난로 + 굴뚝관(천장까지) + 위 주전자. 아궁이 틈에 잉걸불. COL은 둥근 몸통 (굴뚝관은 0.06 m라 없음)."""
    C.cyl("dark", (x, y, 0.12), (x, y, 0.72), r, segs=14)
    C.cyl("r41_metal", (x, y, 0.72), (x, y, 0.76), r + 0.03, segs=14)
    for k in range(3):
        a = k * math.tau / 3 + 0.5
        C.beam("dark", (x + math.cos(a) * (r - 0.04), y + math.sin(a) * (r - 0.04), 0), (x + math.cos(a) * (r - 0.06), y + math.sin(a) * (r - 0.06), 0.14),
               0.05, 0.05, kind="detail")
    # 아궁이 (-y 쪽): 문 + 잉걸불 틈
    C.rbox("r41_metal", (x, y - r + 0.01, 0.38), (0.22, 0.04, 0.18), (0, 0, 0), kind="detail")
    C.rect("ember", (x, y - r - 0.012, 0.36), (0, -1, 0), 0.16, 0.035, lift=0.0)
    C.rect("ember", (x, y - r - 0.012, 0.42), (0, -1, 0), 0.16, 0.035, lift=0.0)
    C.cyl("dark", (x, y, 0.76), (x, y, ceil - 0.005), 0.06, segs=10)
    C.cyl("r41_metal", (x, y, ceil - 0.12), (x, y, ceil - 0.005), 0.1, segs=10, kind="detail")
    # 주전자
    kx = x + 0.12
    C.cyl("tin", (kx, y + 0.08, 0.76), (kx, y + 0.08, 0.92), 0.09, r2=0.07, segs=10, kind="detail")
    C.beam("tin", (kx + 0.08, y + 0.08, 0.84), (kx + 0.16, y + 0.08, 0.92), 0.02, 0.02, kind="detail")
    C.ccyl(x, y, r + 0.03, 0, 0.76, n=12)


def lantern(C, lid, x, y, *, z=None, hang=None, light=0.45):
    """석유 남포등 (양철 받침·갓, 빛나는 유리, 철사 보호대). hang = 천장 높이면 철사로 매단다(z = 등 밑),
    아니면 z(탁자 윗면)에 세운다. FX_fire_lamp_<lid>: 미션이 깜빡이는 점광원을 붙인다(act2Fires, strength=light)."""
    if hang is not None:
        z = hang - 0.62 if z is None else z
        C.beam("cable", (x, y, z + 0.32), (x, y, hang), 0.012, 0.012, kind="detail")
        C.rbox("tin", (x, y, hang - 0.01), (0.12, 0.12, 0.02), kind="detail")
    C.cyl("tin", (x, y, z), (x, y, z + 0.05), 0.075, segs=10, kind="detail")
    C.cyl("lantern", (x, y, z + 0.05), (x, y, z + 0.2), 0.055, segs=10)
    for k in range(4):
        a = k * math.tau / 4 + math.pi / 4
        C.beam("steel", (x + math.cos(a) * 0.068, y + math.sin(a) * 0.068, z + 0.05),
               (x + math.cos(a) * 0.068, y + math.sin(a) * 0.068, z + 0.21), 0.01, 0.01, kind="detail")
    C.cyl("tin", (x, y, z + 0.2), (x, y, z + 0.27), 0.08, r2=0.03, segs=10, kind="detail")
    C.beam("steel", (x - 0.07, y, z + 0.24), (x, y, z + 0.33), 0.01, 0.01, kind="detail")
    C.beam("steel", (x, y, z + 0.33), (x + 0.07, y, z + 0.24), 0.01, 0.01, kind="detail")
    if light > 0:
        C.fx(f"fire_lamp_{lid}", (x, y, z + 0.13 - 0.35), strength=light)


def field_phone(C, x, y, z, *, face=(0, -1)):
    """수동 야전 전화 (자석식: 손잡이를 돌려 건다). 올리브 상자 + 크랭크 + 수화기 + 줄."""
    yaw = face_yaw(face)
    P = _lf(x, y, z, yaw)
    C.rbox("olive_d", P(0, 0, 0.07), (0.26, 0.18, 0.14), (0, 0, yaw), kind="detail")
    C.rbox("dark", P(0, 0.01, 0.15), (0.22, 0.06, 0.03), (0, 0, yaw), kind="detail")
    C.rbox("dark", P(-0.12, 0.01, 0.17), (0.05, 0.07, 0.04), (0, 0, yaw), kind="detail")
    C.rbox("dark", P(0.12, 0.01, 0.17), (0.05, 0.07, 0.04), (0, 0, yaw), kind="detail")
    C.beam("steel", P(0.13, 0, 0.07), P(0.19, 0, 0.07), 0.015, 0.015, kind="detail")
    C.beam("steel", P(0.19, 0, 0.07), P(0.19, -0.06, 0.03), 0.015, 0.015, kind="detail")
    C.rect("paper", P(0, -0.091, 0.07), tuple(Vector(P(0, -1, 0)) - Vector(P(0, 0, 0))), 0.12, 0.04, lift=0.002)
    C.beam("cable", P(-0.1, 0.05, 0.12), P(-0.2, 0.15, 0.0), 0.012, 0.012, kind="detail")


def dead_radio(C, x, y, z, *, face=(0, -1)):
    """R41 무전기 (정전으로 죽었다): 어두운 상자, 꺼진 창, 손잡이, 안테나 밑동 + 끈에 매단 「먹통」 쪽지."""
    yaw = face_yaw(face)
    P = _lf(x, y, z, yaw)
    C.rbox("r41_shell", P(0, 0, 0.13), (0.44, 0.28, 0.26), (0, 0, yaw))
    C.rbox("r41_band", P(0, 0, 0.245), (0.45, 0.29, 0.02), (0, 0, yaw), kind="detail")
    N = Vector(P(0, -1, 0)) - Vector(P(0, 0, 0))
    C.rect("char", P(-0.08, -0.141, 0.15), tuple(N), 0.18, 0.08, lift=0.002)
    for u in (0.09, 0.15):
        C.cyl("dark", P(u, -0.14, 0.12), P(u, -0.16, 0.12), 0.022, segs=8, kind="detail")
    C.beam("steel", P(0.17, 0.08, 0.26), P(0.19, 0.1, 0.5), 0.012, 0.012, kind="detail")
    C.rect("paper", P(-0.04, -0.141, 0.06), tuple(N), 0.2, 0.07, lift=0.004)
    C.text("pin", "먹통", 0.045, P(-0.04, -0.141, 0.06), tuple(N), lift=0.006)


def switchboard(C, x, y, z, *, face=(0, -1)):
    """야전 전화 교환대 (초소끼리 잇는 선이 모인다): 기운 판에 잭 줄, 늘어진 플러그 줄, 크랭크."""
    yaw = face_yaw(face)
    P = _lf(x, y, z, yaw)
    C.rbox("olive_d", P(0, 0.05, 0.08), (0.56, 0.3, 0.16), (0, 0, yaw))
    C.rbox("olive_d", P(0, 0.14, 0.3), (0.56, 0.1, 0.32), (0, 0, yaw))
    N = Vector(P(0, -1, 0)) - Vector(P(0, 0, 0))
    C.rect("char", P(0, 0.089, 0.3), tuple(N), 0.48, 0.24, lift=0.002)
    for i in range(6):
        for j in range(3):
            C.rect("tin", P(-0.2 + i * 0.08, 0.088, 0.22 + j * 0.08), tuple(N), 0.025, 0.025, lift=0.004)
    for i, u in enumerate((-0.16, -0.04, 0.12)):
        C.beam("cable", P(u, 0.08, 0.3 - (i % 2) * 0.08), P(u + 0.05, -0.08, 0.17), 0.01, 0.01, kind="detail")
        C.beam("cable", P(u + 0.05, -0.08, 0.17), P(u + 0.1, -0.06, 0.17), 0.01, 0.01, kind="detail")
    C.rect("paper", P(0, 0.088, 0.47), tuple(N), 0.3, 0.05, lift=0.004)
    C.text("ink", "교환대 · SWITCH", 0.03, P(0, 0.088, 0.47), tuple(N), lift=0.006)


def map_board(R, side, a, *, w=2.2, h=1.2, z0=0.85, title="수용소 배치도", seed=0):
    """벽에 건 지도판: 코르크 판 + 종이 지도(철망 테두리·건물 칸·길) + 핀 + 제목. 판 4 cm (벽에 붙음, COL 없음)."""
    C = R.C
    rng = random.Random(seed)
    R.wbox("wood_d", side, a - w / 2 - 0.04, a + w / 2 + 0.04, -0.01, 0.03, z0 - 0.04, z0 + h + 0.04, kind="detail")
    R.wbox("cork", side, a - w / 2, a + w / 2, 0.0, 0.04, z0, z0 + h)
    N = R.inward(side)
    c = R.wpoint(side, a, 0.04, z0 + h / 2 - 0.05)
    mw, mh = w * 0.8, h * 0.72
    C.rect("paper", tuple(c), tuple(N), mw, mh, lift=0.004)
    Rt, Ut, _ = mk.frame(N)
    def q(u, v):
        return tuple(c + Rt * u + Ut * v + N * 0.008)
    # 철망 테두리 (붉은 선), 칸 (먹), 길 (점선 대신 가는 선)
    fw, fh = mw * 0.8, mh * 0.78
    for (u0, v0, u1, v1) in ((-fw / 2, -fh / 2, fw / 2, -fh / 2), (fw / 2, -fh / 2, fw / 2, fh / 2),
                             (fw / 2, fh / 2, -fw / 2, fh / 2), (-fw / 2, fh / 2, -fw / 2, -fh / 2)):
        C.strip("pin", q(u0, v0), q(u1, v1), 0.012, normal=tuple(N), lift=0.0)
    for _ in range(7):
        bw, bh = rng.uniform(0.1, 0.24), rng.uniform(0.06, 0.12)
        u, v = rng.uniform(-fw / 2 + 0.15, fw / 2 - 0.15), rng.uniform(-fh / 2 + 0.1, fh / 2 - 0.1)
        C.rect("ink", q(u, v), tuple(N), bw, bh, lift=0.0)
    C.strip("ink", q(-fw / 2, 0.0), q(fw / 2, 0.02), 0.008, normal=tuple(N), lift=0.0)
    for _ in range(5):
        u, v = rng.uniform(-fw / 2, fw / 2), rng.uniform(-fh / 2, fh / 2)
        C.cyl("pin", q(u, v), tuple(Vector(q(u, v)) + N * 0.03), 0.014, segs=6, kind="detail")
    C.text("ink", title, 0.08, tuple(c + Ut * (mh / 2 + 0.07) + N * 0.006), tuple(N), lift=0.004)
    # 쪽지 둘
    for k in range(2):
        cc = R.wpoint(side, a + (w / 2 - 0.2 - k * 0.32), 0.04, z0 + 0.14)
        C.rect("paper", tuple(cc), tuple(N), 0.24, 0.16, lift=0.004 + 0.002 * k)


def notice(R, side, a, z, lines, *, w=0.42, h=0.3):
    """벽에 붙인 종이 (근무표·점호 시간 따위): 종이 + 글 줄 + 압정."""
    C = R.C
    N = R.inward(side)
    c = R.wpoint(side, a, 0.0, z)
    C.rect("paper", tuple(c), tuple(N), w, h, lift=0.006)
    _, Ut, _ = mk.frame(N)
    for i, (s, size) in enumerate(lines):
        C.text("ink", s, size, tuple(c + Ut * (h / 2 - 0.05 - i * (size * 1.5 + 0.01))), tuple(N), lift=0.009)
    C.cyl("pin", tuple(c + Ut * (h / 2 - 0.02)), tuple(c + Ut * (h / 2 - 0.02) + N * 0.015), 0.012, segs=6, kind="detail")


def rifle_rack(R, side, a0, a1, *, n=None, d=0.3, h=1.05):
    """총가: 아래 받침 홈 + 위 걸이 막대 + 기둥, R41 소총이 n자루 기대 섰다. COL은 벽에 붙인 상자 (바닥 ~ h)."""
    C = R.C
    R.wbox("wood_d", side, a0, a1, 0.0, d, 0.0, 0.12)
    R.wbox("wood_d", side, a0, a1, 0.0, 0.12, h - 0.06, h)
    for a in (a0 + 0.03, a1 - 0.03):
        R.wbox("wood_d", side, a - 0.03, a + 0.03, 0.0, 0.1, 0.0, h, kind="detail")
    n = n or max(2, int((a1 - a0 - 0.1) / 0.2))
    for i in range(n):
        a = a0 + 0.12 + i * (a1 - a0 - 0.24) / max(1, n - 1)
        b = R.wpoint(side, a, d * 0.62, 0.12)
        t = R.wpoint(side, a, 0.08, h + 0.12)
        C.beam("r41_shell", tuple(b), tuple(b + (t - b) * 0.35), 0.05, 0.11, kind="detail")      # 개머리
        C.beam("r41_metal", tuple(b + (t - b) * 0.35), tuple(t), 0.035, 0.05, kind="detail")       # 몸통·총열
        C.beam("r41_band", tuple(b + (t - b) * 0.42), tuple(b + (t - b) * 0.47), 0.04, 0.06, kind="detail")
    R.wcol(side, a0, a1, 0.0, d, 0.0, h)


def shelf_run(R, side, a0, a1, *, d=0.5, h=1.9, levels=4, seed=0):
    """철제 선반 (기둥·선반판) + 칸마다 물건(상자·자루·탄통·깡통). COL은 벽에 붙인 상자 하나 (바닥 ~ h)."""
    C = R.C
    rng = random.Random(seed)
    nseg = max(1, int(round((a1 - a0) / 1.2)))
    for i in range(nseg + 1):
        a = a0 + 0.03 + (a1 - a0 - 0.06) * i / nseg
        for dd in (0.03, d - 0.03):
            R.wbox("steel", side, a - 0.025, a + 0.025, dd - 0.025, dd + 0.025, 0.0, h, kind="detail")
    for k in range(levels):
        z = 0.1 + k * (h - 0.15) / (levels - 1) if levels > 1 else 0.1
        R.wbox("r41_grey", side, a0, a1, 0.0, d, z - 0.03, z)
        if k == levels - 1:
            continue
        top = 0.1 + (k + 1) * (h - 0.15) / (levels - 1) - 0.04
        a = a0 + 0.06
        while a < a1 - 0.25:
            kind = rng.choice(("crate", "crate", "sack", "cans", "box", "gap"))
            room_h = top - z - 0.02
            if kind == "crate":
                L = rng.uniform(0.35, 0.55)
                hh = min(room_h, rng.uniform(0.22, 0.34))
                R.wbox("r41_shell", side, a, a + L, 0.06, d - 0.06, z, z + hh, kind="detail")
                R.wbox("r41_band", side, a - 0.005, a + L + 0.005, 0.055, d - 0.055, z + hh * 0.6, z + hh * 0.6 + 0.03, kind="detail")
                a += L + 0.04
            elif kind == "box":
                L = rng.uniform(0.25, 0.4)
                hh = min(room_h, rng.uniform(0.16, 0.28))
                R.wbox("plywood", side, a, a + L, 0.08, d - 0.1, z, z + hh, kind="detail")
                a += L + 0.04
            elif kind == "sack":
                p = R.wpoint(side, a + 0.2, d / 2, z + 0.12)
                C.blob("canvas_r", tuple(p), 0.2, (1.0, 0.9, 0.6), segs=8, rings=4)
                a += 0.44
            elif kind == "cans":
                for j in range(3):
                    p = R.wpoint(side, a + 0.08 + j * 0.15, d / 2, z)
                    C.cyl("drum_r41", tuple(p), tuple(p + Vector((0, 0, min(room_h, 0.18)))), 0.065, segs=8, kind="detail")
                a += 0.5
            else:
                a += rng.uniform(0.2, 0.35)
    R.wcol(side, a0, a1, 0.0, d, 0.0, h)


def pallet_stack(C, x, y, *, s=0.55, layers=2, axis="x", sacks=False):
    """나무 깔판 + R41 상자 두 줄 (서로 붙임, COL 틈 0). axis = 상자 두 개가 늘어선 방향."""
    hw = s * 0.61             # r41_crate COL 반폭 (긴 쪽)
    L = 4 * hw
    W = s * 1.1
    if axis == "x":
        C.box("wood_d", x - L / 2, x + L / 2, y - W / 2, y + W / 2, 0, 0.12)
        for k in range(3):
            yy = y - W / 2 + 0.05 + k * (W - 0.1) / 2
            C.box("plywood", x - L / 2 - 0.005, x + L / 2 + 0.005, yy - 0.05, yy + 0.05, 0.1, 0.125, kind="detail")
        C.col(x - L / 2, x + L / 2, y - W / 2, y + W / 2, 0, 0.12)
        for sx in (-1, 1):
            if sacks and sx > 0:
                for k in range(layers):
                    C.blob("canvas_r", (x + hw, y, 0.12 + 0.13 + k * 0.24), 0.32, (1.0, 0.85, 0.42), segs=8, rings=4)
                C.col(x, x + 2 * hw, y - s * 0.5, y + s * 0.5, 0.12, 0.12 + layers * 0.24)
            elif sx > 0 and layers > 1:
                # 한 줄은 한 단 낮고 위에 합판 상자 (검은 상자 기둥 두 개가 나란히 서지 않게)
                r41_crate(C, x + hw, y, s=s, z=0.12, stack=layers - 1)
                zt = 0.12 + (layers - 1) * s
                hd = s * 0.51        # 상자 COL 반깊이: 합판 상자를 아래 상자 윗면에 꼭 맞춘다 (윗면에 좁은 턱을 남기지 않게)
                C.box("plywood", x, x + 2 * hw, y - hd, y + hd, zt, zt + 0.32)
                C.rect("ink", (x + hw, y - hd - 0.001, zt + 0.17), (0, -1, 0), 0.3, 0.04, lift=0.002)
                C.col(x, x + 2 * hw, y - hd, y + hd, zt, zt + 0.32)
            else:
                r41_crate(C, x + sx * hw, y, s=s, z=0.12, stack=layers)
    else:
        C.box("wood_d", x - W / 2, x + W / 2, y - L / 2, y + L / 2, 0, 0.12)
        for k in range(3):
            xx = x - W / 2 + 0.05 + k * (W - 0.1) / 2
            C.box("plywood", xx - 0.05, xx + 0.05, y - L / 2 - 0.005, y + L / 2 + 0.005, 0.1, 0.125, kind="detail")
        C.col(x - W / 2, x + W / 2, y - L / 2, y + L / 2, 0, 0.12)
        for sy in (-1, 1):
            if sy > 0 and layers > 1:
                r41_crate(C, x, y + hw, s=s, yaw=90, z=0.12, stack=layers - 1)
                zt = 0.12 + (layers - 1) * s
                hd = s * 0.51
                C.box("plywood", x - hd, x + hd, y, y + 2 * hw, zt, zt + 0.32)
                C.rect("ink", (x - hd - 0.001, y + hw, zt + 0.17), (-1, 0, 0), 0.3, 0.04, lift=0.002)
                C.col(x - hd, x + hd, y, y + 2 * hw, zt, zt + 0.32)
            else:
                r41_crate(C, x, y + sy * hw, s=s, yaw=90, z=0.12, stack=layers)


def jerrycans(R, side, a0, n, *, key="olive_d"):
    """벽에 붙여 세운 기름통 줄 (서로 붙음). COL은 한 상자."""
    w, d, h = 0.18, 0.36, 0.46
    for i in range(n):
        a = a0 + i * w
        R.wbox(key, side, a + 0.005, a + w - 0.005, 0.0, d, 0.0, h - 0.04)
        R.wbox(key, side, a + 0.03, a + w - 0.03, d * 0.55, d * 0.85, h - 0.04, h, kind="detail")
        R.wbox("dark", side, a + 0.06, a + w - 0.06, d * 0.15, d * 0.3, h - 0.04, h - 0.01, kind="detail")
    R.wcol(side, a0, a0 + n * w, 0.0, d, 0.0, h)


def bucket(C, x, y, *, r=0.16, h=0.3, water=True, key="tin"):
    C.cyl(key, (x, y, 0), (x, y, h - 0.05), r * 0.82, r2=r * 0.97, segs=12)
    C.cyl(key, (x, y, h - 0.05), (x, y, h), r * 0.97, r2=r, segs=12, cap=False)
    C.cyl("glass_d" if water else "dark", (x, y, h - 0.05), (x, y, h - 0.048), r * 0.96, segs=12, kind="detail")
    C.cyl("steel", (x, y, h - 0.02), (x, y, h), r + 0.005, segs=12, kind="detail", cap=False)
    C.beam("steel", (x - r, y, h), (x, y, h + 0.12), 0.012, 0.012, kind="detail")
    C.beam("steel", (x, y, h + 0.12), (x + r, y, h), 0.012, 0.012, kind="detail")
    C.ccyl(x, y, r, 0, h, n=10)


def coat_hooks(R, side, a0, a1, *, z=1.32, seed=0):
    """벽 옷걸이 줄: 가로대 + 걸린 외투·철모 (벽에서 0.12 m 안, COL 없음)."""
    C = R.C
    rng = random.Random(seed)
    R.wbox("wood_d", side, a0, a1, 0.0, 0.04, z, z + 0.06, kind="detail")
    a = a0 + 0.2
    while a < a1 - 0.15:
        if rng.random() < 0.7:
            R.wbox("olive_d" if rng.random() < 0.6 else "r41_grey", side, a - 0.13, a + 0.13, 0.02, 0.11, z - 0.62, z - 0.02)
        else:
            p = R.wpoint(side, a, 0.12, z - 0.1)
            C.blob("r41_shell", tuple(p), 0.13, (1, 1, 0.75), segs=10, rings=4)
        a += rng.uniform(0.34, 0.45)


def tally(R, side, a, z, n=17):
    """벽에 긁은 날짜 세기 (다섯씩 묶어 빗금)."""
    C = R.C
    N = R.inward(side)
    for i in range(n):
        grp, k = divmod(i, 5)
        u = a + grp * 0.16 + k * 0.025
        p = R.wpoint(side, u, 0.0, z)
        if k == 4:
            C.strip("char", tuple(p + Vector((0, 0, -0.06)) - _along(side) * 0.1), tuple(p + Vector((0, 0, 0.06))), 0.008,
                    normal=tuple(N), lift=0.006)
        else:
            C.strip("char", tuple(p + Vector((0, 0, -0.06))), tuple(p + Vector((0, 0, 0.06))), 0.008, normal=tuple(N), lift=0.006)


def _along(side):
    return Vector((1, 0, 0)) if side in ("-y", "+y") else Vector((0, 1, 0))


# ------------------------------------------------------------------ 열린 천막

def cot(C, x, y, *, yaw=0.0, L=1.6, W=0.6, h=0.3, blanket=True):
    """야전 접이 침상 (낮다): 양옆 막대 + X자 다리 + 천 + 갠 담요·베개. COL은 침상 크기 (바닥 ~ h)."""
    P = _lf(x, y, 0, yaw)
    for s in (-1, 1):
        C.beam("fence_post", P(s * W / 2, -L / 2, h - 0.03), P(s * W / 2, L / 2, h - 0.03), 0.035, 0.035, kind="detail")
    C.rbox("olive_d", P(0, 0, h - 0.02), (W - 0.04, L - 0.06, 0.025), (0, 0, yaw))
    for v in (-L / 2 + 0.12, L / 2 - 0.12):
        C.beam("fence_post", P(-W / 2, v - 0.1, 0), P(W / 2, v + 0.1, h - 0.03), 0.025, 0.025, kind="detail")
        C.beam("fence_post", P(W / 2, v - 0.1, 0), P(-W / 2, v + 0.1, h - 0.03), 0.025, 0.025, kind="detail")
    if blanket:
        C.rbox("drum_r41", P(0, L / 2 - 0.45, h + 0.05), (W - 0.12, 0.5, 0.1), (0, 0, yaw))
        C.blob("canvas_r", P(0, -L / 2 + 0.2, h + 0.06), 0.16, (1.5, 0.9, 0.45), segs=8, rings=4, rot_z=math.radians(yaw))
    C.lcol(x, y, 0, yaw, -W / 2, W / 2, -L / 2, L / 2, 0, h)


def tent_open(C, x, y, *, yaw=0.0, w=2.6, d=3.2, h=1.9, key="canvas_r", t=0.04, cots=True, seed=0):
    """열린 A자 천막 (mk.tent와 같은 크기·겉모양): 앞(-Y) 자락을 양옆으로 말아 묶고 서서 들어간다.
    가운데 통로(폭 1 m)는 지붕이 1.17 m 넘게 남는다(엘프 키 1.2, 가운데 1.9). 안에는 바닥 깔개와 낮은 침상 둘(양옆, 뒤 벽에 붙임).
    COL: 양 지붕판(볼록, 두께 t), 뒤 박공, 침상. 앞은 비었다."""
    P = _lf(x, y, 0, yaw)
    rng = random.Random(seed)
    for s in (-1, 1):
        # 지붕판: 바깥면 (s*w/2, v, 0)-(0, v, h), 안쪽 면은 판 법선 반대로 t
        nx, nz = s * h, w / 2
        ln = math.hypot(nx, nz)
        nx, nz = nx / ln, nz / ln
        outer = [(s * w / 2, -d / 2, 0.0), (s * w / 2, d / 2, 0.0), (0.0, d / 2, h), (0.0, -d / 2, h)]
        inner = [(u - nx * t, v, max(0.0, z - nz * t)) for (u, v, z) in outer]
        verts = [P(*q) for q in outer + inner]
        b = C.bm(key, "main")
        vs = [b.verts.new(v) for v in verts]
        faces = []
        for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
            faces.append(b.faces.new([vs[i] for i in f]))
        bmesh.ops.recalc_face_normals(b, faces=faces)
        C.ccol(verts)
        # 앞 자락: 말아서 지붕판 앞 모서리 바깥을 따라 묶었다 (굵은 천 막대 + 끈 둘). 통로(|u| < 0.5) 밖, 판 위에 얹힌다
        def edge(u):
            return Vector((u + nx * 0.07, -d / 2 + 0.08, h * (1 - abs(u) / (w / 2)) + nz * 0.07))
        ea, eb = edge(s * (w / 2 - 0.1)), edge(s * 0.45)
        a_, b_ = P(*ea), P(*eb)
        C.cyl(key, a_, b_, 0.065, segs=8)
        ax = (Vector(b_) - Vector(a_)).normalized()
        for tt in (0.3, 0.7):
            pa = Vector(a_).lerp(Vector(b_), tt)
            C.cyl("wood_d", tuple(pa - ax * 0.025), tuple(pa + ax * 0.025), 0.072, segs=8, kind="detail")
        # 앞 A자 기둥 (지붕판 앞 모서리 밑)
        C.beam("wood_d", P(s * w / 2, -d / 2 - 0.02, 0.0), P(0.0, -d / 2 - 0.02, h + 0.08), 0.05, 0.05, kind="detail")
    # 뒤 박공 (닫힘)
    tri = [(-w / 2, 0.0), (w / 2, 0.0), (0.0, h)]
    verts = [P(u, d / 2 - t, z) for (u, z) in tri] + [P(u, d / 2, z) for (u, z) in tri]
    b = C.bm(key, "main")
    vs = [b.verts.new(v) for v in verts]
    faces = [b.faces.new((vs[0], vs[1], vs[2])), b.faces.new((vs[5], vs[4], vs[3]))]
    for i in range(3):
        j = (i + 1) % 3
        faces.append(b.faces.new((vs[i], vs[3 + i], vs[3 + j], vs[j])))
    bmesh.ops.recalc_face_normals(b, faces=faces)
    C.ccol(verts)
    C.cyl("wood_d", P(0, d / 2 + 0.05, 0), P(0, d / 2 + 0.05, h + 0.25), 0.04, segs=6, kind="detail")
    # 용마루 끈 + 줄·말뚝 (mk.tent와 같다)
    C.beam("wood_d", P(0, -d / 2 - 0.02, h + 0.04), P(0, d / 2 + 0.05, h + 0.04), 0.03, 0.03, kind="detail")
    for s in (-1, 1):
        for tt in (-1, 1):
            a_ = P(s * w * 0.5, tt * d * 0.5, 0.05)
            g = P(s * (w * 0.5 + 0.7), tt * (d * 0.5 + 0.4), 0.0)
            C.beam("wood_d", a_, g, 0.02, 0.02, kind="fine")
    # 바닥 깔개
    yawr = math.radians(yaw)
    up_ = (0.0, 0.0, 1.0)
    C.decal("tarp_o", [(-w / 2 + 0.1, -d / 2 + 0.05), (w / 2 - 0.1, -d / 2 + 0.05), (w / 2 - 0.1, d / 2 - 0.06),
                       (-w / 2 + 0.1, d / 2 - 0.06)], P(0, 0, 0.02), up_, up=(-math.sin(yawr), math.cos(yawr), 0), lift=0.012)
    if cots:
        L = 1.6
        for s in (-1, 1):
            # 침상: u 0.5..1.1 (통로 쪽 가장자리 0.5), 뒤 박공 안쪽 면에 붙인다
            cu = s * 0.8
            cv = d / 2 - t - L / 2
            cx_, cy_, _ = P(cu, cv, 0)
            cot(C, cx_, cy_, yaw=yaw, L=L, W=0.6, h=0.3, blanket=rng.random() < 0.85)
        # 앞쪽 구석: 양철 양동이 (통로 밖, 지붕판 밑)
        bx_, by_, _ = P(-0.82, -d / 2 + 0.45, 0)
        bucket(C, bx_, by_, r=0.14, h=0.26)


# ================================================================== 문 표지 (어느 동·어느 쪽 문인지)
# 2026-11-05 사용자: "M5/M6에서 문짝에 어느 동으로 가는건지, 어느 방향의 문인지 표기좀 해라." R41이 제 시설에 칠한 표지:
# 짙은 판(r41_shell) + 앰버 테 + 밝은 글자. 이름은 목표·지도·대사와 같은 말을 쓴다 (서쪽 쪽문, 북문, B동 …).
# 철망 문은 「~문」, 건물 문은 「~출입구」. 10~15 m 밤 조명에서 읽히게 큰 글자 0.3 m 안팎, 방향 글자 0.2 m 안팎.

BOLD = 0.035    # 칠한 글자 굵기 (글자 크기 대비 윤곽 넓힘). 한글 기본 글꼴(AppleSDGothicNeo 첫 면)이 가늘어 밤에 멀리서 흐리다


def _curve(name, s, size, bold):
    font = "kr" if any(ord(ch) > 0x2000 for ch in s) else "din"
    cu = bpy.data.curves.new(name + "_crv", "FONT")
    cu.body = s
    f = mk.hw._font(font)
    if f:
        cu.font = f
    cu.size = size
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.resolution_u = 3 if size >= 0.3 else 2
    cu.offset = bold * size
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    cb.link(tmp)
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    return me


def text_size(s, size, *, bold=BOLD):
    """글자 메시의 (너비, 높이, 세로 가운데 어긋남). 판 크기를 글자에 맞추고 글자를 판 가운데에 놓는다."""
    me = _curve("measure", s, size, bold)
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    bpy.data.meshes.remove(me)
    if not xs:
        return 0.0, 0.0, 0.0
    return max(xs) - min(xs), max(ys) - min(ys), (max(ys) + min(ys)) / 2


def paint_text(C, key, s, size, center, normal, *, lift=0.005, bold=BOLD):
    """굵게 칠한 글자 (City.text와 같고 윤곽만 넓힌다)."""
    R, U, N = mk.frame(normal)
    me = _curve(C.uid("txt"), s, size, bold)
    o = bpy.data.objects.new("decal_" + me.name, me)
    cb.link(o)
    m4 = mathutils.Matrix((R, U, N)).transposed().to_4x4()
    m4.translation = Vector(center) + N * lift
    o.matrix_world = m4
    return C.obj(key, o, kind="fine")


PAD = (0.12, 0.06)    # 판 안 여백 (가로, 세로)
GAP = 0.05            # 줄 사이


def label_size(rows, *, pad=PAD, gap=GAP):
    """표지판 (너비, 높이, 줄마다 (너비, 높이, 어긋남), 줄 높이). rows = [(글, 크기, 색)]"""
    sz = [text_size(s, size) for (s, size, _) in rows]
    hs = [max(h, size * 0.72) for (_, size, _), (_, h, _) in zip(rows, sz)]
    W = max(w for (w, _, _) in sz) + 2 * pad[0]
    H = sum(hs) + gap * (len(rows) - 1) + 2 * pad[1]
    return W, H, sz, hs


def label(C, center, normal, rows, *, pad=PAD, gap=GAP, depth=0.03, two_sided=False, min_w=0.0,
          bg="r41_shell", rim="r41_band", embed=0.01):
    """칠한 표지판: 짙은 판 + 테 + 글자 줄(위에서 아래로). rows = [(글, 크기, 색)]. 판은 글자에 맞춘다.
    한 면: center = 붙일 면 위 점, normal = 바깥. 판은 면 속으로 embed만큼 묻힌다(면과 같은 평면 없음).
    두 면(two_sided): center = 판 두께 가운데, 양면에 같은 글자 (문 위 가로판·내민 판). 판 (너비, 높이)를 돌려준다."""
    W, H, sz, hs = label_size(rows, pad=pad, gap=gap)
    W = max(W, min_w)
    _, _, N = mk.frame(normal)
    c = Vector(center)
    e = 0.035      # 테 폭
    box = [(-W / 2, -H / 2), (W / 2, -H / 2), (W / 2, H / 2), (-W / 2, H / 2)]
    rimb = [(-W / 2 - e, -H / 2 - e), (W / 2 + e, -H / 2 - e), (W / 2 + e, H / 2 + e), (-W / 2 - e, H / 2 + e)]
    if two_sided:
        C.plate(rim, rimb, tuple(c), tuple(N), depth * 0.6, back=depth * 0.3)
        C.plate(bg, box, tuple(c), tuple(N), depth, back=depth / 2)
        faces = [(N, depth / 2), (-N, depth / 2)]
    else:
        # 테 뒷면은 판 뒷면보다 4 mm 앞 (기둥에 단 판은 뒤에서도 보인다: 두 뒷면이 한 평면이면 깜빡인다)
        C.plate(rim, rimb, tuple(c), tuple(N), depth * 0.6 + embed - 0.004, back=embed - 0.004)
        C.plate(bg, box, tuple(c), tuple(N), depth + embed, back=embed)
        faces = [(N, depth)]
    for (n, front) in faces:
        _, Un, _ = mk.frame(n)
        y = H / 2 - pad[1]
        for (s, size, key), (_, _, cy), hh in zip(rows, sz, hs):
            y -= hh / 2
            paint_text(C, key, s, size, tuple(c + n * front + Un * (y - cy)), tuple(n))
            y -= hh / 2 + gap
    return W, H


def door_label(C, x, y, side, rows, *, wall=0.18, door_h=2.0, roof_h=2.6, z=None, along=0.0, **kw):
    """건물 문 위 표지: side = 문이 난 벽('-y','+y','-x','+x'), (x, y) = 그 벽 가운데 선 위 문 가운데.
    판 밑은 문 위 6 cm, 위는 처마(roof_h) 밑. along = 벽을 따라 옮김 (오른쪽 +, 바깥에서 볼 때)."""
    N = mk.FRONT[side]
    R, _, _ = mk.frame(N)
    _, H, _, _ = label_size(rows)
    if z is None:
        z = door_h + 0.06 + H / 2
        assert z + H / 2 + 0.035 <= roof_h, f"문 위 표지가 처마에 닿는다: {rows[0][0]} ({z + H / 2:.2f} > {roof_h})"
    return label(C, tuple(Vector((x, y, z)) + N * (wall / 2) + R * along), tuple(N), rows, **kw)


def wall_paint(C, x, y, side, s, size, z, *, wall=0.18, key="r41_shell", along=0.0):
    """벽에 칠한 큰 글자 (스텐실). (x, y) = 벽 가운데 선 위 점, z = 글자 가운데 높이."""
    N = mk.FRONT[side]
    R, _, _ = mk.frame(N)
    _, _, cy = text_size(s, size)
    paint_text(C, key, s, size, tuple(Vector((x, y, z - cy)) + N * (wall / 2) + R * along), tuple(N), lift=0.012)


def gate_label(C, x, y, w, rows, *, axis="x", h=3.2, depth=0.1):
    """철망 문 기둥 사이 가로판 (양면 같은 글자). gate_posts와 같은 x, y, w, axis, h. 판 위 끝 = 기둥 끝 5 cm 아래,
    판 양 끝은 기둥(0.32 m, 45° 돌림) 속에 묻힌다."""
    _, H, _, _ = label_size(rows)
    N = (0, 1, 0) if axis == "x" else (1, 0, 0)
    return label(C, (x, y, h - 0.05 - 0.035 - H / 2), N, rows, two_sided=True, depth=depth, min_w=w - 0.1)


def blade_label(C, x, y, z, out, rows, *, depth=0.04):
    """기둥에서 수직으로 내민 판 (양면, 길을 따라 오는 쪽에서 읽힌다). (x, y) = 기둥 가운데, z = 판 가운데 높이,
    out = 내미는 방향 (수평). 판 위에 쇠 받침대가 기둥까지 이어진다."""
    O = Vector((out[0], out[1], 0)).normalized()
    N = Vector((-O.y, O.x, 0))
    W, H, _, _ = label_size(rows)
    c = Vector((x, y, z)) + O * (0.1 + W / 2 + 0.035)
    label(C, tuple(c), tuple(N), rows, two_sided=True, depth=depth)
    top = z + H / 2 + 0.035
    end = c + O * (W / 2 + 0.035)
    C.beam("steel", (x, y, top + 0.05), (end.x, end.y, top + 0.05), 0.04, 0.05, kind="detail")
    for k in (-1, 1):
        q = c + O * (k * W * 0.35)
        C.beam("steel", (q.x, q.y, top - 0.01), (q.x, q.y, top + 0.04), 0.02, 0.02, kind="detail")
    return W, H


def post_label(C, x, y, face, rows, *, h=1.5):
    """기둥에 단 표지판 (한 면). 판 가운데 높이 h, 판 뒷면을 기둥 앞면에 1 cm 묻는다."""
    _, H, _, _ = label_size(rows)
    top = h + H / 2 + 0.05
    C.cyl("fence_post", (x, y, 0), (x, y, top), 0.045, segs=6)
    C.col(x - 0.06, x + 0.06, y - 0.06, y + 0.06, 0, top)
    N = Vector((face[0], face[1], 0)).normalized()
    return label(C, tuple(Vector((x, y, h)) + N * 0.045), tuple(N), rows)


def factory_ruin(C, x0, x1, y0, y1, *, h=6.0, seed=0, broken=0.6):
    """무너진 모나티엄 공장 (통짜 블록 + 톱니 지붕 잔해 + 잔해 더미). 수용소 바깥 은신 지형."""
    rng = random.Random(seed)
    mk.factory_shed(C, x0, x1, y0, y1, h=h, seed=seed, chimney=rng.random() < 0.5)   # 몸통 COL은 factory_shed가 넣는다
    # 남쪽 출입문 틀 (도시 키트 entrance: 벽에서 0.1 m 나온 판, 폭 2.96, 높이 2.6)
    C.col((x0 + x1) / 2 - 1.48, (x0 + x1) / 2 + 1.48, y0 - 0.1, y0, 0, 2.6)
    for k in range(int(1 + broken * 3)):
        side = rng.choice(("-y", "+y", "-x", "+x"))
        if side in ("-y", "+y"):
            px = rng.uniform(x0 + 1, x1 - 1)
            py = (y0 - 1.2) if side == "-y" else (y1 + 1.2)
        else:
            py = rng.uniform(y0 + 1, y1 - 1)
            px = (x0 - 1.2) if side == "-x" else (x1 + 1.2)
        rk.rubble(C, px, py, r=rng.uniform(0.9, 1.4), h=rng.uniform(0.75, 1.0), seed=seed * 11 + k)
