from flask import Blueprint, request, jsonify

from models.database import query
from datetime import date

scans = Blueprint("scans", __name__)


@scans.route("/api/scan/save", methods=["POST"])
def save_scan():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data"}), 400

    user_id = data.get("user_id")
    verdict = data.get("verdict")
    ai_score = data.get("ai_score", 0)
    real_score = data.get("real_score", 0)
    confidence = data.get("confidence", "MEDIUM")
    model_used = data.get("model_used", "CNN v2.1")
    processing_time = data.get("processing_time", "")
    status = data.get("status", "completed")
    error_message = data.get("error_message", "")

    if not user_id or not verdict:
        return {"success": False, "error": "user_id and verdict required"}, 400

    user = query("SELECT * FROM users WHERE id = %s", (user_id,), fetch="one")
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    today = str(date.today())
    limit = 4 if user["plan"] == "free" else 20

    last_date = str(user["last_scan_date"]) if user["last_scan_date"] else ""
    if last_date != today:
        query(
            "UPDATE users SET scans_today = 0, last_scan_date = %s WHERE id = %s",
            (today, user_id),
        )
        current_scans = 0
    else:
        current_scans = user["scans_today"]

    if current_scans >= limit:
        return jsonify({
            "success": False,
            "error": f"Daily scan limit reached ({limit}/day). Upgrade to premium for more scans.",
            "limit_reached": True,
            "scans_today": current_scans,
            "limit": limit,
        }), 429

    scan_id = query(
        """INSERT INTO scan_history
           (user_id, verdict, ai_score, real_score, confidence, model_used, processing_time, status, error_message)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (user_id, verdict, ai_score, real_score, confidence, model_used, processing_time, status, error_message),
    )

    query(
        "UPDATE users SET scans_today = scans_today + 1, total_scans = total_scans + 1, last_scan_date = %s WHERE id = %s",
        (today, user_id),
    )

    return jsonify({
        "success": True,
        "scan_id": scan_id,
        "scans_today": current_scans + 1,
        "limit": limit,
    }), 200


@scans.route("/api/scan/history/<int:user_id>", methods=["GET"])
def get_history(user_id):
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    offset = (page - 1) * limit

    total_row = query(
        "SELECT COUNT(*) as total FROM scan_history WHERE user_id = %s",
        (user_id,),
        fetch="one",
    )
    total = total_row["total"] if total_row else 0

    history = query(
        """SELECT id, verdict, ai_score, real_score, confidence,
                  model_used, processing_time, status, error_message, scanned_at
           FROM scan_history
           WHERE user_id = %s
           ORDER BY scanned_at DESC
           LIMIT %s OFFSET %s""",
        (user_id, limit, offset),
        fetch=True,
    )

    if history:
        for row in history:
            if row.get("scanned_at"):
                row["scanned_at"] = str(row["scanned_at"])

    return jsonify({
        "success": True,
        "history": history or [],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }), 200


@scans.route("/api/scan/stats/<int:user_id>", methods=["GET"])
def get_stats(user_id):
    stats = query(
        """SELECT
             COUNT(*) as total_scans,
             SUM(CASE WHEN verdict = 'ai_generated' THEN 1 ELSE 0 END) as ai_count,
             SUM(CASE WHEN verdict = 'real' THEN 1 ELSE 0 END) as real_count,
             ROUND(AVG(ai_score), 1) as avg_ai_score
           FROM scan_history WHERE user_id = %s""",
        (user_id,),
        fetch="one",
    )

    user = query(
        "SELECT scans_today, total_scans, plan, last_scan_date FROM users WHERE id = %s",
        (user_id,),
        fetch="one",
    )

    today = str(date.today())
    last_date = str(user["last_scan_date"]) if user and user["last_scan_date"] else ""
    scans_today = user["scans_today"] if user and last_date == today else 0
    limit = 4 if (user and user["plan"] == "free") else 20

    return jsonify({
        "success": True,
        "stats": {
            "total_scans": stats["total_scans"] or 0,
            "ai_count": stats["ai_count"] or 0,
            "real_count": stats["real_count"] or 0,
            "avg_ai_score": float(stats["avg_ai_score"] or 0),
            "scans_today": scans_today,
            "limit": limit,
            "plan": user["plan"] if user else "free",
        },
    }), 200
