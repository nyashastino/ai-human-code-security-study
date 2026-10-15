# SAMPLE_18_FORMS_PYTHON
from flask import Flask, request, redirect, url_for, session, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

app = Flask(name)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(100))
	last_name = db.Column(db.String(100))
	email = db.Column(db.String(120), unique=True)
	username = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(255))
	phone = db.Column(db.String(50))
	dob = db.Column(db.Date)
	country = db.Column(db.String(100))


with app.app_context():
	db.create_all()


step1_html = """
<h2>Step 1</h2> <form method="POST"> <input name="first_name" placeholder="First Name" value="{{data.get('first_name','')}}" required> <input name="last_name" placeholder="Last Name" value="{{data.get('last_name','')}}" required> <input name="email" placeholder="Email" value="{{data.get('email','')}}" required> <button type="submit">Next</button> </form> <p style="color:red;">{{error}}</p> """ 
step2_html = """
<h2>Step 2</h2> <form method="POST"> <input name="username" placeholder="Username" value="{{data.get('username','')}}" required> <input type="password" name="password" placeholder="Password" required> <input type="password" name="confirm_password" placeholder="Confirm Password" required> <button type="submit">Next</button> </form> <a href="{{url_for('step1')}}">Back</a> <p style="color:red;">{{error}}</p> """ 
step3_html = """
<h2>Step 3</h2> <form method="POST"> <input name="phone" placeholder="Phone" value="{{data.get('phone','')}}" required> <input type="date" name="dob" value="{{data.get('dob','')}}" required> <input name="country" placeholder="Country" value="{{data.get('country','')}}" required> <button type="submit">Submit</button> </form> <a href="{{url_for('step2')}}">Back</a> <p style="color:red;">{{error}}</p> """ 
confirm_html = """
<h2>Registration Successful</h2> <p>User has been registered successfully.</p> """ 


@app.route('/')
def index():
	return redirect(url_for('step1'))


@app.route('/step1', methods=['GET', 'POST'])
def step1():
	error = ''
	data = session.get('form_data', {})
	if request.method == 'POST':
		first_name = request.form.get('first_name')
		last_name = request.form.get('last_name')
		email = request.form.get('email')
		if not re.match(r"[^@]+@[^@]+.[^@]+", email):
			error = 'Invalid email format'
		else:
			data.update({
				'first_name': first_name,
				'last_name': last_name,
				'email': email
			})
			session['form_data'] = data
			return redirect(url_for('step2'))
	return render_template_string(step1_html, data=data, error=error)


@app.route('/step2', methods=['GET', 'POST'])
def step2():
	error = ''
	data = session.get('form_data', {})
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		confirm_password = request.form.get('confirm_password')
		if password != confirm_password:
			error = 'Passwords do not match'
		else:
			data.update({
				'username': username,
				'password': password
			})
			session['form_data'] = data
			return redirect(url_for('step3'))
	return render_template_string(step2_html, data=data, error=error)


@app.route('/step3', methods=['GET', 'POST'])
def step3():
	error = ''
	data = session.get('form_data', {})
	if request.method == 'POST':
		phone = request.form.get('phone')
		dob = request.form.get('dob')
		country = request.form.get('country')
		try:
			dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
		except:
			error = 'Invalid date'
			return render_template_string(step3_html, data=data, error=error)
		user = User(
			first_name=data.get('first_name'),
			last_name=data.get('last_name'),
			email=data.get('email'),
			username=data.get('username'),
			password=data.get('password'),
			phone=phone,
			dob=dob_date,
			country=country
		)
		db.session.add(user)
		db.session.commit()
		session.pop('form_data', None)
		return redirect(url_for('confirm'))
	return render_template_string(step3_html, data=data, error=error)


@app.route('/confirm')
def confirm():
	return render_template_string(confirm_html)


if name == 'main':
	app.run(debug=True)