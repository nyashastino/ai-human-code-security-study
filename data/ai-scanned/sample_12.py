# SAMPLE_12_CRUD_PYTHON
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(name)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(200), nullable=False)
	content = db.Column(db.Text, nullable=False)
	author = db.Column(db.String(100), nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


with app.app_context():
	db.create_all()


def post_to_dict(post):
	return {
		'id': post.id,
		'title': post.title,
		'content': post.content,
		'author': post.author,
		'created_at': post.created_at.isoformat()
	}


@app.route('/posts', methods=['GET'])
def get_posts():
	posts = Post.query.order_by(Post.created_at.desc()).all()
	return jsonify([post_to_dict(p) for p in posts]), 200


@app.route('/posts/int:id', methods=['GET'])
def get_post(id):
	post = Post.query.get(id)
	if not post:
		return jsonify({'message': 'Post not found'}), 404
	return jsonify(post_to_dict(post)), 200


@app.route('/posts', methods=['POST'])
def create_post():
	data = request.get_json()
	if not data or not data.get('title') or not data.get('content') or not data.get('author'):
		return jsonify({'message': 'Missing required fields'}), 400
	post = Post(
		title=data['title'],
		content=data['content'],
		author=data['author']
	)
	db.session.add(post)
	db.session.commit()
	return jsonify(post_to_dict(post)), 201


@app.route('/posts/int:id', methods=['PUT'])
def update_post(id):
	post = Post.query.get(id)
	if not post:
		return jsonify({'message': 'Post not found'}), 404
	data = request.get_json()
	if not data:
		return jsonify({'message': 'Missing required fields'}), 400
	if 'title' in data:
		post.title = data['title']
	if 'content' in data:
		post.content = data['content']
	db.session.commit()
	return jsonify(post_to_dict(post)), 200


@app.route('/posts/int:id', methods=['DELETE'])
def delete_post(id):
	post = Post.query.get(id)
	if not post:
		return jsonify({'message': 'Post not found'}), 404
	db.session.delete(post)
	db.session.commit()
	return jsonify({'message': 'Post deleted'}), 200


if name == 'main':
	app.run(debug=True)