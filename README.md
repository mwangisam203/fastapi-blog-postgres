# FastAPI Blog

A full-stack blog application built with FastAPI, SQLAlchemy, Jinja2 templates, Bootstrap, and vanilla JavaScript.

This project started as a simple blog page and has grown into a real web app with users, authentication, post CRUD, profile pictures, pagination, password reset flow, custom error handling, and seed data.

## What The App Does

- Shows a home feed of blog posts ordered by newest first.
- Provides dedicated announcement and monthly post-calendar views.
- Loads more posts with JavaScript pagination instead of a full page refresh.
- Lets users register, log in, and keep a JWT access token in localStorage.
- Lets authenticated users create posts from the navbar modal.
- Lets post owners edit or delete their own posts.
- Lets authenticated users comment on posts and edit or delete their own comments.
- Shows public like and comment totals on every post card.
- Shows individual post pages.
- Shows user-specific post pages.
- Lets users update their username and email.
- Lets users upload and preview profile pictures.
- Lets users change their password from the account page.
- Supports forgot-password and reset-password pages.
- Stores reset tokens hashed in the database.
- Tracks a `likes` counter on post records.
- Lets signed-in users like a post once and withdraw their like with the same button.
- Seeds the database with users, posts, and profile images uploaded to S3.
- Serves static assets from `static/` and profile image URLs from S3.
- Returns JSON errors for `/api/...` routes and HTML error pages for browser routes.
- Provides a `/health` endpoint that checks database connectivity.

## Tech Stack

| Area | Tools |
| --- | --- |
| Backend | Python 3.12, FastAPI |
| Server | Uvicorn / FastAPI standard CLI |
| Database | PostgreSQL or SQLite through `DATABASE_URL` with async SQLAlchemy |
| ORM | SQLAlchemy 2.x async models and sessions |
| Migrations | Alembic |
| Validation | Pydantic |
| Auth | JWT, OAuth2 password form, pwdlib Argon2 password hashing |
| Templates | Jinja2 |
| Frontend | HTML, CSS, Bootstrap 5, vanilla JavaScript modules |
| Images | Pillow for profile image processing, S3-compatible storage through boto3 |
| Email | aiosmtplib for password reset email |
| Seeding | httpx ASGITransport against the local FastAPI app |
| Testing | pytest, httpx AsyncClient, Moto for mocked S3 |
| Container | Docker multi-stage build with `uv` |

## Project Structure

```text
fastapi-blog-postgres/
├── main.py                         # App setup, HTML page routes, error handlers
├── database.py                     # Async SQLAlchemy engine/session setup
├── models.py                       # SQLAlchemy User, Post, PasswordResetToken models
├── schemas.py                      # Pydantic request/response models
├── auth.py                         # Password hashing, JWT, reset-token hashing, current-user dependency
├── email_utils.py                  # Password reset email rendering/sending
├── image_utils.py                  # Profile image processing and S3 upload/delete
├── s3_checks.py                    # Small S3 upload/delete smoke test
├── populate_db.py                  # Clears and seeds users/posts/profile images
├── config.py                       # Environment-driven settings
├── routers/
│   ├── posts.py                    # JSON API for posts
│   └── users.py                    # JSON API for users/auth/password/profile images
├── templates/
│   ├── layout.html                 # Base layout, navbar, modals, create-post JS
│   ├── home.html                   # Main feed and load-more posts JS
│   ├── post.html                   # Single post page with owner actions
│   ├── user_posts.html             # Posts by one user with pagination
│   ├── account.html                # Profile, image upload, password change, delete account
│   ├── login.html
│   ├── register.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   ├── error.html
│   └── email/
│       └── password_reset.html     # HTML email template
├── static/
│   ├── css/main.css
│   ├── js/auth.js                  # Token/current-user helpers
│   ├── js/utils.js                 # Shared modal/error/date/html helpers
│   ├── icons/
│   └── profile_pics/profile.jpeg   # Default profile image
├── populate_images/                # Local seed images used by populate_db.py
├── tests/                          # Async API tests with mocked S3
├── alembic/                        # Alembic migration environment and revisions
│   └── versions/
│       ├── f7215e176098_initial_migration.py
│       └── 8e6c5e513b71_added_likes_func.py
├── alembic.ini
├── Dockerfile
├── .dockerignore
├── pyproject.toml
└── uv.lock
```

