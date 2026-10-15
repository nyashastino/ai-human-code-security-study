# SAMPLE_25_API_PYTHON
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(name)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class WeatherRecord(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	city = db.Column(db.String(100), nullable=False)
	temperature = db.Column(db.Float, nullable=False)
	humidity = db.Column(db.Float)
	wind_speed = db.Column(db.Float)
	recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


with app.app_context():
	db.create_all()


def to_dict(record):
	return {
		'id': record.id,
		'city': record.city,
		'temperature': record.temperature,
		'humidity': record.humidity,
		'wind_speed': record.wind_speed,
		'recorded_at': record.recorded_at.isoformat()
	}


@app.route('/api/weather', methods=['GET'])
def get_weather():
	city = request.args.get('city')
	if city:
		records = WeatherRecord.query.filter_by(city=city).all()
	else:
		records = WeatherRecord.query.all()
	return jsonify([to_dict(r) for r in records]), 200


@app.route('/api/weather/int:id', methods=['GET'])
def get_weather_by_id(id):
	record = WeatherRecord.query.get(id)
	if not record:
		return jsonify({'message': 'Record not found'}), 404
	return jsonify(to_dict(record)), 200


@app.route('/api/weather', methods=['POST'])
def create_weather():
	data = request.get_json()
	if not data or not data.get('city') or data.get('temperature') is None:
		return jsonify({'message': 'Invalid input'}), 400
	record = WeatherRecord(
		city=data.get('city'),
		temperature=data.get('temperature'),
		humidity=data.get('humidity'),
		wind_speed=data.get('wind_speed')
	)
	db.session.add(record)
	db.session.commit()
	return jsonify(to_dict(record)), 201


@app.route('/api/weather/int:id', methods=['DELETE'])
def delete_weather(id):
	record = WeatherRecord.query.get(id)
	if not record:
		return jsonify({'message': 'Record not found'}), 404
	db.session.delete(record)
	db.session.commit()
	return jsonify({'message': 'Record deleted'}), 200


if name == 'main':
	app.run(debug=True)