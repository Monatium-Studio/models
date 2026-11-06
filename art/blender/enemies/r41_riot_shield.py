"""R41 진압반 육각 방패 (r41_riot_shield). 진압반(r41_riot)의 왼손 장비.

근거: docs/art/r41-style.md 7.2 (육각 방패: shell 테 + light 면 + 가로 amber 줄 + 엘프 로고, 위쪽 시야창),
도장은 PV 3:00~3:03 소총(회백 + 앰버 + 어두운 테)과 같다. 폭 0.45 m, 높이 0.60 m.

규약 (무기와 같은 소켓 규칙, docs/art/enemies-r41.md)
  - 원점 = 왼손 파지점(세로 손잡이 가운데). socket_hand_L에 그대로 자식으로 붙인다.
  - +Y = 방패 앞(적 쪽), +Z = 위. three.js에서는 앞이 -Z.
  - 앵커: grip(원점), face(앞면 가운데), top(윗변 가운데), bottom(아랫변 가운데)

npm run model -- art/blender/enemies/r41_riot_shield.py
npm run shot -- enemies/r41_riot_shield.glb --views front,34,side,34b
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import r41  # noqa: E402

cb.reset()
M = r41.mats()

Y0 = 0.044          # 판 뒷면
Z_TOP, Z_BOT, Z_MID = 0.27, -0.33, -0.03
HX, TX = 0.225, 0.13   # 옆 꼭짓점 반폭, 위·아래 변 반폭


def hexo(s=1.0, dz=0.0):
    """세로로 긴 육각 외곽선 (X, Z). s: 가운데(Z_MID) 기준 배율."""
    pts = [(-TX, Z_BOT), (TX, Z_BOT), (HX, Z_MID), (TX, Z_TOP), (-TX, Z_TOP), (-HX, Z_MID)]
    return [(x * s, Z_MID + (z - Z_MID) * s + dz) for x, z in pts]


def plate(name, pts, y_back, depth, mat, ch=0.0):
    o = cb.profile_extrude(name, pts, depth, axis="Y", loc=(0, y_back + depth / 2, 0), bevel=ch, bevel_segments=1,
                           material=mat)
    return o


# ---------------------------------------------------------------- 1차: 테 + 면
plate("rim", hexo(1.0), Y0, 0.016, M["shell"], ch=0.004)
FACE_Y = Y0 + 0.018
plate("face", hexo(0.90), Y0 + 0.004, 0.014, M["light"], ch=0.003)

# 2차: 시야창 (위쪽, 육각 테 안의 어두운 창)
win = [(-0.092, 0.150), (0.092, 0.150), (0.104, 0.196), (0.082, 0.232), (-0.082, 0.232), (-0.104, 0.196)]
plate("win_frame", [(x * 1.12, 0.191 + (z - 0.191) * 1.25) for x, z in win], FACE_Y - 0.004, 0.006, M["shell"],
      ch=0.0015)
plate("window", win, FACE_Y - 0.002, 0.006, M["metal"], ch=0.001)
# 창 반사선 (데칼)
for i, (x0, w) in enumerate(((-0.05, 0.010), (-0.028, 0.005))):
    cb.from_pydata(f"decal_win_hl{i}", [(x0, FACE_Y + 0.0045, 0.160), (x0 + w, FACE_Y + 0.0045, 0.160),
                                         (x0 + w + 0.03, FACE_Y + 0.0045, 0.224), (x0 + 0.03, FACE_Y + 0.0045, 0.224)],
                   [[0, 1, 2, 3]], material=M["light"])

# 가로 앰버 줄 (면을 가로지름)
r41.chbox("amber_band", (0.330, 0.004, 0.022), (0, FACE_Y + 0.0012, 0.085), ch=0.0008, mat=M["amber"])
r41.chbox("amber_line", (0.300, 0.003, 0.006), (0, FACE_Y + 0.0010, 0.058), ch=0.0006, mat=M["amber"])
# 줄 양 끝을 테 안으로 자르는 대신 짙은 끝마개
for sx in (1, -1):
    r41.chbox(f"band_cap{sx}", (0.014, 0.006, 0.030), (sx * 0.165, FACE_Y + 0.0015, 0.085), ch=0.001, mat=M["shell"])

# 엘프 로고 (밝은 면 → shell) + 막대 부호
r41.elf_logo("face_", (0, FACE_Y + 0.0004, -0.085), 0.115, axis="Y", sign=1, mat=M["shell"])
r41.stencil_bars("face_", (0, FACE_Y + 0.0004, -0.190), axis="Y", sign=1, h=0.014, unit=0.0055,
                 pattern=(1, 1, 0, 1, 0, 1, 1), mat=M["shell"])

# 아래 발판 (세워 두는 받침) + 테 나사
r41.chbox("kick", (0.20, 0.022, 0.018), (0, Y0 + 0.010, Z_BOT - 0.004), ch=0.003, mat=M["metal"])
for i, (x, z) in enumerate(hexo(0.955)):
    r41.screw(f"screw{i}", (x * 0.97, Y0 + 0.017, z), axis="Y", r=0.0055, h=0.003, mat=M["metal"])

# ---------------------------------------------------------------- 뒷면: 세로 손잡이 + 받침 + 팔 패드
r41.cyl_z("handle", 0.0125, 0.105, (0, 0, 0), verts=10, mat=M["shell"])
for sz in (1, -1):
    r41.chbox(f"standoff{sz}", (0.030, Y0 + 0.004, 0.018), (0, Y0 / 2, sz * 0.060), ch=0.003, mat=M["metal"])
r41.chbox("back_pad", (0.12, 0.012, 0.20), (0, Y0 - 0.005, 0.10), ch=0.004, mat=M["shell"])
r41.chbox("back_strap", (0.13, 0.006, 0.024), (0, Y0 - 0.012, 0.13), ch=0.002, mat=M["metal"])

r41.finish("r41_riot_shield", "enemies/r41_riot_shield.glb",
           anchors={"grip": (0, 0, 0), "face": (0, FACE_Y, Z_MID), "top": (0, Y0 + 0.008, Z_TOP),
                    "bottom": (0, Y0 + 0.008, Z_BOT)},
           props={"outline": 0.004, "socket": "socket_hand_L", "unit": "riot"})
