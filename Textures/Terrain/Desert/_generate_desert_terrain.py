# Unbound Frontier - desert terrain material library generator
#
# Generates 5 seamless terrain material sets (base color 1024, normal 512,
# roughness 512) tuned to match the approved GLB prop palette.
#
# Palette backbone measured from the 9 approved reference GLBs:
#   warm hue axis, hue angle ~31 deg, R:G:B = 1.00 : 0.83 : 0.65 at sat 0.35
#   props: value 0.20-0.43, sat 0.07-0.43, roughness 0.51-0.66, metallic ~0
# Terrain therefore sits BRIGHTER (value 0.54-0.69) and QUIETER (sat 0.22-0.29)
# than the props, and ROUGHER (0.75-0.87), so props stay readable on top of it.
#
# Seamless tiling is guaranteed by construction: every noise field is produced
# by filtering white noise in the frequency domain (inherently periodic), and
# every Voronoi field uses wrapped cell lookups. Coordinate warps are periodic
# and taken modulo 1, which preserves periodicity.
#
# Noise core note: the spectrum is a POWER LAW, not a gaussian low-pass, and
# grain layers are BAND-passed. A narrow gaussian band has a dominant
# wavelength and produces a visible woven/herringbone beat pattern; a power law
# has no dominant wavelength and reads as natural fractal ground detail.

import os, json, zlib, struct
import numpy as np

N = 1024          # base color resolution
M = 512           # normal / roughness resolution
F = N // M        # downsample factor

OUT = os.path.join(
    r"G:\Game Dev\claude-assets\Unbound Frontier Assets",
    "Textures", "Terrain", "Desert")
QA = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else "."


# ---------------------------------------------------------------- png writer

def write_png(path, arr):
    """Write uint8 array as PNG. (H,W)=gray, (H,W,3)=RGB. No colour management."""
    h, w = arr.shape[:2]
    ctype = 0 if arr.ndim == 2 else (2 if arr.shape[2] == 3 else 6)
    arr = np.ascontiguousarray(arr, dtype=np.uint8)
    rows = bytearray()
    for y in range(h):
        rows += b"\x00"
        rows += arr[y].tobytes()

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(rows), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return os.path.getsize(path)


# ---------------------------------------------------------------- noise core

def _radius(size, sx, sy):
    f = np.fft.fftfreq(size) * size
    FX, FY = np.meshgrid(f, f)
    # sx > 1 weights X frequencies up -> they roll off -> features WIDE in X
    return np.sqrt((FX * sx) ** 2 + (FY * sy) ** 2)


def _apply(rng, size, filt):
    w = rng.standard_normal((size, size))
    out = np.real(np.fft.ifft2(np.fft.fft2(w) * filt))
    s = out.std()
    return out / (s if s > 1e-12 else 1.0)


def pnoise(size, rng, beta=2.4, fhp=2.0, fmax=None, sx=1.0, sy=1.0):
    """Seamless fractal (power-law) noise, unit variance.

    beta  spectral slope; higher = smoother, more low-frequency dominant.
    fhp   soft high-pass; suppresses the single-giant-blob frequencies that
          would tile as an obvious repeated landmark.
    fmax  soft anti-alias rolloff at the top end.
    sx/sy directional stretch; sx>1 elongates features along X.
    """
    fmax = fmax or size / 5.0
    R = _radius(size, sx, sy)
    with np.errstate(divide="ignore", invalid="ignore"):
        amp = 1.0 / (1.0 + (R / 1.0) ** (beta * 0.5))
    amp *= (1.0 - np.exp(-(R / fhp) ** 2))        # kill DC + giant blobs
    amp *= np.exp(-(R / fmax) ** 2)               # anti-alias
    amp[0, 0] = 0.0
    return _apply(rng, size, amp)


def bnoise(size, rng, flo, fhi, sx=1.0, sy=1.0):
    """Seamless band-passed noise, unit variance. Used for grain/grit layers."""
    R = _radius(size, sx, sy)
    amp = (1.0 - np.exp(-(R / flo) ** 2)) * np.exp(-(R / fhi) ** 2)
    amp[0, 0] = 0.0
    return _apply(rng, size, amp)


