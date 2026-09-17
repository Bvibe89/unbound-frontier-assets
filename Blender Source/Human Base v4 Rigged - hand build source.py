# Human Base v2 - hand rebuild with separated fingers.
#
# The old hands were fused mittens with splayed claw-like digits (77 unique
# positions per hand, max inter-digit gap 6-7.7 mm). They are cut off at the
# wrist and replaced with generated low-poly hands: a 2x5-grid palm whose
# knuckle end provides four ready-made finger-base quads, plus a thumb
# extruded from the palm's thumb-side face.
#
# Frames are built in WORLD space from the rig, using the thumb axis = world
# +Z for BOTH hands. That is deliberate: with arms in a T-pose and palms
# facing forward, both thumbs point up, so (X_hand, Y_palm, +Z) is left-handed
# on the left and right-handed on the right - which is exactly what makes the
# two hands come out as proper mirrors without any special-casing.
#
# Weights are exact by construction (we generated the geometry, so we know
# which ring belongs to which bone) rather than derived by proximity.

import math
import bmesh
import bpy
import numpy as np
from mathutils import Vector

# finger: (name, length as a FRACTION of palm length, fan_deg, curl_deg)
FINGERS = [
    ("Index",  0.79,  7.0, 14.0),
    ("Middle", 0.83,  2.0, 16.0),
    ("Ring",   0.76, -4.0, 19.0),
    ("Little", 0.60, -11.0, 23.0),
]
SEG2_CURL = 1.9           # distal segment curls further than the proximal
# cross-sections in metres: real adult wrist ~55x40mm, palm ~85x25mm
KNUCKLE_HALF_U = 0.036   # 72mm palm; 84 flared like a paddle
KNUCKLE_HALF_Y = 0.0115
MID_HALF_U = 0.030
MID_HALF_Y = 0.0170
TIP_TAPER = 0.72
SEG1 = 0.56               # proximal share of finger length
THUMB_FRAC = 0.58
THUMB_HALF = 0.0150   # chunky: a thin one taper-tipped into a spike
THUMB_TAPER = 0.86    # barely tapered, so it reads as a thumb not a claw
FINGER_INSET = 0.78      # gap between adjacent digits
THUMB_BASE_FRAC = 0.30   # how far along the palm the thumb springs from

BONES = []                # (name, parent, head, tail) filled during build


