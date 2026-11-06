"""죠안: 세계수 교단의 고참 사제이자 엘다인(몽환살이) 요정. 엘리아스 침공전에서 교주 편으로 싸우고, 에르피엔 결전에서
아멜리아(R41)와 함께 R41 돌격 편대를 설득해 대거 이탈시킨다(원작). 이 작품에서는 3막 M9 종막의 배경 장면에 쓴다.

원작 죠안(트릭컬 리바이브, '찐 근본 교단 사제')의 기본 고위 사제복을 따른다. 근거: docs/art/characters-cameo3.md.
- 식별 요소: 짙은 초록 머리(옆으로 넘긴 흐트러진 앞머리, 가슴까지 오는 옆머리, 뒤로 땋아 올린 경단), 반쯤 감긴 붉은 눈과
  고요한 미소, 머리 양옆의 검은 깃털 날개 두 쌍(금색 깃대, 요정 중 유일하게 머리에 날개), 왼쪽 머리의 작은 잎 장식,
  검은 세운 깃(금 걸쇠)과 흰 몸판, 검은 부푼 소매(흰 소맷단과 금 단추), 금 사슬 허리띠와 큰 금 자물쇠, 금테 검은 앞자락,
  흰 니하이(물결 윗단), 검은 신, 땅까지 오는 검정→초록 그라데이션 망토(금 테두리, 해진 밑단), 몸에 둘러진 금·은 사슬.
- 재해석: 3D SD 비율에 맞춰 사슬은 왼손목에서 땅으로 늘어진 한 줄과 허리 사슬로 정리했다. 원작 망토의 금 덩굴 자수는
  옮기지 않고 금 테두리 두 줄로 바꿨다. 노출(가슴 트임·옆트임)은 흰 몸판과 검은 속바지로 덮었다.
- 표정: 키트 5종 + devout(눈을 감은 기도), zealot(광신: 크게 뜬 눈과 작은 동공, 웃는 입) + stern(설득하는 엄한 얼굴)
  + blink 교정 키(devout 제외).

npm run model -- art/blender/characters/joan.py
npm run shot -- characters/joan.glb
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.environ["COMBATIUM_ROOT"], "art", "blender", "lib"))
import cb  # noqa: E402
import elf  # noqa: E402
import fairy  # noqa: E402
import cameo2 as c2  # noqa: E402
import cameo3 as c3  # noqa: E402
from elf import V, Matrix, Buf, loft, band, rbox, disc, lerp, smoothstep, frame  # noqa: E402

cb.reset()
e = fairy.Fairy("joan", ears="round", ear_size=0.95, height=1.24, head=0.45, leg=1.04, chest=0.50, bust=0.60, hips=1.06,
                segs=0.62, hand_q=0.42, cheek=0.10)
k = e.k
M_ = elf.mat

HAIR, HAIR_D, HAIR_L = "#3f7a5b", "#244a39", "#6ea887"
CAPE_HEX, CAPE_GREEN = "#34313b", "#a8c98d"
black = M_("jo_black", "#25232b")
black_l = M_("jo_black_l", "#3c3944")
white = M_("jo_white", "#fbf9f6")
white_d = M_("jo_white_d", "#e4ded8")
gold = M_("jo_gold", "#e3b955")
gold_d = M_("jo_gold_d", "#b98a33")
silver = M_("jo_silver", "#c8cbd6")
cape_m = M_("jo_cape", CAPE_HEX)
leaf_m = M_("jo_leaf", "#7cae6a")
ember = M_("jo_ember", "#e0743a")

# ---- 얼굴: 반쯤 감긴 붉은 눈, 고요한 미소, 볼 빗금
fairy.face(e, eye_color="#d8464c", iris_dark="#7d1e2c", iris_light="#ff9f8c", pupil="#5a1220",
           lash="#3a2a2c", brow="#2f5a45", brow_th=1.0, blush="#f4a2a4", blush_size=1.1, blush_lines=3,
           base={"eye": {"top": 0.0125, "ktop": 5.6, "tilt_in": 0.002, "cout": 0.016},
                 "brow": {"ang": 6.0, "dz": 0.066, "arch": 0.003},
                 "mouth": {"w": 0.020, "curve": 0.0040}},
           expr={
               # 기도: 눈을 감고 온화하게
               "devout": {"eye": {"close": 1.0, "lift": 0.006},
                          "brow": {"ang": 10.0, "dz": 0.068, "arch": 0.004},
                          "mouth": {"w": 0.018, "curve": 0.0040}},
               # 광신: 크게 뜬 눈, 아주 작은 동공, 활짝 웃는 입 (원작 폭주 장면의 섬뜩함)
               "zealot": {"eye": {"top": 0.036, "ktop": 2.2, "bot": 0.058},
                          "iris": {"pupil": 0.35, "rx": 0.024, "ry": 0.032},
                          "brow": {"ang": 14.0, "dz": 0.076},
                          "mouth": {"w": 0.040, "curve": 0.0110, "open": 0.0160, "top_arch": -0.0020}},
               # 설득: 눈썹을 모은 엄한 얼굴, 말하는 입
               "stern": {"eye": {"top": 0.016, "ktop": 4.4, "tilt_in": -0.008},
                         "brow": {"ang": -12.0, "dz": 0.058, "th": 0.0070},
                         "mouth": {"w": 0.020, "curve": -0.0015, "open": 0.0070, "top_arch": 0.0010}},
           })

# ---- 머리 (헤어 v2): 짙은 초록, 흐트러진 옆가르마 앞머리, 가슴까지 오는 옆머리, 뒤로 땋아 올린 경단
def soft_bangs(h, lk):
    if lk["region"] == "front":
        lk["p"] = 2.0
        lk["free"] *= 0.7


h = fairy.hair(e, HAIR, dark=HAIR_D, light=HAIR_L, volume=1.12, lock_fn=fairy.lock_edit(soft_bangs))
h.cap(front=28, side=-6, back=-48, part=18, segs=16, rows=5)
h.bangs(n=7, spread=58, tip_el=-6, sweep=10, part=18, jag=0.14, curl=1.3, seed=11.0)
h.sides(length=0.26, width=0.084, az=62, curl=0.9, puff=1.2, thick=1.1)
h.back(length=0.05, n=7, spread=96)
h.bun(az=180.0, el=-6.0, size=0.072)
hc = e.head_c
# 경단을 두르는 땋은 고리 (브레이디드 번)
ring = []
for i in range(13):
    a = math.radians(360.0 * i / 12)
    s0 = h.s_of_el(180.0, -6.0)
    p0, n0 = h.path(180.0, s0)
    ring.append(p0 + n0 * 0.040 * k + V((math.cos(a) * 0.050 * k, 0.0, math.sin(a) * 0.044 * k)))
c2.braid(h, ring, 0.034 * k, 0.034 * k, beads=11, tilt=30.0, face_fn=lambda q: V((0, 1, 0)))
h.shine(el=52, spread=70, n=2, size=0.85)


# ---- 머리 양옆 검은 깃털 날개 두 쌍 (금색 깃대) + 왼쪽 잎 장식
def head_wings(buf):
    w = {"head": 1.0}
    for s in (1, -1):
        for (az, el, ang, L, nf, sc) in ((68.0, 36.0, 46.0, 0.200, 4, 1.25), (90.0, 4.0, -38.0, 0.190, 3, 1.15)):
            p, nn = h.path(s * az, h.s_of_el(s * az, el), 0.004 * k)
            out = V((s, 0.10, 0.0)).normalized()
            up = V((0, 0, 1))
            # 날개 평면: 바깥(out)과 위(up) 사이, 약간 뒤로
            d = (out * math.cos(math.radians(ang)) + up * math.sin(math.radians(ang))).normalized()
            # 날개 면은 앞을 본다 (정면에서 깃 모양이 읽히게), 바깥으로 조금 비튼다
            nrm = V((s * 0.30, -1.0, 0.0)).normalized()
            for i in range(nf):
                f = i / max(nf - 1, 1)
                # 깃은 위 깃부터 아래로 부채꼴로 펼쳐진다 (위 날개는 바깥 아래로, 아래 날개는 더 아래로)
                rot = math.radians(-24.0 * f)
                dd = (d * math.cos(rot) + V((0, 0, -1)) * math.sin(-rot) * 0.0 +
                      (V((0, 0, 1)).cross(nrm) * -s) * 0.0)
                side_v = nrm.cross(d).normalized()
                dd = (d * math.cos(rot) + side_v * math.sin(rot) * (s if ang > 0 else -s)).normalized()
                ln = L * sc * (1.0 - 0.18 * f) * k
                root = p + V((0, 0.010 * k * i, -0.004 * k * i))
                Mf = Matrix.Translation(root) @ frame(nrm, dd)
                c2.prism(buf, [(x * k, z * k) for x, z in c3.leaf_poly(ln / k, 0.044 * sc, n=6, tip=1.15)],
                         0.006 * k, Mf @ Matrix.Translation((0, 0.003 * k + 0.0015 * k * i, 0)),
                         mat=black if i % 2 == 0 else black_l, w=w, chamfer=0.0012 * k)
                if i == 0:
                    c2.prism(buf, [(x * k, z * k) for x, z in c3.leaf_poly(ln / k * 0.62, 0.010, n=4)],
                             0.002 * k, Mf @ Matrix.Translation((0.004 * k, -0.0035 * k, 0.020 * k)), mat=gold,
                             w=w)
    # 왼쪽 머리(+X) 잎 장식 (작은 잎 셋 + 주황 불씨 알)
    p, nn = h.path(52.0, h.s_of_el(52.0, -4.0), 0.003 * k)
    Ml = Matrix.Translation(p) @ frame(nn, (0, 0, 1))
    for ang in (-30.0, 20.0, 70.0):
        c2.prism(buf, [(x * k, z * k) for x, z in c3.leaf_poly(0.030, 0.014, n=4)], 0.003 * k,
                 Ml @ Matrix.Rotation(math.radians(ang), 4, "Y"), mat=leaf_m, w=w)
    c2.ellipsoid(buf, Ml @ V((0, -0.004 * k, 0)), V((0, 0, 1)), V((1, 0, 0)), nn, 0.006 * k, 0.006 * k, 0.005 * k,
                 segs=6, rings=4, mat=ember, w=w)


e.part("head_wings", "head", head_wings)

# ---- 몸판: 흰 몸판 + 검은 세운 깃(금 걸쇠), 검은 부푼 소매(흰 소맷단, 금 단추)
cz, wz, hz = e.chest_z, e.waist_z, e.hipj_z
sz = e.shoulder_z
e.shirt(white, hem=hz - 0.010 * k, collar="stand", collar_mat=black, flare=0.008)
e.sleeves(black, length=0.86, off=0.012, flare=0.006, puff=0.016, cuff=(white, 0.030, 0.005))
for sd in ("L", "R"):
    a = e.anchor((f"arm_{sd}", 0.84, 0, 0.026 * k))
    e.part(f"cuff_btn_{sd}", "arms", lambda buf, a=a: disc(buf, a.pos, a.n, (0, 0, 1), 0.0050 * k, 0.0050 * k,
                                                             0.002 * k, segs=8, mat=gold, w=a.w))
# 가슴을 비스듬히 가로지르는 금 사슬 (원작: 몸에 둘러진 사슬)
chest_pts = [e.torso_point(z, a, 0.022 * k)[0] for z, a in
             ((sz + 0.004 * k, 46.0), (cz + 0.010 * k, 18.0), (cz - 0.030 * k, -14.0), (wz + 0.004 * k, -44.0))]
e.part("chain_chest", "body", lambda buf: c3.chain(buf, chest_pts, 0.032 * k, 0.0034 * k, gold, mat2=silver,
                                                   every=3, w=lambda t: e._torso_wfn(chest_pts[min(int(t * 3), 3)], 0),
                                                   segs=5, ring=3))
p_c, n_c = e.torso_point(e.torso_top + 0.004 * k, 0, 0.040 * k)
e.part("collar_clasp", "body", lambda buf: c2.prism(buf, c2.diamond_poly(0.020 * k, 0.026 * k), 0.004 * k,
                                                      Matrix.Translation(p_c) @ frame(n_c, (0, 0, 1)), mat=gold,
                                                      w={"neck": 0.4, "chest": 0.6}, chamfer=0.0015 * k))

# ---- 하의: 검은 속바지, 금테 검은 앞·뒤 자락(땅까지), 흰 니하이, 검은 신
q0 = e.q
e.q = 0.5
e.pants(black, length=0.10, bag=0.004, blouse=0.0, off=0.008)
e.q = q0
front = c2.Shell(e, black, wz + 0.004 * k, 0.030 * k, gap=144.0, back_only=True, off=0.020, th=0.004, skirt=True,
                 rows=9, cols=8, flare=[(0.0, 0.0), (0.4, 0.010), (1.0, 0.030)])
front.edge_trim(gold, width=0.008, th=0.002).hem_trim(gold, width=0.008, th=0.002)
pc, pn = front.surface(0.10, 0.0, 0.004 * k)
Mo = Matrix.Translation(pc) @ frame(pn, (0, 0, 1))
wo = c2.skirt_w(e, pc)
c2.prism(front.buf, [(0.0, 0.020 * k), (0.022 * k, -0.004 * k), (0.0, -0.040 * k), (-0.022 * k, -0.004 * k)],
         0.004 * k, Mo, mat=gold, w=wo, chamfer=0.0015 * k)
c2.prism(front.buf, c2.diamond_poly(0.010 * k, 0.018 * k), 0.003 * k, Mo @ Matrix.Translation((0, -0.004 * k, -0.006 * k)),
         mat=black_l, w=wo)
front.done("front_panel")
back = c2.Shell(e, black, wz + 0.004 * k, 0.030 * k, gap=140.0, off=0.020, th=0.004, skirt=True, rows=9, cols=8,
                flare=[(0.0, 0.0), (0.4, 0.012), (1.0, 0.036)])
back.edge_trim(gold, width=0.008, th=0.002).hem_trim(gold, width=0.008, th=0.002)
back.done("back_panel")
for sd in ("L", "R"):
    c2.leg_tube(e, white, sd, 0.26, 0.90, off=0.005, name=f"stocking_{sd}", segs=10)
    e.ring(white_d, f"leg_{sd}", 0.27, h=0.018, th=0.004, off=0.008, name=f"stocking_top_{sd}")
e.boots(black, top=0.90, sole=(black_l, 0.012), off=0.010, toe=0.004)

# ---- 금 사슬 허리띠 + 큰 금 자물쇠
belt_pts = []
for i in range(17):
    a = 360.0 * i / 16
    p, n = e.torso_point(wz - 0.012 * k, a, 0.030 * k)
    belt_pts.append(p - V((0, 0, 0.010 * k * math.cos(math.radians(a)) ** 2)))
e.part("chain_belt", "body", lambda buf: c3.chain(buf, belt_pts, 0.036 * k, 0.0038 * k, gold,
                                                  w=lambda t: e._torso_wfn(belt_pts[min(int(t * 16), 16)], 0),
                                                  segs=5, ring=3))


def padlock(buf, Mx, w):
    rbox(buf, (0.046 * k, 0.020 * k, 0.040 * k), Mx @ Matrix.Translation((0, -0.012 * k, -0.010 * k)), mat=gold,
         w=w, r=0.35, segs=1)
    pts = [Mx @ V((math.cos(math.radians(a)) * 0.015 * k, -0.012 * k, 0.010 * k + math.sin(math.radians(a)) * 0.016 * k))
           for a in range(0, 181, 20)]
    loft(buf, [{"c": q, "rx": 0.0035 * k, "ry": 0.0035 * k, "w": w} for q in pts], segs=6, cap0="flat",
         cap1="flat", mat=gold_d)
    disc(buf, Mx @ V((0, -0.023 * k, -0.012 * k)), (Mx.to_3x3() @ V((0, -1, 0))).normalized(),
         Mx.to_3x3() @ V((0, 0, 1)), 0.0045 * k, 0.0045 * k, 0.0015 * k, segs=8, mat=black, w=w)


e.gear("padlock", ("torso", wz - 0.030 * k, 4.0, 0.034 * k), padlock)

# ---- 땅까지 오는 망토 (검정 → 초록 그라데이션, 금 테두리 두 줄, 해진 밑단)
cape = c2.Shell(e, cape_m, e.torso_top + 0.008 * k, 0.020 * k, gap=[(0.0, 58.0), (0.3, 70.0), (1.0, 86.0)],
                off=0.034, th=0.005, shoulder=1.06, rows=12, cols=16, skirt=True,
                flare=[(0.0, 0.0), (0.25, 0.026), (1.0, 0.110)], ruffle=(0.010, 9, 0.85),
                drop=[(0.0, 0.0), (1.0, 0.02)])
cape.edge_trim(gold, width=0.008, th=0.002, i0=1).hem_trim(gold, width=0.008, th=0.002, row=cape.rows - 2)
cape.done("cape")

# ---- 사슬: 왼손목에서 땅으로 늘어진 금·은 사슬 (원작: 손목에 감긴 사슬)
W = e.W["L"]
ch_pts = [W + V((0.006 * k, 0.0, 0.0)), W + V((0.040 * k, -0.020 * k, -0.100 * k)),
          V((W.x + 0.080 * k, -0.050 * k, 0.140 * k)), V((W.x + 0.040 * k, -0.090 * k, 0.012 * k)),
          V((W.x - 0.030 * k, -0.120 * k, 0.010 * k))]
e.part("chain_wrist", "arms",
       lambda buf: (c3.chain(buf, ch_pts[:2], 0.032 * k, 0.0038 * k, silver, mat2=gold, every=2,
                             w={"hand_L": 0.5, "forearm_L": 0.5}, segs=6, ring=3)))
e.part("chain_drop", "body",
       lambda buf: c3.chain(buf, ch_pts[1:], 0.032 * k, 0.0038 * k, silver, mat2=gold, every=2,
                            w={"hips": 1.0}, segs=6, ring=3))
for sd in ("L", "R"):
    e.ring(gold, f"arm_{sd}", 0.92, h=0.010, th=0.004, off=0.024, name=f"shackle_{sd}")

e.finalize()
# 망토 그라데이션: 어깨는 검정, 무릎 아래로 갈수록 초록 (원작 망토 아래 연두 물들임)
body = [o for o in e.arm_obj.children if o.name == "joan_body"]
for o in body:
    c2.vc_gradient(o, CAPE_HEX, [(0.10 * k, CAPE_GREEN), (0.34 * k, "#5c7a55"), (0.52 * k, CAPE_HEX)])
e.export("characters/joan.glb")
