// SAMPLE_30_API_NODEJS
const express = require('express');
const mysql = require('mysql2');
const app = express();

app.use(express.json());

const db = mysql.createConnection({
host: 'localhost',
user: 'root',
password: 'password',
database: 'employee_db'
});

db.connect(err => {
if (err) throw err;
console.log('MySQL Connected');
});

app.get('/api/employees', (req, res) => {
const { department } = req.query;
let sql = 'SELECT * FROM employees';
let params = [];

if (department) {
sql += ' WHERE department = ?';
params.push(department);
}

db.query(sql, params, (err, results) => {
if (err) return res.status(500).json(err);
res.json(results);
});
});

app.get('/api/employees/:id', (req, res) => {
db.query('SELECT * FROM employees WHERE id = ?', [req.params.id], (err, results) => {
if (err) return res.status(500).json(err);
if (results.length === 0) return res.status(404).json({ message: 'Employee not found' });
res.json(results[0]);
});
});

app.post('/api/employees', (req, res) => {
const { name, department, job_title, email, salary, hire_date } = req.body;

if (!name || !department || !email) {
return res.status(400).json({ message: 'Missing required fields' });
}

const sql = 'INSERT INTO employees (name, department, job_title, email, salary, hire_date) VALUES (?, ?, ?, ?, ?, ?)';
db.query(sql, [name, department, job_title, email, salary, hire_date], (err, result) => {
if (err) return res.status(500).json(err);
res.json({ id: result.insertId, name, department, job_title, email, salary, hire_date });
});
});

app.put('/api/employees/:id', (req, res) => {
const fields = [];
const values = [];

Object.keys(req.body).forEach(key => {
fields.push(`${key} = ?`);
values.push(req.body[key]);
});

if (fields.length === 0) {
return res.status(400).json({ message: 'No fields to update' });
}

values.push(req.params.id);

const sql = `UPDATE employees SET ${fields.join(', ')} WHERE id = ?`;

db.query(sql, values, (err, result) => {
if (err) return res.status(500).json(err);
if (result.affectedRows === 0) return res.status(404).json({ message: 'Employee not found' });
res.json({ message: 'Employee updated' });
});
});

app.delete('/api/employees/:id', (req, res) => {
db.query('DELETE FROM employees WHERE id = ?', [req.params.id], (err, result) => {
if (err) return res.status(500).json(err);
if (result.affectedRows === 0) return res.status(404).json({ message: 'Employee not found' });
res.json({ message: 'Employee deleted' });
});
});

app.listen(3000, () => {
console.log('Server running on port 3000');
});