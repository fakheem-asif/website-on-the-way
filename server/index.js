'use strict';

const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

const DATA_DIR = path.join(__dirname, '..', 'data');
const BOOKINGS_FILE = path.join(DATA_DIR, 'bookings.json');
const REVIEWS_FILE = path.join(DATA_DIR, 'reviews.json');
const CONTACTS_FILE = path.join(DATA_DIR, 'contacts.json');

if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });

function ensureFile(file, seed) {
  if (!fs.existsSync(file)) fs.writeFileSync(file, JSON.stringify(seed, null, 2));
}

ensureFile(BOOKINGS_FILE, []);
ensureFile(CONTACTS_FILE, []);
ensureFile(REVIEWS_FILE, [
  {
    id: 'r1',
    name: 'Sofia Martinez',
    rating: 5,
    service: 'Silk Press',
    text: 'Absolutely incredible. The atmosphere is calming, the team is genuine, and my hair has never looked healthier. I left feeling like a new person.',
    date: '2026-04-12'
  },
  {
    id: 'r2',
    name: 'Amelia Chen',
    rating: 5,
    service: 'Balayage',
    text: 'The color came out exactly as I imagined. Every detail was thought through — from the consultation to the final styling. Worth every penny.',
    date: '2026-03-28'
  },
  {
    id: 'r3',
    name: 'Jordan Blake',
    rating: 5,
    service: 'Keratin Treatment',
    text: 'Months later and my hair is still smooth and frizz-free. They listen, they care, and the results speak for themselves.',
    date: '2026-03-15'
  },
  {
    id: 'r4',
    name: 'Priya Sharma',
    rating: 5,
    service: 'Cut & Style',
    text: 'A truly luxurious experience. The minimalist studio is so peaceful and the stylist understood my hair texture immediately.',
    date: '2026-02-20'
  }
]);

function loadJson(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf-8')); }
  catch (e) { return []; }
}
function saveJson(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

app.use(cors());
app.use(bodyParser.json({ limit: '1mb' }));
app.use(express.static(path.join(__dirname, '..', 'public')));

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', time: new Date().toISOString() });
});

const SERVICES = [
  { id: 'cut',      name: 'Precision Cut',       duration: 60,  price: 85 },
  { id: 'color',    name: 'Color & Balayage',    duration: 180, price: 220 },
  { id: 'silk',     name: 'Silk Press',          duration: 120, price: 110 },
  { id: 'keratin',  name: 'Keratin Treatment',   duration: 180, price: 250 },
  { id: 'blowout',  name: 'Signature Blowout',   duration: 60,  price: 75 },
  { id: 'treat',    name: 'Deep Repair',         duration: 90,  price: 95 }
];

app.get('/api/services', (req, res) => res.json(SERVICES));

app.post('/api/bookings', (req, res) => {
  const { name, email, phone, service, date, time, notes } = req.body || {};
  if (!name || !email || !service || !date || !time) {
    return res.status(400).json({ ok: false, error: 'Missing required fields.' });
  }
  const booking = {
    id: 'b_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
    name: String(name).slice(0, 80),
    email: String(email).slice(0, 120),
    phone: phone ? String(phone).slice(0, 30) : '',
    service: String(service).slice(0, 60),
    date: String(date).slice(0, 12),
    time: String(time).slice(0, 8),
    notes: notes ? String(notes).slice(0, 500) : '',
    createdAt: new Date().toISOString(),
    status: 'pending'
  };
  const list = loadJson(BOOKINGS_FILE);
  list.push(booking);
  saveJson(BOOKINGS_FILE, list);
  res.json({ ok: true, booking });
});

app.get('/api/bookings', (req, res) => {
  res.json(loadJson(BOOKINGS_FILE));
});

app.get('/api/reviews', (req, res) => {
  const reviews = loadJson(REVIEWS_FILE);
  res.json(reviews);
});

app.post('/api/reviews', (req, res) => {
  const { name, rating, service, text } = req.body || {};
  if (!name || !rating || !text) {
    return res.status(400).json({ ok: false, error: 'Missing required fields.' });
  }
  const review = {
    id: 'r_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
    name: String(name).slice(0, 60),
    rating: Math.max(1, Math.min(5, parseInt(rating, 10) || 5)),
    service: service ? String(service).slice(0, 40) : '',
    text: String(text).slice(0, 800),
    date: new Date().toISOString().slice(0, 10)
  };
  const list = loadJson(REVIEWS_FILE);
  list.unshift(review);
  saveJson(REVIEWS_FILE, list);
  res.json({ ok: true, review });
});

app.post('/api/contacts', (req, res) => {
  const { name, email, message } = req.body || {};
  if (!name || !email || !message) {
    return res.status(400).json({ ok: false, error: 'Missing required fields.' });
  }
  const entry = {
    id: 'c_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
    name: String(name).slice(0, 80),
    email: String(email).slice(0, 120),
    message: String(message).slice(0, 1500),
    createdAt: new Date().toISOString()
  };
  const list = loadJson(CONTACTS_FILE);
  list.push(entry);
  saveJson(CONTACTS_FILE, list);
  res.json({ ok: true });
});

app.get('/api/stats', (req, res) => {
  const reviews = loadJson(REVIEWS_FILE);
  const bookings = loadJson(BOOKINGS_FILE);
  const avg = reviews.length
    ? (reviews.reduce((s, r) => s + (r.rating || 0), 0) / reviews.length)
    : 0;
  res.json({
    reviewCount: reviews.length,
    bookingCount: bookings.length,
    averageRating: Math.round(avg * 10) / 10,
    yearsOpen: 12
  });
});

app.listen(PORT, () => {
  console.log(`Lumiere server running at http://localhost:${PORT}`);
});
