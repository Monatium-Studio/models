"""툰 달 (프롤로그 우주 장면 배경, 선택 요소).

[오리지널] 평탄한 회색 + 어두운 바다(현무암 평원) 얼룩 + 몇 개의 크레이터 고리 (절차 생성, 외부 이미지 없음).
지구처럼 UNLIT 텍스처에 태양 방향으로 툰 2단 + 밤 면을 굽는다. 장면 스크립트가 장면의 태양 방향으로
build(sun_local=...)을 다시 불러 같은 빛을 맞춘다. 단독 실행하면 기본 태양으로 space/moon.glb를 만든다.

npm run model -- art/blender/space/moon.py
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb  # noqa: E402
import space_kit as sk  # noqa: E402

TEX_DIR = os.path.join(os.environ.get("TMPDIR", "/tmp"), "combatium_space_tex")
W, H = 512, 256


def bake(sun_local, seed=5):
    from earth import Noise3, lonlat_grid, unit
    lon, lat = lonlat_grid(W, H)
    N = unit(lon, lat)
    nz = Noise3(seed)
    rgb = np.empty(N.shape, dtype=np.float32)
    rgb[:] = (0xc9, 0xc6, 0xcf)
    maria = nz.fbm(N * 2.2 + 1.0, 4)
    rgb[maria > 0.56] = (0xa3, 0xa0, 0xad)
    rgb[maria > 0.63] = (0x8f, 0x8c, 0x9b)
    rng = np.random.default_rng(seed)
    for _ in range(26):
        c = rng.normal(size=3)
        c /= np.linalg.norm(c)
        r = 0.04 + rng.random() ** 2 * 0.16
        d = np.arccos(np.clip(N @ c.astype(np.float32), -1, 1))
        rgb[(d < r) & (d > r * 0.72)] = (0xb2, 0xaf, 0xbb)
        rgb[d < r * 0.72] = rgb[d < r * 0.72] * 0.93
    s = np.array(sun_local, dtype=np.float32)
    s /= np.linalg.norm(s)
    dd = N @ s
    rgb[(dd < 0.3) & (dd >= 0.0)] *= np.array([0.84, 0.85, 0.92], dtype=np.float32)
    night = dd < 0.0
    rgb[night] = rgb[night] * 0.16 + np.array([0x10, 0x15, 0x2c], dtype=np.float32) * 0.9
    return np.clip(rgb + 0.5, 0, 255).astype(np.uint8)


def build(sun_local=(0.0, 0.6, 0.8), *, radius=18.0, name="moon"):
    os.makedirs(TEX_DIR, exist_ok=True)
    png = sk.save_png(os.path.join(TEX_DIR, f"{name}_toon.png"), bake(sun_local))
    root = cb.empty(name, size=radius * 0.3)
    ball = sk.uv_sphere(f"{name}_surface", radius, 28, 14)
    ball.data.materials.append(sk.image_material(f"{name}_surface", png, unlit=True))
    ball["collider"] = 0
    ball["noOutline"] = 1
    ball.parent = root
    root["collider"] = 0
    root["sunLocal"] = ",".join(f"{v:.4f}" for v in sun_local)
    return root


if __name__ == "__main__":
    cb.reset()
    sk.export_glb("space/moon.glb", root=build())
