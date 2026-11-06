"""우주 배경: 은은한 성운 하늘 돔 + 별 (프롤로그 우주 장면).

[오리지널] 툰 화면에서 깔끔하게 읽히도록
  - 하늘 돔: 안쪽을 보는 구 (UNLIT 텍스처 1024×512). 아주 어두운 남색 바탕에 2~3단으로 끊은
    은하수 띠와 청록·보라 성운 얼룩을 낮은 대비로 넣는다 (레벨 sky 색과 이어짐)
  - 별: 중심을 보는 작은 마름모 판 (UNLIT 정점색: 흰색, 연한 시안, 연한 노랑, 연한 분홍). 은하수 띠에 더 촘촘
  - 반짝이 별: 네 갈래 툰 별 (큰 별 몇 개)
모든 노드 collider=0, noOutline=1. 반지름 RADIUS(기본 540 m)는 장면 카메라 far(600 m) 안에 들게 정한다.

npm run model -- art/blender/space/starfield.py
npm run shot -- space/starfield.glb --views front,top
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh  # noqa: E402
import bpy  # noqa: E402
import cb  # noqa: E402
import space_kit as sk  # noqa: E402
from mathutils import Vector  # noqa: E402

RADIUS = 540.0
N_STARS = 1900
N_SPARKLE = 36
TEX_DIR = os.path.join(os.environ.get("TMPDIR", "/tmp"), "combatium_space_tex")
# 은하수 띠의 극 (이 방향에 수직인 큰 원이 띠): 장면에서 함대 진행 방향을 비스듬히 가로지르게
BAND_POLE = Vector((0.35, 0.25, 0.9)).normalized()
STAR_COLS = ["#ffffff", "#ffffff", "#ffffff", "#eefcff", "#d6f6ff", "#fff6dc"]


def sky_texture(w=1024, h=512, seed=4):
    lon = (np.arange(w, dtype=np.float32) + 0.5) / w * 2 * np.pi - np.pi
    lat = np.pi / 2 - (np.arange(h, dtype=np.float32) + 0.5) / h * np.pi
    LO, LA = np.meshgrid(lon, lat)
    P = np.stack([np.cos(LA) * np.sin(LO), -np.cos(LA) * np.cos(LO), np.sin(LA)], axis=-1)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from earth import Noise3
    nz = Noise3(seed)
    pole = np.array(BAND_POLE, dtype=np.float32)
    band = np.exp(-((P @ pole) / 0.22) ** 2) * (0.6 + 0.8 * nz.fbm(P * 2.5, 4))
    neb_a = nz.fbm(P * 1.6 + 5.0, 4)
    neb_b = nz.fbm(P * 1.9 - 3.0, 4)
    base = np.array([0x06, 0x09, 0x1a], dtype=np.float32)
    rgb = np.empty(P.shape, dtype=np.float32)
    rgb[:] = base
    # 2단 툰 계단, 바탕과 아주 가깝게 (은은하게)
    rgb[band > 0.5] = (0x0a, 0x0f, 0x26)
    rgb[band > 0.8] = (0x0e, 0x14, 0x30)
    rgb[(neb_a > 0.68)] = (0x09, 0x15, 0x27)
    rgb[(neb_a > 0.74)] = (0x0b, 0x1b, 0x2e)
    rgb[(neb_b > 0.70)] = (0x10, 0x0e, 0x26)
    rgb[(neb_b > 0.76)] = (0x15, 0x11, 0x2e)
    return np.clip(rgb, 0, 255).astype(np.uint8)


def star_points(n, rng):
    """은하수 띠 근처에 더 몰리는 무작위 방향."""
    out = []
    while len(out) < n:
        v = Vector(rng.normal(size=3)).normalized()
        dens = 0.35 + 0.65 * math.exp(-(v.dot(BAND_POLE) / 0.3) ** 2)
        if rng.random() < dens:
            out.append(v)
    return out


def build(radius=RADIUS, *, name="starfield", seed=11):
    rng = np.random.default_rng(seed)
    root = cb.empty(name, size=10.0)
    root["collider"] = 0
    root["noOutline"] = 1
    # 하늘 돔
    os.makedirs(TEX_DIR, exist_ok=True)
    png = sk.save_png(os.path.join(TEX_DIR, f"{name}_sky.png"), sky_texture())
    dome = sk.uv_sphere(f"{name}_dome", radius * 1.03, 32, 16, inward=True)
    dome.data.materials.append(sk.image_material(f"{name}_dome", png, unlit=True, double_sided=False))
    dome.parent = root
    dome["collider"] = 0
    # 별: 마름모 판
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    for v in star_points(N_STARS, rng):
        c = v * radius
        size = (1.2 + rng.random() ** 3 * 2.4) * radius / 540.0
        U = Vector((0, 0, 1)) if abs(v.z) < 0.95 else Vector((1, 0, 0))
        R = U.cross(v).normalized()
        U = v.cross(R).normalized()
        ang = rng.random() * math.pi
        R, U = R * math.cos(ang) + U * math.sin(ang), U * math.cos(ang) - R * math.sin(ang)
        vs = [bm.verts.new(c + R * size), bm.verts.new(c + U * size), bm.verts.new(c - R * size),
              bm.verts.new(c - U * size)]
        f = bm.faces.new(vs)
        rgb = sk.srgb(STAR_COLS[int(rng.integers(len(STAR_COLS)))])
        dim = 0.72 + 0.28 * rng.random()
        for lp in f.loops:
            lp[col] = (*[cb.srgb_to_linear(x * dim) for x in rgb], 1.0)
    # 반짝이 별 (네 갈래)
    for v in star_points(N_SPARKLE, rng):
        c = v * radius * 0.995
        size = (4.0 + rng.random() * 5.0) * radius / 540.0
        U = Vector((0, 0, 1)) if abs(v.z) < 0.95 else Vector((1, 0, 0))
        R = U.cross(v).normalized()
        U = v.cross(R).normalized()
        pts = []
        for k in range(8):
            a = math.pi / 4 * k
            r = size if k % 2 == 0 else size * 0.22
            pts.append(c + (R * math.cos(a) + U * math.sin(a)) * r)
        center = bm.verts.new(c)
        ring = [bm.verts.new(p) for p in pts]
        rgb = sk.srgb(STAR_COLS[int(rng.integers(len(STAR_COLS)))])
        for k in range(8):
            f = bm.faces.new((center, ring[k], ring[(k + 1) % 8]))
            for lp in f.loops:
                lp[col] = (*[cb.srgb_to_linear(x) for x in rgb], 1.0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    flip = [f for f in bm.faces if f.normal.dot(f.calc_center_median()) > 0]
    if flip:
        bmesh.ops.reverse_faces(bm, faces=flip)       # 중심(카메라 쪽)을 보게
    stars = cb._new_mesh_obj(f"{name}_stars", bm)
    me = stars.data
    # loop 색 레이어 → 'Col' 색 속성
    if "Col" in me.color_attributes:
        me.color_attributes.active_color = me.color_attributes["Col"]
    stars.data.materials.append(sk.vc_material("sk_star_vc", unlit=True))
    stars.parent = root
    stars["collider"] = 0
    stars["noOutline"] = 1
    return root


if __name__ == "__main__":
    cb.reset()
    root = build()
    sk.export_glb("space/starfield.glb", root=root)