def build_hand(bm, side, wrist_ring, W, X, Y, U, a_wrist, a_knuckle):
    """wrist_ring: ordered BMVerts. a_wrist / a_knuckle are distances along
    X from the cut ring to the Hand bone's head and tail, so the rebuilt
    geometry restores the forearm length the cut removed."""
    PALM_MID, PALM_LEN = a_wrist, a_knuckle
    P_LEN = a_knuckle - a_wrist
    def P(a, b, c):
        return Vector(W + a * X + b * Y + c * U)

    groups = {}          # bone name -> list of (BMVert, weight)

    def add(bone, v, w):
        groups.setdefault(bone, []).append((v, w))

    # ---- palm: two 2x5 grids (palmar row j=0, dorsal row j=1)
    EDGE_ROUND = (0.55, 0.86, 1.0, 0.86, 0.62)   # thins the palm at its edges

    def grid(a, hu, hy):
        rows = []
        for j, sy in ((0, +1.0), (1, -1.0)):
            row = []
            for i in range(5):
                t = -1.0 + 2.0 * (i / 4.0)          # -1 (little) .. +1 (thumb)
                row.append(bm.verts.new(P(a, sy * hy * EDGE_ROUND[i], t * hu)))
            rows.append(row)
        return rows

    midg = grid(PALM_MID, MID_HALF_U, MID_HALF_Y)
    kng = grid(PALM_LEN, KNUCKLE_HALF_U, KNUCKLE_HALF_Y)
    bm.verts.ensure_lookup_table()

    def perim(g):
        return g[0] + [g[1][4], g[1][3], g[1][2], g[1][1], g[1][0]]

    mid_p, kn_p = perim(midg), perim(kng)

    def ring_edges(ring):
        es = []
        for i in range(len(ring)):
            a, b = ring[i], ring[(i + 1) % len(ring)]
            e = bm.edges.get((a, b)) or bm.edges.new((a, b))
            es.append(e)
        return es

    e_mid = ring_edges(mid_p)
    e_kn = ring_edges(kn_p)
    e_wrist = []
    for i in range(len(wrist_ring)):
        a, b = wrist_ring[i], wrist_ring[(i + 1) % len(wrist_ring)]
        e = bm.edges.get((a, b))
        if e:
            e_wrist.append(e)

    bmesh.ops.bridge_loops(bm, edges=e_wrist + e_mid)
    bmesh.ops.bridge_loops(bm, edges=e_mid + e_kn)

    for v in mid_p:
        add(f"{side}Hand", v, 0.85)
        add(f"{side}LowerArm", v, 0.15)
    for v in kn_p:
        add(f"{side}Hand", v, 1.0)

    # ---- four fingers, each extruded from its own knuckle quad
    def finger(name, quad_verts, base_a, u0, length, half, fan, curl, parent):
        fa = math.radians(fan)
        cu = math.radians(curl)
        D = (X * math.cos(fa) * math.cos(cu) + U * math.sin(fa)
             + Y * math.sin(cu))
        D = D / np.linalg.norm(D)
        base = np.array([sum(v.co[k] for v in quad_verts) / 4.0
                         for k in range(3)])
        l1 = length * SEG1
        joint = base + D * l1
        tip = base + D * length
        ring0, ring1, ring2 = [], [], []
        for v in quad_verts:
            off = np.array(v.co) - base
            off = off - np.dot(off, D) * D
            ring0.append(bm.verts.new(Vector(base + off * FINGER_INSET)))
        cu2 = math.radians(curl * (SEG2_CURL - 1.0))
        D2 = D * math.cos(cu2) + Y * math.sin(cu2)
        D2 = D2 / np.linalg.norm(D2)
        joint = base + D * l1
        tip = joint + D2 * (length - l1)
        for r0 in ring0:
            off = np.array(r0.co) - base
            off = off - np.dot(off, D) * D
            ring1.append(bm.verts.new(Vector(joint + off * 0.88)))
        for r1 in ring1:
            off = np.array(r1.co) - joint
            off = off - np.dot(off, D2) * D2
            ring2.append(bm.verts.new(Vector(tip + off * TIP_TAPER)))
        bm.verts.ensure_lookup_table()
        for a, b in ((quad_verts, ring0), (ring0, ring1), (ring1, ring2)):
            for i in range(4):
                bm.faces.new((a[i], a[(i + 1) % 4], b[(i + 1) % 4], b[i]))
        bm.faces.new(tuple(ring2))
        prox, dist = f"{side}{name}Proximal", f"{side}{name}Distal"
        BONES.append((prox, parent, tuple(base), tuple(joint)))
        BONES.append((dist, prox, tuple(joint), tuple(tip)))
        for v in quad_verts:
            add(f"{side}Hand", v, 1.0)
        for v in ring0:
            add(prox, v, 0.8); add(f"{side}Hand", v, 0.2)
        for v in ring1:
            add(prox, v, 0.5); add(dist, v, 0.5)
        for v in ring2:
            add(dist, v, 1.0)

    for idx, (nm, frac, fan, curl) in enumerate(FINGERS):
        i = 3 - idx                     # grid i=4 is the thumb side
        quad = [kng[0][i], kng[0][i + 1], kng[1][i + 1], kng[1][i]]
        finger(nm, quad, PALM_LEN, 0.0, P_LEN * frac, 0.0, fan, curl,
               f"{side}Hand")

    # ---- thumb from the palm's thumb-side face, angled out and forward
    want = {midg[0][4], midg[1][4], kng[1][4], kng[0][4]}
    face = next((f for f in bm.faces if set(f.verts) == want), None)
    if face is not None:
        quad = list(face.verts)
        D = (X * 0.74 + U * 0.58 + Y * 0.26)
        D = D / np.linalg.norm(D)
        base = (W + (PALM_MID + P_LEN * THUMB_BASE_FRAC) * X
                + MID_HALF_U * 0.62 * U + MID_HALF_Y * 0.45 * Y)
        t_len = P_LEN * THUMB_FRAC
        l1 = t_len * 0.55
        joint = base + D * l1
        tip = base + D * t_len
        e1 = Y - np.dot(Y, D) * D
        e1 = e1 / np.linalg.norm(e1)
        e2 = np.cross(D, e1)
        quad = sorted(quad, key=lambda v: math.atan2(
            float(np.dot(np.array(v.co) - base, e2)),
            float(np.dot(np.array(v.co) - base, e1))))
        r0, r1, r2 = [], [], []
        for k in range(4):
            ang = math.pi / 4.0 + k * math.pi / 2.0
            off = (e1 * math.cos(ang) + e2 * math.sin(ang)) * THUMB_HALF
            r0.append(bm.verts.new(Vector(base + off)))
        for v in r0:
            off = np.array(v.co) - base
            r1.append(bm.verts.new(Vector(joint + off * 0.90)))
        for v in r1:
            off = np.array(v.co) - joint
            r2.append(bm.verts.new(Vector(tip + off * THUMB_TAPER)))
        bm.verts.ensure_lookup_table()
        for a, b in ((quad, r0), (r0, r1), (r1, r2)):
            for i in range(4):
                bm.faces.new((a[i], a[(i + 1) % 4], b[(i + 1) % 4], b[i]))
        bm.faces.new(tuple(r2))
        bm.faces.remove(face)
        prox, dist = f"{side}ThumbProximal", f"{side}ThumbDistal"
        BONES.append((prox, f"{side}Hand", tuple(base), tuple(joint)))
        BONES.append((dist, prox, tuple(joint), tuple(tip)))
        for v in r0:
            add(prox, v, 0.8); add(f"{side}Hand", v, 0.2)
        for v in r1:
            add(prox, v, 0.55); add(dist, v, 0.45)
        for v in r2:
            add(dist, v, 1.0)
        for v in quad:
            add(f"{side}Hand", v, 1.0)
    return groups, dict(thumb_face_found=face is not None)



