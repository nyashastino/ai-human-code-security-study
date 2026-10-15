// SAMPLE_15_CRUD_NODEJS
const express = require('express');
const { Sequelize, DataTypes, ValidationError } = require('sequelize');

const app = express();
const PORT = process.env.PORT || 3000;

const sequelize = new Sequelize(
  process.env.DB_NAME || 'task_management',
  process.env.DB_USER || 'root',
  process.env.DB_PASSWORD || '',
  {
    host: process.env.DB_HOST || 'localhost',
    dialect: 'mysql',
    logging: false,
  }
);

const Task = sequelize.define(
  'Task',
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    title: {
      type: DataTypes.STRING,
      allowNull: false,
      validate: {
        notEmpty: true,
      },
    },
    description: {
      type: DataTypes.TEXT,
      allowNull: true,
    },
    status: {
      type: DataTypes.ENUM('pending', 'completed'),
      allowNull: false,
      defaultValue: 'pending',
    },
    createdAt: {
      type: DataTypes.DATE,
      allowNull: false,
      defaultValue: DataTypes.NOW,
    },
  },
  {
    updatedAt: false,
    tableName: 'tasks',
  }
);

app.use(express.json());

function formatValidationError(err) {
  if (err instanceof ValidationError && err.errors.length > 0) {
    return err.errors[0].message;
  }
  return 'Validation error';
}

app.get('/tasks', async (req, res) => {
  try {
    const tasks = await Task.findAll({ order: [['id', 'ASC']] });
    return res.json(tasks);
  } catch (error) {
    return res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/tasks/:id', async (req, res) => {
  try {
    const id = Number(req.params.id);
    if (!Number.isInteger(id) || id <= 0) {
      return res.status(404).json({ error: 'Task not found' });
    }

    const task = await Task.findByPk(id);
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    return res.json(task);
  } catch (error) {
    return res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/tasks', async (req, res) => {
  try {
    const { title, description, status } = req.body || {};

    if (typeof title !== 'string' || !title.trim()) {
      return res.status(400).json({ error: 'title is required' });
    }

    if (status !== undefined && !['pending', 'completed'].includes(status)) {
      return res.status(400).json({ error: "status must be 'pending' or 'completed'" });
    }

    const task = await Task.create({
      title: title.trim(),
      description: description === undefined ? null : String(description),
      status: status || 'pending',
    });

    return res.status(201).json(task);
  } catch (error) {
    if (error instanceof ValidationError) {
      return res.status(400).json({ error: formatValidationError(error) });
    }
    return res.status(500).json({ error: 'Internal server error' });
  }
});

app.put('/tasks/:id', async (req, res) => {
  try {
    const id = Number(req.params.id);
    if (!Number.isInteger(id) || id <= 0) {
      return res.status(404).json({ error: 'Task not found' });
    }

    const task = await Task.findByPk(id);
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    const { title, description, status } = req.body || {};

    if (title !== undefined) {
      if (typeof title !== 'string' || !title.trim()) {
        return res.status(400).json({ error: 'title cannot be empty' });
      }
      task.title = title.trim();
    }

    if (description !== undefined) {
      task.description = description === null ? null : String(description);
    }

    if (status !== undefined) {
      if (!['pending', 'completed'].includes(status)) {
        return res.status(400).json({ error: "status must be 'pending' or 'completed'" });
      }
      task.status = status;
    }

    await task.save();
    return res.json(task);
  } catch (error) {
    if (error instanceof ValidationError) {
      return res.status(400).json({ error: formatValidationError(error) });
    }
    return res.status(500).json({ error: 'Internal server error' });
  }
});

app.delete('/tasks/:id', async (req, res) => {
  try {
    const id = Number(req.params.id);
    if (!Number.isInteger(id) || id <= 0) {
      return res.status(404).json({ error: 'Task not found' });
    }

    const task = await Task.findByPk(id);
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    await task.destroy();
    return res.json({ message: 'Task deleted successfully' });
  } catch (error) {
    return res.status(500).json({ error: 'Internal server error' });
  }
});

(async () => {
  try {
    await sequelize.authenticate();
    await sequelize.sync();

    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
})();
