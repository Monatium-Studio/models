"""2·3막 시네마틱 세트 공용 (cine_kit): monatium_city_kit 위에 밤 팔레트와 폐허·정전 모듈을 더한다.

사용 (세트 스크립트 art/blender/levels/cine_*.py):
    import os, sys
    sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
    import cb, monatium_city_kit as mk, cine_kit as ck
    cb.reset()
    ck.night()                       # 도시 키트 팔레트를 밤빛으로 (머티리얼을 만들기 전에 부른다)
    C = mk.City("cine_ruins")
    ck.rubble(C, 3, 4, 2.0, seed=1)
    C.finish("levels/cine_ruins.glb", root_props={**ck.NIGHT_ROOT, ...})

설계
  - 도시 키트(monatium_city_kit)는 고치지 않는다. 팔레트 dict(mk.PAL·GLOW·ALPHA)에 값을 더하거나 바꾸는 것만 한다.
    Blender는 스크립트마다 새 프로세스라 다른 세트에 번지지 않는다.
  - 엔진 툰 셰이딩은 주광 세기만으로 밤이 되지 않아(그림자 띠가 그대로 밝다) 색 자체를 밤색으로 누른다
    (interlude_kit의 mode="night"와 같은 방식). 발광(GLOW)은 그대로 밝다.
  - 정전: 모나티엄 망에 묶인 가로등·창·화면은 전부 꺼진 색. 빛은 달빛, 불, 뮤트의 시안 실, R41 휴대등(마젠타)뿐이다.
"""
from __future__ import annotations

import math
import random

from mathutils import Matrix, Vector

import monatium_city_kit as mk

NIGHT_TINT = "#1a2442"
DUSK_TINT = "#5a3a58"

# 밤 세트 루트 속성 (달빛). 세트마다 덮어쓴다
NIGHT_ROOT = {
    "sky": "#0b1022",
    "fog": "30,190",
    "sun": "-0.35,0.75,-0.55",
    "ambient": 0.85,
    "sunColor": "#a9bbe8",
    "sunIntensity": 1.0,
    "hemiSky": "#4a5a8a",
    "hemiGround": "#15161f",
    "physics": 0,
    "near": 0.05,
    "far": 700,
}


def _mix(a, b, t):
    a, b = a.lstrip("#"), b.lstrip("#")
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cbb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cbb))


def _scale(h, k):
    h = h.lstrip("#")
    return "#" + "".join(f"{min(255, round(int(h[i:i + 2], 16) * k)):02x}" for i in (0, 2, 4))


def shade(h, tint=NIGHT_TINT, t=0.5, k=0.62):
    """색 하나를 밤빛으로 (남청 쪽으로 섞고 어둡게)."""
    return _scale(_mix(h, tint, t), k)


# 정전된 도시의 '꺼진' 발광체: GLOW 키를 꺼진 색(보통 머티리얼)으로 옮긴다
_BLACKOUT = {
    "lamp": "#3d4150",
    "lamp_off": "#3d4150",
    "win_lit": "#232a3e",
    "screen": "#0d1420",
    "glow_off": "#1d3438",
}


def night(*, t=0.5, k=0.62, tint=NIGHT_TINT, blackout=True):
    """도시 키트 팔레트를 밤빛으로 누른다. blackout이면 가로등·창·화면 발광을 꺼진 색으로 바꾼다.
    머티리얼을 하나라도 만들기 전에 불러야 한다."""
    for key, val in list(mk.PAL.items()):
        mk.PAL[key] = shade(val, tint, t, k)
    if blackout:
        for key, val in _BLACKOUT.items():
            mk.GLOW.pop(key, None)
            mk.PAL[key] = val
    # 이 키트가 더하는 색 (밤 기준값)
    mk.PAL.update({
        "rubble": shade("#cfc6b8", tint, t, k),
        "rubble_d": shade("#9a9290", tint, t, k),
        "char": "#1c1a20",          # 그을음
        "rebar": "#3a3036",
        "cloth_r": shade("#a8443c", tint, t, k),
        "r41_panel": "#24212c",     # R41 시설 판 (밤에도 거의 같은 흑)
        "r41_trim": "#3d3848",
        "barrel": shade("#5a5f66", tint, t, k),
        "dirt_n": shade("#8b6a52", tint, t, k),
    })
    mk.GLOW.update({
        "fire_glow": "#ffb35a",
        "fire_core": "#fff0b0",
        "ember": "#ff7a3a",
        "moonlit": "#c9d6ff",
        "mute": "#7ff0ea",
        "r41_lamp": "#ff4fd8",
    })
    mk.ALPHA.update({
        "firelight": ("#ff9a4a", 0.22),
        "moonbeam": ("#b9c8ff", 0.08),
        "mute_haze": ("#7ff0ea", 0.18),
        "dust": ("#c8c2c8", 0.28),
    })
    mk._R41.update({"r41_panel", "r41_trim"})
    mk._DARK.update({"char", "rebar", "barrel"})


