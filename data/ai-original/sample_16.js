// SAMPLE_16_CRUD_NODEJS
const express = require('express');
const mysql = require('mysql2/promise');
const app = express();
app.use(express.json());
const pool = mysql.createPool({
host: 'localhost',
user: 'root',
password: '',
database: 'company_db'
});
const initDB = async () => {
const conn = await pool.getConnection();
await conn.query( CREATE TABLE IF NOT EXISTS employees ( id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL, department VARCHAR(255) NOT NULL, salary DECIMAL(10,2), email VARCHAR(255) UNIQUE NOT NULL, hire_date DATE ) );
conn.release();
};
initDB();
app.get('/employees', async (req, res) => {
try {
const [rows] = await pool.query('SELECT * FROM employees');
res.json(rows);
} catch (err) {
res.status(400).json({ message: 'Error fetching employees' });
}
});
app.get('/employees/:id', async (req, res) => {
try {
const [rows] = await pool.query('SELECT * FROM employees WHERE id = ?', [req.params.id]);
if (rows.length === 0) {
return res.status(404).json({ message: 'Employee not found' });
}
res.json(rows[0]);
} catch (err) {
res.status(400).json({ message: 'Invalid request' });
}
});
app.post('/employees', async (req, res) => {
const { name, department, salary, email, hire_date } = req.body;
if (!name || !department || !email) {
return res.status(400).json({ message: 'Missing required fields' });
}
try {
const [result] = await pool.query(
'INSERT INTO employees (name, department, salary, email, hire_date) VALUES (?, ?, ?, ?, ?)',
[name, department, salary || null, email, hire_date || null]
);
const [rows] = await pool.query('SELECT * FROM employees WHERE id = ?', [result.insertId]);
res.status(201).json(rows[0]);
} catch (err) {
res.status(400).json({ message: 'Error creating employee' });
}
});
app.put('/employees/:id', async (req, res) => {
const { name, department, salary, email, hire_date } = req.body;
try {
const [rows] = await pool.query('SELECT * FROM employees WHERE id = ?', [req.params.id]);
if (rows.length === 0) {
return res.status(404).json({ message: 'Employee not found' });
}
const employee = rows[0];
const updatedName = name !== undefined ? name : employee.name;
const updatedDepartment = department !== undefined ? department : employee.department;
const updatedSalary = salary !== undefined ? salary : employee.salary;
const updatedEmail = email !== undefined ? email : employee.email;
const updatedHireDate = hire_date !== undefined ? hire_date : employee.hire_date;
await pool.query(
'UPDATE employees SET name = ?, department = ?, salary = ?, email = ?, hire_date = ? WHERE id = ?',
[updatedName, updatedDepartment, updatedSalary, updatedEmail, updatedHireDate, req.params.id]
);
const [updatedRows] = await pool.query('SELECT * FROM employees WHERE id = ?', [req.params.id]);
res.json(updatedRows[0]);
} catch (err) {
res.status(400).json({ message: 'Error updating employee' });
}
});
app.delete('/employees/:id', async (req, res) => {
try {
const [result] = await pool.query('DELETE FROM employees WHERE id = ?', [req.params.id]);
if (result.affectedRows === 0) {
return res.status(404).json({ message: 'Employee not found' });
}
res.json({ message: 'Employee deleted' });
} catch (err) {
res.status(400).json({ message: 'Error deleting employee' });
}
});
const PORT = 3000;
app.listen(PORT, () => {
console.log(Server running on port ${PORT});
});