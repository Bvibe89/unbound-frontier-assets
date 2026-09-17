# Human Base v2 - core animation set for third-person shooter gameplay.
#
# Axis conventions, derived from the actual rig geometry (not assumed):
#   character faces +Y, up is +Z, character's LEFT is -X, RIGHT is +X.
#   Rotations are authored in ARMATURE space and conjugated into each bone's
#   rest frame, so bone roll/orientation is irrelevant:
#       basis = Mrest^-1 @ R @ Mrest
#   Composition order is fixed: R = Rx(pitch) @ Rz(yaw) @ Ry(roll)
#   (roll applied first, so arms drop out of the T-pose before swinging).
#
#   pitch (X): positive swings a DOWNWARD-pointing limb FORWARD (legs, hung
#              arms). For an UPWARD-pointing bone (spine/neck/head) positive
#              pitch leans BACKWARD, so forward lean is negative.
#   yaw   (Z): positive turns left (counter-clockwise from above).
#   roll  (Y): positive raises a -X-pointing limb (left arm) and moves a
#              downward limb toward -X. Hence arms lower with roll = s*deg
#              where s = -1 for Left and +1 for Right.
#
# Locomotion is strictly IN PLACE: the Root bone is never translated or
# rotated in any clip. Vertical body bob lives on Hips, which is body motion,
# not world movement - Godot owns world-space translation.

import math
import bpy
from mathutils import Matrix, Vector

FPS = 30
L, R = -1, +1          # side sign: Left = -1, Right = +1


# --- per-limb axis rules, each verified empirically against this rig ---------
# UPPER ARM: rest direction is +/-X (T-pose). roll drops it out of the T-pose
#   (roll = s*deg lowers); pitch is composed LAST so, once the arm is lowered,
#   pitch swings it forward. Both work.
# FOREARM / HAND / FINGERS: rest direction is also +/-X but their own roll is
#   small, so they stay along X and a rotation about X barely moves them -
#   measured: forearm pitch +28 gives an 8.2 deg elbow, pitch +80 only 14.4 deg.
#   Flexion must therefore use YAW: yaw = s*deg gives 82 deg with the forearm
#   pointing straight forward. NEVER express an elbow bend as pitch.
# LEGS: rest direction is -Z, so pitch swings them and roll abducts. Both work.
# SPINE / NECK / HEAD: rest direction +Z, so negative pitch leans forward.

def fl(s, deg):
    """Flexion YAW for forearm / hand / fingers (elbow and wrist bend)."""
    return s * deg


def ab(s, deg):
    """Roll OFFSET abducting (raising) an upper arm toward the T-pose.

    BASE already drops each arm with roll = s*69, so raising is -s*deg.
    Writing s*deg would ADD to the drop and swing the arm across the body.
    """
    return -s * deg


def dr(s, deg):
    """Roll OFFSET dropping an upper arm further (elbow tucked to the ribs)."""
    return s * deg

# ---------------------------------------------------------------- base stance
# A grounded, restrained "ready" posture. Every clip is expressed as offsets
# from this, which keeps the whole set stylistically consistent.
BASE = {
    "Hips":          (0, 0, 0),
    "Spine":         (-3, 0, 0),
    "Chest":         (-2, 0, 0),
    "UpperChest":    (-1, 0, 0),
    "Neck":          (3, 0, 0),
    "Head":          (1, 0, 0),
    "LeftShoulder":  (0, 0, 5),
    "RightShoulder": (0, 0, -5),
    "LeftUpperArm":  (6, 0, L*64),     # 64 not 69: eases the armpit crease
    "RightUpperArm": (6, 0, R*64),
    "LeftLowerArm":  (0, fl(L, 18), L*8),   # elbow bend is YAW, not pitch
    "RightLowerArm": (0, fl(R, 18), R*8),
    "LeftHand":      (0, fl(L, 4), 0),
    "RightHand":     (0, fl(R, 4), 0),
    "LeftUpperLeg":  (2, 0, 0),
    "RightUpperLeg": (2, 0, 0),
    "LeftLowerLeg":  (-5, 0, 0),
    "RightLowerLeg": (-5, 0, 0),
    "LeftFoot":      (3, 0, 0),
    "RightFoot":     (3, 0, 0),
    "LeftToes":      (0, 0, 0),
    "RightToes":     (0, 0, 0)
}

# Arms held forward as if supporting a weapon. Deliberately generic - not
# tuned to any specific firearm. Absolute targets: upper arm ~50 deg down and
# ~56 deg forward, elbows bent ~80 deg, hands closed.
AIM = {
    "LeftUpperArm":  (26, 0, dr(L, 11)), "RightUpperArm": (4, 0, ab(R, 14)),
    "LeftLowerArm":  (0, fl(L, 56), 0),  "RightLowerArm": (0, fl(R, 82), 0),
    "LeftHand":      (0, fl(L, 8), 0),   "RightHand":     (0, fl(R, 6), 0),
    "LeftShoulder":  (0, 0, 4),          "RightShoulder": (0, 0, -5),
    "UpperChest":    (-2, -8, 0),        "Chest": (-3, -5, 0), "Spine": (-3, -2, 0),
    "Neck":          (4, 6, 0),          "Head": (1, 4, 0)
}


