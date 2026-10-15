# SAMPLE_10_CRUD_PYTHON
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(name)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Product(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), nullable=False)
	description = db.Column(db.String(255), nullable=True)
	price = db.Column(db.Float, nullable=False)
	quantity = db.Column(db.Integer, nullable=False)


with app.app_context():
	db.create_all()


def product_to_dict(product):
	return {
		'id': product.id,
		'name': product.name,
		'description': product.description,
		'price': product.price,
		'quantity': product.quantity
	}


@app.route('/products', methods=['GET'])
def get_products():
	products = Product.query.all()
	return jsonify([product_to_dict(p) for p in products]), 200


@app.route('/products/int:id', methods=['GET'])
def get_product(id):
	product = Product.query.get(id)
	if not product:
		return jsonify({'message': 'Product not found'}), 404
	return jsonify(product_to_dict(product)), 200


@app.route('/products', methods=['POST'])
def create_product():
	data = request.get_json()
	if not data or not data.get('name') or data.get('price') is None or data.get('quantity') is None:
		return jsonify({'message': 'Missing required fields'}), 400
	product = Product(
		name=data['name'],
		description=data.get('description'),
		price=data['price'],
		quantity=data['quantity']
	)
	db.session.add(product)
	db.session.commit()
	return jsonify(product_to_dict(product)), 201


@app.route('/products/int:id', methods=['PUT'])
def update_product(id):
	product = Product.query.get(id)
	if not product:
		return jsonify({'message': 'Product not found'}), 404
	data = request.get_json()
	if not data:
		return jsonify({'message': 'Missing required fields'}), 400
	if 'name' in data:
		product.name = data['name']
	if 'description' in data:
		product.description = data['description']
	if 'price' in data:
		product.price = data['price']
	if 'quantity' in data:
		product.quantity = data['quantity']
	db.session.commit()
	return jsonify(product_to_dict(product)), 200


@app.route('/products/int:id', methods=['DELETE'])
def delete_product(id):
	product = Product.query.get(id)
	if not product:
		return jsonify({'message': 'Product not found'}), 404
	db.session.delete(product)
	db.session.commit()
	return jsonify({'message': 'Product deleted'}), 200


if name == 'main':
	app.run(debug=True)