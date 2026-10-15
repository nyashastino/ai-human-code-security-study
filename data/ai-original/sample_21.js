// SAMPLE_21_FORMS_NODEJS
const express = require('express');
const { body, validationResult } = require('express-validator');
const mysql = require('mysql2/promise');

const app = express();
const PORT = process.env.PORT || 3000;

const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'contact_app',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
};

let pool;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

async function initDatabase() {
  const rootConnection = await mysql.createConnection({
    host: dbConfig.host,
    user: dbConfig.user,
    password: dbConfig.password,
  });

  await rootConnection.query(`CREATE DATABASE IF NOT EXISTS \`${dbConfig.database}\``);
  await rootConnection.end();

  pool = mysql.createPool(dbConfig);

  await pool.query(`
    CREATE TABLE IF NOT EXISTS contact_submissions (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      email VARCHAR(255) NOT NULL,
      subject VARCHAR(255) NOT NULL,
      message TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
  `);
}

const contactValidators = [
  body('name')
    .exists({ checkFalsy: true })
    .withMessage('name is required')
    .bail()
    .isString()
    .withMessage('name must be a string')
    .bail()
    .trim()
    .notEmpty()
    .withMessage('name cannot be empty'),
  body('email')
    .exists({ checkFalsy: true })
    .withMessage('email is required')
    .bail()
    .isString()
    .withMessage('email must be a string')
    .bail()
    .trim()
    .isEmail()
    .withMessage('email must be a valid email address')
    .normalizeEmail(),
  body('subject')
    .exists({ checkFalsy: true })
    .withMessage('subject is required')
    .bail()
    .isString()
    .withMessage('subject must be a string')
    .bail()
    .trim()
    .notEmpty()
    .withMessage('subject cannot be empty'),
  body('message')
    .exists({ checkFalsy: true })
    .withMessage('message is required')
    .bail()
    .isString()
    .withMessage('message must be a string')
    .bail()
    .trim()
    .notEmpty()
    .withMessage('message cannot be empty'),
];

app.post('/contact', contactValidators, async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      message: 'Validation failed',
      errors: errors.array({ onlyFirstError: true }),
    });
  }

  const { name, email, subject, message } = req.body;

  try {
    const [result] = await pool.execute(
      'INSERT INTO contact_submissions (name, email, subject, message) VALUES (?, ?, ?, ?)',
      [name.trim(), String(email).trim().toLowerCase(), subject.trim(), message.trim()]
    );

    return res.status(200).json({
      message: 'Contact form submitted successfully',
      submissionId: result.insertId,
    });
  } catch (error) {
    return res.status(500).json({
      message: 'Internal server error',
    });
  }
});

(async () => {
  try {
    await initDatabase();
    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
})();
