# SAMPLE_19_FORMS_PYTHON
import os
import uuid
from datetime import datetime

from flask import Flask, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///uploads.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}

db = SQLAlchemy(app)


class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Upload File</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 700px; margin: 2rem auto; padding: 0 1rem; }
    form { display: grid; gap: 1rem; }
    input[type="text"], input[type="file"] { width: 100%; padding: 0.6rem; box-sizing: border-box; }
    button { padding: 0.7rem 1rem; border: none; background: #2563eb; color: #fff; cursor: pointer; border-radius: 6px; }
    .message { margin-bottom: 1rem; padding: 0.8rem; border-radius: 6px; }
    .success { background: #e8f7ed; color: #136b2f; border: 1px solid #a8ddb7; }
    .error { background: #fdeceb; color: #8b1c13; border: 1px solid #f4b4ae; }
  </style>
</head>
<body>
  <h1>Upload Image</h1>

  {% if success_message %}
    <div class="message success">{{ success_message }}</div>
  {% endif %}

  {% if error_message %}
    <div class="message error">{{ error_message }}</div>
  {% endif %}

  <form method="post" action="{{ url_for('upload_file') }}" enctype="multipart/form-data">
    <div>
      <label for="file">Image File</label>
      <input type="file" id="file" name="file" accept=".jpg,.jpeg,.png,.gif" required>
    </div>
    <div>
      <label for="description">Description</label>
      <input type="text" id="description" name="description" required>
    </div>
    <button type="submit">Upload</button>
  </form>
</body>
</html>
"""


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(_):
    return render_template_string(
        TEMPLATE,
        success_message=None,
        error_message="File is too large. Maximum allowed size is 2MB.",
    ), 413


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "GET":
        return render_template_string(TEMPLATE, success_message=None, error_message=None)

    description = (request.form.get("description") or "").strip()
    if not description:
        return render_template_string(
            TEMPLATE,
            success_message=None,
            error_message="Description is required.",
        ), 400

    if "file" not in request.files:
        return render_template_string(
            TEMPLATE,
            success_message=None,
            error_message="No file part found in the request.",
        ), 400

    file = request.files["file"]
    if file.filename == "":
        return render_template_string(
            TEMPLATE,
            success_message=None,
            error_message="No file selected.",
        ), 400

    if not allowed_file(file.filename):
        return render_template_string(
            TEMPLATE,
            success_message=None,
            error_message="Invalid file type. Only .jpg, .jpeg, .png, and .gif are allowed.",
        ), 400

    original_name = secure_filename(file.filename)
    extension = original_name.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{extension}"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)

    file.save(save_path)

    record = Upload(filename=unique_filename, description=description)
    db.session.add(record)
    db.session.commit()

    return render_template_string(
        TEMPLATE,
        success_message=f"File uploaded successfully. Stored filename: {unique_filename}",
        error_message=None,
    ), 200


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
