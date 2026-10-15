// SAMPLE_23_FORMS_NODEJS
const express = require('express');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

function createValidationMiddleware(schema) {
  return (req, res, next) => {
    const errors = {};

    for (const [field, validators] of Object.entries(schema)) {
      const value = req.body[field];

      for (const validator of validators) {
        const result = validator(value, req.body);
        if (result !== true) {
          errors[field] = result;
          break;
        }
      }
    }

    if (Object.keys(errors).length > 0) {
      return res.status(400).json({ errors });
    }

    return next();
  };
}

const validators = {
  required: (fieldName) => (value) => {
    if (value === undefined || value === null || String(value).trim() === '') {
      return `${fieldName} is required`;
    }
    return true;
  },
  username: () => (value) => {
    if (typeof value !== 'string') {
      return 'username must be a string';
    }
    const trimmed = value.trim();
    if (!/^[a-zA-Z0-9]{4,20}$/.test(trimmed)) {
      return 'username must be 4-20 characters and alphanumeric';
    }
    return true;
  },
  email: () => (value) => {
    if (typeof value !== 'string') {
      return 'email must be a string';
    }
    const trimmed = value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmed)) {
      return 'email must be a valid email address';
    }
    return true;
  },
  password: () => (value) => {
    if (typeof value !== 'string') {
      return 'password must be a string';
    }
    if (value.length < 8) {
      return 'password must be at least 8 characters long';
    }
    if (!/[A-Za-z]/.test(value) || !/[0-9]/.test(value)) {
      return 'password must contain at least one letter and one number';
    }
    return true;
  },
  confirmPassword: () => (value, body) => {
    if (typeof value !== 'string') {
      return 'confirm_password must be a string';
    }
    if (value !== body.password) {
      return 'confirm_password must match password';
    }
    return true;
  },
  age: () => (value) => {
    if (value === undefined || value === null || value === '') {
      return 'age is required';
    }
    const age = Number(value);
    if (!Number.isInteger(age)) {
      return 'age must be a number';
    }
    if (age < 18 || age > 99) {
      return 'age must be between 18 and 99';
    }
    return true;
  },
};

const registerValidation = createValidationMiddleware({
  username: [validators.required('username'), validators.username()],
  email: [validators.required('email'), validators.email()],
  password: [validators.required('password'), validators.password()],
  confirm_password: [validators.required('confirm_password'), validators.confirmPassword()],
  age: [validators.age()],
});

app.post('/register', registerValidation, (req, res) => {
  return res.status(201).json({ message: 'Registration successful' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
