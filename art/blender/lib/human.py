"""인간 비율 키트 (human): 엘프 키트(elf.Elf)의 리그·소켓·스키닝·합치기를 그대로 쓰고 몸 비율만 성인 인간으로 바꾼다.

엘리아스에서 인간은 교주 하나다. 원작에서 교주는 사도들보다 키와 팔다리가 길고 손가락이 다섯 개인 평범한 지구인 체격이다
(나무위키 「교주(트릭컬 리바이브)」 2.1절). 그래서 SD 엘프(1.20 m, 2.7등신) 옆에 서면 어른과 아이로 보여야 한다.

    import cb, human
    cb.reset()
    e = human.Human("kyoju")                  # 키 1.78 m(정수리), 머리 0.235 m → 7.6등신. 리그·소켓은 엘프 키트와 같다
    ...옷·장비 (elf 함수, human.Drape)...
    e.finalize(); e.export("characters/kyoju.glb")

엘프 키트와 같은 것 (런타임 NPC 시스템이 그대로 쓴다)
- 본 이름·계층·축 (ELF_KIT.md 3장), A 포즈 40°, 소켓(socket_hand_R/L, socket_eye, socket_back, socket_hip_R)
- 손가락 본은 엄지 + f1~f3. 인간의 새끼손가락은 f3(약지) 본을 같이 따른다(포즈의 fingers()가 다섯 손가락을 다 만다)
- 계산 웨이트 스키닝, finalize()의 그룹 합치기(body/arms/head), 정점색 툰 머티리얼 하나

다른 것
- 비율: 성인 남성 실측 비율(키 1.78 m 기준. height를 주면 전체가 같은 비율로 커지거나 작아진다)
- 머리: 사실적인 달걀형. 귀(엘프의 뾰족 귀)는 만들지 않는다(ear 본은 리그 호환을 위해 남긴다)
- 얼굴: face()를 부르지 않으면 표정 모프가 없다. head_mat으로 머리·목 재질을 따로 줄 수 있다(교주: 그림자)
- 손: 다섯 손가락의 가는 손, 발: 신발 모양(foot(..., sole=)로 밑창)
- e.k(작은 디테일 배율)는 1.40이다. 엘프 키트 함수(sleeves, belt, ring, patch…)는 e.k를 곱하므로 그대로 써도 크기가 맞는다
- export()가 런타임 NPC 충돌 캡슐 크기(npcHeight, npcRadius)를 리그 루트에 싣는다 (Npc.ts: 없으면 엘프 캡슐)
"""
from __future__ import annotations

import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cb  # noqa: E402
import elf  # noqa: E402
from elf import V, Buf, Chain, loft, band, keys, lerp, smoothstep, mixw, clamp  # noqa: E402

H_REF = 1.78          # 기준 키 (정수리, m)
K_DETAIL = 1.40       # 작은 디테일 배율 (엘프 키트 함수의 e.k)

# 몸통 단면 (기준 키에서 m): u(0=가랑이, 1=목 밑), 반폭 rx, 앞뒤 반두께 ry, 중심 y(+ = 등 쪽)
TORSO = [
    (0.00, (0.100, 0.080, 0.010)),
    (0.07, (0.160, 0.100, 0.016)),
    (0.17, (0.170, 0.106, 0.020)),
    (0.33, (0.147, 0.097, 0.006)),
    (0.48, (0.150, 0.100, 0.000)),
    (0.65, (0.163, 0.110, -0.004)),
    (0.80, (0.168, 0.106, 0.002)),
    (0.90, (0.150, 0.090, 0.010)),
    (0.96, (0.104, 0.070, 0.014)),
    (1.00, (0.062, 0.054, 0.016)),
]
ARM_R = [(0.0, 0.047), (0.12, 0.047), (0.45, 0.041), (0.53, 0.038), (0.70, 0.040), (1.0, 0.029)]
LEG_R = [(0.0, 0.088), (0.25, 0.077), (0.52, 0.054), (0.62, 0.058), (0.78, 0.050), (1.0, 0.036)]
# 손가락: 이름, 손바닥 폭 방향 위치(+ = 엄지 쪽, m), 길이(m), 굵기(m), 벌림(도). 새끼는 f3 본을 따른다
FINGERS = [("f1", 0.029, 0.074, 0.0090, 4), ("f2", 0.009, 0.082, 0.0092, 0), ("f3", -0.011, 0.077, 0.0086, -4),
           ("f4", -0.029, 0.060, 0.0078, -10)]


