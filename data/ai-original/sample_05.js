// SAMPLE_05_AUTH_NODEJS
const express = require('express');
const session = require('express-session');
const mysql = require('mysql2/promise');
const bcrypt = require('bcrypt');

const app = express();

const PORT = process.env.PORT || 3000;
const SALT_ROUNDS = 12;

const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'auth_app',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
};

let pool;

app.use(express.json());

app.use(
  session({
    secret: process.env.SESSION_SECRET || 'change-this-session-secret',
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      sameSite: 'lax',
      maxAge: 1000 * 60 * 60 * 24,
    },
  })
);

function requireAuth(req, res, next) {
  if (!req.session || !req.session.userId) {
    return res.status(401).json({ message: 'Unauthorized' });
  }
  next();
}

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
    CREATE TABLE IF NOT EXISTS users (
      id INT AUTO_INCREMENT PRIMARY KEY,
      username VARCHAR(100) NOT NULL,
      email VARCHAR(255) NOT NULL UNIQUE,
      password_hash VARCHAR(255) NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
  `);
}

app.post('/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;

    if (!username || !email || !password) {
      return res.status(400).json({ message: 'username, email, and password are required' });
    }

    const normalizedEmail = String(email).trim().toLowerCase();

    const [existing] = await pool.execute('SELECT id FROM users WHERE email = ?', [normalizedEmail]);
    if (existing.length > 0) {
      return res.status(409).json({ message: 'Email already registered' });
    }

    const passwordHash = await bcrypt.hash(password, SALT_ROUNDS);

    await pool.execute(
      'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
      [String(username).trim(), normalizedEmail, passwordHash]
    );

    return res.status(201).json({ message: 'User registered successfully' });
  } catch (error) {
    return res.status(500).json({ message: 'Internal server error' });
  }
});

app.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: 'email and password are required' });
    }

    const normalizedEmail = String(email).trim().toLowerCase();

    const [rows] = await pool.execute(
      'SELECT id, username, email, password_hash FROM users WHERE email = ?',
      [normalizedEmail]
    );

    if (rows.length === 0) {
      return res.status(401).json({ message: 'Invalid email or password' });
    }

    const user = rows[0];
    const isMatch = await bcrypt.compare(password, user.password_hash);

    if (!isMatch) {
      return res.status(401).json({ message: 'Invalid email or password' });
    }

    req.session.userId = user.id;
    req.session.username = user.username;
    req.session.email = user.email;

    return res.json({ message: 'Login successful' });
  } catch (error) {
    return res.status(500).json({ message: 'Internal server error' });
  }
});

app.get('/dashboard', requireAuth, async (req, res) => {
  return res.json({
    message: 'Welcome to your dashboard',
    user: {
      id: req.session.userId,
      username: req.session.username,
      email: req.session.email,
    },
  });
});

app.post('/logout', (req, res) => {
  if (!req.session) {
    return res.json({ message: 'Logged out' });
  }

  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ message: 'Internal server error' });
    }
    res.clearCookie('connect.sid');
    return res.json({ message: 'Logged out' });
  });
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