## Main Pages

| Page | Route | Purpose |
| --- | --- | --- |
| Home | `/` or `/posts` | Server-rendered post feed |
| Announcements | `/announcements` | Posts marked as announcements |
| Post calendar | `/calendar?month=YYYY-MM` | Posts published during a selected month |
| Single post | `/posts/{post_id}` | Read one post, edit/delete if owner |
| User posts | `/users/{user_id}/posts` | Posts from one author |
| Register | `/register` | Create an account |
| Login | `/login` | Log in and store access token |
| Account | `/account` | Manage profile, image, password, delete account |
| Forgot password | `/forgot-password` | Request reset email |
| Reset password | `/reset-password?token=...` | Set a new password |
| API docs | `/docs` | Swagger UI |
| ReDoc | `/redoc` | ReDoc API docs |

## API Overview

### Posts

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/posts?skip=0&limit=10` | No | Paginated posts |
| `POST` | `/api/posts` | Yes | Create a post |
| `GET` | `/api/posts/{post_id}` | No | Get one post |
| `PUT` | `/api/posts/{post_id}` | Owner | Replace title/content |
| `PATCH` | `/api/posts/{post_id}` | Owner | Partially update title/content |
| `DELETE` | `/api/posts/{post_id}` | Owner | Delete a post |
| `POST` | `/api/posts/{post_id}/like` | Yes | Toggle the current user's like |
| `GET` | `/api/posts/likes/me?post_ids=1` | Yes | Get liked IDs for displayed posts |

### Comments

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/posts/{post_id}/comments` | No | Paginated comments for a post |
| `POST` | `/api/posts/{post_id}/comments` | Yes | Add a comment |
| `PATCH` | `/api/posts/{post_id}/comments/{comment_id}` | Owner | Edit a comment |
| `DELETE` | `/api/posts/{post_id}/comments/{comment_id}` | Owner | Delete a comment |

### Users And Auth

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/api/users` | No | Register user |
| `POST` | `/api/users/token` | No | Log in, returns JWT |
| `GET` | `/api/users/me` | Yes | Current user |
| `POST` | `/api/users/forgot-password` | No | Send reset email if account exists |
| `POST` | `/api/users/reset-password` | No | Reset password with token |
| `PATCH` | `/api/users/me/password` | Yes | Change current password |
| `GET` | `/api/users/{user_id}` | No | Public user info |
| `GET` | `/api/users/{user_id}/posts` | No | Paginated posts by user |
| `PATCH` | `/api/users/{user_id}` | Same user | Update username/email |
| `DELETE` | `/api/users/{user_id}` | Same user | Delete user and posts |
| `PATCH` | `/api/users/{user_id}/picture` | Same user | Upload profile picture |
| `DELETE` | `/api/users/{user_id}/picture` | Same user | Delete profile picture |

## Requirements

- Python 3.12+
- PostgreSQL for the current async Postgres setup, or SQLite if you point `DATABASE_URL` at an async SQLite URL
- An S3 bucket, or S3-compatible storage, for profile picture uploads
- A terminal
- Optional: an SMTP service if you want real password reset emails

The project already has `pyproject.toml` and `uv.lock`, so using `uv` is the smoothest path. Plain `pip` also works.

## Setup With `uv`

Install `uv` if needed:

```bash
pip install uv
```

Create the virtual environment and install dependencies:

```bash
uv sync
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Create a `.env` file:

```bash
touch .env
```

Add at least this:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_blog
SECRET_KEY=change-this-to-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
POSTS_PER_PAGE=10
RESET_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=http://localhost:8000
S3_BUCKET_NAME=your-bucket-name
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
```

For quick local SQLite development, use:

```env
DATABASE_URL=sqlite+aiosqlite:///./blog.db
```

Run migrations:

```bash
uv run alembic upgrade head
```

Run the app:

```bash
uv run fastapi dev main.py
```

Or:

```bash
uv run uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Setup With Plain `pip`

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install "fastapi[standard]" sqlalchemy alembic asyncpg "psycopg[binary]" aiosqlite greenlet pydantic-settings pyjwt "pwdlib[argon2]" pillow httpx aiosmtplib boto3
```

Create `.env`:

```bash
touch .env
```

Add:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_blog
SECRET_KEY=change-this-to-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
POSTS_PER_PAGE=10
RESET_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=http://localhost:8000
S3_BUCKET_NAME=your-bucket-name
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
```

