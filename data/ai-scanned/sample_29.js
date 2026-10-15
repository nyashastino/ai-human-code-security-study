// SAMPLE_29_API_NODEJS
const express = require('express');
const mysql = require('mysql2/promise');
const app = express();
app.use(express.json());
const pool = mysql.createPool({
host: 'localhost',
user: 'root',
password: '',
database: 'todo_db'
});
const initDB = async () => {
const conn = await pool.getConnection();
await conn.query( `CREATE TABLE IF NOT EXISTS todos ( id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255) NOT NULL, description TEXT, completed BOOLEAN DEFAULT FALSE, created_at DATETIME DEFAULT CURRENT_TIMESTAMP )` );
conn.release();
};
initDB();
app.get('/api/todos', async (req, res) => {
try {
const { completed } = req.query;
let query = 'SELECT * FROM todos';
let params = [];
if (completed !== undefined) {
query += ' WHERE completed = ?';
params.push(completed === 'true');
}
const [rows] = await pool.query(query, params);
res.json(rows);
} catch (err) {
res.status(400).json({ message: 'Error fetching todos' });
}
});
app.get('/api/todos/:id', async (req, res) => {
try {
const [rows] = await pool.query('SELECT * FROM todos WHERE id = ?', [req.params.id]);
if (rows.length === 0) {
return res.status(404).json({ message: 'Todo not found' });
}
res.json(rows[0]);
} catch (err) {
res.status(400).json({ message: 'Invalid request' });
}
});
app.post('/api/todos', async (req, res) => {
const { title, description, completed } = req.body;
if (!title) {
return res.status(400).json({ message: 'Title is required' });
}
try {
const [result] = await pool.query(
'INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)',
[title, description || null, completed !== undefined ? completed : false]
);
const [rows] = await pool.query('SELECT * FROM todos WHERE id = ?', [result.insertId]);
res.status(201).json(rows[0]);
} catch (err) {
res.status(400).json({ message: 'Error creating todo' });
}
});
app.put('/api/todos/:id', async (req, res) => {
const { title, description, completed } = req.body;
try {
const [rows] = await pool.query('SELECT * FROM todos WHERE id = ?', [req.params.id]);
if (rows.length === 0) {
return res.status(404).json({ message: 'Todo not found' });
}
const todo = rows[0];
const updatedTitle = title !== undefined ? title : todo.title;
const updatedDescription = description !== undefined ? description : todo.description;
const updatedCompleted = completed !== undefined ? completed : todo.completed;
await pool.query(
'UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?',
[updatedTitle, updatedDescription, updatedCompleted, req.params.id]
);
const [updatedRows] = await pool.query('SELECT * FROM todos WHERE id = ?', [req.params.id]);
res.json(updatedRows[0]);
} catch (err) {
res.status(400).json({ message: 'Error updating todo' });
}
});
app.delete('/api/todos/:id', async (req, res) => {
try {
const [result] = await pool.query('DELETE FROM todos WHERE id = ?', [req.params.id]);
if (result.affectedRows === 0) {
return res.status(404).json({ message: 'Todo not found' });
}
res.json({ message: 'Todo deleted' });
} catch (err) {
res.status(400).json({ message: 'Error deleting todo' });
}
});
const PORT = 3000;
app.listen(PORT, () => {
console.log(`Server running on port ${PORT}`);
});