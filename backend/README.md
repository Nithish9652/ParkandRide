---

### ✅ `README.md`

```markdown
# 🗓️ FastAPI Parking Slot Booking System

This is a simple and modular FastAPI-based booking system for parking slots. It supports user authentication, slot booking, cancellation, occupancy tracking, and QR code generation for each reservation. All bookings are stored and replayed from a local log file.

---

## 🚀 Features

- 🔒 JWT-based Authentication
- 📅 Book parking slots by hour, day, or month
- ❌ Cancel bookings
- 📊 View occupancy at any datetime
- ✅ Slot availability check
- 🧾 Booking log stored in `realtime.log`
- 📦 Built with FastAPI, Pydantic, and Uvicorn

---

## 🛠️ Technologies Used

- FastAPI
- Python-Jose (JWT)
- Passlib (bcrypt)
- Python-dotenv
- Uvicorn (ASGI server)
- Logging to file + console

---

## 📁 Project Structure

```

project-root/
│
├── main.py
├── .env
├── requirements.txt
│
├── auth/
│   ├── routes.py
│   └── auth\_utils.py
│
├── models/
│   └── schemas.py
│
├── services/
│   └── booking\_service.py
│
├── utils/
│   └── logger.py
│
└── realtime.log

````

---

## 🧑‍💻 Getting Started

### 1. 🔁 Clone the repository

```bash
git clone https://github.com/yourusername/fastapi-booking-system.git
cd fastapi-booking-system
````

### 2. 🐍 Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. 📦 Install dependencies

```bash
pip install -r requirements.txt
```

### 4. 🔐 Set up your `.env` file

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## ▶️ Running the Server

```bash
uvicorn main:app --reload
```

The server will be available at:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 📬 API Endpoints

### 🔐 Auth

* `POST /auth/register` - Register a new user
* `POST /auth/login` - Get JWT token

### 📘 Bookings (Requires JWT token)

* `POST /book` - Book a slot
* `POST /cancel` - Cancel a booking
* `GET /occupancy?at=2025-06-22T14:00:00` - Get occupancy at a datetime
* `GET /slot-occupied?slot=0-1&at=2025-06-22T14:00:00` - Check if a specific slot is occupied
* `POST /find-slot?start=...&end=...` - Find a free slot

You can test all endpoints using:

* [Swagger UI](http://127.0.0.1:8000/docs)
* [ReDoc](http://127.0.0.1:8000/redoc)

---

## 📝 Logging

All bookings and cancellations are logged to:

```
realtime.log
```

They are also printed in the terminal.

---

## ✅ Example `.env`

```env
SECRET_KEY=supersecretkey123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 📌 Notes

* This app uses in-memory storage + log replay for simplicity.
* For production, integrate with a real database (like PostgreSQL or MongoDB).
* Use HTTPS and rotate JWT secrets securely.

---

## 📜 License

This project is licensed under the MIT License.

```

---
