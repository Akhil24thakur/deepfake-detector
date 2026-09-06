import numpy as np
from PIL import Image, ImageFilter
import math


def predict(image: Image.Image) -> dict:
    image = image.convert("RGB")
    w, h = image.size
    if w > 512 or h > 512:
        image.thumbnail((512, 512), Image.LANCZOS)

    arr = np.array(image, dtype=np.float64)

    scores = []

    # 1. Noise pattern analysis — real cameras have sensor noise, AI images are often too clean
    noise_score = _noise_analysis(arr)
    scores.append(("noise", noise_score))

    # 2. Frequency analysis — AI images often lack high-frequency detail
    freq_score = _frequency_analysis(arr)
    scores.append(("frequency", freq_score))

    # 3. Texture smoothness — AI skin/surfaces are often unnaturally smooth
    texture_score = _texture_analysis(image)
    scores.append(("texture", texture_score))

    # 4. Color channel correlation — AI images may have unnatural channel correlations
    color_score = _color_correlation(arr)
    scores.append(("color", color_score))

    # 5. Edge consistency — AI edges can be too perfect or inconsistent
    edge_score = _edge_analysis(image)
    scores.append(("edge", edge_score))

    # 6. Saturation & contrast anomalies
    sat_score = _saturation_analysis(arr)
    scores.append(("saturation", sat_score))

    # Weighted average of all scores
    weights = [0.18, 0.22, 0.18, 0.15, 0.15, 0.12]
    ai_score = sum(s * w for s, (_, w) in zip(
        [s[1] for s in scores],
        [("noise", weights[0]), ("frequency", weights[1]),
         ("texture", weights[2]), ("color", weights[3]),
         ("edge", weights[4]), ("saturation", weights[5])]
    ))

    # Recalculate properly
    ai_score = (
        noise_score * weights[0] +
        freq_score * weights[1] +
        texture_score * weights[2] +
        color_score * weights[3] +
        edge_score * weights[4] +
        sat_score * weights[5]
    )

    ai_score = round(min(max(ai_score, 5), 95), 1)
    real_score = round(100 - ai_score, 1)
    is_ai = ai_score > 50

    if ai_score > 70:
        confidence = "HIGH"
    elif ai_score > 55:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    verdict = "AI Generated" if is_ai else "Real Image"

    return {
        "verdict": verdict,
        "ai_score": ai_score,
        "real_score": real_score,
        "confidence": confidence,
        "is_ai": is_ai,
    }


def _noise_analysis(arr):
    """Real images have sensor noise; AI images are often too clean."""
    gray = np.mean(arr, axis=2)
    h, w = gray.shape
    if h < 3 or w < 3:
        return 50.0

    laplacian = (
        gray[1:-1, 1:-1] * 4
        - gray[:-2, 1:-1]
        - gray[2:, 1:-1]
        - gray[1:-1, :-2]
        - gray[1:-1, 2:]
    )
    noise_var = np.var(laplacian)

    if noise_var < 20:
        return 80
    elif noise_var < 80:
        return 65
    elif noise_var < 200:
        return 45
    elif noise_var < 500:
        return 30
    else:
        return 15


def _frequency_analysis(arr):
    """AI images often lack high-frequency detail."""
    gray = np.mean(arr, axis=2).astype(np.float64)
    h, w = gray.shape

    rows = min(h, 512)
    cols = min(w, 512)
    patch = gray[:rows, :cols]

    row_fft = np.abs(np.fft.rfft(patch, axis=0))
    col_fft = np.abs(np.fft.rfft(patch, axis=1))

    row_spectrum = np.mean(row_fft, axis=1)
    col_spectrum = np.mean(col_fft, axis=0)

    n = min(len(row_spectrum), 20)
    if n < 3:
        return 50.0

    high_freq_row = np.mean(row_spectrum[n // 2:n])
    low_freq_row = np.mean(row_spectrum[:n // 2] + 1e-10)
    row_ratio = high_freq_row / low_freq_row

    high_freq_col = np.mean(col_fft[:rows // 2, n // 2:n])
    low_freq_col = np.mean(col_fft[:rows // 2, :n // 2] + 1e-10)
    col_ratio = high_freq_col / low_freq_col

    avg_ratio = (row_ratio + col_ratio) / 2

    if avg_ratio > 0.5:
        return 25
    elif avg_ratio > 0.3:
        return 40
    elif avg_ratio > 0.15:
        return 60
    elif avg_ratio > 0.05:
        return 75
    else:
        return 85


def _texture_analysis(pil_image):
    """AI images often have unnatural smoothness or repetitive textures."""
    gray = pil_image.convert("L")
    gray = gray.resize((256, 256))
    arr = np.array(gray, dtype=np.float64)

    h, w = arr.shape
    if h < 3 or w < 3:
        return 50.0

    laplacian = (
        arr[1:-1, 1:-1] * 4
        - arr[:-2, 1:-1]
        - arr[2:, 1:-1]
        - arr[1:-1, :-2]
        - arr[1:-1, 2:]
    )

    edge_density = np.sum(np.abs(laplacian) > 30) / laplacian.size
    texture_var = np.var(arr)

    if texture_var < 300 and edge_density < 0.05:
        return 80
    elif texture_var < 800 and edge_density < 0.1:
        return 65
    elif texture_var < 1500:
        return 45
    elif texture_var < 3000:
        return 30
    else:
        return 20


def _color_correlation(arr):
    """AI images may have unnatural RGB channel correlations."""
    r = arr[:, :, 0].flatten()
    g = arr[:, :, 1].flatten()
    b = arr[:, :, 2].flatten()

    r_std = np.std(r)
    g_std = np.std(g)
    b_std = np.std(b)

    if r_std < 1e-6 or g_std < 1e-6 or b_std < 1e-6:
        return 50.0

    sample_size = min(5000, len(r))
    idx = np.random.choice(len(r), sample_size, replace=False)
    r_s, g_s, b_s = r[idx], g[idx], b[idx]

    rg_corr = abs(np.corrcoef(r_s, g_s)[0, 1])
    gb_corr = abs(np.corrcoef(g_s, b_s)[0, 1])
    rb_corr = abs(np.corrcoef(r_s, b_s)[0, 1])
    avg_corr = (rg_corr + gb_corr + rb_corr) / 3

    if avg_corr > 0.95:
        return 75
    elif avg_corr > 0.85:
        return 60
    elif avg_corr > 0.7:
        return 40
    else:
        return 25


def _edge_analysis(pil_image):
    """AI edges can be too perfect or have inconsistent sharpness."""
    gray = pil_image.convert("L")
    gray = gray.resize((256, 256))
    edges = gray.filter(ImageFilter.FIND_EDGES)
    arr = np.array(edges, dtype=np.float64)

    edge_mean = np.mean(arr)
    edge_std = np.std(arr)

    if edge_std < 15:
        return 75
    elif edge_std < 25:
        return 60
    elif edge_std < 40:
        return 40
    else:
        return 25


def _saturation_analysis(arr):
    """AI images may have unnatural saturation patterns."""
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    max_c = np.maximum(np.maximum(r, g), b)
    min_c = np.minimum(np.minimum(r, g), b)

    mask = max_c > 0
    saturation = np.zeros_like(max_c)
    saturation[mask] = (max_c[mask] - min_c[mask]) / max_c[mask]

    sat_mean = np.mean(saturation)
    sat_std = np.std(saturation)

    if sat_std < 0.05 and sat_mean > 0.3:
        return 75
    elif sat_std < 0.1:
        return 55
    elif sat_std < 0.15:
        return 40
    else:
        return 25