class Human(elf.Elf):
    """성인 인간 한 명. 인자: height(정수리 키), head(턱~정수리), shoulders/hips/limb(배율), head_mat(머리·목 재질),
    skin, line, segs, hand_q, head_q(머리 분할 배율: 모자·두건에 가려지면 낮춘다). 리그·소켓·finalize는 elf.Elf와 같다."""

    def __init__(self, name="human", *, height=H_REF, head=0.235, shoulders=1.0, hips=1.0, limb=1.0, head_mat=None,
                 skin="#f7dfd2", line=elf.LINE, segs=1.0, hand_q=1.0, eye_depth=0.03, apose=40.0, head_q=1.0):
        self.s = height / H_REF
        self.head_q = head_q
        self._head_mat = head_mat
        super().__init__(name, height=height, head=head, head_w=0.66, head_d=0.84, cheek=0.0, shoulders=shoulders,
                         hips=hips, limb=limb, arm=1.0, leg=1.0, chest=0.0, bust=0.0, apose=apose, ear_len=0.02,
                         ear_inner=False, skin=skin, line=line, segs=segs, hand_q=hand_q, eye_depth=eye_depth)

    # ------------------------------------------------------------------ 내보내기
    def export(self, rel_path, *, outline=0.006, props=None):
        """엘프 키트 export + 런타임 NPC 충돌 캡슐 크기 (리그 루트 extras): npcHeight = 캡슐 위 끝(정수리 + 4 cm),
        npcRadius = 0.25 m(키 비례). 엘프 모델에는 이 값이 없어 Npc.ts가 엘프 캡슐(0.02~1.14 m, 반지름 0.2)을 쓴다.
        모자가 높거나 옷이 넓으면 props로 덮어쓴다(교주: 미트라)."""
        pr = {"npcHeight": round(self.H + 0.04 * self.s, 3), "npcRadius": round(0.25 * self.s, 3)}
        pr.update(props or {})
        return super().export(rel_path, outline=outline, props=pr)

    # ------------------------------------------------------------------ 비율
    def _layout(self):
        s = self.s
        H, hh = self.H, self.hh
        self.chin = H - hh
        self.k = K_DETAIL * s
        self.head_c = V((0, -0.010 * s, self.chin + hh / 2))
        self.shoulder_z = 1.445 * s
        self.torso_top = 1.492 * s
        self.hipj_z = 0.925 * s
        self.crotch_z = 0.862 * s
        self.knee_z = 0.505 * s
        self.ankle_z = 0.080 * s
        self.waist_z = 1.075 * s
        self.chest_z = 1.275 * s
        self.bust_z = self.chest_z
        self.neck_top = self.chin + 0.022 * s
        a = math.radians(self.apose)
        self.arm_len = (0.300 * s, 0.262 * s)
        self.hand_len = 0.098 * s
        self.finger_len = 0.080 * s
        sx = 0.182 * s * self.sh
        self.S, self.E, self.W, self.adir, self.palm_n = {}, {}, {}, {}, {}
        for side, sg in (("L", 1), ("R", -1)):
            d = V((sg * math.cos(a), 0, -math.sin(a)))
            S = V((sg * sx, 0.0, self.shoulder_z))
            E = S + d * self.arm_len[0]
            W = E + d * self.arm_len[1]
            self.S[side], self.E[side], self.W[side], self.adir[side] = S, E, W, d
            self.palm_n[side] = V((-sg * math.sin(a), 0, -math.cos(a)))
        hx = 0.088 * s * self.hp
        self.Hj, self.K, self.A = {}, {}, {}
        for side, sg in (("L", 1), ("R", -1)):
            self.Hj[side] = V((sg * hx, 0.0, self.hipj_z))
            self.K[side] = V((sg * 0.080 * s, -0.008 * s, self.knee_z))
            self.A[side] = V((sg * 0.076 * s, 0.012 * s, self.ankle_z))
        self.torso_tab = [(u, (rx / self.k, ry / self.k, cy / self.k)) for u, (rx, ry, cy) in TORSO]

    def torso_at(self, z):
        u = (z - self.crotch_z) / (self.torso_top - self.crotch_z)
        rx, ry, cy = keys(TORSO, u)
        hpk = lerp(self.hp, self.sh, smoothstep(0.35, 0.65, u))
        return rx * hpk * self.s, ry * self.s, cy * self.s

    def arm_r(self, t):
        r = keys(ARM_R, t) * self.s * self.lb
        return r, r * 0.92

    def leg_r(self, t):
        r = keys(LEG_R, t) * self.s * self.lb
        return r, r * 0.96

    def eye_z(self):
        return self.chin + self.hh * 0.46

    # ------------------------------------------------------------------ 머리 (귀 없음)
    def _head_fn(self, x, y, z):
        """단위구 → 사실적인 머리: 둥근 머리뼈, 좁아지는 턱, 뒤통수, 평평한 얼굴 앞면."""
        s = self.s
        W, D, Hh = 0.078 * s, 0.098 * s, self.hh / 2
        jaw = smoothstep(-0.15, -1.0, z)
        sx = 1.0 - 0.30 * jaw
        sy = 1.0 - (0.10 if y < 0 else 0.30) * jaw
        if y > 0:
            sy *= 1.0 + 0.07 * smoothstep(-0.5, 0.3, z) * (1 - smoothstep(0.3, 0.95, z))
        else:
            sy *= 1.0 - 0.10 * (1 - abs(x)) * smoothstep(0.8, -0.3, z)
        zz = z * (1 - 0.05 * smoothstep(-0.85, -1.0, z))
        return V((x * W * sx, y * D * sy, zz * Hh)) + self.head_c

    def _head(self):
        segs = max(14, int(28 * self.q * self.head_q) // 2 * 2)
        rings = max(9, int(18 * self.q * self.head_q))
        buf = Buf()
        verts = [[None] * segs for _ in range(rings - 1)]
        w = {"head": 1.0}
        for i in range(1, rings):
            el = math.pi / 2 - math.pi * i / rings
            for j in range(segs):
                az = 2 * math.pi * j / segs
                x = math.cos(el) * math.sin(az)
                y = -math.cos(el) * math.cos(az)
                z = math.sin(el)
                verts[i - 1][j] = buf.vert(self._head_fn(x, y, z), w)
        top = buf.vert(self._head_fn(0, 0, 1), w)
        bot = buf.vert(self._head_fn(0, 0, -1), w)
        m = self._head_mat or self.skin_mat
        for j in range(segs):
            j2 = (j + 1) % segs
            buf.face((top, verts[0][j], verts[0][j2]), m)
            buf.face((bot, verts[-1][j2], verts[-1][j]), m)
        for i in range(rings - 2):
            for j in range(segs):
                j2 = (j + 1) % segs
                buf.face((verts[i][j], verts[i + 1][j], verts[i + 1][j2], verts[i][j2]), m)
        ob = buf.obj(f"{self.name}_head_skin")
        self.head_obj = ob
        self.add(ob, group="head", tag="head")
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bm.transform(ob.matrix_world)
        self.head_bvh = BVHTree.FromBMesh(bm)
        bm.free()
        ez = self.eye_z()
        hit = self.head_bvh.ray_cast(V((0, -2, ez)), V((0, 1, 0)))
        fy = hit[0].y if hit[0] else self.head_c.y - 0.09 * self.s
        self.face_y = fy
        self._socket("socket_eye", "head", V((0, fy + self.eye_depth * self.s, ez)), None)

    def _ears(self):
        """인간: 엘프 귀 기하는 만들지 않는다 (ear 본은 리그 호환을 위해 _rig에 남는다)."""
        return

    def _neck(self):
        s = self.s
        buf = Buf()
        z0, z1 = self.torso_top - 0.035 * s, self.chin + 0.045 * s
        st = []
        for i in range(5):
            t = i / 4
            z = lerp(z0, z1, t)
            w = mixw({"chest": 1.0}, {"neck": 1.0}, smoothstep(0.0, 0.35, t))
            w = mixw(w, {"head": 1.0}, smoothstep(0.7, 1.0, t))
            st.append({"c": (0, 0.012 * s, z), "rx": 0.058 * s, "ry": 0.056 * s, "w": w})
        loft(buf, st, segs=14, cap0=None, cap1="round", mat=self._head_mat or self.skin_mat, ref=(1, 0, 0))
        self.add(buf.obj(f"{self.name}_neck"), group="head", tag="neck")

    # ------------------------------------------------------------------ 손 (다섯 손가락)
    def _finger_frame(self, side):
        W, L, P = self.W[side], self.adir[side], self.palm_n[side]
        T = V((0, -1, 0))
        return W, L, P, T

    def _finger_joints(self, side):
        """[(이름, base, mid, tip)] 엄지 + f1~f3 (본). f4(새끼)는 _finger_geo에서만 쓴다."""
        return [j for j in self._finger_geo(side) if j[0] != "f4"]

    def _finger_geo(self, side):
        s = self.s
        W, L, P, T = self._finger_frame(side)
        knuck = W + L * self.hand_len
        out = []
        for nm, toff, ln, _r, fan in FINGERS:
            base = knuck + T * (toff * s) + P * (0.002 * s) - L * (0.004 * s if nm in ("f1", "f4") else 0.0)
            d = (L + T * math.tan(math.radians(fan))).normalized()
            d1 = (d + P * 0.10).normalized()
            d2 = (d + P * 0.28).normalized()
            Lf = ln * s
            mid = base + d1 * Lf * 0.52
            tip = mid + d2 * Lf * 0.48
            out.append((nm, base, mid, tip))
        base = W + L * (0.022 * s) + T * (0.026 * s) + P * (0.010 * s)
        d = (T * 0.72 + L * 0.58 + P * 0.34).normalized()
        Lt = 0.064 * s
        mid = base + d * Lt * 0.5
        d2 = (T * 0.45 + L * 0.80 + P * 0.38).normalized()
        tip = mid + d2 * Lt * 0.5
        out.insert(0, ("thumb", base, mid, tip))
        return out

    def _grip_point(self, side):
        W, d, P = self.W[side], self.adir[side], self.palm_n[side]
        return W + d * (self.hand_len * 0.62) + P * (0.030 * self.s)

    def hand(self, side, material, *, inflate=0.0, cuff=None, name=None):
        """다섯 손가락 손 (새끼는 f3 본 웨이트). inflate>0이면 장갑."""
        s = self.s
        W, L, P, T = self._finger_frame(side)
        buf = Buf()
        hb = f"hand_{side}"
        st = []
        tab = [(0.0, (0.026, 0.0155)), (0.30, (0.039, 0.0165)), (0.75, (0.044, 0.0150)), (1.0, (0.042, 0.0125))]
        for i in range(6):
            t = i / 5
            rx, ry = keys(tab, t)
            c = W + L * (lerp(-0.01, 1.0, t) * self.hand_len) + P * (0.001 * s)
            w = mixw({f"forearm_{side}": 1.0}, {hb: 1.0}, smoothstep(0.0, 0.25, t))
            st.append({"c": c, "rx": rx * s + inflate, "ry": ry * s + inflate, "w": w, "ref": tuple(T), "p": 2.8})
        loft(buf, st, segs=max(10, int(14 * self.hq) // 2 * 2), cap0="round", cap1="round", mat=material,
             cap_len0=0.008 * s, cap_len1=0.008 * s, cap_rings=2)
        rad = {nm: r for nm, _o, _l, r, _f in FINGERS}
        for nm, base, mid, tip in self._finger_geo(side):
            bn = "f3" if nm == "f4" else nm
            r0 = (0.0108 if nm == "thumb" else rad[nm]) * s + inflate
            r1 = r0 * 0.80
            back = base - (mid - base).normalized() * 0.010 * s
            ch = Chain([back, base, mid, tip], [hb, f"{bn}_01_{side}", f"{bn}_02_{side}"], blend=0.40)
            st = []
            nn = 6 if self.hq >= 1 else 4
            for i in range(nn):
                t = i / (nn - 1)
                c, _tan = ch.at(t)
                r = lerp(r0, r1, t)
                st.append({"c": c, "rx": r, "ry": r * 0.88, "w": ch.weights(t), "ref": tuple(T)})
            loft(buf, st, segs=max(6, int(8 * self.hq) // 2 * 2), cap0="round", cap1="round", mat=material,
                 cap_len1=r1 * 0.9, cap_rings=2)
        if cuff:
            cm, ch_, th = cuff
            ar = self.arm_r(1.0)
            band(buf, W - L * (ch_ * 0.35), L, T, ar[0] + inflate * 0.6, ar[1] + inflate * 0.6, ch_, th,
                 segs=self._s(16), mat=cm, w={f"forearm_{side}": 0.6, hb: 0.4})
        return buf.obj(name or f"{self.name}_hand_{side}")

    # ------------------------------------------------------------------ 발 (신발)
    def foot(self, side, material, *, inflate=0.0, name=None, sole=None, toe_up=0.0, length=0.275, width=0.050,
             height=0.075):
        """신발 모양 발 (뒤꿈치 → 발끝 +앞). sole=(재질, 두께)면 밑창. length/width(반폭)/height(m, 기준 키)."""
        s = self.s
        A = self.A[side]
        buf = Buf()
        fb = f"foot_{side}"
        # t: 0 뒤꿈치 → 1 발끝. (y 위치 비율, 반폭, 윗면 높이, 아랫면 높이)
        tab = [(0.00, (0.80, 0.70, 0.95)), (0.20, (0.95, 1.00, 1.00)), (0.50, (1.00, 0.80, 1.0)),
               (0.75, (1.00, 0.55, 1.0)), (1.00, (0.80, 0.40, 1.0))]
        st = []
        n = 9
        y0, y1 = A.y + 0.055 * s, A.y + 0.055 * s - length * s
        for i in range(n):
            t = i / (n - 1)
            wk, hk, _ = keys(tab, t)
            hz = height * s * hk
            c = V((A.x, lerp(y0, y1, t), hz * 0.5 + toe_up * t * t))
            w = mixw({f"shin_{side}": 1.0}, {fb: 1.0}, smoothstep(0.0, 0.35, t))
            st.append({"c": c, "rx": width * s * wk + inflate, "ry": hz * 0.5 + inflate, "w": w, "ref": (1, 0, 0),
                       "p": 2.6})
        loft(buf, st, segs=max(10, int(14 * self.q) // 2 * 2), cap0="round", cap1="round", mat=material,
             cap_len0=0.025 * s, cap_len1=0.030 * s, cap_rings=2)
        if sole:
            sm, th = sole
            stp = []
            for i in range(n):
                t = i / (n - 1)
                wk, _hk, _ = keys(tab, t)
                stp.append({"c": V((A.x, lerp(y0, y1, t), th / 2)), "rx": width * s * wk + inflate + 0.004 * s,
                            "ry": th / 2, "w": {fb: 1.0}, "ref": (1, 0, 0), "p": 4.0})
            loft(buf, stp, segs=max(10, int(14 * self.q) // 2 * 2), cap0="round", cap1="round", mat=sm,
                 cap_len0=0.028 * s, cap_len1=0.033 * s, cap_rings=2)
        return buf.obj(name or f"{self.name}_foot_{side}")


# =========================================================================== 늘어지는 천 (수단 자락, 망토)

class Drape:
    """몸에서 떨어지는 두께 있는 천 (cameo2.Shell과 같은 생각, 인간 비율용). 행(z) × 열(방위) 격자.

    section(z) → (rx, ry, cy): 높이 z의 바깥 타원(초타원 p). gap(z) → 앞트임 반각(도). gap=None이면 닫힌 고리.
    wfn(점) → 웨이트. drop(u, a) → 아래로 처지는 양(m). 행 u: 0=윗단, 1=밑단. 열 a: 0=앞, 90=왼쪽, 180=뒤."""

    def __init__(self, e, mat, zs, section, *, gap=None, th=0.005, cols=28, p=2.3, wfn=None, drop=None, mat_in=None,
                 a_fn=None):
        self.e = e
        self.mat = mat
        self.mat_in = mat_in or mat
        self.buf = Buf()
        self.zs = list(zs)
        self.section = section
        self.gap = gap
        self.p = p
        self.closed = gap is None
        self.cols = cols
        self.rows = len(self.zs)
        wfn = wfn or (lambda q: e._torso_wfn(q, 0))
        self.P, self.N, self.Wt, self.A = [], [], [], []
        for i, z in enumerate(self.zs):
            u = i / (self.rows - 1)
            rx, ry, cy = section(z)
            rowP, rowN, rowW, rowA = [], [], [], []
            for j in range(cols):
                if self.closed:
                    a = 360.0 * j / cols
                else:
                    g = gap(z)
                    a = g + (360.0 - 2 * g) * j / (cols - 1)
                if a_fn:
                    a = a_fn(a, u)
                q, n = elf_ring_pt(rx, ry, cy, z, a, p)
                if drop:
                    q.z -= drop(u, a)
                rowP.append(q)
                rowN.append(n)
                rowW.append(wfn(q))
                rowA.append(a)
            self.P.append(rowP)
            self.N.append(rowN)
            self.Wt.append(rowW)
            self.A.append(rowA)
        self._build(th)

    def _build(self, th):
        b, P, N, W = self.buf, self.P, self.N, self.Wt
        R, C = self.rows, self.cols
        o = [[b.vert(P[i][j], W[i][j]) for j in range(C)] for i in range(R)]
        n = [[b.vert(P[i][j] - N[i][j] * th, W[i][j]) for j in range(C)] for i in range(R)]
        jr = range(C) if self.closed else range(C - 1)
        for i in range(R - 1):
            for j in jr:
                j2 = (j + 1) % C
                b.face((o[i][j], o[i + 1][j], o[i + 1][j2], o[i][j2]), self.mat)
                b.face((n[i][j], n[i][j2], n[i + 1][j2], n[i + 1][j]), self.mat_in)
        for j in jr:
            j2 = (j + 1) % C
            b.face((o[0][j], o[0][j2], n[0][j2], n[0][j]), self.mat_in)
            b.face((o[R - 1][j], n[R - 1][j], n[R - 1][j2], o[R - 1][j2]), self.mat_in)
        if not self.closed:
            for i in range(R - 1):
                b.face((o[i][0], n[i][0], n[i + 1][0], o[i + 1][0]), self.mat_in)
                jl = C - 1
                b.face((o[i][jl], o[i + 1][jl], n[i + 1][jl], n[i][jl]), self.mat_in)

    def strip_edge(self, mat, width, th, *, side=0, i0=0, i1=None, lift=0.0006):
        """앞트임 가장자리 띠 (side 0: 첫 열(캐릭터 왼쪽 앞), 1: 마지막 열). 띠 폭은 천 안쪽(열 방향)으로 잰다."""
        i1 = self.rows if i1 is None else i1
        jj, jn = (0, 1) if side == 0 else (self.cols - 1, self.cols - 2)
        pts, nrm, ups, ws = [], [], [], []
        for i in range(i0, i1):
            d = (self.P[i][jn] - self.P[i][jj]).normalized()
            pts.append(self.P[i][jj] + d * (width * 0.5) + self.N[i][jj] * lift)
            nrm.append(self.N[i][jj])
            ups.append(d)
            ws.append(self.Wt[i][jj])
        elf._loop(self.buf, pts, nrm, ups, width, th, mat=mat, closed=False,
                  w=lambda t: ws[min(int(round(t * (len(ws) - 1))), len(ws) - 1)])
        return self

    def strip_row(self, mat, width, th, *, row=None, lift=0.0006, up=True):
        """행을 따라 도는 띠 (밑단·윗단 테두리). row 기본은 밑단. 띠 폭은 위쪽(행 방향)으로 잰다."""
        i = self.rows - 1 if row is None else row
        ia = i - 1 if (up and i > 0) else min(i + 1, self.rows - 1)
        idx = list(range(self.cols)) + ([0] if self.closed else [])
        pts, nrm, ups, ws = [], [], [], []
        for j in idx:
            d = (self.P[ia][j] - self.P[i][j]).normalized()
            pts.append(self.P[i][j] + d * (width * 0.5) + self.N[i][j] * lift)
            nrm.append(self.N[i][j])
            ups.append(d)
            ws.append(self.Wt[i][j])
        elf._loop(self.buf, pts, nrm, ups, width, th, mat=mat, closed=False,
                  w=lambda t: ws[min(int(round(t * (len(ws) - 1))), len(ws) - 1)])
        return self

    def surface(self, z, a_deg, lift=0.0):
        """천 바깥면의 점과 법선 (z 높이, 방위 a)."""
        rx, ry, cy = self.section(z)
        q, n = elf_ring_pt(rx, ry, cy, z, a_deg, self.p)
        return q + n * lift, n

    def done(self, name, group="body", angle=50.0):
        ob = self.buf.obj(f"{self.e.name}_{name}", angle=angle)
        return self.e.add(ob, group=group, tag=name)


def elf_ring_pt(rx, ry, cy, z, a_deg, p=2.3):
    """초타원 단면 위 점과 바깥 법선. a: 0=앞(-Y), 90=왼쪽(+X), 180=뒤."""
    a = math.radians(a_deg)
    dx, dy = math.sin(a), -math.cos(a)
    ee = 2.0 / p
    x = math.copysign(abs(dx) ** ee, dx) * rx
    y = math.copysign(abs(dy) ** ee, dy) * ry + cy
    n = V((x / (rx * rx), (y - cy) / (ry * ry), 0.0))
    n = n.normalized() if n.length > 1e-9 else V((dx, dy, 0))
    return V((x, y, z)), n


def skirt_w(e, q, *, legs=0.6):
    """긴 자락 웨이트: 골반 위는 몸통 규칙, 아래로 갈수록 좌우 허벅지를 legs만큼 따라간다(걷기)."""
    if q.z >= e.hipj_z:
        return e._torso_wfn(q, 0)
    a = smoothstep(e.hipj_z, e.knee_z, q.z)
    sx = clamp(q.x / (0.14 * e.s), -1.0, 1.0)
    wl = 0.5 + 0.5 * sx
    leg = {kk: v for kk, v in (("thigh_L", wl), ("thigh_R", 1 - wl)) if v > 1e-4}
    return mixw({"hips": 1.0}, leg, a * legs)


__all__ = ["Human", "Drape", "skirt_w", "elf_ring_pt", "Matrix"]
