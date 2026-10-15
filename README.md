# CodeAlpha_CloudBusPassSystem

A Flask-based cloud-ready online bus ticket/Bus Pass booking application for the CodeAlpha Cloud Computing Internship **Task 3: Cloud-Based Bus Pass System**.

## Features

- Online bus ticket booking interface.
- Predefined routes and server-side pricing.
- Booking confirmation reference such as `CAP-AB12CD34`.
- Booking lookup API.
- Input validation and seat limits.
- Parameterized SQL queries to reduce SQL injection risk.
- Server-side price calculation prevents incorrect client-side pricing.
- Database uniqueness for booking references.
- Automated pytest tests.
- Dockerfile and Procfile for cloud deployment.

## Project structure

```text
CodeAlpha_CloudBusPassSystem/
├── app.py
├── requirements.txt
├── Procfile
├── Dockerfile
├── README.md
├── .gitignore
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── tests/
    └── test_app.py
```

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5001`.

## Test

```bash
pytest -q
```

## API

### Create booking

`POST /api/bookings`

Example JSON:

```json
{
  "passenger_name": "Ayaan Qureshi",
  "email": "ayaan@example.com",
  "route": "Delhi - Jaipur",
  "travel_date": "2026-12-01",
  "seats": 2
}
```

### Get booking

`GET /api/bookings/<BOOKING_REFERENCE>`

## Cloud deployment

The project includes both a `Procfile` and `Dockerfile`.

Typical Gunicorn command:

```bash
gunicorn --bind 0.0.0.0:5001 app:app
```

For a real production system, use a managed PostgreSQL/MySQL database, HTTPS, a proper authentication system, payment gateway, centralized logging, and cloud autoscaling.

## Internship task mapping

| Requirement | Implementation |
|---|---|
| Online ticket booking | Flask web UI + `/api/bookings` |
| Prevent ticket loss/theft/incorrect pricing | Persistent DB + secure random booking ref + server-side price |
| High traffic/scalability | Stateless Flask app + Gunicorn/Docker deployment model |
| Reliability | Validation, DB constraints and automated tests |
| Test/deploy | Pytest + Dockerfile + Procfile |

## Demo

1. Select a route.
2. Choose a date and number of seats.
3. Submit the form.
4. Save the generated `CAP-...` booking reference.
5. Use the lookup section to retrieve the booking.

## Author

CodeAlpha Cloud Computing Internship project.
