// SAMPLE_07_AUTH_NODEJS
const express = require('express');
const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

const app = express();

const PORT = process.env.PORT || 3000;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/auth_rbac_app';
const JWT_SECRET = process.env.JWT_SECRET || 'change-this-jwt-secret';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '2h';
const SALT_ROUNDS = 12;

app.use(express.json());

const userSchema = new mongoose.Schema(
  {
    username: {
      type: String,
      required: true,
      trim: true,
    },
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
    },
    passwordHash: {
      type: String,
      required: true,
    },
    role: {
      type: String,
      enum: ['admin', 'moderator', 'user'],
      required: true,
      default: 'user',
    },
  },
  { timestamps: true }
);

const User = mongoose.model('User', userSchema);

function signToken(user) {
  return jwt.sign(
    {
      id: user._id.toString(),
      role: user.role,
    },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRES_IN }
  );
}

async function verifyToken(req, res, next) {
  const authHeader = req.headers.authorization || '';
  const [scheme, token] = authHeader.split(' ');

  if (scheme !== 'Bearer' || !token) {
    return res.status(403).json({ message: 'Forbidden' });
  }

  try {
    const payload = jwt.verify(token, JWT_SECRET);
    const user = await User.findById(payload.id).select('_id username email role');

    if (!user) {
      return res.status(403).json({ message: 'Forbidden' });
    }

    req.user = {
      id: user._id.toString(),
      username: user.username,
      email: user.email,
      role: user.role,
    };

    return next();
  } catch (error) {
    return res.status(403).json({ message: 'Forbidden' });
  }
}

function authorizeRoles(...allowedRoles) {
  return (req, res, next) => {
    if (!req.user || !allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ message: 'Forbidden' });
    }
    return next();
  };
}

app.post('/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: 'email and password are required' });
    }

    const normalizedEmail = String(email).trim().toLowerCase();
    const user = await User.findOne({ email: normalizedEmail });

    if (!user) {
      return res.status(401).json({ message: 'Invalid email or password' });
    }

    const isMatch = await bcrypt.compare(password, user.passwordHash);
    if (!isMatch) {
      return res.status(401).json({ message: 'Invalid email or password' });
    }

    const token = signToken(user);
    return res.json({ token });
  } catch (error) {
    return res.status(500).json({ message: 'Internal server error' });
  }
});

app.get('/admin', verifyToken, authorizeRoles('admin'), (req, res) => {
  return res.json({
    message: 'Admin content',
    user: req.user,
  });
});

app.get('/moderator', verifyToken, authorizeRoles('admin', 'moderator'), (req, res) => {
  return res.json({
    message: 'Moderator content',
    user: req.user,
  });
});

app.get('/user', verifyToken, (req, res) => {
  return res.json({
    message: 'User content',
    user: req.user,
  });
});

async function seedUsers() {
  const users = [
    { username: 'admin', email: 'admin@example.com', password: 'admin123', role: 'admin' },
    { username: 'moderator', email: 'moderator@example.com', password: 'moderator123', role: 'moderator' },
    { username: 'user', email: 'user@example.com', password: 'user123', role: 'user' },
  ];

  for (const item of users) {
    const existing = await User.findOne({ email: item.email });
    if (!existing) {
      const passwordHash = await bcrypt.hash(item.password, SALT_ROUNDS);
      await User.create({
        username: item.username,
        email: item.email,
        passwordHash,
        role: item.role,
      });
    }
  }
}

(async () => {
  try {
    await mongoose.connect(MONGO_URI);
    await seedUsers();

    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
})();
