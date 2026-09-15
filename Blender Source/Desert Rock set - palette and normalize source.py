# Normalize the desert rock set and unify it (plus Finished Mound) onto the
# pack palette.
#
# Palette provenance: the nine approved reference GLBs share a warm hue axis at
# R : G : B = 1.00 : 0.83 : 0.65 (hue ~31 deg), saturation 0.07-0.43, value
# 0.20-0.43. The raw rocks AND Finished Mound measured 1 : 0.61-0.66 :
# 0.38-0.44 at saturation 0.56-0.62 - far more saturated than any approved
# prop, and they would read as orange blobs on the new sand terrain
# (saturation 0.24, value 0.69). Both are therefore brought onto the pack axis.
#
# The recolour is a principled reparameterisation, not a hue-shift filter:
# every pixel is decomposed into value V = max(RGB) and saturation
# S = (V - min)/V, those are remapped to the pack targets, and the colour is
# rebuilt on the pack axis as R = V, G = V(1 - 0.486 S), B = V(1 - S). A
# fraction of each pixel's deviation from that axis is added back so the
# texture keeps its character instead of flattening to a single hue.

import os, zlib, struct
import numpy as np
import bpy

REPO = r"G:\Game Dev\claude-assets\Unbound Frontier Assets"
ENV = os.path.join(REPO, "GLB", "Environment")
TMP = r"C:\Users\nepho\AppData\Local\Temp\claude\G--Game-Dev-claude-assets-Unbound-Frontier-Assets\4bdbe3a8-72e7-496a-b135-a61ac51c69b1\scratchpad\rockout"
os.makedirs(TMP, exist_ok=True)

HUE_G = 0.486          # G sits this far along the R->B path (measured)
TARGET_VAL = 0.44      # just above the props' 0.20-0.43, sunlit stone
TARGET_SAT = 0.36      # inside the warm props' 0.31-0.43 band
KEEP_RESIDUAL = 0.30   # how much off-axis character to retain
CONTRAST = 0.95

# source stem -> (new name, target longest dimension in metres, note)
PLAN = [
    ("desert_rock_small_clu_needsrecolor", "Desert Rock Cluster",     0.90,
     "small scatter cluster, ankle-to-knee"),
    ("desert_rock_medium_alt_needsrecolor", "Desert Rock Medium B",   1.30,
     "medium boulder, thigh-high"),
    ("desert_rock_medium_needsrecolor",    "Desert Rock Medium A",    1.50,
     "medium boulder, waist-high"),
    ("desert_rock_half_buri_needrecolor",  "Desert Rock Half Buried", 1.60,
     "half-buried boulder, low and wide"),
    ("desert_rock_flat_slab_needsrecolor", "Desert Rock Slab",        1.70,
     "flat slab, low seat/step height"),
    ("desert_rock_jagged_needsrecolor",    "Desert Rock Jagged",      1.90,
     "jagged outcrop, chest-high landmark"),
]


