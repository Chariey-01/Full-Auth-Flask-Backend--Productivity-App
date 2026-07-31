# Productivity App API

A simple Flask REST API for a productivity app. Users can sign up, log in, and manage their own personal notes. Every note belongs to exactly one user, and users can only see, edit, or delete their own notes.

## Libraries Used

| Library | What it does in this project |
|---|---|
| **Flask** | The web framework itself. Handles incoming HTTP requests and routes them to the right function (e.g. `POST /signup`). |
| **Flask-SQLAlchemy** | Connects Flask to the database and lets us define `User` and `Note` as Python classes (models) instead of writing raw SQL. |
| **Flask-Migrate** | Tracks changes to the models over time and turns them into migration files, so the database schema can be created/updated with a command instead of manually editing tables. |
| **Flask-Bcrypt** | Hashes passwords before they are saved, and checks a plain-text password against the stored hash at login. Passwords are never stored as plain text. |
| **Flask-JWT-Extended** | Creates a JWT (JSON Web Token) when a user logs in, and protects routes with `@jwt_required()` so only requests with a valid token can reach them. It also lets a route read `get_jwt_identity()` to know which user made the request. |
| **Marshmallow** | Installed per the lab requirements for schema-based serialization/validation. This project ended up using simple manual checks in the routes instead (e.g. checking `if not title`), since the validation needs were small enough not to need a full schema. |
| **Faker** | Used only in `seed.py` to generate realistic-looking fake usernames, note titles, and note content for testing. |

## Project Structure

```
app.py          - creates and configures the Flask app
config.py       - configuration (database URI, secret keys)
extensions.py   - sets up db, migrate, bcrypt, and jwt objects
models.py       - User and Note database models
resources.py    - all the routes (signup, login, me, notes CRUD)
seed.py         - fills the database with fake test data
migrations/     - Flask-Migrate migration files
```

## Installation

This project uses `pipenv` to manage dependencies.

```bash
pipenv install
pipenv shell
```

## Migration

Set the Flask app entry point and run the migration commands:

```bash
export FLASK_APP=app.py
flask db upgrade
```

This creates `app.db` (a SQLite database) with the `users` and `notes` tables.

If you ever change the models, generate a new migration with:

```bash
flask db migrate -m "describe your change"
flask db upgrade
```

## Seeding the Database

To fill the database with sample users and notes:

```bash
python seed.py
```

Every seeded user has the password `password123`. Running the script again will **not** create duplicate users — it checks first and skips anyone who already exists.

## Running the App

```bash
python app.py
```

The API will be available at `http://127.0.0.1:5000`.

## Endpoint Documentation

### Auth

| Method | Endpoint | Description | Auth required? |
|---|---|---|---|
| POST | `/signup` | Create a new user. Body: `{"username": "...", "password": "..."}`. Password must be at least 6 characters, username must be unique. | No |
| POST | `/login` | Log in and receive a JWT access token. Body: `{"username": "...", "password": "..."}`. | No |
| GET | `/me` | Get the currently logged-in user's info. | Yes |

### Notes

All notes routes require a JWT sent as a header: `Authorization: Bearer <token>`. Users only ever see or affect their own notes — trying to access another user's note returns a `404`.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/notes?page=1&per_page=10` | List the current user's notes, paginated. Returns `notes`, `total`, `page`, `per_page`, and `pages`. |
| POST | `/notes` | Create a note. Body: `{"title": "...", "content": "..."}`. Both fields are required. |
| GET | `/notes/<id>` | Get a single note by id. |
| PATCH | `/notes/<id>` | Update a note's title and/or content. Body can include either or both fields. |
| DELETE | `/notes/<id>` | Delete a note. |

### Example: signing up, logging in, and creating a note on thunder client (check thde screenshot)

```bash
POST http://127.0.0.1:5000/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'

 POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'
# copy the access_token from the respons

 POST http://127.0.0.1:5000/notes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"title": "My first note", "content": "Hello world"}'
```
