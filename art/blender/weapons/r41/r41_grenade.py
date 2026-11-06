"""R41 G-5 '땅벌' 세열 수류탄 (노획품).

R41 소총병의 표준 세열 수류탄. 육각 캔 표면의 벌집 돌기가 미리 나눈 파편이다(예비 파편).
테마극장 PV에는 수류탄이 나오지 않아서 형태는 R41 형태 언어(육각, 말벌 이름)와 소총 도장(어두운 몸통 + 회백 띠 + 앰버)을 따른다.
엘프 손에 맞춘 높이 0.115 m. 원점 = 쥐는 손 중심(몸통 중심), 위 = +Z, 안전손잡이(레버)는 -X 면.

npm run model -- art/blender/weapons/r41/r41_grenade.py
npm run shot -- weapons/r41/r41_grenade.glb --views side,34,top,muzzle --focus r41_grenade
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import r41  # noqa: E402

cb.reset()
M = r41.mats()
R = 0.023                       # 육각 외접 반지름
APO = R * math.cos(math.radians(30))


def hexz(name, r, h, z, mat, r2=None, ch=0.0012):
    """Z축 육각 기둥, 평면이 ±X를 향함."""
    return r41.ngon_prism(name, 6, r, h, (0, 0, z), axis="Z", rot_deg=30, r2=r2, mat=mat, ch=ch)


def studs(prefix, z_rows, skip=(), r=0.0034, cols=(-0.0068, 0.0068)):
    """면마다 작은 육각 돌기 (예비 파편). skip = 건너뛸 면 각도."""
    out = []
    for k in range(6):
        ang = 60 * k
        if ang in skip:
            continue
        a = math.radians(ang)
        n = (math.cos(a), math.sin(a))
        t = (-math.sin(a), math.cos(a))
        for z in z_rows:
            for u in cols:
                c = (n[0] * (APO + 0.0006) + t[0] * u, n[1] * (APO + 0.0006) + t[1] * u, z)
                o = cb.cylinder(f"{prefix}{k}_{z}_{u}", radius=r, depth=0.0016, loc=c, rot=(0, 90, ang), verts=6,
                                material=M["metal"])
                out.append(o)
    return out


# ---------------------------------------------------------------- 아래 몸통 (어두운 색 + 벌집 돌기)
hexz("bottom_cap", R * 0.72, 0.010, -0.051, M["shell"], r2=R * 0.98, ch=0.0015)
hexz("bottom_ring", R * 1.0, 0.004, -0.0445, M["amber"], ch=0.0006)
hexz("lower_body", R, 0.040, -0.0235, M["shell"], ch=0.0015)
studs("stud_lo", (-0.0335, -0.0225, -0.0115), skip=(180,))
r41.cyl_z("base_plug", 0.0075, 0.003, (0, 0, -0.0575), verts=12, mat=M["metal"])

# ---------------------------------------------------------------- 가운데 회백 띠 + 위 몸통
hexz("band", R * 1.03, 0.008, -0.0005, M["light"], ch=0.0010)
for k in range(6):
    if k * 60 == 180:
        continue
    a = math.radians(60 * k)
    cb.box(f"band_stripe{k}", size=(0.0010, 0.016, 0.0022), loc=(math.cos(a) * (R * 1.03 * math.cos(math.radians(30)) + 0.0003),
                                                                    math.sin(a) * (R * 1.03 * math.cos(math.radians(30)) + 0.0003), -0.0005),
           rot=(0, 0, 60 * k), material=M["amber"])
hexz("body", R, 0.032, 0.0195, M["shell"], ch=0.0015)
hexz("shoulder", R * 0.98, 0.012, 0.0415, M["shell"], r2=R * 0.52, ch=0.0012)
studs("stud_hi", (0.0110, 0.0230), skip=(0, 180))
# 엘프 로고 (+X 면, 앰버)
r41.elf_logo("X_", (APO + 0.0001, 0.0, 0.0185), 0.022, axis="X", sign=1, mat=M["amber"])

# ---------------------------------------------------------------- 신관
r41.cyl_z("fuse", 0.0095, 0.012, (0, 0, 0.0525), verts=16, mat=M["metal"], ch=0.0010)
r41.cyl_z("fuse_top", 0.0070, 0.003, (0, 0, 0.0595), verts=16, mat=M["steel"])
r41.cyl_z("fuse_plug", 0.0030, 0.0015, (0, 0, 0.0612), verts=10, mat=M["amber"])
for sx in (1, -1):
    r41.cyl_y(f"pin_lug{sx}", 0.0030, 0.004, (0, sx * 0.0100, 0.0505), verts=8, mat=M["metal"])

# ---------------------------------------------------------------- 안전손잡이 (움직이는 파츠, -X 면)
lever_pts = [(0.004, 0.0600), (-0.0100, 0.0600), (-0.0205, 0.0505), (-0.0218, 0.0420), (-0.0218, -0.0010),
             (-0.0199, -0.0040), (-0.0199, 0.0410), (-0.0188, 0.0488), (-0.0094, 0.0582), (0.004, 0.0582)]
lever = [cb.profile_extrude("lever_strip", lever_pts, 0.011, axis="Y", bevel=0.0005, bevel_segments=1,
                            material=M["amber"])]
lever.append(cb.box("lever_rib", size=(0.0010, 0.004, 0.030), loc=(-0.0222, 0, 0.020), material=M["shell"]))

# ---------------------------------------------------------------- 안전핀 + 고리 (움직이는 파츠)
pin = [r41.cyl_y("pin_rod", 0.0012, 0.026, (0, -0.002, 0.0505), verts=8, mat=M["steel"]),
       r41.tube("pin_ring", 0.0105, 0.0078, 0.0022, (0, -0.0225, 0.0440), axis="X", verts=20, mat=M["steel"]),
       cb.box("pin_tab", size=(0.003, 0.006, 0.006), loc=(0, -0.0145, 0.0490), rot=(-30, 0, 0), material=M["steel"])]
# 노획 태그는 핀 고리에 묶는다 (던지기 전 떼어 냄)
tag = r41.capture_tag("cap_", (0, -0.0300, 0.0370), mat_tag=M["ceramic"], mat_cord=M["amber"],
                      size=(0.014, 0.0010, 0.018), drop=0.016, swing=6)
pin += tag

r41.finish(
    "r41_grenade", "weapons/r41/r41_grenade.glb",
    moving={
        "lever": (lever, (0.000, 0, 0.0590)),
        "pin": (pin, (0, -0.002, 0.0505)),
    },
    anchors={
        "fuse": (0, 0, 0.062),
        "core": (0, 0, -0.010),
        "grip_support": (-0.024, 0, 0.020),
    },
    props={"outline": 0.0016, "fpOffset": "0.11,-0.095,-0.24", "fpRot": "0,-115,0"},
)
