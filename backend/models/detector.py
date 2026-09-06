import os
import uuid
import base64
import re
import requests
from PIL import Image
import io
import json
import numpy as np

HIVE_API_URL = "https://api.hivemoderation.com/api/v2/task/sync"
HIVE_API_KEY = os.environ.get("HIVE_API_KEY", "")
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_images")
os.makedirs(TEMP_DIR, exist_ok=True)


def predict(image: Image.Image) -> dict:
    results = []
    errors = []

    # Try Hive first
    if HIVE_API_KEY:
        try:
            hive_result = _predict_hive(image)
            hive_result["model"] = "Hive AI Detection"
            results.append(hive_result)
        except Exception as e:
            errors.append(f"Hive: {e}")
            print(f"Hive API failed: {e}")

    # Try NVIDIA second
    if NVIDIA_API_KEY:
        try:
            nvidia_result = _predict_nvidia(image)
            nvidia_result["model"] = "NVIDIA Vision (kimi-k3)"
            results.append(nvidia_result)
        except Exception as e:
            errors.append(f"NVIDIA: {e}")
            print(f"NVIDIA API failed: {e}")

    # If we have results from multiple models, combine them
    if len(results) >= 2:
        return _combine_results(results)
    elif len(results) == 1:
        return results[0]
    else:
        # Fallback to heuristic
        print(f"All APIs failed, using heuristic. Errors: {errors}")
        return _predict_heuristic(image)


def _combine_results(results: list) -> dict:
    """Combine results from multiple models for higher confidence."""
    avg_ai = sum(r["ai_score"] for r in results) / len(results)
    avg_real = sum(r["real_score"] for r in results) / len(results)

    # Check if models agree
    all_agree = all(r["is_ai"] for r in results) or all(not r["is_ai"] for r in results)

    if all_agree:
        confidence_boost = 10
    else:
        confidence_boost = -10

    ai_score = round(min(100, max(0, avg_ai + confidence_boost)), 1)
    real_score = round(100 - ai_score, 1)
    is_ai = ai_score > 50

    if max(ai_score, real_score) >= 85:
        confidence = "HIGH"
    elif max(ai_score, real_score) >= 65:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    # Merge sources and generators
    all_sources = []
    all_generators = {}
    for r in results:
        if r.get("source"):
            all_sources.append(r["source"])
        if r.get("generators"):
            for gen, score in r["generators"].items():
                all_generators[gen] = max(all_generators.get(gen, 0), score)

    result = {
        "verdict": "AI Generated" if is_ai else "Real Image",
        "ai_score": ai_score,
        "real_score": real_score,
        "confidence": confidence,
        "is_ai": is_ai,
        "model": "Ensemble (" + " + ".join(r["model"] for r in results) + ")",
        "models_used": len(results),
        "models_agree": all_agree,
    }

    if all_sources:
        result["source"] = all_sources[0]
    if all_generators:
        result["generators"] = all_generators

    return result


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
        }

        if source and source != "unknown":
            result["source"] = source.replace("_", " ").title()
            result["generators"] = generators

        return result

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


def _predict_nvidia(image: Image.Image) -> dict:
    """Use NVIDIA Vision model (kimi-k3) to detect AI-generated images."""
    try:
        from langchain_nvidia_ai_endpoints import ChatNVIDIA
    except ImportError:
        raise Exception("langchain_nvidia_ai_endpoints not installed")

    client = ChatNVIDIA(
        model="moonshotai/kimi-k3",
        api_key=NVIDIA_API_KEY,
        temperature=0.1,
        max_completion_tokens=1024,
    )

    # Convert image to base64
    image = image.convert("RGB")
    if image.size[0] > 512 or image.size[1] > 512:
        image.thumbnail((512, 512), Image.LANCZOS)

    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=85)
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """Analyze this image and determine if it is AI-generated or a real photograph.

Respond with ONLY a JSON object in this exact format:
{"is_ai": true/false, "confidence": 0.0-1.0, "reason": "brief explanation"}

Examples:
{"is_ai": true, "confidence": 0.95, "reason": "Perfect symmetry, unnatural skin texture, no noise patterns"}
{"is_ai": false, "confidence": 0.88, "reason": "Natural noise, realistic lighting, visible compression artifacts"}

Do NOT include any text before or after the JSON.""",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_b64}",
                    },
                },
            ],
        }
    ]

    response = client.invoke(messages)
    text = response.content.strip()

    # Try to extract JSON from response
    json_match = re.search(r'\{[^}]+\}', text)
    if not json_match:
        raise Exception(f"No JSON in NVIDIA response: {text[:200]}")

    data = json.loads(json_match.group())

    is_ai = data.get("is_ai", False)
    nvidia_conf = data.get("confidence", 0.5) * 100

    if is_ai:
        ai_score = round(nvidia_conf, 1)
        real_score = round(100 - nvidia_conf, 1)
    else:
        real_score = round(nvidia_conf, 1)
        ai_score = round(100 - nvidia_conf, 1)

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
    }


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
