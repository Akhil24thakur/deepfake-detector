from flask import Blueprint, request, jsonify

from models.database import query
from models.detector import predict
from utils.image_utils import validate_and_load, get_image_info

auth = Blueprint("auth", __name__)


class PasswordManager:
    @staticmethod
    def hash(password, salt):
        import hashlib

        return hashlib.sha256((password + salt).encode()).hexdigest()

    @staticmethod
    def generate_salt():
        import secrets

        return secrets.token_hex(16)

    @staticmethod
    def verify(entered_password, salt, stored_hash):
        return PasswordManager.hash(entered_password, salt) == stored_hash


class Validator:
    @staticmethod
    def email(email):
        import re

        return re.match(r"^[^@]+@[^@]+\.[^@]+$", email) is not None

    @staticmethod
    def mobile(mobile):
        import re

        digits = re.sub(r"\D", "", mobile)
        return 10 <= len(digits) <= 13

    @staticmethod
    def password(password):
        return password and len(password) >= 6

    @staticmethod
    def name(name):
        return bool(name and name.strip())


class UserRepository:
    @staticmethod
    def find_by_email(email):
        return query(
            "SELECT id FROM users WHERE email = %s", (email,), fetch="one"
        )

    @staticmethod
    def find_by_mobile(mobile):
        return query(
            "SELECT id FROM users WHERE mobile = %s", (mobile,), fetch="one"
        )

    @staticmethod
    def find_by_identifier(identifier):
        return query(
            "SELECT * FROM users WHERE email = %s OR mobile = %s",
            (identifier.lower(), identifier),
            fetch="one",
        )

    @staticmethod
    def find_by_id(user_id):
        return query(
            "SELECT id, name, username, email, mobile, plan, scans_today, total_scans FROM users WHERE id = %s",
            (user_id,),
            fetch="one",
        )

    @staticmethod
    def create(name, username, email, mobile, password_hash, salt, dob, gender, city):
        return query(
            """INSERT INTO users
               (name, username, email, mobile, password_hash, salt, dob, gender, city)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (name, username, email, mobile, password_hash, salt, dob, gender, city),
        )


class AuthService:
    def signup(self, data):
        if not data:
            return {"success": False, "error": "No data received"}, 400

        name = data.get("name", "").strip()
        username = data.get("username", "").strip()
        email = data.get("email", "").strip().lower()
        mobile = data.get("mobile", "").strip()
        password = data.get("password", "")
        dob = data.get("dob", None)
        gender = data.get("gender", None)
        city = data.get("city", "").strip()

        if not Validator.name(name):
            return {"success": False, "error": "Name is required"}, 400
        if not email or not Validator.email(email):
            return {"success": False, "error": "Valid email is required"}, 400
        if not mobile or not Validator.mobile(mobile):
            return (
                {"success": False, "error": "Valid mobile number is required"},
                400,
            )
        if not Validator.password(password):
            return (
                {
                    "success": False,
                    "error": "Password must be at least 6 characters",
                },
                400,
            )

        if UserRepository.find_by_email(email):
            return (
                {
                    "success": False,
                    "error": "Email already registered. Please sign in.",
                },
                400,
            )
        if UserRepository.find_by_mobile(mobile):
            return (
                {
                    "success": False,
                    "error": "Mobile already registered. Please sign in.",
                },
                400,
            )

        salt = PasswordManager.generate_salt()
        password_hash = PasswordManager.hash(password, salt)

        new_id = UserRepository.create(
            name, username, email, mobile, password_hash, salt, dob, gender, city
        )

        if not new_id:
            return (
                {"success": False, "error": "Registration failed. Try again."},
                500,
            )

        return {
            "success": True,
            "user": {
                "id": new_id,
                "name": name,
                "username": username,
                "email": email,
                "mobile": mobile,
                "plan": "free",
            },
        }, 200

    def login(self, data):
        if not data:
            return {"success": False, "error": "No data received"}, 400

        identifier = data.get("identifier", "").strip()
        password = data.get("password", "")

        if not identifier:
            return {"success": False, "error": "Enter email or mobile"}, 400
        if not password:
            return {"success": False, "error": "Enter password"}, 400

        user = UserRepository.find_by_identifier(identifier)

        if not user:
            return (
                {"success": False, "error": "Account not found. Please sign up."},
                404,
            )

        if not PasswordManager.verify(password, user["salt"], user["password_hash"]):
            return {"success": False, "error": "Incorrect password"}, 401

        return {
            "success": True,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "username": user["username"],
                "email": user["email"],
                "mobile": user["mobile"],
                "plan": user["plan"],
                "scansToday": user["scans_today"],
                "totalScans": user["total_scans"],
            },
        }, 200


_auth_service = AuthService()


@auth.route("/api/signup", methods=["POST"])
def signup():
    response, status = _auth_service.signup(request.get_json())
    return jsonify(response), status


@auth.route("/api/login", methods=["POST"])
def login():
    response, status = _auth_service.login(request.get_json())
    return jsonify(response), status


@auth.route("/api/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = UserRepository.find_by_id(user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    return jsonify({"success": True, "user": user}), 200
