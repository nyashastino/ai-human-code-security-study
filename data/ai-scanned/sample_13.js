// SAMPLE_13_CRUD_NODEJS
const express = require('express');
const mysql = require('mysql2/promise');

const app = express();
const PORT = process.env.PORT || 3000;

const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'users_api',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
};

let pool;

app.use(express.json());

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
      name VARCHAR(255) NOT NULL,
      email VARCHAR(255) NOT NULL UNIQUE,
      age INT NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
  `);
}

function validateUserInput(body) {
  const name = typeof body.name === 'string' ? body.name.trim() : '';
  const email = typeof body.email === 'string' ? body.email.trim() : '';
  const age = body.age;

  if (!name || !email || age === undefined || age === null || age === '') {
    return { error: 'name, email, and age are required' };
  }

  const parsedAge = Number(age);
  if (!Number.isInteger(parsedAge) || parsedAge < 0) {
    return { error: 'age must be a non-negative integer' };
  }

  return { data: { name, email, age: parsedAge } };
}

app.get('/users', async (req, res) => {
  try {
    const [rows] = await pool.execute('SELECT id, name, email, age FROM users ORDER BY id ASC');
    return res.json(rows);
  } catch (error) {
    return res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/users/:id', async (req, res) => {
  try {
    const userId = Number(req.params.id);
    if (!Number.isInteger(userId) || userId <= 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    const [rows] = await pool.execute('SELECT id, name, email, age FROM users WHERE id = ?', [userId]);
    if (rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    return res.json(rows[0]);
  } catch (error) {
    return res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/users', async (req, res) => {
  try {
    const { data, error } = validateUserInput(req.body || {});
    if (error) {
      return res.status(400).json({ error });
    }

    const [result] = await pool.execute(
      'INSERT INTO users (name, email, age) VALUES (?, ?, ?)',
      [data.name, data.email, data.age]
    );

    return res.status(201).json({ id: result.insertId, ...data });
  } catch (error) {
    if (error && error.code === 'ER_DUP_ENTRY') {
      return res.status(400).json({ error: 'email already exists' });
    }
    return res.status(500).json({ error: 'Internal server error' });
  }
});

app.put('/users/:id', async (req, res) => {
  try {
    const userId = Number(req.params.id);
    if (!Number.isInteger(userId) || userId <= 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    const { data, error } = validateUserInput(req.body || {});
    if (error) {
      return res.status(400).json({ error });
    }

    const [exists] = await pool.execute('SELECT id FROM users WHERE id = ?', [userId]);
    if (exists.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    await pool.execute('UPDATE users SET name = ?, email = ?, age = ? WHERE id = ?', [
      data.name,
      data.email,
      data.age,
      userId,
    ]);

    return res.json({ id: userId, ...data });
  } catch (error) {
    if (error && error.code === 'ER_DUP_ENTRY') {
      return res.status(400).json({ error: 'email already exists' });
    }
    return res.status(500).json({ error: 'Internal server error' });
  }
});

app.delete('/users/:id', async (req, res) => {
  try {
    const userId = Number(req.params.id);
    if (!Number.isInteger(userId) || userId <= 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    const [result] = await pool.execute('DELETE FROM users WHERE id = ?', [userId]);
    if (result.affectedRows === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    return res.json({ message: 'User deleted successfully' });
  } catch (error) {
    return res.status(500).json({ error: 'Internal server error' });
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