def finger_pose(side, curl, thumb=None, index=None):
    """Curl offsets for one hand. Finger bones run along +/-X like the forearm,
    so flexion is YAW, never pitch (pitch barely moves an X-aligned bone).
    Values are OFFSETS on top of BASE, like every other clip value."""
    s = L if side == "Left" else R
    d = {}
    for f in ("Index", "Middle", "Ring", "Little"):
        c = curl if (index is None or f != "Index") else index
        d[f"{side}{f}Proximal"] = (0.0, fl(s, c), 0.0)
        d[f"{side}{f}Distal"] = (0.0, fl(s, c * 1.2), 0.0)
    t = curl * 0.55 if thumb is None else thumb
    d[f"{side}ThumbProximal"] = (0.0, fl(s, t), 0.0)
    d[f"{side}ThumbDistal"] = (0.0, fl(s, t * 0.9), 0.0)
    return d


def both_hands(curl, thumb=None, index=None):
    d = dict(finger_pose("Left", curl, thumb, index))
    d.update(finger_pose("Right", curl, thumb, index))
    return d


BASE.update(both_hands(6.0))


def step(thigh_f, knee_f, foot_f, thigh_b, knee_b, foot_b,
         arm_f, arm_b, lead="Left"):
    """One contact pose. `lead` is the forward leg; arms counter-swing."""
    o = "Right" if lead == "Left" else "Left"
    sl = L if lead == "Left" else R
    so = L if o == "Left" else R
    return {
        f"{lead}UpperLeg": (thigh_f, 0, 0), f"{lead}LowerLeg": (knee_f, 0, 0),
        f"{lead}Foot":     (foot_f, 0, 0),
        f"{o}UpperLeg":    (thigh_b, 0, 0), f"{o}LowerLeg":    (knee_b, 0, 0),
        f"{o}Foot":        (foot_b, 0, 0),
        # arm opposite the forward leg swings forward
        f"{o}UpperArm":    (arm_f, 0, so*0), f"{lead}UpperArm": (arm_b, 0, sl*0)
    }


