// SAMPLE_28_API_NODEJS
const express = require('express');
const mongoose = require('mongoose');
const app = express();
const port = 3000;

app.use(express.json());

mongoose.connect('mongodb://localhost:27017/booksdb');

const bookSchema = new mongoose.Schema({
  title: { type: String, required: true },
  author: { type: String, required: true },
  isbn: String,
  publishedYear: Number,
  genre: String,
  createdAt: { type: Date, default: Date.now }
});

const Book = mongoose.model('Book', bookSchema);

app.get('/api/books', async (req, res) => {
  try {
    const { genre } = req.query;
    const query = genre ? { genre } : {};
    const books = await Book.find(query);
    res.json(books);
  } catch (err) {
    res.status(500).send(err);
  }
});

app.get('/api/books/:id', async (req, res) => {
  try {
    const book = await Book.findById(req.params.id);
    if (!book) return res.status(404).send();
    res.json(book);
  } catch (err) {
    res.status(500).send(err);
  }
});

app.post('/api/books', async (req, res) => {
  try {
    const book = new Book(req.body);
    await book.save();
    res.status(201).json(book);
  } catch (err) {
    if (err.name === 'ValidationError') {
      return res.status(400).send(err);
    }
    res.status(500).send(err);
  }
});

app.put('/api/books/:id', async (req, res) => {
  try {
    const book = await Book.findByIdAndUpdate(req.params.id, req.body, { new: true, runValidators: true });
    if (!book) return res.status(404).send();
    res.json(book);
  } catch (err) {
    if (err.name === 'ValidationError') {
      return res.status(400).send(err);
    }
    res.status(500).send(err);
  }
});

app.delete('/api/books/:id', async (req, res) => {
  try {
    const book = await Book.findByIdAndDelete(req.params.id);
    if (!book) return res.status(404).send();
    res.json(book);
  } catch (err) {
    res.status(500).send(err);
  }
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});