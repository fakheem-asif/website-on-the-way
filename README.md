# Lumiere — Minimalist Beauty Studio

A minimalist beauty salon website with a full Node/Express backend, Three.js 3D hero, GSAP scroll animations, and complete booking/reviews/contact flows.

## Stack

- **Backend**: Node.js + Express (REST API, JSON file persistence)
- **Frontend**: Vanilla HTML/CSS/JS
- **3D graphics**: Three.js (particle field, soft glass icosahedron, dual rings)
- **Animations**: GSAP + ScrollTrigger, Lenis smooth scroll
- **Type**: Fraunces (serif) + Inter (sans)

## Features

- Quiet, editorial layout — cream, ink, soft rose palette
- 3D Three.js hero scene with mouse-parallax camera
- Scroll-driven section reveals, clip-path titles, magnetic CTAs
- Custom cursor (dot + ring)
- Smooth Lenis scroll, scroll-progress bar, side-nav dots
- Services menu loaded from API
- Reviews carousel + leave-a-review form (POST → API)
- Bookings form with date/time/service (POST → API)
- Contact form (POST → API)
- Live stats fed by API (review count, avg rating, years)

## Run

```bash
npm install
npm start
# open http://localhost:3000
```

## API

| Method | Endpoint        | Purpose            |
| ------ | --------------- | ------------------ |
| GET    | /api/health     | Health check       |
| GET    | /api/services   | List services      |
| GET    | /api/reviews    | List reviews       |
| POST   | /api/reviews    | Add a review       |
| POST   | /api/bookings   | Create a booking   |
| GET    | /api/bookings   | List bookings      |
| POST   | /api/contacts   | Submit contact msg |
| GET    | /api/stats      | Live stats         |

## Structure

```
.
├── server/index.js          # Express API + static serving
├── public/
│   ├── index.html           # Markup
│   ├── css/styles.css       # Minimal palette + layout
│   └── js/
│       ├── three-scene.js   # 3D hero
│       └── app.js           # GSAP + API + forms
└── data/                    # JSON persistence (auto-seeded)
```
