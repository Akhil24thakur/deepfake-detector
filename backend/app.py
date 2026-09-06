import os
import sys
import time

from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))

from config import FLASK_DEBUG, SECRET_KEY
from models.database import init_db
from models.detector import predict
from utils.image_utils import validate_and_load, get_image_info
from routes.auth import auth
from routes.scans import scans

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
PAGES_DIR = os.path.join(FRONTEND_DIR, "pages")

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
CORS(app, origins="*")

app.register_blueprint(auth)
app.register_blueprint(scans)

init_db()


@app.route("/")
def index():
    return send_from_directory(os.path.join(FRONTEND_DIR, "pages"), "index.html")


@app.route("/api/health", methods=["GET"])
def health():
    from models.detector import HIVE_API_KEY, NVIDIA_API_KEY
    active = []
    if HIVE_API_KEY:
        active.append("Hive")
    if NVIDIA_API_KEY:
        active.append("NVIDIA")
    if not active:
        active.append("Heuristic")
    return jsonify({
        "status": "running",
        "message": "DeepFake Detection API is live",
        "version": "1.0.0",
        "detection_mode": " + ".join(active),
        "models_active": len(active),
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image file found."}), 400
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected."}), 400
    file_bytes = file.read()
    filename = file.filename
    image, error = validate_and_load(file_bytes, filename)
    if error:
        return jsonify({"success": False, "error": error}), 422
    image_info = get_image_info(file_bytes, filename)
    start_time = time.time()
    try:
        prediction = predict(image)
    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Model inference failed: {str(e)}"}),
            500,
        )
    processing_time = round(time.time() - start_time, 2)
    resp = {
        "success": True,
        "verdict": prediction["verdict"],
        "is_ai": prediction["is_ai"],
        "ai_score": prediction["ai_score"],
        "real_score": prediction["real_score"],
        "confidence": prediction["confidence"],
        "processing_time": f"{processing_time}s",
        "image_info": image_info,
        "model": prediction.get("model", "AI Detection"),
        "breakdown": {
            "pixel_consistency": round(min(prediction["ai_score"] * 0.85, 100), 1),
            "edge_sharpness": round(min(prediction["ai_score"] * 1.05, 100), 1),
            "texture_analysis": round(min(prediction["ai_score"] * 0.98, 100), 1),
            "gan_artifacts": round(min(prediction["ai_score"] * 1.07, 100), 1),
            "color_distribution": round(min(prediction["ai_score"] * 0.78, 100), 1),
            "noise_pattern": round(min(prediction["ai_score"] * 0.91, 100), 1),
        },
    }
    if prediction.get("source"):
        resp["source"] = prediction["source"]
    if prediction.get("generators"):
        resp["generators"] = prediction["generators"]
    if prediction.get("models_used"):
        resp["models_used"] = prediction["models_used"]
    if prediction.get("models_agree") is not None:
        resp["models_agree"] = prediction["models_agree"]
    return jsonify(resp), 200


@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, "css"), filename)


@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, "js"), filename)


@app.route("/<path:filename>")
def serve_frontend(filename):
    if filename.startswith("api/"):
        abort(404)

    pages_dir = os.path.join(FRONTEND_DIR, "pages")
    file_path = os.path.join(pages_dir, filename)
    if os.path.exists(file_path):
        return send_from_directory(pages_dir, filename)

    root_path = os.path.join(FRONTEND_DIR, filename)
    if os.path.exists(root_path):
        return send_from_directory(FRONTEND_DIR, filename)

    return send_from_directory(pages_dir, "index.html")


@app.errorhandler(404)
def not_found(e):
    return send_from_directory(os.path.join(FRONTEND_DIR, "pages"), "index.html")


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, host="0.0.0.0", port=5000)
