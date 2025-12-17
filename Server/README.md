# FastAPI Server

A simple FastAPI server template following a straightforward structure.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the `Server/` directory:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
# Or for SQLite: DATABASE_URL=sqlite:///./app.db
DEBUG=False
SECRET_KEY=your-secret-key-here
```

## Running the Server

You can start the server in two ways:

### Method 1: Run main.py directly (Recommended)
```bash
cd Server
python main.py
```

### Method 2: Use uvicorn command
```bash
cd Server
uvicorn main:app --reload
```

The server will be available at `http://localhost:8000`

**Note:** The database connection will be tested automatically on startup. Check the logs to see if the connection is successful.

## Project Structure

```
Server/
├── main.py              # FastAPI app entry
├── config.py            # Environment variables & settings
├── db.py                # Database connection (with logger)
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas/DTOs
├── utils.py             # Helper functions
├── routes/              # API routes (HTTP layer)
│   ├── auth.py
│   ├── users.py
│   └── bookings.py
└── controllers/         # Business logic
    ├── auth_controller.py
    ├── user_controller.py
    └── booking_controller.py
```

## API Endpoints

### General
- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

### Auth
- `POST /auth/login` - Login user

### Users
- `POST /users/` - Create a new user
- `GET /users/{user_id}` - Get user by ID

### Bookings
- `POST /bookings/` - Create a new booking
- `GET /bookings/{booking_id}` - Get booking by ID

## API Documentation

Once the server is running, you can access:
- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

## Database Connection Logger

The database connection is automatically tested on startup. You'll see logs like:
- ✅ `Database connection successful!` - Connection works
- ❌ `Database connection failed: [error]` - Connection failed (check your DATABASE_URL)

