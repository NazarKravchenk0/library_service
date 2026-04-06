# Library Service API

DRF-based library management service for books, users, borrowings, payments, and notifications.

## Features

- JWT authentication with custom `Authorize: Bearer <token>` header support
- Book CRUD with admin-only write access
- User registration and profile management
- Borrowing creation, filtering, detail view, and return endpoint
- Automatic payment creation for borrowings and overdue fines
- Telegram notifications for new borrowings, overdue borrowings, and successful payments
- Celery background tasks with Redis broker
- Swagger docs at `/api/docs/`
- Environment-based configuration with `.env.sample`

## API overview

- `POST /api/users/` - register user
- `POST /api/users/token/` - obtain JWT pair
- `POST /api/users/token/refresh/` - refresh access token
- `GET|PUT|PATCH /api/users/me/` - manage current user
- `GET /api/books/` - public books list
- `GET /api/books/{id}/` - public book detail
- `POST|PUT|PATCH|DELETE /api/books/` - admin book management
- `GET /api/borrowings/?is_active=true&user_id=1` - list borrowings with filters
- `POST /api/borrowings/` - create borrowing
- `GET /api/borrowings/{id}/` - borrowing detail
- `POST /api/borrowings/{id}/return/` - return borrowing
- `GET /api/payments/` - list payments
- `GET /api/payments/{id}/` - payment detail
- `GET /api/payments/success/?session_id=...` - confirm payment
- `GET /api/payments/cancel/` - cancel page

## Run locally

1. Install dependencies from `requirements.txt`.
2. Copy `.env.sample` to `.env`.
3. Run migrations: `python manage.py makemigrations && python manage.py migrate`
4. Start server: `python manage.py runserver`

## Telegram setup

1. Put `TELEGRAM_BOT_TOKEN` into `.env`.
2. Open a chat with your bot and send it any message.
3. If you know the chat id, set `TELEGRAM_CHAT_ID` in `.env`.
4. If `TELEGRAM_CHAT_ID` is empty, the app will try to resolve it from Telegram `getUpdates`.

## Stripe setup

1. Add your Stripe test secret key to `STRIPE_SECRET_KEY`.
2. New borrowings will create real Stripe Checkout sessions.
3. `GET /api/payments/success/?session_id=...` confirms the session and marks payment as paid.

## Docker

Use `docker-compose up --build` to start the app, Redis, Celery worker, and Celery beat.
