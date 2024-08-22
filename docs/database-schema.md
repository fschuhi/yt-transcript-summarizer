# Database Schema

The YouTube Transcript Summarizer uses PostgreSQL as its database. The main entity in the database is the User model.

## User Table

Table Name: users

Columns:
- user_id: Integer, Primary Key
- user_name: String(255), Unique, Indexed
- email: String(255), Unique, Not Null
- last_login_date: DateTime, Nullable
- token_issuance_date: DateTime, Nullable
- token: String(255), Nullable
- password_hash: String(100), Not Null
- identity_provider: String(30), Nullable, Default: "local"

## Schema Management

The project uses Alembic for database migrations. Migration scripts are located in the `alembic/` directory.

To create a new migration:

```
alembic revision --autogenerate -m "Migration description"

```

To apply migrations:

```
alembic upgrade head

```

For more details on the database model, see `models/user.py`.