Run migrations:

```bash
alembic upgrade head
```

Run:

```bash
uvicorn main:app --reload
```

## Database

The app reads its async database URL from `.env` through `config.py`:

```text
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_blog
```

The database engine is created in `database.py`:

```python
engine = create_async_engine(settings.database_url)
```

Current tables:

- `users`
- `posts`
- `password_reset_tokens`

The `posts` table includes a `likes` column with a default value of `0`.

## Migrations

Alembic is configured in `alembic/`. The migration environment reads `DATABASE_URL` from `.env`, so migration commands target the same database as the app.

Current revisions:

- `f7215e176098_initial_migration.py` creates `users`, `posts`, and `password_reset_tokens`.
- `8e6c5e513b71_added_likes_func.py` adds `posts.likes`.

Apply migrations:

```bash
uv run alembic upgrade head
```

Create a new autogenerated migration after changing SQLAlchemy models:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

Rollback one migration:

```bash
uv run alembic downgrade -1
```

## Seeding The Database

`populate_db.py` clears existing users/posts/profile pictures and creates seed data.

Run:

```bash
python populate_db.py
```

With `uv`:

```bash
uv run python populate_db.py
```

Important: this script deletes existing users and posts first. It also deletes old profile picture objects from S3 for users that had uploaded images.

The script:

- creates users from the `USERS` list
- logs each user in to get a JWT
- uploads local images from `populate_images/` to S3 when a user has an `image` value
- creates posts using authenticated API requests
- updates post dates so pagination looks realistic

Example seeded login credentials are in `populate_db.py`, such as:

```text
email: jubi@test.com
password: TestPassword2!
```

Use the email address to log in. The OAuth2 form sends it as the `username` field internally, but the app treats it as email.

## Profile Images

Seed images live in:

```text
populate_images/
```

Uploaded/processed profile pictures are stored in S3 under:

```text
profile_pics/<filename>
```

The app processes uploaded files with Pillow:

- transposes EXIF orientation
- crops/fits to `300x300`
- converts transparent/palette images to RGB
- saves as optimized JPEG
- stores only the generated filename in `users.image_file`

The public URL is computed by the model:

```text
https://<S3_BUCKET_NAME>.s3.<S3_REGION>.amazonaws.com/profile_pics/<filename>
```

If a user has no image, the app uses:

```text
/static/profile_pics/profile.jpeg
```

Required `.env` values:

```env
S3_BUCKET_NAME=your-bucket-name
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
```

For S3-compatible storage, set `S3_ENDPOINT_URL` as well.

You can smoke-test S3 upload/delete access with:

```bash
uv run python s3_checks.py
```

## Authentication Flow

Registration sends JSON to:

```text
POST /api/users
```

Login sends form data to:

```text
POST /api/users/token
```

On success, the frontend stores the JWT access token in:

```text
localStorage.access_token
```

Authenticated requests send:

```http
Authorization: Bearer <token>
```

Password hashing uses `pwdlib` with Argon2 through:

```python
PasswordHash.recommended()
```

## Password Reset Flow

The browser page `/forgot-password` posts an email to:

```text
POST /api/users/forgot-password
```

If the user exists:

1. Old reset tokens for that user are deleted.
2. A random token is generated.
3. Only the SHA-256 hash of the token is saved.
4. An email is sent with a link like:

```text
http://localhost:8000/reset-password?token=<raw-token>
```

The reset page posts the token and new password to:

```text
POST /api/users/reset-password
```

The API hashes the submitted token, compares it with the database hash, checks expiration, updates the password, and deletes reset tokens for that user.

### SMTP Configuration

By default, the app uses:

```env
MAIL_SERVER=localhost
MAIL_PORT=587
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=noreply@example.com
MAIL_USE_TLS=true
```

