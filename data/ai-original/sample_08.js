// SAMPLE_08_AUTH_NODEJS
const express = require('express');
const mysql = require('mysql2/promise');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const app = express();
app.use(express.json());
const pool = mysql.createPool({
host: 'localhost',
user: 'root',
password: '',
database: 'auth_db'
});
const initDB = async () => {
const conn = await pool.getConnection();
await conn.query( CREATE TABLE IF NOT EXISTS users ( id INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(255) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL ) );
await conn.query( CREATE TABLE IF NOT EXISTS password_resets ( id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, token VARCHAR(255) UNIQUE NOT NULL, expires_at DATETIME NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ) );
conn.release();
};
initDB();
app.post('/forgot-password', async (req, res) => {
const { email } = req.body;
if (!email) {
return res.status(400).json({ message: 'Email is required' });
}
try {
const [users] = await pool.query('SELECT * FROM users WHERE email = ?', [email]);
if (users.length === 0) {
return res.status(400).json({ message: 'User not found' });
}
const user = users[0];
const token = crypto.randomBytes(32).toString('hex');
const expiresAt = new Date(Date.now() + 30 * 60 * 1000);
await pool.query(
'INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)',
[user.id, token, expiresAt]
);
res.json({ token });
} catch (err) {
res.status(400).json({ message: 'Error generating reset token' });
}
});
app.get('/reset-password/:token', async (req, res) => {
const { token } = req.params;
try {
const [rows] = await pool.query(
'SELECT * FROM password_resets WHERE token = ?',
[token]
);
if (rows.length === 0) {
return res.status(400).json({ message: 'Invalid or expired token' });
}
const record = rows[0];
if (new Date(record.expires_at) < new Date()) {
return res.status(400).json({ message: 'Invalid or expired token' });
}
res.json({ message: 'Token is valid' });
} catch (err) {
res.status(400).json({ message: 'Error validating token' });
}
});
app.post('/reset-password/:token', async (req, res) => {
const { token } = req.params;
const { password } = req.body;
if (!password) {
return res.status(400).json({ message: 'Password is required' });
}
try {
const [rows] = await pool.query(
'SELECT * FROM password_resets WHERE token = ?',
[token]
);
if (rows.length === 0) {
return res.status(400).json({ message: 'Invalid or expired token' });
}
const record = rows[0];
if (new Date(record.expires_at) < new Date()) {
return res.status(400).json({ message: 'Invalid or expired token' });
}
const hashedPassword = await bcrypt.hash(password, 10);
await pool.query(
'UPDATE users SET password = ? WHERE id = ?',
[hashedPassword, record.user_id]
);
await pool.query(
'DELETE FROM password_resets WHERE token = ?',
[token]
);
res.json({ message: 'Password reset successful' });
} catch (err) {
res.status(400).json({ message: 'Error resetting password' });
}
});
const PORT = 3000;
app.listen(PORT, () => {
console.log(Server running on port ${PORT});
});