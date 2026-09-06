import os
import uuid
import base64
import requests
from PIL import Image
import io
import json
import numpy as np

HIVE_API_URL = "https://api.hivemoderation.com/api/v2/task/sync"
HIVE_API_KEY = os.environ.get("HIVE_API_KEY", "")
TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_images")
os.makedirs(TEMP_DIR, exist_ok=True)

HEAVY_ENABLED = False


def predict(image: Image.Image) -> dict:
    if HIVE_API_KEY:
        try:
            return _predict_hive(image)
        except Exception as e:
            print(f"Hive API failed, falling back to heuristic: {e}")

    return _predict_heuristic(image)


def _predict_hive(image: Image.Image) -> dict:
    image = image.convert("RGB")
    if image.size[0] > 1024 or image.size[1] > 1024:
        image.thumbnail((1024, 1024), Image.LANCZOS)

    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(TEMP_DIR, filename)
    image.save(filepath, "JPEG", quality=90)

    try:
        with open(filepath, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()

        payload = {
            "url": f"data:image/jpeg;base64,{img_b64}",
            "models": ["ai_generated_media"],
            "user_id": "deepfake-detector-app",
            "post_id": f"scan-{uuid.uuid4().hex[:8]}",
        }

        headers = {
            "Authorization": f"token {HIVE_API_KEY}",
            "Content-Type": "application/json",
        }

        resp = requests.post(HIVE_API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        task_id = data.get("task_ids", [None])[0]
        if not task_id:
            raise Exception("No task_id in response")

        results_resp = requests.get(
            f"https://api.hivemoderation.com/api/v2/task/{task_id}",
            headers=headers,
            timeout=30,
        )
        results_resp.raise_for_status()
        results = results_resp.json()

        classes = results.get("status", [{}])[0].get("status", {}).get("response", {}).get("output", [{}])[0].get("classes", [])

        if not classes:
            raise Exception("No classes in response")

        ai_prob = 0.0
        not_ai_prob = 0.0
        source = "unknown"

        generators = {}
        for c in classes:
            name = c.get("class", "")
            score = c.get("score", 0)
            if name == "ai_generated":
                ai_prob = score
            elif name == "not_ai_generated":
                not_ai_prob = score
            elif name not in ("deepfake", "inconclusive", "inconclusive_video", "none") and score > 0.01:
                generators[name] = round(score * 100, 1)

        if generators:
            source = max(generators, key=generators.get)

        ai_score = round(ai_prob * 100, 1)
        real_score = round(not_ai_prob * 100, 1)
        is_ai = ai_prob > not_ai_prob

        if max(ai_score, real_score) >= 80:
            confidence = "HIGH"
        elif max(ai_score, real_score) >= 60:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        verdict = "AI Generated" if is_ai else "Real Image"

        result = {
            "verdict": verdict,
            "ai_score": ai_score,
            "real_score": real_score,
            "confidence": confidence,
            "is_ai": is_ai,
            "model": "Hive AI Detection",
        }

        if source and source != "unknown":
            result["source"] = source.replace("_", " ").title()
            result["generators"] = generators

        return result

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


def _predict_heuristic(image: Image.Image) -> dict:
    image = image.convert("RGB")
    if image.size[0] > 512 or image.size[1] > 512:
        image.thumbnail((512, 512), Image.LANCZOS)

    arr = np.array(image, dtype=np.float64)
    gray = np.mean(arr, axis=2)
    h, w = gray.shape

    if h < 3 or w < 3:
        return _fallback_result(50.0)

    laplacian = (
        gray[1:-1, 1:-1] * 4
        - gray[:-2, 1:-1] - gray[2:, 1:-1]
        - gray[1:-1, :-2] - gray[1:-1, 2:]
    )
    noise_var = float(np.var(laplacian))

    r = arr[:, :, 0].flatten()
    g = arr[:, :, 1].flatten()
    b = arr[:, :, 2].flatten()
    r_std, g_std, b_std = float(np.std(r)), float(np.std(g)), float(np.std(b))

    sample_n = min(5000, len(r))
    idx = np.random.choice(len(r), sample_n, replace=False)
    rg_corr = abs(float(np.corrcoef(r[idx], g[idx])[0, 1])) if r_std > 1e-6 and g_std > 1e-6 else 0.5
    gb_corr = abs(float(np.corrcoef(g[idx], b[idx])[0, 1])) if g_std > 1e-6 and b_std > 1e-6 else 0.5
    rb_corr = abs(float(np.corrcoef(r[idx], b[idx])[0, 1])) if r_std > 1e-6 and b_std > 1e-6 else 0.5
    avg_corr = (rg_corr + gb_corr + rb_corr) / 3

    max_c = np.maximum(np.maximum(arr[:, :, 0], arr[:, :, 1]), arr[:, :, 2])
    min_c = np.minimum(np.minimum(arr[:, :, 0], arr[:, :, 1]), arr[:, :, 2])
    mask = max_c > 0
    sat = np.zeros_like(max_c)
    sat[mask] = (max_c[mask] - min_c[mask]) / max_c[mask]
    sat_std = float(np.std(sat))

    score = 50.0

    if noise_var < 20:
        score += 15
    elif noise_var > 500:
        score -= 15

    if avg_corr > 0.92:
        score += 10
    elif avg_corr < 0.6:
        score -= 10

    if sat_std < 0.05:
        score += 10
    elif sat_std > 0.2:
        score -= 10

    if h >= 8 and w >= 8:
        block_size = min(h, w) // 4
        blocks = []
        for i in range(0, h - block_size + 1, block_size):
            for j in range(0, w - block_size + 1, block_size):
                block = gray[i:i+block_size, j:j+block_size]
                blocks.append(float(np.std(block)))
        if blocks:
            block_std = np.std(blocks)
            if block_std < 5:
                score += 8
            elif block_std > 30:
                score -= 8

    half = w // 2
    if half > 4:
        left = gray[:, :half]
        right = np.fliplr(gray[:, half:half+left.shape[1]])
        min_h = min(left.shape[0], right.shape[0])
        min_w = min(left.shape[1], right.shape[1])
        symmetry = 1.0 - float(np.mean(np.abs(left[:min_h, :min_w] - right[:min_h, :min_w]))) / 128.0
        if symmetry > 0.9:
            score += 12
        elif symmetry > 0.8:
            score += 6

    score = max(5, min(95, score))

    return _fallback_result(score)


def _fallback_result(score):
    ai_score = round(score, 1)
    real_score = round(100 - score, 1)
    is_ai = ai_score > 50

    if max(ai_score, real_score) >= 80:
        confidence = "HIGH"
    elif max(ai_score, real_score) >= 60:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "verdict": "AI Generated" if is_ai else "Real Image",
        "ai_score": ai_score,
        "real_score": real_score,
        "confidence": confidence,
        "is_ai": is_ai,
        "model": "Heuristic Analysis",
    }
