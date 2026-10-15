# SAMPLE_20_FORMS_PYTHON
from flask import Flask, request, jsonify
import re
from urllib.parse import urlparse

app = Flask(name)


def is_valid_email(email):
    return re.match(r"^[^@]+@[^@]+.[^@]+$", email)


def is_valid_username(username):
    return re.match(r"^[a-zA-Z0-9]{3,20}$", username)


def is_valid_url(url):
    try:
        parsed = urlparse(url)
        return all([parsed.scheme in ("http", "https"), parsed.netloc])
    except:
        return False


@app.route('/profile', methods=['POST'])
def update_profile():
    data = request.get_json() or request.form
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    age = (data.get('age') or '').strip()
    website = (data.get('website') or '').strip()
    bio = (data.get('bio') or '').strip()

    errors = {}

    if not is_valid_username(username):
        errors['username'] = 'Username must be 3-20 alphanumeric characters'

    if not is_valid_email(email):
        errors['email'] = 'Invalid email format'

    try:
        age_val = int(age)
        if age_val < 13 or age_val > 120:
            errors['age'] = 'Age must be between 13 and 120'
    except:
        errors['age'] = 'Age must be a valid number'

    if website:
        if not is_valid_url(website):
            errors['website'] = 'Invalid URL'

    if len(bio) > 500:
        errors['bio'] = 'Bio must be 500 characters or less'

    if errors:
        return jsonify({'errors': errors}), 400

    result = {
        'username': username,
        'email': email,
        'age': age_val,
        'website': website,
        'bio': bio
    }

    return jsonify(result), 200


if name == 'main':
    app.run(debug=True)