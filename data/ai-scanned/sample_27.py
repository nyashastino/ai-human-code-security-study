# SAMPLE_27_API_PYTHON
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(name)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Student(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(120), nullable=False)
	course = db.Column(db.String(100), nullable=False)


class Grade(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
	subject = db.Column(db.String(100), nullable=False)
	score = db.Column(db.Float, nullable=False)
	grade_letter = db.Column(db.String(2), nullable=False)


with app.app_context():
	db.create_all()


def calculate_grade_letter(score):
	if score >= 90:
		return 'A'
	elif score >= 80:
		return 'B'
	elif score >= 70:
		return 'C'
	elif score >= 60:
		return 'D'
	else:
		return 'F'


def student_to_dict(student):
	return {
		'id': student.id,
		'name': student.name,
		'email': student.email,
		'course': student.course
	}


def grade_to_dict(grade):
	return {
		'id': grade.id,
		'student_id': grade.student_id,
		'subject': grade.subject,
		'score': grade.score,
		'grade_letter': grade.grade_letter
	}


@app.route('/api/students', methods=['GET'])
def get_students():
	students = Student.query.all()
	return jsonify([student_to_dict(s) for s in students]), 200


@app.route('/api/students/int:id/grades', methods=['GET'])
def get_student_grades(id):
	student = Student.query.get(id)
	if not student:
		return jsonify({'message': 'Student not found'}), 404
	grades = Grade.query.filter_by(student_id=id).all()
	return jsonify([grade_to_dict(g) for g in grades]), 200


@app.route('/api/grades', methods=['POST'])
def create_grade():
	data = request.get_json()
	if not data or data.get('student_id') is None or not data.get('subject') or data.get('score') is None:
		return jsonify({'message': 'Invalid input'}), 400
	student = Student.query.get(data.get('student_id'))
	if not student:
		return jsonify({'message': 'Student not found'}), 404
	score = data.get('score')
	grade_letter = calculate_grade_letter(score)
	grade = Grade(
		student_id=data.get('student_id'),
		subject=data.get('subject'),
		score=score,
		grade_letter=grade_letter
	)
	db.session.add(grade)
	db.session.commit()
	return jsonify(grade_to_dict(grade)), 201


@app.route('/api/grades/int:id', methods=['PUT'])
def update_grade(id):
	grade = Grade.query.get(id)
	if not grade:
		return jsonify({'message': 'Grade not found'}), 404
	data = request.get_json()
	if not data or data.get('score') is None:
		return jsonify({'message': 'Invalid input'}), 400
	score = data.get('score')
	grade.score = score
	grade.grade_letter = calculate_grade_letter(score)
	db.session.commit()
	return jsonify(grade_to_dict(grade)), 200


@app.route('/api/grades/int:id', methods=['DELETE'])
def delete_grade(id):
	grade = Grade.query.get(id)
	if not grade:
		return jsonify({'message': 'Grade not found'}), 404
	db.session.delete(grade)
	db.session.commit()
	return jsonify({'message': 'Grade deleted'}), 200


if name == 'main':
	app.run(debug=True)