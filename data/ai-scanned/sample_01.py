# SAMPLE_01_AUTH_PYTHON
from flask import Flask, redirect, url_for, session, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


REGISTER_TEMPLATE = """
<!doctype html>
<html>
<head><title>Register</title></head>
<body>
  <h1>Register</h1>
  {% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
  <form method="POST">
    {{ form.hidden_tag() }}
    <p>{{ form.username.label }}<br>{{ form.username(size=32) }}</p>
    <p>{{ form.email.label }}<br>{{ form.email(size=32) }}</p>
    <p>{{ form.password.label }}<br>{{ form.password(size=32) }}</p>
    <p>{{ form.confirm_password.label }}<br>{{ form.confirm_password(size=32) }}</p>
    <p>{{ form.submit() }}</p>
  </form>
  <p>Already have an account? <a href="{{ url_for('login') }}">Login</a></p>
</body>
</html>
"""


LOGIN_TEMPLATE = """
<!doctype html>
<html>
<head><title>Login</title></head>
<body>
  <h1>Login</h1>
  {% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
  <form method="POST">
    {{ form.hidden_tag() }}
    <p>{{ form.email.label }}<br>{{ form.email(size=32) }}</p>
    <p>{{ form.password.label }}<br>{{ form.password(size=32) }}</p>
    <p>{{ form.submit() }}</p>
  </form>
  <p>No account? <a href="{{ url_for('register') }}">Register</a></p>
</body>
</html>
"""


DASHBOARD_TEMPLATE = """
<!doctype html>
<html>
<head><title>Dashboard</title></head>
<body>
  <h1>Dashboard</h1>
  <p>Welcome, {{ user.username }}!</p>
  <p><a href="{{ url_for('logout') }}">Logout</a></p>
</body>
</html>
"""


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    error = None
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            error = "Username or email already exists"
        else:
            password_hash = generate_password_hash(form.password.data)
            user = User(username=username, email=email, password_hash=password_hash)
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
    return render_template_string(REGISTER_TEMPLATE, form=form, error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        error = "Invalid email or password"
    return render_template_string(LOGIN_TEMPLATE, form=form, error=error)


@app.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    user = db.session.get(User, user_id)
    if not user:
        session.clear()
        return redirect(url_for("login"))
    return render_template_string(DASHBOARD_TEMPLATE, user=user)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
