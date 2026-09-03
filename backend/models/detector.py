from PIL import Image


def predict(image: Image.Image) -> dict:
    image = image.convert("RGB")
    w, h = image.size
    pixels = list(image.getdata())
    sample = pixels[::max(1, len(pixels) // 1000)]
    r_avg = sum(p[0] for p in sample) / len(sample)
    g_avg = sum(p[1] for p in sample) / len(sample)
    b_avg = sum(p[2] for p in sample) / len(sample)

    diff = abs(r_avg - g_avg) + abs(g_avg - b_avg) + abs(r_avg - b_avg)
    ai_score = round(min(max((diff / 60) * 100, 20), 95), 2)
    real_score = round(100 - ai_score, 2)

    is_ai = ai_score > real_score
    verdict = "AI Generated" if is_ai else "Real Image"
    top_score = max(ai_score, real_score)

    if top_score >= 80:
        confidence = "HIGH"
    elif top_score >= 55:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "verdict": verdict,
        "ai_score": ai_score,
        "real_score": real_score,
        "confidence": confidence,
        "is_ai": is_ai,
    }
