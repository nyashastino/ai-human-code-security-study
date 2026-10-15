// SAMPLE_22_FORMS_NODEJS
const express = require('express');
const multer = require('multer');
const mysql = require('mysql2/promise');
const path = require('path');
const fs = require('fs');
const app = express();
const pool = mysql.createPool({
host: 'localhost',
user: 'root',
password: '',
database: 'file_uploads_db'
});
const initDB = async () => {
const conn = await pool.getConnection();
await conn.query( CREATE TABLE IF NOT EXISTS uploads ( id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255) NOT NULL, original_filename VARCHAR(255) NOT NULL, stored_filename VARCHAR(255) NOT NULL, size INT NOT NULL, upload_date DATETIME NOT NULL ) );
conn.release();
};
initDB();
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) {
fs.mkdirSync(uploadDir);
}
const storage = multer.diskStorage({
destination: (req, file, cb) => {
cb(null, uploadDir);
},
filename: (req, file, cb) => {
const uniqueName = Date.now() + '-' + Math.round(Math.random() * 1E9) + path.extname(file.originalname);
cb(null, uniqueName);
}
});
const fileFilter = (req, file, cb) => {
const allowedExt = ['.pdf', '.doc', '.docx'];
const ext = path.extname(file.originalname).toLowerCase();
if (!allowedExt.includes(ext)) {
return cb(new Error('Only PDF and Word documents are allowed'));
}
cb(null, true);
};
const upload = multer({
storage: storage,
limits: { fileSize: 5 * 1024 * 1024 },
fileFilter: fileFilter
});
app.post('/upload', (req, res) => {
upload.single('document')(req, res, async (err) => {
if (err instanceof multer.MulterError) {
if (err.code === 'LIMIT_FILE_SIZE') {
return res.status(400).json({ message: 'File size exceeds 5MB limit' });
}
return res.status(400).json({ message: err.message });
} else if (err) {
return res.status(400).json({ message: err.message });
}
    const title = req.body.title;
    if (!title) {
        return res.status(400).json({ message: 'Title is required' });
    }

    if (!req.file) {
        return res.status(400).json({ message: 'File is required' });
    }

    try {
        const { originalname, filename, size } = req.file;
        const uploadDate = new Date();

        const [result] = await pool.query(
            'INSERT INTO uploads (title, original_filename, stored_filename, size, upload_date) VALUES (?, ?, ?, ?, ?)',
            [title, originalname, filename, size, uploadDate]
        );

        res.status(200).json({
            id: result.insertId,
            stored_filename: filename
        });
    } catch (e) {
        res.status(400).json({ message: 'Error saving file metadata' });
    }
});
});
const PORT = 3000;
app.listen(PORT, () => {
console.log(Server running on port ${PORT});
});