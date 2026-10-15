# SAMPLE_02_AUTH_PYTHON
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import jwt
import datetime
from functools import wraps

app = Flask(name)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password_hash = db.Column(db.String(128), nullable=False)


with app.app_context():
	db.create_all()


def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None
		auth_header = request.headers.get('Authorization')
		if auth_header and auth_header.startswith('Bearer '):
			token = auth_header.split(" ")[1]
		if not token:
			return jsonify({'message': 'Token is missing'}), 401
		try:
			data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
			current_user = User.query.get(data['user_id'])
			if not current_user:
				return jsonify({'message': 'Invalid token'}), 401
		except jwt.ExpiredSignatureError:
			return jsonify({'message': 'Token has expired'}), 401
		except:
			return jsonify({'message': 'Token is invalid'}), 401
		return f(current_user, *args, **kwargs)
	return decorated


@app.route('/register', methods=['POST'])
def register():
	data = request.get_json()
	username = data.get('username')
	email = data.get('email')
	password = data.get('password')
	if not username or not email or not password:
		return jsonify({'message': 'Missing fields'}), 400
	existing_user = User.query.filter_by(email=email).first()
	if existing_user:
		return jsonify({'message': 'User already exists'}), 409
	hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
	new_user = User(username=username, email=email, password_hash=hashed_password)
	db.session.add(new_user)
	db.session.commit()
	return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
	data = request.get_json()
	email = data.get('email')
	password = data.get('password')
	if not email or not password:
		return jsonify({'message': 'Missing credentials'}), 400
	user = User.query.filter_by(email=email).first()
	if not user or not bcrypt.check_password_hash(user.password_hash, password):
		return jsonify({'message': 'Invalid credentials'}), 401
	token = jwt.encode({
		'user_id': user.id,
		'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
	}, app.config['SECRET_KEY'], algorithm="HS256")
	return jsonify({'token': token}), 200


@app.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
	return jsonify({
		'id': current_user.id,
		'username': current_user.username,
		'email': current_user.email
	}), 200


if name == 'main':
	app.run(debug=True)