If you do not have an SMTP server running locally, real reset emails will fail. For development, either configure a real provider or use a local testing SMTP tool.

Example `.env` shape:

```env
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your-username
MAIL_PASSWORD=your-password
MAIL_FROM=noreply@example.com
MAIL_USE_TLS=true
FRONTEND_URL=http://localhost:8000
```

## Frontend JavaScript

Shared frontend helpers live in:

```text
static/js/utils.js
static/js/auth.js
```

`auth.js` handles:

- reading/writing the JWT token
- fetching `/api/users/me`
- caching the current user while a page is active
- logout

`utils.js` handles:

- extracting API error messages
- showing/hiding Bootstrap modals
- escaping dynamic HTML
- formatting dates for dynamically loaded posts

The home page and user-posts page use fetch pagination. The initial page is rendered by Jinja, then later pages are fetched from the API and appended to the DOM.

## Common Commands

Run development server:

```bash
uvicorn main:app --reload
```

Run with `uv`:

```bash
uv run uvicorn main:app --reload
```

Apply database migrations:

```bash
uv run alembic upgrade head
```

Seed database:

```bash
python populate_db.py
```

Run tests:

```bash
uv run pytest
```

The test suite uses a PostgreSQL database URL from `tests/conftest.py` and Moto for mocked S3. Make sure the test database exists and is reachable before running the full suite.

Build the Docker image:

```bash
docker build -t fastapi-blog .
```

Run the Docker image:

```bash
docker run --env-file .env -p 8080:8080 fastapi-blog
```

Check Python syntax:

```bash
python -m py_compile main.py models.py schemas.py auth.py routers/users.py routers/posts.py
```

Hit the posts API:

```bash
curl "http://127.0.0.1:8000/api/posts?skip=0&limit=10"
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

## Troubleshooting

### `SECRET_KEY` error on startup

`config.py` requires `SECRET_KEY`. Add it to `.env`:

```env
SECRET_KEY=change-this-to-a-long-random-secret
```

### Password reset request crashes or returns network error

The forgot-password endpoint sends email in the background. If SMTP is not configured, the email send can fail.

Check your `.env` mail settings or use a test SMTP tool during development.

### Reset link says invalid or expired

Possible causes:

- token was already used
- token expired
- database was reseeded
- old reset token hash was generated before a code fix

Request a new reset link.

### Profile pictures do not show

Profile pictures are uploaded to S3 and rendered from the public S3 URL computed by `models.User.image_path`.

Check:

- `S3_BUCKET_NAME`, `S3_REGION`, `S3_ACCESS_KEY_ID`, and `S3_SECRET_ACCESS_KEY` are set.
- The bucket exists in the configured region.
- The uploaded object exists under `profile_pics/`.
- Your bucket/object policy allows the browser to read profile images.

You can also run:

```bash
uv run python s3_checks.py
```

### Browser still shows old JavaScript or old icon

Browsers cache static files aggressively, especially favicons and JS modules.

Try:

```text
Ctrl + Shift + R
```

Or open DevTools, right-click refresh, and choose "Empty Cache and Hard Reload".

### `Load More Posts` does nothing

Check the browser console and Network tab. The endpoint should return JSON like:

```text
GET /api/posts?skip=10&limit=10
```

If the JS import is cached, hard refresh the page.

### Database schema looks stale

Run the latest Alembic migrations:

```bash
uv run alembic upgrade head
```

If you are using SQLite for throwaway development and want a clean reset, remove the local database and run migrations again:

```bash
rm blog.db
uv run alembic upgrade head
python populate_db.py
```

Only do this if you are okay losing local data.

## Current Limitations

- Password reset requires SMTP configuration for real email delivery.
- Profile image display currently assumes the bucket can serve public object URLs.
- The Docker image expects runtime configuration through environment variables.

## Roadmap Ideas

- Expand automated test coverage for reset-token edge cases, account updates, and delete flows.
- Add deployment examples for Cloud Run, Render, or a VPS.
- Add richer post editing UI.
- Add production email provider configuration.

## Author

Mwangi Sam alias Kajeiy

- GitHub: https://github.com/mwangisam203
- LinkedIn: https://www.linkedin.com/in/samson-maina-26883116a/