def write_png(path, arr):
    h, w = arr.shape[:2]
    ctype = 2 if arr.shape[2] == 3 else 6
    arr = np.ascontiguousarray(arr, dtype=np.uint8)
    rows = bytearray()
    for y in range(h):
        rows += b"\x00"
        rows += arr[y].tobytes()

    def ck(t, d):
        return (struct.pack(">I", len(d)) + t + d +
                struct.pack(">I", zlib.crc32(t + d) & 0xffffffff))

    png = (b"\x89PNG\r\n\x1a\n"
           + ck(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0))
           + ck(b"IDAT", zlib.compress(bytes(rows), 9)) + ck(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return os.path.getsize(path)


def read_scaled(img, size):
    """Raw stored pixel values at `size`, with no colour management.

    Forcing Non-Color makes foreach_get return the stored values rather than a
    converted variant. image.scale() only mutates the in-memory buffer, which
    is fine here because the pixels are written out to a real PNG afterwards
    rather than relied on surviving pack()/export.
    """
    cs = img.colorspace_settings.name
    img.colorspace_settings.name = "Non-Color"
    img.scale(size, size)
    ch = img.channels
    buf = np.empty(size * size * ch, dtype=np.float32)
    img.pixels.foreach_get(buf)
    a = buf.reshape(size, size, ch)
    if ch == 4 and float(a[..., 3].min()) > 0.999:
        a = a[..., :3]
    return np.clip(a, 0.0, 1.0), cs


def recolour(a):
    """Reparameterise onto the pack hue axis at the target value/saturation."""
    px = a.reshape(-1, a.shape[2])[:, :3].astype(np.float64)
    V = px.max(axis=1)
    mn = px.min(axis=1)
    S = np.where(V > 1e-6, (V - mn) / np.maximum(V, 1e-6), 0.0)
    # deviation from the pack axis at the SOURCE value/saturation
    resG = px[:, 1] - V * (1.0 - HUE_G * S)
    resB = px[:, 2] - V * (1.0 - S)
    before = dict(val=float(V.mean()), sat=float(S.mean()),
                  mean255=[round(float(px[:, c].mean() * 255), 1) for c in range(3)])
    kS = TARGET_SAT / max(float(S.mean()), 1e-6)
    S2 = np.clip(S * kS, 0.0, 0.95)
    V2 = np.clip(TARGET_VAL + (V - V.mean()) * CONTRAST, 0.03, 0.97)
    sc = np.clip(V2 / np.maximum(V, 1e-3), 0.0, 3.0)
    G2 = V2 * (1.0 - HUE_G * S2) + resG * KEEP_RESIDUAL * sc
    B2 = V2 * (1.0 - S2) + resB * KEEP_RESIDUAL * sc
    out = np.clip(np.stack([V2, G2, B2], axis=1), 0.0, 1.0)
    mx = out.max(axis=1); mn2 = out.min(axis=1)
    S3 = np.where(mx > 0, (mx - mn2) / np.maximum(mx, 1e-6), 0.0)
    after = dict(val=round(float(mx.mean()), 3), sat=round(float(S3.mean()), 3),
                 mean255=[round(float(out[:, c].mean() * 255), 1) for c in range(3)],
                 hue_ratio=[1.0,
                            round(float(out[:, 1].mean() / max(out[:, 0].mean(), 1e-6)), 3),
                            round(float(out[:, 2].mean() / max(out[:, 0].mean(), 1e-6)), 3)])
    before["val"] = round(before["val"], 3); before["sat"] = round(before["sat"], 3)
    return out.reshape(a.shape[0], a.shape[1], 3), before, after


def swap_texture(node, size, tag, do_recolour):
    """Downsample (and optionally recolour), then replace the datablock via a
    real file on disk so the result actually survives pack() and export."""
    img = node.image
    a, cs = read_scaled(img, size)
    info = None
    if do_recolour:
        a, before, after = recolour(a)
        info = dict(before=before, after=after)
    px = np.rint(a * 255.0).astype(np.uint8)
    path = os.path.join(TMP, tag + ".png")
    kb = write_png(path, px) / 1024
    new = bpy.data.images.load(path, check_existing=False)
    new.colorspace_settings.name = cs
    new.pack()
    old = img
    node.image = new
    if old.users == 0:
        bpy.data.images.remove(old)
    return dict(size=[size, size], kb=round(kb), colorspace=cs, recolour=info)


def import_glb(path):
    scene = bpy.context.scene
    bpy.ops.wm.read_homefile(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    win = bpy.data.window_managers[0].windows[0]
    # read_homefile leaves bpy.context without .object, which the glTF
    # importer dereferences; override with a freshly fetched window
    with bpy.context.temp_override(window=win, screen=win.screen,
                                   view_layer=scene.view_layers[0]):
        bpy.ops.import_scene.gltf(filepath=path)
    o = next(x for x in scene.objects if x.type == "MESH"
             and "glTF_not_exported" not in [c.name for c in x.users_collection])
    return scene, o


def texture_roles(mat):
    """Identify maps by what they FEED, not by datablock name."""
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")

    def feeder(sock):
        return sock.links[0].from_node if sock.links else None

    base = feeder(bsdf.inputs["Base Color"])
    sep = feeder(bsdf.inputs["Roughness"])
    orm = feeder(sep.inputs["Color"]) if sep and sep.type == "SEPARATE_COLOR" else None
    nmap = feeder(bsdf.inputs["Normal"])
    nrm = feeder(nmap.inputs["Color"]) if nmap else None
    return bsdf, base, orm, nrm, nmap


def geometry_report(me):
    from collections import defaultdict
    n = len(me.vertices)
    raw = np.empty(n * 3, dtype=np.float32)
    me.vertices.foreach_get("co", raw)
    raw = raw.reshape(-1, 3)
    eu = np.zeros(n, dtype=np.int32)
    for e in me.edges:
        eu[e.vertices[0]] += 1
        eu[e.vertices[1]] += 1
    fe = defaultdict(int)
    for p in me.polygons:
        for k in p.edge_keys:
            fe[k] += 1
    # merge by position first: the faceted look splits verts, so a naive
    # boundary-edge count reads every split edge as a hole
    rep = {}
    mid = np.empty(n, dtype=np.int64)
    for i, c in enumerate(raw):
        mid[i] = rep.setdefault((round(float(c[0]), 5), round(float(c[1]), 5),
                                 round(float(c[2]), 5)), i)
    mef = defaultdict(int)
    for p in me.polygons:
        vs = [int(mid[v]) for v in p.vertices]
        for i in range(len(vs)):
            a, b = vs[i], vs[(i + 1) % len(vs)]
            mef[(min(a, b), max(a, b))] += 1
    ar = np.array([p.area for p in me.polygons])
    return dict(tris=sum(len(p.vertices) - 2 for p in me.polygons),
                unique_positions=len(set(mid.tolist())),
                loose_verts=int((eu == 0).sum()),
                wire_edges=sum(1 for k, v in fe.items() if v == 0),
                degenerate_faces=int((ar < 1e-9).sum()),
                real_holes=sum(1 for k, v in mef.items() if v == 1),
                nonmanifold=sum(1 for k, v in mef.items() if v > 2),
                custom_normals=me.has_custom_normals)


def fit_and_ground(o, target_len):
    """Scale to a real-world size and set the pack's prop origin convention:
    X/Y centred, Z min = 0 (ground contact), matching Finished Mound."""
    me = o.data
    co = np.empty(len(me.vertices) * 3, dtype=np.float32)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3).astype(np.float64)
    before = [round(float(np.ptp(co[:, i])), 4) for i in range(3)]
    k = target_len / max(np.ptp(co[:, 0]), np.ptp(co[:, 1]), np.ptp(co[:, 2]))
    co *= k
    co[:, 0] -= (co[:, 0].max() + co[:, 0].min()) * 0.5
    co[:, 1] -= (co[:, 1].max() + co[:, 1].min()) * 0.5
    co[:, 2] -= co[:, 2].min()
    me.vertices.foreach_set("co", co.ravel().astype(np.float32))
    me.update()
    o.location = (0.0, 0.0, 0.0)
    o.scale = (1.0, 1.0, 1.0)
    o.rotation_euler = (0.0, 0.0, 0.0)
    after = [round(float(np.ptp(co[:, i])), 4) for i in range(3)]
    return dict(size_before=before, factor=round(float(k), 6), size_after=after,
                z_min=round(float(co[:, 2].min()), 6),
                x_centre=round(float((co[:, 0].max() + co[:, 0].min()) * 0.5), 6),
                y_centre=round(float((co[:, 1].max() + co[:, 1].min()) * 0.5), 6))


def export(o, path):
    scene = bpy.context.scene
    vl = scene.view_layers[0]
    vl.objects.active = o
    win = bpy.data.window_managers[0].windows[0]
    with bpy.context.temp_override(window=win, screen=win.screen, scene=scene,
                                   view_layer=vl, active_object=o, object=o):
        bpy.ops.export_scene.gltf(filepath=path, export_format="GLB",
                                  export_apply=True, export_cameras=False,
                                  export_lights=False, use_selection=False)
    return round(os.path.getsize(path) / 1048576, 2)


def process_rock(stem, newname, target_len, note):
    src = os.path.join(ENV, stem + ".glb")
    scene, o = import_glb(src)
    me = o.data
    o.name = newname.replace(" ", "_")
    me.name = newname.replace(" ", "_")
    geo = geometry_report(me)
    fit = fit_and_ground(o, target_len)
    mat = me.materials[0]
    mat.name = newname.replace(" ", "_") + "_Mat"
    bsdf, base, orm, nrm, nmap = texture_roles(mat)
    nstr_before = round(nmap.inputs["Strength"].default_value, 3)
    nmap.inputs["Strength"].default_value = 0.35
    tex = {}
    tex["base"] = swap_texture(base, 1024, newname.replace(" ", "_") + "_BaseColor", True)
    tex["orm"] = swap_texture(orm, 512, newname.replace(" ", "_") + "_ORM", False)
    tex["normal"] = swap_texture(nrm, 512, newname.replace(" ", "_") + "_Normal", False)
    out = os.path.join(ENV, newname + ".glb")
    mb = export(o, out)
    return dict(new_name=newname, note=note, src_mb=round(os.path.getsize(src)/1048576, 2),
                out_mb=mb, geometry=geo, scale=fit,
                normal_strength=[nstr_before, 0.35], textures=tex)

