# SAMPLE_26_API_PYTHON
import os
from datetime import datetime

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def parse_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes"}:
            return True
        if normalized in {"false", "0", "no"}:
            return False
    return None


@app.route("/api/todos", methods=["GET"])
def get_todos():
    completed_filter = request.args.get("completed")
    query = Todo.query

    if completed_filter is not None:
        parsed = parse_bool(completed_filter)
        if parsed is None:
            return jsonify({"error": "Invalid value for completed. Use true or false."}), 400
        query = query.filter(Todo.completed == parsed)

    todos = query.order_by(Todo.id.asc()).all()
    return jsonify([todo.to_dict() for todo in todos]), 200


@app.route("/api/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    todo = db.session.get(Todo, todo_id)
    if not todo:
        return jsonify({"error": "Todo not found"}), 404
    return jsonify(todo.to_dict()), 200


@app.route("/api/todos", methods=["POST"])
def create_todo():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON payload"}), 400

    title = data.get("title")
    if title is None or str(title).strip() == "":
        return jsonify({"error": "title is required"}), 400

    description = data.get("description")
    if description is not None:
        description = str(description)

    completed = data.get("completed", False)
    parsed_completed = parse_bool(completed)
    if parsed_completed is None:
        return jsonify({"error": "completed must be a boolean"}), 400

    todo = Todo(
        title=str(title).strip(),
        description=description,
        completed=parsed_completed,
    )
    db.session.add(todo)
    db.session.commit()

    return jsonify(todo.to_dict()), 201


@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    todo = db.session.get(Todo, todo_id)
    if not todo:
        return jsonify({"error": "Todo not found"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON payload"}), 400

    if "title" in data:
        title = data.get("title")
        if title is None or str(title).strip() == "":
            return jsonify({"error": "title cannot be empty"}), 400
        todo.title = str(title).strip()

    if "description" in data:
        description = data.get("description")
        todo.description = None if description is None else str(description)

    if "completed" in data:
        parsed_completed = parse_bool(data.get("completed"))
        if parsed_completed is None:
            return jsonify({"error": "completed must be a boolean"}), 400
        todo.completed = parsed_completed

    db.session.commit()
    return jsonify(todo.to_dict()), 200


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    todo = db.session.get(Todo, todo_id)
    if not todo:
        return jsonify({"error": "Todo not found"}), 404

    db.session.delete(todo)
    db.session.commit()
    return jsonify({"message": "Todo deleted successfully"}), 200


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
