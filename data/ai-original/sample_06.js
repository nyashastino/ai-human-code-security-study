// SAMPLE_06_AUTH_NODEJS
const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());
const JWT_SECRET = 'your_jwt_secret';
const MONGO_URI = 'mongodb://127.0.0.1:27017/auth_db';
mongoose.connect(MONGO_URI, {
useNewUrlParser: true,
useUnifiedTopology: true
});
const userSchema = new mongoose.Schema({
username: { type: String, required: true },
email: { type: String, required: true, unique: true },
password: { type: String, required: true }
});
const User = mongoose.model('User', userSchema);
const authMiddleware = async (req, res, next) => {
const authHeader = req.headers['authorization'];
if (!authHeader || !authHeader.startsWith('Bearer ')) {
return res.status(401).json({ message: 'Missing token' });
}
const token = authHeader.split(' ')[1];
try {
const decoded = jwt.verify(token, JWT_SECRET);
const user = await User.findById(decoded.id).select('-password');
if (!user) {
return res.status(401).json({ message: 'Invalid token' });
}
req.user = user;
next();
} catch (err) {
return res.status(401).json({ message: 'Invalid token' });
}
};
app.post('/api/auth/register', async (req, res) => {
const { username, email, password } = req.body;
if (!username || !email || !password) {
return res.status(400).json({ message: 'Validation error' });
}
try {
const existingUser = await User.findOne({ email });
if (existingUser) {
return res.status(400).json({ message: 'User already exists' });
}
const hashedPassword = await bcrypt.hash(password, 10);
const user = new User({
username,
email,
password: hashedPassword
});
await user.save();
res.status(201).json({ message: 'User created' });
} catch (err) {
res.status(400).json({ message: 'Error creating user' });
}
});
app.post('/api/auth/login', async (req, res) => {
const { email, password } = req.body;
if (!email || !password) {
return res.status(400).json({ message: 'Validation error' });
}
try {
const user = await User.findOne({ email });
if (!user) {
return res.status(400).json({ message: 'Invalid credentials' });
}
const isMatch = await bcrypt.compare(password, user.password);
if (!isMatch) {
return res.status(400).json({ message: 'Invalid credentials' });
}
const token = jwt.sign(
{ id: user._id },
JWT_SECRET,
{ expiresIn: '24h' }
);
res.json({ token });
} catch (err) {
res.status(400).json({ message: 'Login failed' });
}
});
app.get('/api/profile', authMiddleware, async (req, res) => {
res.json(req.user);
});
const PORT = 3000;
app.listen(PORT, () => {
console.log(Server running on port ${PORT});
});