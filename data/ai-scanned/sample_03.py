# SAMPLE_03_AUTH_PYTHON
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import Flask, jsonify, request, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///auth.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


def create_token(user: User) -> str:
    payload = {
        "sub": user.id,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=2),
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")


def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"message": "Forbidden"}), 403

        token = parts[1]
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return jsonify({"message": "Forbidden"}), 403

        user = User.query.get(payload.get("sub"))
        if not user:
            return jsonify({"message": "Forbidden"}), 403

        g.current_user = user
        g.jwt_payload = payload
        return fn(*args, **kwargs)

    return wrapper


def roles_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if not user:
                return jsonify({"message": "Forbidden"}), 403
            if user.role not in allowed_roles:
                return jsonify({"message": "Forbidden"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"message": "Invalid credentials"}), 401

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_token(user)
    return jsonify({"token": token})


@app.route("/admin", methods=["GET"])
@jwt_required
@roles_required("admin")
def admin_route():
    return jsonify({"message": f"Hello {g.current_user.username}, you are an admin."})


@app.route("/moderator", methods=["GET"])
@jwt_required
@roles_required("admin", "moderator")
def moderator_route():
    return jsonify({"message": f"Hello {g.current_user.username}, you have moderator access."})


@app.route("/user", methods=["GET"])
@jwt_required
def user_route():
    return jsonify({"message": f"Hello {g.current_user.username}, you are authenticated.", "role": g.current_user.role})


def seed_users():
    if User.query.count() == 0:
        users = [
            ("admin", "admin123", "admin"),
            ("moderator", "moderator123", "moderator"),
            ("user", "user123", "user"),
        ]
        for username, password, role in users:
            u = User(username=username, role=role)
            u.set_password(password)
            db.session.add(u)
        db.session.commit()


with app.app_context():
    db.create_all()
    seed_users()


if __name__ == "__main__":
    app.run(debug=True)
