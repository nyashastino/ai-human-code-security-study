# SAMPLE_04_AUTH_PYTHON
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import datetime

app = Flask(name)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password_hash = db.Column(db.String(256), nullable=False)


class PasswordResetToken(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	token = db.Column(db.String(200), unique=True, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	expires_at = db.Column(db.DateTime, nullable=False)


with app.app_context():
	db.create_all()


reset_form_html = """
<!doctype html> <title>Reset Password</title> <h2>Reset Password</h2> <form method="POST"> <input type="password" name="password" placeholder="Enter new password" required> <button type="submit">Reset Password</button> </form> """ 


@app.route('/forgot-password', methods=['POST'])
def forgot_password():
	data = request.get_json()
	email = data.get('email')
	if not email:
		return jsonify({'message': 'Email is required'}), 400
	user = User.query.filter_by(email=email).first()
	if not user:
		return jsonify({'message': 'User not found'}), 404
	token_str = str(uuid.uuid4())
	expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
	token = PasswordResetToken(token=token_str, user_id=user.id, expires_at=expires_at)
	db.session.add(token)
	db.session.commit()
	return jsonify({'reset_token': token_str}), 200


@app.route('/reset-password/<token>', methods=['GET'])
def validate_token(token):
	token_record = PasswordResetToken.query.filter_by(token=token).first()
	if not token_record or token_record.expires_at < datetime.datetime.utcnow():
		return jsonify({'message': 'Invalid or expired token'}), 400
	return render_template_string(reset_form_html)


@app.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
	token_record = PasswordResetToken.query.filter_by(token=token).first()
	if not token_record or token_record.expires_at < datetime.datetime.utcnow():
		return jsonify({'message': 'Invalid or expired token'}), 400
	password = request.form.get('password') or request.json.get('password')
	if not password:
		return jsonify({'message': 'Password is required'}), 400
	user = User.query.get(token_record.user_id)
	user.password_hash = generate_password_hash(password)
	db.session.commit()
	db.session.delete(token_record)
	db.session.commit()
	return jsonify({'message': 'Password has been reset successfully'}), 200


if name == 'main':
	app.run(debug=True)