def snoise(size, rng, freq):
    """Seamless SMOOTH (gaussian low-pass) noise, unit variance.

    Use this for domain warps and broad masks. A power-law field must never be
    used as a domain warp: its high-frequency tail pinches Voronoi cells into
    loops and squiggles instead of gently displacing them.
    """
    R = _radius(size, 1.0, 1.0)
    amp = np.exp(-(R / max(freq, 0.5)) ** 2)
    amp[0, 0] = 0.0
    return _apply(rng, size, amp)


def norm01(a, lo=1.0, hi=99.0):
    l, h = np.percentile(a, lo), np.percentile(a, hi)
    return np.clip((a - l) / (h - l + 1e-12), 0.0, 1.0)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-12), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def voronoi(size, cells, rng, U=None, V=None):
    """Periodic Voronoi. Returns (F1, F2, cell_id); distances in tile units."""
    gx, gy = np.meshgrid(np.arange(cells), np.arange(cells))
    px = (gx + rng.random((cells, cells))) / cells
    py = (gy + rng.random((cells, cells))) / cells
    if U is None:
        u = (np.arange(size) + 0.5) / size
        U, V = np.meshgrid(u, u)
    ci = np.clip((U * cells).astype(np.int64), 0, cells - 1)
    cj = np.clip((V * cells).astype(np.int64), 0, cells - 1)

    F1 = np.full((size, size), 9.0)
    F2 = np.full((size, size), 9.0)
    ID = np.zeros((size, size), dtype=np.int64)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            ax, ay = ci + dx, cj + dy
            ii, jj = ax % cells, ay % cells
            fx = px[jj, ii] + np.where(ax < 0, -1.0, np.where(ax >= cells, 1.0, 0.0))
            fy = py[jj, ii] + np.where(ay < 0, -1.0, np.where(ay >= cells, 1.0, 0.0))
            d = np.sqrt((fx - U) ** 2 + (fy - V) ** 2)
            ID = np.where(d < F1, jj * cells + ii, ID)
            F2 = np.minimum(F2, np.maximum(F1, d))   # must precede F1 update
            F1 = np.minimum(F1, d)
    return F1, F2, ID


