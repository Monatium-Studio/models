"""모나티엄 구 기갑병기 보관고·공장 지대 키트 (monatium_depot_kit).

2막 M6 「돌파」의 차고(병기창고와 별개)와 시청까지 가는 산업 도로. 도시 키트·폐허 키트 위에 쌓는다.
문서: docs/art/m6-route.md

설정: 지구에서 노획해 온 미군 구 기갑병기(M1A1 `MNT-T01` 등)를 모아 둔 모나티엄 보관고 [오리지널, 2026-11-01 사용자 확정].
인간이 만든 물건이라 모나티엄 망에 묶이지 않아 둠스데이 정전의 영향을 적게 받았다.
"""
from __future__ import annotations

import math
import random

from mathutils import Vector

import monatium_city_kit as mk
import monatium_ruins_kit as rk

mk.PAL.update({
    "depot": "#d9cdb8",       # 보관고 벽 (크림 콘크리트)
    "depot_d": "#a99c88",
    "roller": "#7d8590",      # 셔터
    "tarp_us": "#5f6b45",     # 올리브 방수포
    "floor_c": "#8f8b88",     # 차고 바닥
    "shelf": "#6f6a72",
})


def garage(C, x0, x1, y0, y1, *, h=8.5, door_side="+x", door_c=-18.0, door_w=12.0, door_h=5.6, side_door=(-20.0, -32.0),
           z_ground=-0.05):
    """구 기갑병기 보관고. door_side 벽에 큰 셔터(DOOR_garage, 위로 열림), 남쪽 벽에 사람 문(항상 열림).
    벽마다 COL, 안을 걷고 전차가 나갈 수 있다. 지붕은 깨진 채광창 줄(달빛·새벽빛).
    z_ground = 둘레 땅 높이: 벽은 거기서 선다. 바닥 판(윗면 0.03)은 COL도 같은 높이 (예전에는 COL이 없어 사람·전차·소품이
    둘레 땅 COL(-0.05)에 서서 판 속 8 cm에 묻히고, 소품 COL은 5 cm 떠 있었다: floatcheck 2026-11-03)."""
    t = 0.4
    C.box("floor_c", x0, x1, y0, y1, 0.0, 0.03, kind="detail")
    C.col(x0, x1, y0, y1, z_ground, 0.03)
    zg = z_ground
    # 벽 (문 자리를 비운다)
    sx, sy = side_door
    # 남쪽 벽 (y0): 사람 문 x sx±0.7, 높이 2.0
    C.box("depot", x0, sx - 0.7, y0 - t, y0, zg, h, col=True)
    C.box("depot", sx + 0.7, x1, y0 - t, y0, zg, h, col=True)
    C.box("depot", sx - 0.7, sx + 0.7, y0 - t, y0, 2.1, h, col=True)
    C.box("navy", sx - 0.8, sx + 0.8, y0 - t - 0.02, y0 - t, 2.1, 2.25, kind="detail")
    # 북쪽 벽
    C.box("depot", x0, x1, y1, y1 + t, zg, h, col=True)
    # 서쪽 벽
    C.box("depot", x0 - t, x0, y0 - t, y1 + t, zg, h, col=True)
    # 동쪽 벽 (큰 문)
    a0, a1 = door_c - door_w / 2, door_c + door_w / 2
    C.box("depot", x1, x1 + t, y0 - t, a0, zg, h, col=True)
    C.box("depot", x1, x1 + t, a1, y1 + t, zg, h, col=True)
    C.box("depot", x1, x1 + t, a0, a1, door_h + 0.2, h, col=True)
    C.box("navy", x1 + t, x1 + t + 0.05, a0 - 0.3, a1 + 0.3, door_h + 0.2, door_h + 0.55, kind="detail")
    rk.door(C, "garage", x1 + 0.05, x1 + 0.3, a0, a1, 0.0, door_h + 0.2, key="roller", move="0,5.6,0")
    # 지붕 + 채광창
    C.box("depot_d", x0 - t, x1 + t, y0 - t, y1 + t, h, h + 0.4)
    C.box("navy", x0 - t - 0.1, x1 + t + 0.1, y0 - t - 0.1, y1 + t + 0.1, h - 0.4, h - 0.1, kind="detail")
    # 간판
    C.text("navy", "구 기갑병기 보관고", 1.0, (x1 + t + 0.03, (y0 + y1) / 2 + 9.5, h - 1.6), (1, 0, 0))
    C.text("depot_d", "OLD ARMOR DEPOT · MNT-VEH", 0.42, (x1 + t + 0.03, (y0 + y1) / 2 + 9.5, h - 2.5), (1, 0, 0))
    C.text("teal", "MNT", 1.6, (x1 + t + 0.03, a0 - 3.5, 3.0), (1, 0, 0))
    C.text("navy", "구 기갑병기 보관고", 0.6, (sx, y0 - t - 0.03, 3.0), (0, -1, 0))
    rk.soot(C, (x1 + t, a1 + 3.0, 5.0), (1, 0, 0), 3.0, 3.5, seed=3)  # 벽에서 3 cm, 간판 글자(약 5 cm)보다 2 cm 뒤
    # 안: 선반, 상자, 작업대, 체인 호이스트, 드럼통
    for k in range(4):
        yy = y1 - 1.0
        xx = x0 + 3 + k * 6.5
        C.box("shelf", xx - 2.5, xx + 2.5, yy - 0.5, yy + 0.5, 0, 2.4, col=True)
        for j in range(3):
            C.box("tarp_us" if (k + j) % 2 else "olive", xx - 2.2 + j * 1.5, xx - 1.0 + j * 1.5, yy - 0.4, yy + 0.4,
                  0.9 + (j % 2) * 0.8, 1.5 + (j % 2) * 0.8, kind="detail")
    C.box("wood", x0 + 1.0, x0 + 3.4, y0 + 2.0, y0 + 3.0, 0.0, 0.85, col=True)
    for k in range(5):
        mk.crate(C, x0 + 1.5 + (k % 3) * 1.4, y0 + 5.5 + (k // 3) * 1.2, s=0.7, yaw=(k * 23) % 60)
    C.beam("steel", (x0 + 4, (y0 + y1) / 2, h - 0.6), (x1 - 4, (y0 + y1) / 2, h - 0.6), 0.3, 0.4, kind="detail")
    C.beam("steel", ((x0 + x1) / 2, (y0 + y1) / 2, h - 0.7), ((x0 + x1) / 2, (y0 + y1) / 2, 3.4), 0.03, 0.03, kind="detail")
    for k in range(3):
        C.cyl("barrel", (x1 - 2.0 - k * 0.65, y0 + 1.2, 0), (x1 - 2.0 - k * 0.65, y0 + 1.2, 0.85), 0.29, segs=10)
        rk.col_cyl(C, (x1 - 2.0 - k * 0.65, y0 + 1.2, 0), (x1 - 2.0 - k * 0.65, y0 + 1.2, 0.85), 0.29, segs=10)


def tarp_over(C, name, cx, cy, *, L=9.6, W=4.3, H=2.7, yaw=0.0, key="tarp_us", col=False):
    """차량 위에 덮은 방수포 (이름 있는 메시: 미션이 걷어 내며 숨긴다). 원점 = 덮개 가운데.
    col=True: 덮개 모양 그대로의 볼록 COL (밑에 차량 VEH_가 없고 미션이 걷지 않는 덮개만. 걷는 덮개는 밑의 차량이 막는다)."""
    a = math.radians(yaw)
    ca, sa = math.cos(a), math.sin(a)

    def P(u, v, z):
        return (cx + u * ca - v * sa, cy + u * sa + v * ca, z)

    def build(b):
        rows = [(-W / 2 - 0.15, 0.25), (-W / 2 + 0.25, H - 0.4), (-0.6, H), (0.6, H), (W / 2 - 0.25, H - 0.4), (W / 2 + 0.15, 0.25)]
        cols = 9
        verts = []
        for i in range(cols):
            u = -L / 2 + L * i / (cols - 1)
            sag = 0.12 * math.sin(i * 1.7)
            verts.append([b.verts.new(P(u, v, z - (sag if 0 < j < 5 else 0))) for j, (v, z) in enumerate(rows)])
        for i in range(cols - 1):
            for j in range(len(rows) - 1):
                b.faces.new((verts[i][j], verts[i + 1][j], verts[i + 1][j + 1], verts[i][j + 1]))
        for i in (0, cols - 1):
            ring = verts[i]
            b.faces.new(ring if i else list(reversed(ring)))
    if col:
        rows = [(-W / 2 - 0.15, 0.0), (-W / 2 - 0.15, 0.25), (-W / 2 + 0.25, H - 0.4), (-0.6, H), (0.6, H),
                (W / 2 - 0.25, H - 0.4), (W / 2 + 0.15, 0.25), (W / 2 + 0.15, 0.0)]
        C.ccol([P(u, v, z) for u in (-L / 2, L / 2) for (v, z) in rows])
    return C.special(name, build, key, {"tarp": 1})


def warehouse(C, x0, x1, y0, y1, *, h=7.0, seed=0, front="+x", ruin=0.3, z_ground=-0.05):
    """길가 창고 (단순 블록 + 셔터 + 간판). 통짜 COL. z_ground = 둘레 땅 높이 (블록 밑면, 땅 위로 5 cm 뜨지 않게)."""
    rng = random.Random(seed)
    C.box("depot" if rng.random() < 0.5 else "concrete", x0, x1, y0, y1, z_ground, h, col=True)
    C.box("depot_d", x0 - 0.2, x1 + 0.2, y0 - 0.2, y1 + 0.2, h, h + 0.5)
    N = mk.FRONT[front]
    if front in ("+x", "-x"):
        fx = x1 if front == "+x" else x0
        for k in range(max(1, int((y1 - y0) / 9))):
            yc = y0 + (k + 0.5) * (y1 - y0) / max(1, int((y1 - y0) / 9))
            C.rect("roller", (fx, yc, 2.3), tuple(N), 5.0, 4.4, lift=0.02)
            C.rect("navy", (fx, yc, 4.7), tuple(N), 5.4, 0.3, lift=0.025)
        if rng.random() < ruin:
            rk.soot(C, (fx, rng.uniform(y0 + 2, y1 - 2), rng.uniform(3, h - 1)), tuple(N), 3.0, 3.0, seed=seed)
    else:
        fy = y1 if front == "+y" else y0
        C.rect("roller", ((x0 + x1) / 2, fy, 2.3), tuple(N), 5.0, 4.4, lift=0.02)


def industrial_road(C, x0, x1, y0, y1, *, lanes=4):
    """도로 (y 방향, 아스팔트 + 차선 + 갓길). 바닥 COL."""
    C.box("asphalt", x0, x1, y0, y1, -0.4, 0.0)
    C.col(x0, x1, y0, y1, -0.4, 0.0)
    w = x1 - x0
    for i in range(1, lanes):
        x = x0 + w * i / lanes
        y = y0
        while y < y1:
            C.strip("line" if i != lanes // 2 else "line_y", (x, y, 0.0), (x, min(y + 3, y1), 0.0), 0.14, lift=0.015)
            y += 7 if i != lanes // 2 else 3.5
    C.strip("line", (x0 + 0.4, y0, 0), (x0 + 0.4, y1, 0), 0.14, lift=0.015)
    C.strip("line", (x1 - 0.4, y0, 0), (x1 - 0.4, y1, 0), 0.14, lift=0.015)


def jersey(C, x, y, *, yaw=0.0, L=2.0, z=0.0):
    """콘크리트 방호벽 (엄폐, 0.85 m)."""
    C.rbox("concrete", (x, y, z + 0.42), (L, 0.5, 0.84), (0, 0, yaw))
    C.rbox("hazard", (x, y, z + 0.72), (L * 1.01, 0.52, 0.06), (0, 0, yaw), kind="detail")
    C.lcol(x, y, z, yaw, -L / 2, L / 2, -0.26, 0.26, 0, 0.84)     # 방호벽과 같이 돌린 상자


def hull_down(C, x, y, *, yaw=0.0):
    """장갑차 은폐호: 모래주머니 두 줄 + 흙 둔덕."""
    a = math.radians(yaw)
    f = Vector((math.cos(a), math.sin(a), 0))
    s = Vector((-math.sin(a), math.cos(a), 0))
    for k in (-1, 0, 1):
        p = Vector((x, y, 0)) + f * 3.4 + s * (k * 2.4)
        mk.sandbag_wall(C, p.x, p.y, yaw=yaw + 90, n=4, rows=3)
    C.blob("soil", (x + f.x * 4.6, y + f.y * 4.6, 0.2), 3.2, (0.6, 2.0, 0.35), rot_z=a)
    rk.col_blob(C, (x + f.x * 4.6, y + f.y * 4.6, 0.2), 3.2, (0.6, 2.0, 0.35), rot_z=a)