# ================================================================== 폐허 모듈

def rubble(C, x, y, r, *, seed=0, n=None, z=0.0, keys=("rubble", "rubble_d", "concrete"), h=0.7):
    """잔해 더미: 기울어진 콘크리트 덩어리 n개 (반경 r, 높이 h)."""
    rng = random.Random(seed * 7919 + 13)
    n = n or max(4, int(r * r * 3))
    for i in range(n):
        a = rng.uniform(0, math.tau)
        d = r * math.sqrt(rng.random())
        cx, cy = x + math.cos(a) * d, y + math.sin(a) * d
        s = rng.uniform(0.18, 0.55) * (1.2 - d / max(r, 0.01) * 0.6)
        zz = z + max(0.0, (1 - d / max(r, 0.01)) * h * rng.uniform(0.3, 1.0))
        C.rbox(keys[i % len(keys)], (cx, cy, zz + s * 0.3), (s * rng.uniform(1, 2.2), s * rng.uniform(0.8, 1.6), s * 0.7),
               rot=(rng.uniform(-25, 25), rng.uniform(-25, 25), rng.uniform(0, 180)))
    # 철근 몇 가닥
    for i in range(max(1, n // 6)):
        a = rng.uniform(0, math.tau)
        cx, cy = x + math.cos(a) * r * 0.4, y + math.sin(a) * r * 0.4
        C.beam("rebar", (cx, cy, z + 0.1), (cx + rng.uniform(-0.4, 0.4), cy + rng.uniform(-0.4, 0.4), z + rng.uniform(0.6, 1.4)),
               0.035, 0.035, kind="detail")


def debris(C, x0, x1, y0, y1, *, n=30, seed=0, z=0.0):
    """바닥에 흩어진 작은 파편 (조각, 종이, 깨진 판)."""
    rng = random.Random(seed * 31 + 7)
    for i in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        s = rng.uniform(0.08, 0.3)
        key = ("rubble", "rubble_d", "char", "pave_d")[i % 4]
        C.rbox(key, (x, y, z + s * 0.12), (s, s * rng.uniform(0.6, 1.4), s * 0.22), rot=(0, 0, rng.uniform(0, 180)),
               kind="detail")


def scorch(C, x, y, r, *, seed=0, z=0.0):
    """그을린 바닥 자국 (데칼)."""
    rng = random.Random(seed)
    pts = []
    for i in range(14):
        a = i / 14 * math.tau
        rr = r * rng.uniform(0.65, 1.1)
        pts.append((math.cos(a) * rr, math.sin(a) * rr))
    C.decal("char", pts, (x, y, z), (0, 0, 1), lift=0.02)


def toppled_lamp(C, x, y, *, yaw=0.0, z=0.0, h=3.6):
    """쓰러진 가로등 (기둥이 yaw 쪽으로 누움, 등갓은 꺼짐)."""
    a = math.radians(yaw)
    d = Vector((-math.sin(a), -math.cos(a), 0))
    p0 = Vector((x, y, z + 0.12))
    p1 = p0 + d * h + Vector((0, 0, 0.15))
    C.cyl("dark", (x, y, z), (x, y, z + 0.3), 0.16, r2=0.12, segs=8, kind="detail")
    C.cyl("dark", p0, p1, 0.065, r2=0.05, segs=6, kind="detail")
    C.cyl("lamp_off", p1, p1 + d * 0.4 + Vector((0, 0, -0.05)), 0.2, r2=0.17, segs=8, kind="detail")


def broken_facade(C, x0, x1, y, *, h=9.0, z=0.0, seed=0, key="concrete", key_d="concrete_d", normal=(0, -1, 0),
                  holes=3, depth=0.4):
    """무너진 건물 정면 (x0~x1, 벽면 y). 윗선이 들쭉날쭉하고 창이 뻥 뚫려 있다. 정면 = normal."""
    rng = random.Random(seed * 17 + 3)
    sgn = 1 if normal[1] < 0 else -1
    yb = y + sgn * depth      # 벽 뒷면 쪽
    n = max(3, int((x1 - x0) / 1.6))
    xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    for i in range(n):
        top = z + h * rng.uniform(0.45, 1.0)
        C.box(key, xs[i], xs[i + 1], min(y, yb), max(y, yb), z, top)
        # 창 구멍 (어두운 판을 벽면 앞에)
        for k in range(int((top - z - 1.5) / 2.7)):
            if rng.random() < 0.55:
                zz = z + 1.4 + k * 2.7
                C.rect("char", ((xs[i] + xs[i + 1]) / 2, y - sgn * 0.0, zz + 0.7), normal, 0.9, 1.3, lift=0.03)
        C.box(key_d, xs[i], xs[i + 1], min(y, yb) - 0.05, max(y, yb) + 0.05, z, z + 0.5, kind="detail")
    for i in range(holes):
        cx = rng.uniform(x0 + 1, x1 - 1)
        rubble(C, cx, y - sgn * 1.2, rng.uniform(0.9, 1.6), seed=seed + i, z=z)


def dead_screen(C, center, normal, w, h, *, seed=0):
    """꺼진 도시 화면 (깨진 금 몇 줄)."""
    rng = random.Random(seed)
    C.plate("navy", [(-w / 2 - 0.2, -h / 2 - 0.2), (w / 2 + 0.2, -h / 2 - 0.2), (w / 2 + 0.2, h / 2 + 0.2), (-w / 2 - 0.2, h / 2 + 0.2)],
            center, normal, 0.25, kind="detail")
    R, U, N = mk.frame(normal)
    c = Vector(center) + N * 0.27
    C.rect("screen", tuple(c), normal, w, h, lift=0.0)
    for i in range(3):
        a = Vector((rng.uniform(-w / 3, w / 3), rng.uniform(-h / 3, h / 3)))
        b = a + Vector((rng.uniform(-w / 2, w / 2), rng.uniform(-h / 2, h / 2)))
        C.strip("rubble_d", c + R * a.x + U * a.y, c + R * b.x + U * b.y, 0.03, normal, lift=0.01)


def fire_barrel(C, x, y, *, z=0.0, lit=True, fid=None):
    """불 피운 드럼통 (빛: UNLIT 불꽃 + 가산 번짐). fid가 있으면 FX_fire_<fid> 마커."""
    C.cyl("barrel", (x, y, z), (x, y, z + 0.62), 0.22, segs=10)
    C.cyl("char", (x, y, z + 0.6), (x, y, z + 0.64), 0.23, segs=10, kind="detail")
    if lit:
        for i, (dx, dy, s) in enumerate(((0, 0, 0.16), (0.06, -0.04, 0.11), (-0.05, 0.05, 0.1))):
            C.blob("fire_glow", (x + dx, y + dy, z + 0.72 + i * 0.06), s, scale=(1, 1, 1.7), segs=8, rings=5)
        C.blob("fire_core", (x, y, z + 0.7), 0.09, scale=(1, 1, 1.6), segs=8, rings=5)
        C.cyl("firelight", (x, y, z + 0.02), (x, y, z + 0.03), 1.8, segs=20, kind="fine")
    if fid:
        C.fx(f"fire_{fid}", (x, y, z + 0.8), kind="fire")


def moon(C, at, r=14.0, *, key="moon"):
    """하늘의 달 (원판 + 테)."""
    d = Vector(at).normalized()
    C.decal(key, [(math.cos(i / 24 * math.tau) * r, math.sin(i / 24 * math.tau) * r) for i in range(24)], at, tuple(-d),
            lift=0.0)


def night_skyline(C, *, r=150.0, n=26, seed=5, fl=(8, 20), skip=None, key_far="far"):
    """원경 고층 실루엣 (밤 공기 원근). skip(x, y) → True면 그 자리는 비운다."""
    rng = random.Random(seed)
    for i in range(n):
        a = math.tau * (i + rng.uniform(-0.3, 0.3)) / n
        rr = r * rng.uniform(0.85, 1.2)
        sx, sy = math.cos(a) * rr, math.sin(a) * rr
        if skip and skip(sx, sy):
            continue
        w = rng.uniform(12, 24)
        d = rng.uniform(10, 18)
        mk.building(C, sx - w / 2, sx + w / 2, sy - d / 2, sy + d / 2, floors=rng.randint(*fl), style=("glass", "office")[i % 2],
                    far=True, seed=seed + i, h0=3.0, fh=3.0, r=3.0, col=False, sides="-y+y-x+x")