def blockavg(a, f):
    if a.ndim == 2:
        h, w = a.shape
        return a.reshape(h // f, f, w // f, f).mean(axis=(1, 3))
    h, w, c = a.shape
    return a.reshape(h // f, f, w // f, f, c).mean(axis=(1, 3))


# ---------------------------------------------------------------- palette

HUE_G = 0.486   # G sits this far along the R->B path (measured from the props)


def warm(V, S):
    """Dusty warm tone on the pack's measured hue axis. Hue angle is constant
    at ~31 deg for any S, so every material shares one hue family."""
    return (V, V * (1.0 - HUE_G * S), V * (1.0 - S))


def ramp(t, stops):
    pos = np.array([s[0] for s in stops], dtype=np.float64)
    col = np.array([s[1] for s in stops], dtype=np.float64)
    out = np.empty(t.shape + (3,))
    for c in range(3):
        out[..., c] = np.interp(t, pos, col[:, c])
    return out


def mix(base, color, mask):
    """Blend a flat colour into an image by a 2D mask."""
    m = mask[..., None]
    return base * (1.0 - m) + np.asarray(color, dtype=np.float64) * m


# ---------------------------------------------------------------- normal map

def height_to_normal(h, target_deg):
    """Tangent-space normal, OpenGL / glTF convention (+Y up).

    Strength is auto-calibrated so the 99th-percentile slope lands on
    target_deg. That keeps intensity comparable across the family and
    deliberately restrained relative to the props.
    """
    dx = (np.roll(h, -1, axis=1) - np.roll(h, 1, axis=1)) * 0.5
    dy = (np.roll(h, -1, axis=0) - np.roll(h, 1, axis=0)) * 0.5
    g = np.sqrt(dx ** 2 + dy ** 2)
    k = np.tan(np.radians(target_deg)) / (np.percentile(g, 99.0) + 1e-12)
    # row index increases downward, so +V is -row, hence ny = +dy
    nx, ny = -dx * k, dy * k
    nz = np.ones_like(h)
    l = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    n = np.stack([nx / l, ny / l, nz / l], axis=-1)
    actual = float(np.degrees(np.arctan(
        np.percentile(np.sqrt(nx ** 2 + ny ** 2), 99.0))))
    return n, actual


# ---------------------------------------------------------------- materials

def m_desert_sand():
    """Primary open-world surface. Dusty warm tan, broad wind variation,
    extremely restrained rippling, sparse grit."""
    rng = np.random.default_rng(20260915)
    broad = norm01(pnoise(N, rng, beta=2.6, fhp=2.2))        # wind drift
    mid = pnoise(N, rng, beta=1.7, fhp=6.0)                  # fractal body
    grain = bnoise(N, rng, 90, 210)                          # sand grain
    ripple = pnoise(N, rng, beta=2.2, fhp=8.0, sx=4.0)       # stretched along X

    grit_n = bnoise(N, rng, 110, 240)
    grit = smoothstep(1.9, 2.8, grit_n)                      # sparse specks

    t = norm01(broad + 0.30 * mid + 0.045 * ripple + 0.055 * grain, 0.5, 99.5)
    col = ramp(t, [
        (0.00, warm(0.550, 0.265)),
        (0.35, warm(0.655, 0.250)),
        (0.70, warm(0.740, 0.230)),
        (1.00, warm(0.815, 0.205)),
    ])
    col = mix(col, warm(0.50, 0.17), 0.30 * grit)            # warm grit, not blue

    h = norm01(0.70 * broad + 0.24 * mid + 0.10 * norm01(ripple)
               + 0.10 * grain + 0.10 * grit)
    rough = 0.865 - 0.030 * (t - 0.5) + 0.018 * grit
    return col, h, rough, 7.0


def m_hardpacked_dirt():
    """Settlements, camps, paths, travelled ground. Darker and browner than
    sand, compacted, faint scuffing, embedded grit, broad worn patches."""
    rng = np.random.default_rng(770231)
    broad = norm01(pnoise(N, rng, beta=2.5, fhp=2.6))
    mid = pnoise(N, rng, beta=1.6, fhp=7.0)
    # mild directional stretch only - no narrow band, so no weave artifact
    scuff = pnoise(N, rng, beta=1.9, fhp=12.0, sx=1.9)
    grain = bnoise(N, rng, 70, 190)
    grit = smoothstep(1.7, 2.7, bnoise(N, rng, 95, 230))
    worn = smoothstep(0.42, 0.96, norm01(pnoise(N, rng, beta=3.0, fhp=2.0)))

    t = norm01(broad + 0.34 * mid + 0.055 * scuff + 0.075 * grain
               + 0.22 * worn, 0.5, 99.5)
    col = ramp(t, [
        (0.00, warm(0.395, 0.320)),
        (0.33, warm(0.475, 0.310)),
        (0.66, warm(0.555, 0.290)),
        (1.00, warm(0.635, 0.260)),
    ])
    col = mix(col, warm(0.44, 0.19), 0.32 * grit)

    h = norm01(0.58 * broad + 0.26 * mid + 0.12 * norm01(scuff)
               + 0.14 * grain + 0.16 * grit + 0.10 * (1.0 - worn))
    rough = 0.820 - 0.055 * worn + 0.028 * grit - 0.020 * (t - 0.5)
    return col, h, rough, 9.0


def m_rocky_desert():
    """Cliffs, rocky regions, ruins, creature areas. Dusty brown/tan soil with
    scattered embedded stone fragments - readable chunks, not gravel mush.

    Stones are kept warm-tinted (sat >= 0.16). Very low saturation reads COOL
    by simultaneous contrast against warm soil and looks like blue-grey dots.
    """
    rng = np.random.default_rng(411907)
    CELLS = 11                                   # fewer, larger, readable
    soil = norm01(pnoise(N, rng, beta=2.4, fhp=2.4))
    mid = pnoise(N, rng, beta=1.6, fhp=7.0)
    grain = bnoise(N, rng, 70, 190)
    broad = norm01(pnoise(N, rng, beta=3.0, fhp=1.9))        # broad rocky zones

    F1, _, ID = voronoi(N, CELLS, rng)
    nc = CELLS * CELLS
    # stone density follows the broad zones, so rocky areas clump naturally
    thresh = rng.random(nc)
    radius = 0.42 + 0.30 * rng.random(nc)
    shade = rng.random(nc)

    d = F1 / (0.5 / CELLS)                       # 1.0 at half cell spacing
    # wobble the outline at the stone-edge scale, but only enough to break the
    # circle. Too much turns rocks into amoeba/camouflage patches.
    wob = norm01(bnoise(N, rng, 40, 100))
    rad = radius[ID] * (0.88 + 0.24 * wob)
    zone = smoothstep(0.30, 0.75, broad)
    present = (thresh[ID] < (0.26 + 0.40 * zone)).astype(np.float64)
    stone = smoothstep(rad, rad * 0.78, d) * present
    # The contact-AO disc MUST be gated by `present` too. Ungated, every cell
    # that was chosen NOT to hold a stone still leaves a solid darkened disc,
    # which reads as a dark stain the exact size and shape of a missing stone.
    disc = smoothstep(rad * 1.16, rad, d) * present
    ring = (disc - stone).clip(0.0, 1.0)                             # contact AO

    SOIL_V = [0.465, 0.555, 0.635, 0.705]
    SOIL_S = [0.285, 0.265, 0.250, 0.225]
    SOIL_T = [0.00, 0.40, 0.75, 1.00]
    t = norm01(0.66 * soil + 0.34 * broad + 0.22 * mid + 0.07 * grain, 0.5, 99.5)
    col = ramp(t, list(zip(SOIL_T, [warm(v, s) for v, s in zip(SOIL_V, SOIL_S)])))

    # Pale grey-brown stone, derived RELATIVE to the local soil tone rather
    # than as an absolute value. The soil varies broadly across the tile, so an
    # absolute mid-tone stone lands darker than bright soil and reads as a
    # stain instead of rock. Anchoring to local soil keeps every stone
    # consistently a little lighter and greyer than whatever it sits in.
    v_soil = np.interp(t, SOIL_T, SOIL_V)
    lift = 1.00 + 0.20 * shade[ID]            # never darker than its own soil
    v_st = np.clip(v_soil * lift, 0.0, 0.74)
    s_st = 0.165 + 0.060 * shade[ID]                   # always greyer
    mott = norm01(bnoise(N, rng, 26, 80))              # within-stone mottling
    v_st = v_st * (0.90 + 0.13 * mott + 0.05 * norm01(grain))
    scol = np.stack([v_st,
                     v_st * (1.0 - HUE_G * s_st),
                     v_st * (1.0 - s_st)], axis=-1)
    col = col * (1 - (stone * 0.94)[..., None]) + scol * (stone * 0.94)[..., None]
    col = col * (1.0 - 0.20 * ring[..., None])              # embed the stones

    dome = np.sqrt(np.clip(1.0 - (d / np.maximum(rad, 1e-6)) ** 2, 0.0, 1.0))
    h = norm01(0.42 * t + 0.10 * grain + 0.48 * (dome * stone) - 0.10 * ring)
    rough = 0.880 - 0.020 * (t - 0.5) - 0.150 * stone + 0.020 * ring
    return col, h, rough, 16.0


def m_cracked_earth():
    """Dried basins, lairs, environmental storytelling. Pale dusty earth with
    broad readable crack plates, not dense micro-cracking."""
    rng = np.random.default_rng(88541)
    u = (np.arange(N) + 0.5) / N
    U, V = np.meshgrid(u, u)
    # Periodic coordinate warp -> irregular non-polygonal plates, still tiles.
    # Must be SMOOTH noise and modest relative to cell size (~14% of 1/7),
    # otherwise the cells pinch into squiggly loops instead of shifting.
    Uw = (U + 0.020 * snoise(N, rng, 3.0)) % 1.0
    Vw = (V + 0.020 * snoise(N, rng, 3.0)) % 1.0
    wj = 0.70 + 0.55 * norm01(snoise(N, rng, 5.0))            # width jitter

    A1, A2, _ = voronoi(N, 7, rng, Uw, Vw)       # primary large plates
    c1 = 1.0 - smoothstep(0.0, 0.0100 * wj, A2 - A1)
    B1, B2, _ = voronoi(N, 15, rng, Uw, Vw)      # secondary, clearly subordinate
    c2 = 1.0 - smoothstep(0.0, 0.0038 * wj, B2 - B1)
    crack = np.clip(c1 + 0.30 * c2 * (1.0 - c1), 0.0, 1.0)
    dish = smoothstep(0.0, 0.055, A2 - A1)       # plates curl up away from cracks

    plate = norm01(pnoise(N, rng, beta=2.5, fhp=2.4))
    mid = pnoise(N, rng, beta=1.6, fhp=7.0)
    dust = bnoise(N, rng, 60, 180)

    t = norm01(plate + 0.30 * mid + 0.060 * dust + 0.10 * dish, 0.5, 99.5)
    col = ramp(t, [
        (0.00, warm(0.595, 0.235)),
        (0.40, warm(0.680, 0.220)),
        (0.75, warm(0.750, 0.208)),
        (1.00, warm(0.810, 0.190)),
    ])
    col = mix(col, warm(0.225, 0.305), crack * 0.88)   # shadowed crack interior

    h = norm01(0.36 * t + 0.10 * dust + 0.54 * dish)
    rough = 0.845 - 0.015 * (t - 0.5) + 0.055 * crack
    return col, h, rough, 14.0


def m_frontier_path():
    """Roads, settlement paths, checkpoint approaches. Dusty muted brown/tan,
    compacted and smoother, faint travel-direction wear, no baked tracks."""
    rng = np.random.default_rng(6120884)
    broad = norm01(pnoise(N, rng, beta=2.5, fhp=2.8))
    mid = pnoise(N, rng, beta=1.7, fhp=8.0)
    # gentle stretch only; keeps a travel-direction read without smearing
    wear = pnoise(N, rng, beta=2.0, fhp=10.0, sx=2.6)
    grain = bnoise(N, rng, 80, 200)
    grit = smoothstep(2.0, 2.9, bnoise(N, rng, 100, 235))
    buildup = smoothstep(0.38, 0.96, norm01(pnoise(N, rng, beta=3.0, fhp=2.2)))

    t = norm01(broad + 0.32 * mid + 0.040 * wear + 0.050 * grain
               - 0.18 * buildup, 0.5, 99.5)
    col = ramp(t, [
        (0.00, warm(0.490, 0.260)),
        (0.35, warm(0.560, 0.252)),
        (0.70, warm(0.622, 0.240)),
        (1.00, warm(0.685, 0.220)),
    ])
    col = mix(col, warm(0.46, 0.18), 0.25 * grit)

    h = norm01(0.60 * broad + 0.22 * mid + 0.10 * norm01(wear)
               + 0.10 * grain + 0.16 * buildup + 0.08 * grit)
    rough = 0.745 + 0.050 * buildup + 0.025 * grit - 0.020 * (t - 0.5)
    return col, h, rough, 6.0


MATERIALS = [
    ("Terrain_DesertSand",     m_desert_sand,     20260915,
     "Primary open-world desert surface"),
    ("Terrain_HardpackedDirt", m_hardpacked_dirt, 770231,
     "Settlements, camps, frequently travelled ground"),
    ("Terrain_RockyDesert",    m_rocky_desert,    411907,
     "Cliffs, rocky regions, ruins, creature areas"),
    ("Terrain_CrackedEarth",   m_cracked_earth,   88541,
     "Dried basins, lairs, environmental storytelling"),
    ("Terrain_FrontierPath",   m_frontier_path,   6120884,
     "Roads, settlement paths, checkpoint approaches"),
]


# ---------------------------------------------------------------- driver

def main(qa_dir=None):
    qa_dir = qa_dir or QA
    os.makedirs(OUT, exist_ok=True)
    summary, tiles, crops = {}, [], []

    for name, fn, seed, use in MATERIALS:
        col, h, rough, deg = fn()
        col = np.clip(col, 0.0, 1.0)

        bc = np.rint(col * 255.0).astype(np.uint8)
        p_bc = os.path.join(OUT, name + "_BaseColor_1k.png")
        s_bc = write_png(p_bc, bc)

        # downsample height to 512 first so the normal does not alias
        h512 = blockavg(norm01(h, 0.2, 99.8), F)
        n, actual = height_to_normal(h512, deg)
        p_nm = os.path.join(OUT, name + "_Normal_512.png")
        s_nm = write_png(p_nm, np.rint((n * 0.5 + 0.5) * 255.0).astype(np.uint8))

        r512 = np.clip(blockavg(rough, F), 0.0, 1.0)
        p_rg = os.path.join(OUT, name + "_Roughness_512.png")
        s_rg = write_png(p_rg, np.rint(r512 * 255.0).astype(np.uint8))

        mx, mn = col.max(axis=2), col.min(axis=2)
        sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
        # seam proof: wrap-edge step must be no worse than a typical interior step
        seam_x = float(np.abs(col[:, 0] - col[:, -1]).mean())
        seam_y = float(np.abs(col[0, :] - col[-1, :]).mean())
        interior = float(np.abs(np.diff(col, axis=1)).mean())

        summary[name] = dict(
            use=use, seed=seed,
            files=[os.path.basename(p_bc), os.path.basename(p_nm),
                   os.path.basename(p_rg)],
            kb=[round(s_bc / 1024), round(s_nm / 1024), round(s_rg / 1024)],
            mean255=[round(float(col[..., c].mean() * 255), 1) for c in range(3)],
            val_mean=round(float(mx.mean()), 3),
            val_p10=round(float(np.percentile(mx, 10)), 3),
            val_p90=round(float(np.percentile(mx, 90)), 3),
            sat_mean=round(float(sat.mean()), 3),
            sat_p90=round(float(np.percentile(sat, 90)), 3),
            rough_mean=round(float(r512.mean()), 3),
            rough_p10=round(float(np.percentile(r512, 10)), 3),
            rough_p90=round(float(np.percentile(r512, 90)), 3),
            normal_p99_deg=round(actual, 2),
            seam_ok=bool(max(seam_x, seam_y) <= interior * 1.35),
            seam=dict(x=round(seam_x, 5), y=round(seam_y, 5),
                      interior=round(interior, 5)),
        )
        tiles.append(blockavg(col, 4))          # 256 thumb, for 2x2 tile check
        crops.append(col[:512, :512])           # 1:1 crop, for detail check

    def sheet(imgs, cell, path, tile2x2):
        out = np.ones((cell * 2, cell * 3, 3))
        for i, p in enumerate(imgs):
            if tile2x2:
                p = np.concatenate([np.concatenate([p, p], 1)] * 2, 0)
            r, c = divmod(i, 3)
            out[r * cell:(r + 1) * cell, c * cell:(c + 1) * cell] = p
        write_png(path, np.rint(np.clip(out, 0, 1) * 255).astype(np.uint8))
        return path

    summary["_qa_tiled"] = sheet(tiles, 512, os.path.join(
        qa_dir, "qa_tiled.png"), True)
    summary["_qa_detail"] = sheet(crops, 512, os.path.join(
        qa_dir, "qa_detail.png"), False)
    summary["_out_dir"] = OUT
    return summary


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
