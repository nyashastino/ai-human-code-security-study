# SAMPLE_09_CRUD_PYTHON
import os

from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "users_api"),
}


def get_connection(include_database=True):
    config = dict(DB_CONFIG)
    if not include_database:
        config.pop("database", None)
    return mysql.connector.connect(**config)


def init_db():
    conn = None
    cursor = None
    try:
        conn = get_connection(include_database=False)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`")
        conn.commit()
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                age INT NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        conn.commit()
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def validate_user_payload(data):
    if not isinstance(data, dict):
        return None, "Invalid JSON payload"

    required_fields = ["name", "email", "age"]
    for field in required_fields:
        if field not in data:
            return None, f"Missing field: {field}"

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    age = data.get("age")

    if not name:
        return None, "Field 'name' is required"
    if not email:
        return None, "Field 'email' is required"

    try:
        age = int(age)
    except (TypeError, ValueError):
        return None, "Field 'age' must be an integer"

    if age < 0:
        return None, "Field 'age' must be a non-negative integer"

    return {"name": name, "email": email, "age": age}, None


@app.route("/users", methods=["GET"])
def get_users():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, age FROM users ORDER BY id ASC")
        users = cursor.fetchall()
        return jsonify(users), 200
    except Error:
        return jsonify({"error": "Database error"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, age FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify(user), 200
    except Error:
        return jsonify({"error": "Database error"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True)
    payload, error_message = validate_user_payload(data)
    if error_message:
        return jsonify({"error": error_message}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)",
            (payload["name"], payload["email"], payload["age"]),
        )
        conn.commit()

        new_id = cursor.lastrowid
        return jsonify({"id": new_id, "name": payload["name"], "email": payload["email"], "age": payload["age"]}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400
    except Error:
        return jsonify({"error": "Database error"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json(silent=True)
    payload, error_message = validate_user_payload(data)
    if error_message:
        return jsonify({"error": error_message}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        existing = cursor.fetchone()
        if not existing:
            return jsonify({"error": "User not found"}), 404

        update_cursor = conn.cursor()
        update_cursor.execute(
            "UPDATE users SET name = %s, email = %s, age = %s WHERE id = %s",
            (payload["name"], payload["email"], payload["age"], user_id),
        )
        conn.commit()
        update_cursor.close()

        return jsonify({"id": user_id, "name": payload["name"], "email": payload["email"], "age": payload["age"]}), 200
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400
    except Error:
        return jsonify({"error": "Database error"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "User deleted successfully"}), 200
    except Error:
        return jsonify({"error": "Database error"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.errorhandler(404)
def handle_404(_):
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
