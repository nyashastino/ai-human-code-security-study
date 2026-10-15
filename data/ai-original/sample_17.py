# SAMPLE_17_FORMS_PYTHON
import os
from flask import Flask, render_template_string, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///contact_submissions.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class ContactSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    subject = StringField("Subject", validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send")


TEMPLATE = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Contact Form</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; }
    form { display: grid; gap: 0.9rem; }
    label { font-weight: 600; margin-bottom: 0.25rem; display: block; }
    input, textarea { width: 100%; padding: 0.6rem; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; }
    textarea { min-height: 140px; resize: vertical; }
    .error { color: #b00020; font-size: 0.92rem; margin-top: 0.2rem; }
    .flash-success { background: #e7f9ed; color: #176b2d; border: 1px solid #9fe0b4; padding: 0.8rem; border-radius: 6px; margin-bottom: 1rem; }
    button { padding: 0.65rem 1rem; border: none; background: #2563eb; color: #fff; border-radius: 6px; cursor: pointer; }
    button:hover { background: #1d4ed8; }
  </style>
</head>
<body>
  <h1>Contact Us</h1>

  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for category, msg in messages %}
        {% if category == 'success' %}
          <div class=\"flash-success\">{{ msg }}</div>
        {% endif %}
      {% endfor %}
    {% endif %}
  {% endwith %}

  <form method=\"POST\" action=\"{{ url_for('contact') }}\" novalidate>
    {{ form.hidden_tag() }}

    <div>
      {{ form.name.label }}
      {{ form.name() }}
      {% for err in form.name.errors %}
        <div class=\"error\">{{ err }}</div>
      {% endfor %}
    </div>

    <div>
      {{ form.email.label }}
      {{ form.email() }}
      {% for err in form.email.errors %}
        <div class=\"error\">{{ err }}</div>
      {% endfor %}
    </div>

    <div>
      {{ form.subject.label }}
      {{ form.subject() }}
      {% for err in form.subject.errors %}
        <div class=\"error\">{{ err }}</div>
      {% endfor %}
    </div>

    <div>
      {{ form.message.label }}
      {{ form.message() }}
      {% for err in form.message.errors %}
        <div class=\"error\">{{ err }}</div>
      {% endfor %}
    </div>

    <div>{{ form.submit() }}</div>
  </form>
</body>
</html>
"""


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        submission = ContactSubmission(
            name=form.name.data.strip(),
            email=form.email.data.strip(),
            subject=form.subject.data.strip(),
            message=form.message.data.strip(),
        )
        db.session.add(submission)
        db.session.commit()
        flash("Your message has been submitted successfully.", "success")
        return redirect(url_for("contact"))

    return render_template_string(TEMPLATE, form=form)


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
