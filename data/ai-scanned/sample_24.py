# SAMPLE_24_API_PYTHON
import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(64), nullable=False, unique=True)
    published_year = db.Column(db.Integer, nullable=True)
    genre = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "published_year": self.published_year,
            "genre": self.genre,
        }


def validate_required_fields(data):
    if not isinstance(data, dict):
        return "Invalid JSON payload"
    for field in ["title", "author", "isbn"]:
        value = data.get(field)
        if value is None or str(value).strip() == "":
            return f"{field} is required"
    return None


def apply_book_updates(book, data):
    allowed_fields = ["title", "author", "isbn", "published_year", "genre"]
    for field in allowed_fields:
        if field in data:
            value = data[field]
            if field in ["title", "author", "isbn"]:
                if value is None or str(value).strip() == "":
                    return f"{field} cannot be empty"
                setattr(book, field, str(value).strip())
            elif field == "published_year":
                if value is None or value == "":
                    setattr(book, field, None)
                else:
                    try:
                        setattr(book, field, int(value))
                    except (TypeError, ValueError):
                        return "published_year must be an integer"
            else:
                if value is None:
                    setattr(book, field, None)
                else:
                    setattr(book, field, str(value).strip())
    return None


@app.route("/api/books", methods=["GET"])
def get_books():
    genre = request.args.get("genre", type=str)
    query = Book.query

    if genre is not None and genre.strip() != "":
        query = query.filter(Book.genre == genre.strip())

    books = query.order_by(Book.id.asc()).all()
    return jsonify([book.to_dict() for book in books]), 200


@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book.to_dict()), 200


@app.route("/api/books", methods=["POST"])
def create_book():
    data = request.get_json(silent=True)
    error = validate_required_fields(data)
    if error:
        return jsonify({"error": error}), 400

    book = Book()
    apply_error = apply_book_updates(book, data)
    if apply_error:
        return jsonify({"error": apply_error}), 400

    try:
        db.session.add(book)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to create book. ISBN may already exist."}), 400

    return jsonify(book.to_dict()), 201


@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON payload"}), 400

    apply_error = apply_book_updates(book, data)
    if apply_error:
        return jsonify({"error": apply_error}), 400

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to update book. ISBN may already exist."}), 400

    return jsonify(book.to_dict()), 200


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"}), 200


@app.errorhandler(404)
def handle_404(_):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def handle_405(_):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def handle_500(_):
    return jsonify({"error": "Internal server error"}), 500


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