def find_skin_patch(mesh, rings, surv_uv):
    """Pick the UV of the lowest-variance skin-toned tile in the base colour
    atlas. Anchoring the new hands on the wrist's own UV put them in a noisy
    region and they came out streaky."""
    img = None
    for m in mesh.data.materials:
        if not m or not m.use_nodes:
            continue
        for n in m.node_tree.nodes:
            if n.type == "TEX_IMAGE" and n.image and n.outputs[0].links:
                for l in n.outputs[0].links:
                    if l.to_socket.name == "Base Color":
                        img = n.image
    wu = [surv_uv[v.index] for r in rings for v in r if v.index in surv_uv]
    fallback = np.array(wu).mean(axis=0) if wu else np.array([0.5, 0.5])
    if img is None:
        return fallback
    cs = img.colorspace_settings.name
    img.colorspace_settings.name = "Non-Color"
    S = 256
    img.scale(S, S)
    ch = img.channels
    buf = np.empty(S * S * ch, dtype=np.float32)
    img.pixels.foreach_get(buf)
    img.colorspace_settings.name = cs
    a = buf.reshape(S, S, ch)[..., :3]
    T = 16                              # tile size in pixels
    best, best_uv = None, fallback
    for ty in range(0, S - T, T):
        for tx in range(0, S - T, T):
            tile = a[ty:ty + T, tx:tx + T]
            mean = tile.reshape(-1, 3).mean(axis=0)
            if mean[0] < 0.25 or mean[0] > 0.85:
                continue            # too dark (underwear) or blown out
            if not (mean[0] > mean[1] > mean[2]):
                continue            # not a warm skin tone
            var = float(tile.reshape(-1, 3).std(axis=0).mean())
            if best is None or var < best:
                best = var
                best_uv = np.array([(tx + T / 2) / S, (ty + T / 2) / S])
    return best_uv

