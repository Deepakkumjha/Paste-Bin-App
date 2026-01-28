# Pastebin-Lite (Django)

A minimal Pastebin-like application that allows users to create text pastes, share a link, and view them until they expire based on time (TTL) or view count.

This project was implemented as a take-home assignment with a focus on API correctness, persistence, and predictable behavior under automated testing. UI styling is intentionally minimal.

--------------------------------------------------

FEATURES

- Create a paste containing arbitrary text
- Optional paste constraints:
  - Time-based expiry (TTL)
  - View-count limit
- Receive a shareable URL for each paste
- View pastes via JSON API or HTML page
- Pastes become unavailable once any constraint is triggered
- Deterministic time handling for automated tests

--------------------------------------------------

TECH STACK

- Backend: Django
- Database: SQLite (persistent storage)
- API: JSON-based HTTP endpoints
- UI: Minimal HTML templates

--------------------------------------------------

ROUTES

Health Check
GET /api/healthz
Returns HTTP 200 with JSON response: { "ok": true }

--------------------------------------------------

Create Paste (API)
POST /api/pastes

Request body:
{
  "content": "string",
  "ttl_seconds": 60,
  "max_views": 5
}

Response:
{
  "id": "uuid",
  "url": "http://<host>/p/<id>"
}

--------------------------------------------------

Fetch Paste (API)
GET /api/pastes/<id>

Response:
{
  "content": "string",
  "remaining_views": 4,
  "expires_at": "2026-01-01T00:00:00.000Z"
}

Notes:
- remaining_views is null if unlimited
- expires_at is null if no TTL
- each successful fetch counts as a view
- expired or unavailable pastes return HTTP 404

--------------------------------------------------

View Paste (HTML)
GET /p/<id>

- Returns an HTML page containing the paste content
- Paste content is rendered safely (no script execution)
- Expired or unavailable pastes return HTTP 404

--------------------------------------------------

RUN LOCALLY

1. Create virtual environment and activate it
2. Install dependencies
3. Run migrations
4. Start server

Example:
python manage.py migrate
python manage.py runserver

--------------------------------------------------

PERSISTENCE

SQLite is used as the persistence layer. It provides durable storage across requests and is sufficient for the scope of this assignment.

--------------------------------------------------

DESIGN NOTES

- Paste expiry is enforced using stored expires_at timestamps
- View limits are enforced using a remaining_views counter
- Core availability logic is centralized in the model
- API and HTML routes share the same business rules
- The project avoids global mutable state and hardcoded URLs

--------------------------------------------------

STATUS

This project satisfies all functional, UI, and robustness requirements described in the assignment.
