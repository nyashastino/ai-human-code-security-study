// SAMPLE_14_CRUD_NODEJS
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());
const MONGO_URI = 'mongodb://127.0.0.1:27017/products_db';
mongoose.connect(MONGO_URI, {
useNewUrlParser: true,
useUnifiedTopology: true
});
const productSchema = new mongoose.Schema({
name: { type: String, required: true },
description: { type: String },
price: { type: Number, required: true },
quantity: { type: Number, default: 0 },
createdAt: { type: Date, default: Date.now }
});
const Product = mongoose.model('Product', productSchema);
app.get('/api/products', async (req, res) => {
const products = await Product.find();
res.json(products);
});
app.get('/api/products/:id', async (req, res) => {
try {
const product = await Product.findById(req.params.id);
if (!product) {
return res.status(404).json({ message: 'Product not found' });
}
res.json(product);
} catch (err) {
res.status(400).json({ message: 'Invalid product ID' });
}
});
app.post('/api/products', async (req, res) => {
const { name, description, price, quantity } = req.body;
if (!name || price === undefined) {
return res.status(400).json({ message: 'Invalid input' });
}
try {
const product = new Product({ name, description, price, quantity });
await product.save();
res.status(201).json(product);
} catch (err) {
res.status(400).json({ message: 'Error creating product' });
}
});
app.put('/api/products/:id', async (req, res) => {
try {
const product = await Product.findById(req.params.id);
if (!product) {
return res.status(404).json({ message: 'Product not found' });
}
const { name, description, price, quantity } = req.body;
if (name !== undefined) product.name = name;
if (description !== undefined) product.description = description;
if (price !== undefined) product.price = price;
if (quantity !== undefined) product.quantity = quantity;
await product.save();
res.json(product);
} catch (err) {
res.status(400).json({ message: 'Invalid input' });
}
});
app.delete('/api/products/:id', async (req, res) => {
try {
const product = await Product.findByIdAndDelete(req.params.id);
if (!product) {
return res.status(404).json({ message: 'Product not found' });
}
res.json({ message: 'Product deleted' });
} catch (err) {
res.status(400).json({ message: 'Invalid product ID' });
}
});
const PORT = 3000;
app.listen(PORT, () => {
console.log(`Server running on port ${PORT}`);
});