# --------------------------------------------------------------- full pipeline
def rebuild(blend_path):
    """Everything in one pass: the exec namespace does not persist between
    tool calls, so geometry, bones, weights and UVs must all be done here."""
    from collections import defaultdict
    log = {}
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene
    arm = next(o for o in scene.objects if o.type == "ARMATURE")
    mesh = next(o for o in scene.objects if o.type == "MESH" and o.name != "Icosphere")
    ico = bpy.data.objects.get("Icosphere")
    if ico:
        bpy.data.objects.remove(ico, do_unlink=True)
    me = mesh.data
    log["start"] = dict(verts=len(me.vertices),
                        tris=sum(len(p.vertices) - 2 for p in me.polygons),
                        bones=len(arm.data.bones))

    # 1. Meshy's custom split normals go: verified visually equivalent to
    #    smooth shading with angle-based sharp edges (mean pixel diff 1.52/255),
    #    and keeping them would block any topology edit.
    if "custom_normal" in me.attributes:
        me.attributes.remove(me.attributes["custom_normal"])

    def mark_sharp(angle=38.0):
        for p in me.polygons:
            p.use_smooth = True
        for e in me.edges:
            e.use_edge_sharp = False
        fn = np.empty(len(me.polygons) * 3, dtype=np.float32)
        me.polygons.foreach_get("normal", fn)
        fn = fn.reshape(-1, 3)
        ef = defaultdict(list)
        for p in me.polygons:
            for k in p.edge_keys:
                ef[k].append(p.index)
        ekey = {tuple(sorted(e.vertices)): e for e in me.edges}
        n = 0
        for k, fs in ef.items():
            if len(fs) == 2 and float(np.dot(fn[fs[0]], fn[fs[1]])) < math.cos(
                    math.radians(angle)):
                e = ekey.get(tuple(sorted(k)))
                if e:
                    e.use_edge_sharp = True
                    n += 1
        me.update()
        return n

    # 2. Weld coincident verts. UVs are per-LOOP so this is lossless, and it
    #    turns ~95 seam "boundary" loops into real topology.
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-5)
    bm.to_mesh(me); bm.free(); me.update()
    log["after_weld"] = dict(verts=len(me.vertices))

    # 3. Cut the old hands off at the wrist
    gi = {g.index: g.name for g in mesh.vertex_groups}
    kill = [v.index for v in me.vertices
            if any(gi[g.group] in ("LeftHand", "LeftFingers", "RightHand",
                                   "RightFingers") and g.weight > 0.5
                   for g in v.groups)]
    uvl = me.uv_layers[0].data
    orig_uv = {}
    for p in me.polygons:
        for li, vi in zip(p.loop_indices, p.vertices):
            orig_uv.setdefault(vi, (uvl[li].uv.x, uvl[li].uv.y))
    bm = bmesh.new(); bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.verts[i] for i in kill], context="VERTS")
    bm.verts.index_update()
    # re-key surviving UVs by their NEW indices
    surv_uv = {}
    bm.to_mesh(me); bm.free(); me.update()
    uvl = me.uv_layers[0].data
    for p in me.polygons:
        for li, vi in zip(p.loop_indices, p.vertices):
            surv_uv.setdefault(vi, (uvl[li].uv.x, uvl[li].uv.y))
    n_orig = len(me.vertices)
    log["after_cut"] = dict(verts=n_orig, removed=len(kill))

    # 4. Build the new hands
    bm = bmesh.new(); bm.from_mesh(me)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    uvlay = bm.loops.layers.uv.verify()
    bnd = [e for e in bm.edges if len(e.link_faces) == 1]
    adj = defaultdict(list)
    for e in bnd:
        adj[e.verts[0]].append(e.verts[1]); adj[e.verts[1]].append(e.verts[0])
    rings, seen = [], set()
    for s in list(adj):
        if s in seen:
            continue
        ring = [s]; seen.add(s); cur, prev = s, None
        while True:
            nxt = next((n for n in adj[cur] if n is not prev and n not in seen), None)
            if nxt is None:
                break
            ring.append(nxt); seen.add(nxt); prev, cur = cur, nxt
        rings.append(ring)
    log["wrist_rings"] = [len(r) for r in rings]
    Bd = arm.data.bones
    # the source rig is slightly asymmetric (right Hand bone is ~9% longer),
    # so both hands are built to the MEAN so they come out identical
    _aw, _ak = [], []
    for ring in rings:
        cc = np.array([sum(v.co[k] for v in ring) / len(ring) for k in range(3)])
        sd = "Left" if cc[0] < 0 else "Right"
        hb2 = Bd[f"{sd}Hand"]
        XX = np.array(hb2.tail_local) - np.array(hb2.head_local)
        XX /= np.linalg.norm(XX)
        _aw.append(float(np.dot(np.array(hb2.head_local) - cc, XX)))
        _ak.append(float(np.dot(np.array(hb2.tail_local) - cc, XX)))
    A_MEAN = (sum(_aw) / len(_aw), sum(_ak) / len(_ak))
    BONES.clear()
    pre_faces = set(bm.faces)
    groups, diag = {}, {}
    Bd = arm.data.bones
    for ring in rings:
        c = np.array([sum(v.co[k] for v in ring) / len(ring) for k in range(3)])
        side = "Left" if c[0] < 0 else "Right"
        hb = Bd[f"{side}Hand"]
        X = np.array(hb.tail_local) - np.array(hb.head_local)
        X /= np.linalg.norm(X)
        Y0 = np.array([0.0, 1.0, 0.0]); Y = Y0 - np.dot(Y0, X) * X
        Y /= np.linalg.norm(Y)
        U0 = np.array([0.0, 0.0, 1.0])
        U = U0 - np.dot(U0, X) * X - np.dot(U0, Y) * Y
        U /= np.linalg.norm(U)
        a_w, a_k = A_MEAN
        g, d = build_hand(bm, side, ring, c, X, Y, U, a_w, a_k)
        d["a_wrist"] = round(a_w, 4); d["a_knuckle"] = round(a_k, 4)
        for k, vl in g.items():
            groups.setdefault(k, []).extend(vl)
        diag[side] = dict(ring=len(ring), handedness=round(float(np.dot(np.cross(X, Y), U)), 2), **d)
    new_faces = [f for f in bm.faces if f not in pre_faces]
    bm.verts.index_update(); bm.faces.index_update()

    base_uv = find_skin_patch(mesh, rings, surv_uv)
    newv = [v for v in bm.verts if v.index >= n_orig]
    pts = np.array([[v.co[0], v.co[1], v.co[2]] for v in newv])
    mn = pts.min(axis=0); span = np.maximum(pts.max(axis=0) - mn, 1e-6)
    for f in new_faces:
        for l in f.loops:
            vi = l.vert.index
            if vi < n_orig and vi in surv_uv:
                l[uvlay].uv = surv_uv[vi]
            else:
                q = (np.array([l.vert.co[0], l.vert.co[1], l.vert.co[2]]) - mn) / span
                l[uvlay].uv = (float(base_uv[0] + (q[0] - 0.5) * 0.022),
                               float(base_uv[1] + (q[2] - 0.5) * 0.022))
    wmap = defaultdict(list)
    for bone, vl in groups.items():
        for v, w in vl:
            wmap[v.index].append((bone, w))
    bm.to_mesh(me); bm.free(); me.update()
    log["after_build"] = dict(verts=len(me.vertices),
                              tris=sum(len(p.vertices) - 2 for p in me.polygons))
    log["diag"] = diag
    log["sharp_edges"] = mark_sharp()

    # 5. Armature: drop the fused-finger bones, add the real finger chain
    win = bpy.data.window_managers[0].windows[0]
    vl_ = scene.view_layers[0]; vl_.objects.active = arm
    for o in scene.objects:
        o.select_set(False)
    arm.select_set(True)
    with bpy.context.temp_override(window=win, screen=win.screen, scene=scene,
                                   view_layer=vl_, active_object=arm, object=arm,
                                   selected_objects=[arm],
                                   selected_editable_objects=[arm]):
        bpy.ops.object.mode_set(mode="EDIT")
        eb = arm.data.edit_bones
        for nm in ("LeftFingers", "RightFingers"):
            if nm in eb:
                eb.remove(eb[nm])
        for name, parent, head, tail in BONES:
            if name in eb:
                eb.remove(eb[name])
            b = eb.new(name); b.head = head; b.tail = tail; b.use_connect = False
        for name, parent, head, tail in BONES:
            eb[name].parent = eb[parent]
        for name, parent, head, tail in BONES:
            eb[name].align_roll((0.0, 1.0, 0.0))
        bpy.ops.object.mode_set(mode="OBJECT")

    # 6. Vertex groups + exact weights + normalise
    for nm in ("LeftFingers", "RightFingers"):
        if nm in mesh.vertex_groups:
            mesh.vertex_groups.remove(mesh.vertex_groups[nm])
    for name, _, _, _ in BONES:
        if name not in mesh.vertex_groups:
            mesh.vertex_groups.new(name=name)
    for vi, pairs in wmap.items():
        for bone, w in pairs:
            g = mesh.vertex_groups.get(bone)
            if g:
                g.add([vi], float(w), "REPLACE")
    gi = {g.index: g.name for g in mesh.vertex_groups}
    for v in me.vertices:
        tot = sum(g.weight for g in v.groups)
        if tot > 1e-9 and abs(tot - 1.0) > 1e-4:
            for g in v.groups:
                mesh.vertex_groups[gi[g.group]].add([v.index], g.weight / tot, "REPLACE")
    # Soften the shoulder/armpit transition. The stress test puts every
    # remaining bad edge at Shoulder<->UpperArm, so smooth ONLY that region -
    # a global smooth would blur the good weights everywhere else.
    from collections import defaultdict as _dd
    REGION = {"LeftShoulder", "LeftUpperArm", "LeftLowerArm", "UpperChest",
              "RightShoulder", "RightUpperArm", "RightLowerArm"}
    gi2 = {g.index: g.name for g in mesh.vertex_groups}
    nbr = _dd(set)
    for e in me.edges:
        nbr[e.vertices[0]].add(e.vertices[1])
        nbr[e.vertices[1]].add(e.vertices[0])
    wof = {}
    for v in me.vertices:
        wof[v.index] = {gi2[g.group]: g.weight for g in v.groups}
    target = [v.index for v in me.vertices
              if wof[v.index] and max(wof[v.index], key=wof[v.index].get) in REGION]
    BLEND = 0.35
    for _ in range(2):
        newv = {}
        for vi in target:
            acc = _dd(float)
            for nb in nbr[vi]:
                for b, w in wof[nb].items():
                    acc[b] += w
            n = max(len(nbr[vi]), 1)
            mixed = _dd(float)
            for b, w in wof[vi].items():
                mixed[b] += (1.0 - BLEND) * w
            for b, w in acc.items():
                mixed[b] += BLEND * (w / n)
            tot = sum(mixed.values())
            if tot > 1e-9:
                newv[vi] = {b: w / tot for b, w in mixed.items() if w / tot > 0.003}
        for vi, d in newv.items():
            for g in list(me.vertices[vi].groups):
                mesh.vertex_groups[gi2[g.group]].remove([vi])
            for b, w in d.items():
                mesh.vertex_groups[b].add([vi], float(w), "REPLACE")
            wof[vi] = d
    log["shoulder_verts_smoothed"] = len(target)
    log["zero_weight_verts"] = sum(
        1 for v in me.vertices if sum(g.weight for g in v.groups) <= 1e-9)
    log["unnormalised"] = sum(
        1 for v in me.vertices if abs(sum(g.weight for g in v.groups) - 1.0) > 0.01)
    bn = {b.name for b in arm.data.bones}
    vg = {g.name for g in mesh.vertex_groups}
    log["vgroups_without_bone"] = sorted(vg - bn)
    log["bones_without_vgroup"] = sorted(bn - vg)
    log["bones_total"] = len(arm.data.bones)
    log["new_finger_bones"] = sorted(b[0] for b in BONES)
    return log