def merge(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            if k in out:
                out[k] = tuple(a + b for a, b in zip(out[k], v))
            else:
                out[k] = tuple(v)
    return out


# ---------------------------------------------------------------- clip data
# Each clip: frames, loop flag, and keyframes as {frame: {bone: (p,y,r) offset}}
# plus optional "hips" {frame: (x,y,z)} armature-space offset for body bob.
CLIPS = {}

# 1. Idle - breathing and a barely-there weight shift.
CLIPS["Idle"] = dict(frames=60, loop=True, keys={
    0:  {},
    15: {"Spine": (-1.2, 0.8, 0), "Chest": (-1.0, 0.6, 0), "UpperChest": (-0.8, 0, 0),
         "Neck": (0.6, -0.6, 0), "Head": (0.4, -1.2, 0),
         "LeftUpperArm": (0, 0, L*1.5), "RightUpperArm": (0, 0, R*1.5)},
    30: {"Spine": (0.6, 0, 0), "Chest": (0.5, 0, 0), "UpperChest": (0.4, 0, 0),
         "Neck": (-0.4, 0, 0), "Head": (-0.3, 0, 0),
         "LeftUpperArm": (0, 0, L*2.5), "RightUpperArm": (0, 0, R*2.5)},
    45: {"Spine": (-1.0, -0.8, 0), "Chest": (-0.8, -0.6, 0), "UpperChest": (-0.6, 0, 0),
         "Neck": (0.5, 0.6, 0), "Head": (0.3, 1.0, 0),
         "LeftUpperArm": (0, 0, L*1.5), "RightUpperArm": (0, 0, R*1.5)},
    60: {}
}, hips={0: (0, 0, 0), 15: (0, 0, -0.004), 30: (0, 0, 0.003),
        45: (0, 0, -0.004), 60: (0, 0, 0)})

# 2. Walk_Forward - 32f cycle (~1.07 s), two steps. In place.
_wf_contactL = step(22, -6, -4, -18, -14, 8, 0, 0, "Left")
_wf_passL    = {"LeftUpperLeg": (2, 0, 0), "LeftLowerLeg": (-8, 0, 0), "LeftFoot": (2, 0, 0),
                "RightUpperLeg": (8, 0, 0), "RightLowerLeg": (-48, 0, 0), "RightFoot": (14, 0, 0)}
_wf_contactR = step(22, -6, -4, -18, -14, 8, 0, 0, "Right")
_wf_passR    = {"RightUpperLeg": (2, 0, 0), "RightLowerLeg": (-8, 0, 0), "RightFoot": (2, 0, 0),
                "LeftUpperLeg": (8, 0, 0), "LeftLowerLeg": (-48, 0, 0), "LeftFoot": (14, 0, 0)}
_wf_armA = {"LeftUpperArm": (16, 0, 0), "RightUpperArm": (-14, 0, 0),
            "LeftLowerArm": (0, fl(L, 6), 0), "RightLowerArm": (0, fl(R, 2), 0),
            "UpperChest": (0, -4, 0), "Chest": (0, -2.5, 0), "Neck": (0, 3, 0)}
_wf_armB = {"LeftUpperArm": (-14, 0, 0), "RightUpperArm": (16, 0, 0),
            "LeftLowerArm": (0, fl(L, 2), 0), "RightLowerArm": (0, fl(R, 6), 0),
            "UpperChest": (0, 4, 0), "Chest": (0, 2.5, 0), "Neck": (0, -3, 0)}
CLIPS["Walk_Forward"] = dict(frames=32, loop=True, keys={
    0:  merge(_wf_contactL, _wf_armA),
    8:  merge(_wf_passL, {"LeftUpperArm": (1, 0, 0), "RightUpperArm": (1, 0, 0)}),
    16: merge(_wf_contactR, _wf_armB),
    24: merge(_wf_passR, {"LeftUpperArm": (1, 0, 0), "RightUpperArm": (1, 0, 0)}),
    32: merge(_wf_contactL, _wf_armA)
}, hips={0: (0, 0, -0.008), 8: (0, 0, 0.010), 16: (0, 0, -0.008),
         24: (0, 0, 0.010), 32: (0, 0, -0.008)})

# 3. Walk_Backward - shorter stride, reduced arm swing, slight rearward lean.
_wb_cL = {"LeftUpperLeg": (-14, 0, 0), "LeftLowerLeg": (-10, 0, 0), "LeftFoot": (6, 0, 0),
          "RightUpperLeg": (14, 0, 0), "RightLowerLeg": (-16, 0, 0), "RightFoot": (-2, 0, 0)}
_wb_pL = {"LeftUpperLeg": (-2, 0, 0), "LeftLowerLeg": (-34, 0, 0), "LeftFoot": (10, 0, 0),
          "RightUpperLeg": (4, 0, 0), "RightLowerLeg": (-8, 0, 0), "RightFoot": (2, 0, 0)}
_wb_cR = {"RightUpperLeg": (-14, 0, 0), "RightLowerLeg": (-10, 0, 0), "RightFoot": (6, 0, 0),
          "LeftUpperLeg": (14, 0, 0), "LeftLowerLeg": (-16, 0, 0), "LeftFoot": (-2, 0, 0)}
_wb_pR = {"RightUpperLeg": (-2, 0, 0), "RightLowerLeg": (-34, 0, 0), "RightFoot": (10, 0, 0),
          "LeftUpperLeg": (4, 0, 0), "LeftLowerLeg": (-8, 0, 0), "LeftFoot": (2, 0, 0)}
_wb_lean = {"Spine": (2.5, 0, 0), "Chest": (1.5, 0, 0), "Neck": (-2, 0, 0)}
CLIPS["Walk_Backward"] = dict(frames=36, loop=True, keys={
    0:  merge(_wb_cL, _wb_lean, {"LeftUpperArm": (9, 0, 0), "RightUpperArm": (-8, 0, 0)}),
    9:  merge(_wb_pL, _wb_lean),
    18: merge(_wb_cR, _wb_lean, {"LeftUpperArm": (-8, 0, 0), "RightUpperArm": (9, 0, 0)}),
    27: merge(_wb_pR, _wb_lean),
    36: merge(_wb_cL, _wb_lean, {"LeftUpperArm": (9, 0, 0), "RightUpperArm": (-8, 0, 0)})
}, hips={0: (0, 0, -0.006), 9: (0, 0, 0.007), 18: (0, 0, -0.006),
         27: (0, 0, 0.007), 36: (0, 0, -0.006)})


def strafe(direction):
    """Side-step cycle. direction -1 = toward -X (character's left), +1 = right.
    Torso keeps facing forward; a downward limb moves toward -X on +roll, so
    lateral leg motion uses roll = -direction."""
    d = direction
    lead = "Left" if d < 0 else "Right"
    trail = "Right" if d < 0 else "Left"
    rl = -d                                    # roll sign that moves legs toward d
    # torso leans into the direction: spine points up, +roll tilts toward +X
    lean = {"Spine": (0, 0, d*2.5), "Chest": (0, 0, d*1.5), "UpperChest": (0, 0, d*1.0),
            "Neck": (0, 0, -d*1.5), "Head": (0, 0, -d*1.0)}
    arms = {"LeftUpperArm": (0, 0, L*4), "RightUpperArm": (0, 0, R*4)}
    wide = {f"{lead}UpperLeg": (0, 0, rl*16), f"{lead}LowerLeg": (-8, 0, 0),
            f"{lead}Foot": (2, 0, rl*4),
            f"{trail}UpperLeg": (0, 0, rl*2), f"{trail}LowerLeg": (-6, 0, 0),
            f"{trail}Foot": (2, 0, 0)}
    liftT = {f"{trail}UpperLeg": (6, 0, rl*8), f"{trail}LowerLeg": (-38, 0, 0),
             f"{trail}Foot": (12, 0, 0),
             f"{lead}UpperLeg": (0, 0, rl*12), f"{lead}LowerLeg": (-6, 0, 0),
             f"{lead}Foot": (2, 0, 0)}
    close = {f"{lead}UpperLeg": (0, 0, rl*4), f"{lead}LowerLeg": (-7, 0, 0),
             f"{lead}Foot": (2, 0, 0),
             f"{trail}UpperLeg": (0, 0, rl*4), f"{trail}LowerLeg": (-7, 0, 0),
             f"{trail}Foot": (2, 0, 0)}
    liftL = {f"{lead}UpperLeg": (6, 0, rl*10), f"{lead}LowerLeg": (-34, 0, 0),
             f"{lead}Foot": (12, 0, 0),
             f"{trail}UpperLeg": (0, 0, rl*3), f"{trail}LowerLeg": (-7, 0, 0),
             f"{trail}Foot": (2, 0, 0)}
    return dict(frames=32, loop=True, keys={
        0:  merge(wide, lean, arms),
        8:  merge(liftT, lean, arms),
        16: merge(close, lean, arms),
        24: merge(liftL, lean, arms),
        32: merge(wide, lean, arms)
    }, hips={0: (0, 0, -0.004), 8: (0, 0, 0.006), 16: (0, 0, -0.003),
             24: (0, 0, 0.006), 32: (0, 0, -0.004)})


CLIPS["Strafe_Left"] = strafe(-1)
CLIPS["Strafe_Right"] = strafe(+1)

# 6. Sprint - 20f cycle (~0.67 s), forward lean, bent pumping arms. In place.
_sp_cL = {"LeftUpperLeg": (34, 0, 0), "LeftLowerLeg": (-16, 0, 0), "LeftFoot": (-2, 0, 0),
          "RightUpperLeg": (-30, 0, 0), "RightLowerLeg": (-30, 0, 0), "RightFoot": (12, 0, 0)}
_sp_pL = {"LeftUpperLeg": (6, 0, 0), "LeftLowerLeg": (-14, 0, 0), "LeftFoot": (0, 0, 0),
          "RightUpperLeg": (26, 0, 0), "RightLowerLeg": (-86, 0, 0), "RightFoot": (18, 0, 0)}
_sp_cR = {"RightUpperLeg": (34, 0, 0), "RightLowerLeg": (-16, 0, 0), "RightFoot": (-2, 0, 0),
          "LeftUpperLeg": (-30, 0, 0), "LeftLowerLeg": (-30, 0, 0), "LeftFoot": (12, 0, 0)}
_sp_pR = {"RightUpperLeg": (6, 0, 0), "RightLowerLeg": (-14, 0, 0), "RightFoot": (0, 0, 0),
          "LeftUpperLeg": (26, 0, 0), "LeftLowerLeg": (-86, 0, 0), "LeftFoot": (18, 0, 0)}
_sp_lean = {"Spine": (-9, 0, 0), "Chest": (-6, 0, 0), "UpperChest": (-3, 0, 0),
            "Neck": (10, 0, 0), "Head": (3, 0, 0)}
_sp_armA = {"LeftUpperArm": (34, 0, L*6), "RightUpperArm": (-26, 0, R*6),
            "LeftLowerArm": (0, fl(L, 62), 0), "RightLowerArm": (0, fl(R, 54), 0),
            "UpperChest": (0, -7, 0), "Chest": (0, -4, 0)}
_sp_armB = {"LeftUpperArm": (-26, 0, L*6), "RightUpperArm": (34, 0, R*6),
            "LeftLowerArm": (0, fl(L, 54), 0), "RightLowerArm": (0, fl(R, 62), 0),
            "UpperChest": (0, 7, 0), "Chest": (0, 4, 0)}
CLIPS["Sprint"] = dict(frames=20, loop=True, keys={
    0:  merge(_sp_cL, _sp_lean, _sp_armA),
    5:  merge(_sp_pL, _sp_lean, {"LeftUpperArm": (4, 0, L*6), "RightUpperArm": (4, 0, R*6),
                                 "LeftLowerArm": (0, fl(L, 58), 0), "RightLowerArm": (0, fl(R, 58), 0)}),
    10: merge(_sp_cR, _sp_lean, _sp_armB),
    15: merge(_sp_pR, _sp_lean, {"LeftUpperArm": (4, 0, L*6), "RightUpperArm": (4, 0, R*6),
                                 "LeftLowerArm": (0, fl(L, 58), 0), "RightLowerArm": (0, fl(R, 58), 0)}),
    20: merge(_sp_cL, _sp_lean, _sp_armA)
}, hips={0: (0, 0, -0.022), 5: (0, 0, 0.026), 10: (0, 0, -0.022),
         15: (0, 0, 0.026), 20: (0, 0, -0.022)})

# 7. Fire - aim, sharp recoil, settle back to aim. Not weapon specific.
_recoil = merge(AIM, {"UpperChest": (5, 0, 0), "Chest": (3, 0, 0), "Spine": (1.5, 0, 0),
                      "LeftUpperArm": (-7, 0, 0), "RightUpperArm": (-8, 0, 0),
                      "LeftLowerArm": (0, fl(L, 5), 0), "RightLowerArm": (0, fl(R, 6), 0),
                      "RightShoulder": (0, 0, 3), "Neck": (-3, 0, 0), "Head": (-2, 0, 0)})
_settle = merge(AIM, {"UpperChest": (-1.5, 0, 0), "LeftUpperArm": (2, 0, 0),
                      "RightUpperArm": (2, 0, 0), "Head": (0.8, 0, 0)})
CLIPS["Fire"] = dict(frames=18, loop=False, keys={
    0:  merge(AIM, {}),
    2:  _recoil,
    7:  _settle,
    12: merge(AIM, {"UpperChest": (0.6, 0, 0)}),
    18: merge(AIM, {})
})

# 8. Reload - right hand leaves the grip, fetches, seats a magazine, returns.
# Clean arm/hand motion, no prop interaction modelled.
CLIPS["Reload"] = dict(frames=48, loop=False, keys={
    0:  merge(AIM, {}),
    8:  merge(AIM, finger_pose("Right", -34, thumb=-18), {"RightUpperArm": (-34, 0, R*8), "RightLowerArm": (0, fl(R, -18), 0), "LeftUpperArm": (-8, 0, L*6),
                    "LeftLowerArm": (0, fl(L, -6), 0), "UpperChest": (-1, 6, 0),
                    "Head": (3, -8, 0), "Neck": (0, -5, 0)}),
    16: merge(AIM, finger_pose("Right", -20, thumb=-10), {"RightUpperArm": (-16, 0, R*4), "RightLowerArm": (0, fl(R, 14), 0), "LeftUpperArm": (-6, 0, L*4),
                    "Head": (2, -10, 0), "Neck": (0, -6, 0)}),
    24: merge(AIM, finger_pose("Right", -6), {"RightUpperArm": (6, 0, 0), "RightLowerArm": (0, fl(R, 22), 0), "LeftUpperArm": (-3, 0, 0),
                    "Head": (1, -6, 0), "Neck": (0, -3, 0)}),
    30: merge(AIM, {"RightUpperArm": (10, 0, 0), "RightLowerArm": (0, fl(R, 10), 0),
                    "UpperChest": (1, 0, 0), "Head": (0, -2, 0)}),
    40: merge(AIM, {"RightUpperArm": (2, 0, 0), "RightLowerArm": (0, fl(R, 3), 0)}),
    48: merge(AIM, {})
})

# 9. Jump_Start - anticipation crouch then drive off the ground.
CLIPS["Jump_Start"] = dict(frames=12, loop=False, keys={
    0: {},
    5: {"LeftUpperLeg": (26, 0, 0), "RightUpperLeg": (26, 0, 0),
        "LeftLowerLeg": (-52, 0, 0), "RightLowerLeg": (-52, 0, 0),
        "LeftFoot": (24, 0, 0), "RightFoot": (24, 0, 0),
        "Spine": (-11, 0, 0), "Chest": (-7, 0, 0), "UpperChest": (-4, 0, 0),
        "Neck": (10, 0, 0),
        "LeftUpperArm": (-26, 0, L*4), "RightUpperArm": (-26, 0, R*4),
        "LeftLowerArm": (0, fl(L, 10), 0), "RightLowerArm": (0, fl(R, 10), 0)},
    10: {"LeftUpperLeg": (-8, 0, 0), "RightUpperLeg": (-8, 0, 0),
         "LeftLowerLeg": (2, 0, 0), "RightLowerLeg": (2, 0, 0),
         "LeftFoot": (-26, 0, 0), "RightFoot": (-26, 0, 0),
         "LeftToes": (-10, 0, 0), "RightToes": (-10, 0, 0),
         "Spine": (2, 0, 0), "Neck": (-2, 0, 0),
         "LeftUpperArm": (40, 0, ab(L, 12)), "RightUpperArm": (40, 0, ab(R, 12)),
         "LeftLowerArm": (0, fl(L, -6), 0), "RightLowerArm": (0, fl(R, -6), 0)},
    12: {"LeftUpperLeg": (4, 0, 0), "RightUpperLeg": (2, 0, 0),
         "LeftLowerLeg": (-16, 0, 0), "RightLowerLeg": (-10, 0, 0),
         "LeftFoot": (-16, 0, 0), "RightFoot": (-16, 0, 0),
         # hand off toward the Airborne_Loop arms-out pose
         "LeftUpperArm": (32, 0, ab(L, 20)), "RightUpperArm": (32, 0, ab(R, 20))}
}, hips={0: (0, 0, 0), 5: (0, 0, -0.085), 10: (0, 0, 0.030), 12: (0, 0, 0.022)})

# 10. Airborne_Loop - neutral controllable falling pose, gentle drift.
# Deliberately ASYMMETRIC (lead leg up and forward, trail leg tucked back) so
# the silhouette reads as airborne rather than standing.
_air = {"LeftUpperLeg": (40, 0, L*-8), "RightUpperLeg": (-26, 0, R*-5),
        "LeftLowerLeg": (-72, 0, 0), "RightLowerLeg": (-88, 0, 0),
        "LeftFoot": (-18, 0, 0), "RightFoot": (-24, 0, 0),
        "LeftToes": (-8, 0, 0), "RightToes": (-10, 0, 0),
        "Spine": (-8, 0, 0), "Chest": (-4, 0, 0), "Neck": (8, 0, 0), "Head": (2, 0, 0),
        "LeftUpperArm": (14, 0, ab(L, 34)), "RightUpperArm": (10, 0, ab(R, 38)),
        "LeftLowerArm": (0, fl(L, 44), 0), "RightLowerArm": (0, fl(R, 38), 0)}
CLIPS["Airborne_Loop"] = dict(frames=40, loop=True, keys={
    0:  merge(_air, {}),
    13: merge(_air, {"LeftUpperLeg": (4, 0, 0), "RightUpperLeg": (8, 0, 0),
                     "LeftLowerLeg": (6, 0, 0), "RightLowerLeg": (-10, 0, 0),
                     "LeftUpperArm": (0, 0, L*4), "RightUpperArm": (0, 0, R*3),
                     "Spine": (1.2, 0, 0), "Head": (0, 3, 0)}),
    26: merge(_air, {"LeftUpperLeg": (-6, 0, 0), "RightUpperLeg": (-3, 0, 0),
                     "LeftLowerLeg": (-8, 0, 0), "RightLowerLeg": (8, 0, 0),
                     "LeftUpperArm": (0, 0, -L*3), "RightUpperArm": (0, 0, -R*4),
                     "Spine": (-1.0, 0, 0), "Head": (0, -3, 0)}),
    40: merge(_air, {})
}, hips={0: (0, 0, 0), 13: (0, 0, 0.006), 26: (0, 0, -0.005), 40: (0, 0, 0)})

# 11. Land - readable impact, restrained compression, quick recovery.
CLIPS["Land"] = dict(frames=22, loop=False, keys={
    # Frame 0 is legs REACHING, not the airborne tuck. Godot blends into Land
    # from Airborne_Loop, and starting from the full tuck made a vertex travel
    # 0.70 m in a single frame - a visible pop.
    0: {"LeftUpperLeg": (10, 0, 0), "RightUpperLeg": (9, 0, 0),
        "LeftLowerLeg": (-12, 0, 0), "RightLowerLeg": (-11, 0, 0),
        "LeftFoot": (-12, 0, 0), "RightFoot": (-11, 0, 0),
        "Spine": (-5, 0, 0), "Neck": (4, 0, 0),
        "LeftUpperArm": (-10, 0, ab(L, 14)), "RightUpperArm": (-10, 0, ab(R, 14)),
        "LeftLowerArm": (0, fl(L, 16), 0), "RightLowerArm": (0, fl(R, 16), 0)},
    4: {"LeftUpperLeg": (20, 0, 0), "RightUpperLeg": (19, 0, 0),
        "LeftLowerLeg": (-28, 0, 0), "RightLowerLeg": (-26, 0, 0),
        "LeftFoot": (14, 0, 0), "RightFoot": (13, 0, 0),
        "Spine": (-8, 0, 0), "Neck": (7, 0, 0),
        "LeftUpperArm": (-14, 0, ab(L, 13)), "RightUpperArm": (-14, 0, ab(R, 13)),
        "LeftLowerArm": (0, fl(L, 20), 0), "RightLowerArm": (0, fl(R, 20), 0)},
    9: {"LeftUpperLeg": (30, 0, 0), "RightUpperLeg": (29, 0, 0),
        "LeftLowerLeg": (-52, 0, 0), "RightLowerLeg": (-50, 0, 0),
        "LeftFoot": (24, 0, 0), "RightFoot": (23, 0, 0),
        "Spine": (-14, 0, 0), "Chest": (-8, 0, 0), "UpperChest": (-4, 0, 0),
        "Neck": (12, 0, 0), "Head": (4, 0, 0),
        "LeftUpperArm": (-18, 0, ab(L, 15)), "RightUpperArm": (-18, 0, ab(R, 15)),
        "LeftLowerArm": (0, fl(L, 24), 0), "RightLowerArm": (0, fl(R, 24), 0)},
    15: {"LeftUpperLeg": (15, 0, 0), "RightUpperLeg": (14, 0, 0),
         "LeftLowerLeg": (-28, 0, 0), "RightLowerLeg": (-27, 0, 0),
         "LeftFoot": (13, 0, 0), "RightFoot": (12, 0, 0),
         "Spine": (-7, 0, 0), "Chest": (-3, 0, 0), "Neck": (6, 0, 0),
         "LeftUpperArm": (-7, 0, ab(L, 7)), "RightUpperArm": (-7, 0, ab(R, 7)),
         "LeftLowerArm": (0, fl(L, 10), 0), "RightLowerArm": (0, fl(R, 10), 0)},
    19: {"LeftUpperLeg": (5, 0, 0), "RightUpperLeg": (5, 0, 0),
         "LeftLowerLeg": (-10, 0, 0), "RightLowerLeg": (-10, 0, 0),
         "LeftFoot": (4, 0, 0), "RightFoot": (4, 0, 0),
         "Spine": (-3, 0, 0), "Neck": (2, 0, 0)},
    22: {},
}, hips={0: (0, 0, 0.055), 4: (0, 0, -0.018), 9: (0, 0, -0.092),
         15: (0, 0, -0.036), 19: (0, 0, -0.010), 22: (0, 0, 0)})

# 12. Death - grounded backward collapse to a slumped supine rest.
# Deliberately simple, not cinematic. Once Hips pitches back by theta, a thigh
# needs +theta of its own to lie horizontal (rest thighs point straight down),
# hence the large positive thigh offsets late in the clip. Final hip height is
# solved by the ground clamp rather than guessed.
CLIPS["Death"] = dict(frames=48, loop=False, keys={
    0: {},
    6: {"Spine": (8, 0, 0), "Chest": (5, 0, 0), "UpperChest": (3, 0, 0),
        "Neck": (-6, 0, 0), "Head": (-5, 0, 0),
        "LeftUpperArm": (-18, 0, ab(L, 18)), "RightUpperArm": (-16, 0, ab(R, 16)),
        "LeftLowerArm": (0, fl(L, 16), 0), "RightLowerArm": (0, fl(R, 14), 0),
        "LeftUpperLeg": (-6, 0, 0), "RightUpperLeg": (4, 0, 0)},
    16: {"Hips": (16, 0, 0),
         "Spine": (-12, 0, 0), "Chest": (-7, 0, 0), "Neck": (11, 0, 0), "Head": (6, 0, 0),
         "LeftUpperLeg": (30, 0, 0), "RightUpperLeg": (26, 0, -L*6),
         "LeftLowerLeg": (-64, 0, 0), "RightLowerLeg": (-58, 0, 0),
         "LeftFoot": (22, 0, 0), "RightFoot": (20, 0, 0),
         "LeftUpperArm": (-26, 0, ab(L, 10)), "RightUpperArm": (-22, 0, ab(R, 8)),
         "LeftLowerArm": (0, fl(L, 30), 0), "RightLowerArm": (0, fl(R, 26), 0)},
    30: {"Hips": (50, 0, 0),
         "Spine": (2, 0, 0), "Chest": (1, 0, 0), "Neck": (-4, 0, 0), "Head": (-8, 0, 0),
         "LeftUpperLeg": (22, 0, L*8), "RightUpperLeg": (18, 0, R*6),
         "LeftLowerLeg": (-34, 0, 0), "RightLowerLeg": (-30, 0, 0),
         "LeftFoot": (6, 0, 0), "RightFoot": (4, 0, 0),
         "LeftUpperArm": (-40, 0, ab(L, 34)), "RightUpperArm": (-36, 0, ab(R, 30)),
         "LeftLowerArm": (0, fl(L, 22), 0), "RightLowerArm": (0, fl(R, 18), 0)},
    # Legs must finish HORIZONTAL or bent knees hold the feet down and the
    # ground clamp cannot lower the body: thigh_pitch = 90 - hips_pitch.
    42: {"Hips": (72, 0, 0),
         "Spine": (5, 0, 0), "Chest": (3, 0, 0), "Neck": (-6, 0, 0), "Head": (-12, 0, 3),
         "LeftUpperLeg": (14, 0, L*15), "RightUpperLeg": (11, 0, R*11),
         "LeftLowerLeg": (-12, 0, 0), "RightLowerLeg": (-16, 0, 0),
         "LeftFoot": (-6, 0, 0), "RightFoot": (-4, 0, 0),
         # arms go OUT to the sides, not back/under: a back-swung arm reaches
         # the floor first and props the whole torso up off the ground
         "LeftUpperArm": (-18, 0, ab(L, 58)), "RightUpperArm": (-15, 0, ab(R, 54)),
         "LeftLowerArm": (0, fl(L, 10), 0), "RightLowerArm": (0, fl(R, 8), 0)},
    48: {"Hips": (85, 0, 0),
         "Spine": (3, 0, 0), "Chest": (2, 0, 0), "Neck": (-3, 0, 0), "Head": (-10, 0, 6),
         "LeftUpperLeg": (3, 0, L*18), "RightUpperLeg": (1, 0, R*14),
         "LeftLowerLeg": (-3, 0, 0), "RightLowerLeg": (-6, 0, 0),
         "LeftFoot": (-8, 0, 0), "RightFoot": (-6, 0, 0),
         "LeftUpperArm": (-16, 0, ab(L, 62)), "RightUpperArm": (-13, 0, ab(R, 58)),
         "LeftLowerArm": (0, fl(L, 8), 0), "RightLowerArm": (0, fl(R, 6), 0)}
}, hips={0: (0, 0, 0), 6: (0, 0, -0.02), 16: (0, 0, -0.26), 30: (0, 0, -0.50),
         42: (0, 0, -0.72), 48: (0, 0, -0.80)})

# ---------------------------------------------------------------- ground clamp
# Target height of the LOWEST body vertex at each keyframe. The solver adjusts
# Hips Z until it is met, which is also what physically keeps a planted foot on
# the floor while the body bobs over it. None = airborne, leave alone.
CLAMP = {
    "Idle": 0.0, "Walk_Forward": 0.0, "Walk_Backward": 0.0,
    "Strafe_Left": 0.0, "Strafe_Right": 0.0,
    "Fire": 0.0, "Reload": 0.0, "Land": {0: 0.075, 4: 0.0, 9: 0.0, 15: 0.0, 19: 0.0, 22: 0.0}, "Death": 0.0,
    # sprint has a real flight phase, so the passing frames are allowed to lift
    "Sprint": {0: 0.0, 5: 0.05, 10: 0.0, 15: 0.05, 20: 0.0},
    # Land is clamped at every breakdown so the feet stay planted

    # the jump leaves the ground on the drive frames
    "Jump_Start": {0: 0.0, 5: 0.0, 10: 0.07, 12: 0.15},
    "Airborne_Loop": None
}

# weapon grip: trigger finger stays straighter than the rest
AIM.update(finger_pose("Left", 36.0, thumb=20.0))
AIM.update(finger_pose("Right", 40.0, thumb=22.0, index=14.0))

LOOPING = {k for k, v in CLIPS.items() if v["loop"]}
NON_LOOPING = {k for k, v in CLIPS.items() if not v["loop"]}


def action_fcurves(act):
    """Blender 4.4+/5.x moved Action F-curves into layers -> strips ->
    channelbags (slotted actions). Fall back to the legacy flat list."""
    legacy = getattr(act, "fcurves", None)
    if legacy is not None:
        try:
            return list(legacy)
        except TypeError:
            pass
    out = []
    for layer in getattr(act, "layers", []):
        for strip in getattr(layer, "strips", []):
            for cb in getattr(strip, "channelbags", []):
                out.extend(cb.fcurves)
    return out


# ---------------------------------------------------------------- application
def build(arm, mesh=None):
    scene = bpy.context.scene
    scene.render.fps = FPS
    bones = arm.data.bones
    pose = arm.pose.bones
    rest3 = {b.name: b.matrix_local.to_3x3() for b in bones}

    def clear():
        for pb in pose:
            pb.rotation_mode = "QUATERNION"
            pb.matrix_basis = Matrix.Identity(4)

    def apply(offsets, hips_off):
        clear()
        for name, base in BASE.items():
            p, y, r = base
            if name in offsets:
                dp, dy, dr = offsets[name]
                p, y, r = p + dp, y + dy, r + dr
            Mr = rest3[name]
            Rm = (Matrix.Rotation(math.radians(p), 3, "X") @
                  Matrix.Rotation(math.radians(y), 3, "Z") @
                  Matrix.Rotation(math.radians(r), 3, "Y"))
            pose[name].rotation_quaternion = (Mr.inverted() @ Rm @ Mr).to_quaternion()
        # any bone the clip drives that is not in BASE (none today, but safe)
        for name, off in offsets.items():
            if name in BASE or name not in pose:
                continue
            p, y, r = off
            Mr = rest3[name]
            Rm = (Matrix.Rotation(math.radians(p), 3, "X") @
                  Matrix.Rotation(math.radians(y), 3, "Z") @
                  Matrix.Rotation(math.radians(r), 3, "Y"))
            pose[name].rotation_quaternion = (Mr.inverted() @ Rm @ Mr).to_quaternion()
        # hips offset is authored in armature space; pose location is bone-local
        if hips_off is not None:
            pose["Hips"].location = rest3["Hips"].inverted() @ Vector(hips_off)

    def lowest_z():
        dg = bpy.context.evaluated_depsgraph_get()
        e = mesh.evaluated_get(dg)
        t = e.to_mesh()
        import numpy as _np
        co = _np.empty(len(t.vertices)*3, dtype=_np.float32)
        t.vertices.foreach_get("co", co)
        e.to_mesh_clear()
        M = _np.array(mesh.matrix_world)
        return float((co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3])[:, 2].min())

    if arm.animation_data is None:
        arm.animation_data_create()
    arm.animation_data.action = None      # solve with no action driving the pose

    made = {}
    for name, spec in CLIPS.items():
        frames = sorted(spec["keys"])
        hips_track = {f: tuple(spec.get("hips", {}).get(f, (0.0, 0.0, 0.0)))
                      for f in frames}
        clamp = CLAMP.get(name, None)
        solved = None
        if clamp is not None and mesh is not None:
            for _ in range(3):            # converges fast; hips move rigidly
                for f in frames:
                    tgt = clamp if isinstance(clamp, (int, float)) else clamp.get(f, 0.0)
                    apply(spec["keys"][f], hips_track[f])
                    bpy.context.view_layer.update()
                    x, y, z = hips_track[f]
                    hips_track[f] = (x, y, z + (tgt - lowest_z()))
            solved = {f: round(hips_track[f][2], 4) for f in frames}

        act = bpy.data.actions.new(name)
        act.use_fake_user = True
        arm.animation_data.action = act
        for f in frames:
            hp = hips_track[f]
            apply(spec["keys"][f], hp)
            for pb in pose:
                pb.keyframe_insert("rotation_quaternion", frame=f)
            pose["Hips"].keyframe_insert("location", frame=f)
        # Root must never move: pin it explicitly at both ends
        pose["Root"].matrix_basis = Matrix.Identity(4)
        for f in (frames[0], frames[-1]):
            pose["Root"].keyframe_insert("location", frame=f)
            pose["Root"].keyframe_insert("rotation_quaternion", frame=f)
        fcs = action_fcurves(act)
        for fc in fcs:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
        act.use_frame_range = True
        act.frame_start, act.frame_end = float(frames[0]), float(frames[-1])
        made[name] = dict(frames=[frames[0], frames[-1]], loop=spec["loop"],
                          seconds=round((frames[-1]-frames[0])/FPS, 2),
                          fcurves=len(fcs), solved_hips_z=solved)
    arm.animation_data.action = None
    clear()
    return made
