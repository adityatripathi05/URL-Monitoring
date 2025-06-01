```markdown
# Backend Services

This document provides an overview of the backend services for the URL Monitoring System.

## Table of Contents

- [Directory Structure](#directory-structure)
- [Backend Architecture Highlights](#backend-architecture-highlights)
- [Environment Setup](#environment-setup)
- [Database Migrations](#database-migrations)
- [Running the Backend Server](#running-the-backend-server)
- [Authentication](#authentication)
- [Super Admin Management](#super-admin-management)

## Directory Structure

The backend code is organized as follows:

- **`alembic/`**: Contains Alembic migration scripts for database schema management.
    - `versions/`: Individual migration files.
    - `env.py`: Alembic environment configuration.
    - `script.py.mako`: Migration script template.
- **`apps/`**: Contains the different application modules.
    - `auth/`: Authentication logic, user management, JWT handling.
    - `monitoring/`: Core monitoring logic (if specific services are built here).
    - `telegraf_mgmt/`: Telegraf configuration management (if applicable).
- **`config/`**: Application configuration files.
    - `database.py`: Database connection setup and management (`asyncpg`).
    - `lifespan.py`: Handles application startup and shutdown events (e.g., initializing DB pool).
    - `logging_util.py`: Logging configuration.
    - `routes.py`: Main API router, aggregates routers from different apps.
    - `settings.py`: Pydantic-based settings management, loads from environment variables.
- **`main.py`**: FastAPI application entry point.
- **`plugins/`**: For custom plugins or extensions.
- **`requirements/`**: Python dependency files (`base.txt`, `dev.txt`, `prod.txt`).
- **`utils/`**: Utility scripts and helper functions.
    - `create_super_admin.py`: Command-line script to create/update super admin users.
    - `db_utils.py`: Database utility functions.
- **`.env.template`**: Template for environment variables.
- **`alembic.ini`**: Alembic configuration file.
- **`Dockerfile.dev` / `Dockerfile.prod`**: Dockerfiles for development and production.

## Backend Architecture Highlights

The backend is designed with modularity and maintainability in mind:

*   **Centralized Configuration (`config/`)**: Key aspects like application settings (`settings.py` via Pydantic), database connections (`database.py`), logging (`logging_util.py` using Structlog), API routing (`routes.py`), and application lifespan events (`lifespan.py`) are managed centrally within this directory.
*   **Modular Applications (`apps/`)**: Features are organized into distinct applications (e.g., `auth`, `monitoring`, `telegraf_mgmt`). Each module typically contains its own routes, services (business logic), and schemas (data models with Pydantic).
*   **Lean Entry Point (`main.py`)**: The main application file (`main.py`) is kept minimal. Its primary responsibilities are instantiating the FastAPI application, including the main API router from `config.routes`, and setting up lifespan events.
*   **Dependency Injection**: FastAPI's powerful dependency injection system is utilized extensively for managing dependencies like database connections (e.g., `Depends(get_db_connection)`), security checks (e.g., `Depends(get_current_active_user)`), and service access within route handlers.
*   **Database Interaction**: Uses `asyncpg` for asynchronous communication with the PostgreSQL database, ensuring non-blocking database operations suitable for an async framework like FastAPI.
*   **Task Management**: Background tasks or scheduled jobs (like `cleanup_expired_tokens` in `main.py`) can be managed using libraries like `fastapi-utilities`.

## Environment Setup

1.  **Create a `.env` file:**
    Copy the `backend/.env.template` file to `backend/.env`. This `.env` file is located in the `backend/` directory on your host machine but is read by the backend service running inside its Docker container (due to volume mounting).
    ```bash
    cp backend/.env.template backend/.env
    ```
2.  **Configure Environment Variables:**
    Edit the `backend/.env` file and provide appropriate values for your environment.
    The following variables are essential:

    *   `APP_NAME`: Name of the application (e.g., "URL Monitoring System").
    *   `ADMIN_EMAIL`: Default admin email for certain operations or notifications.
    *   `DB_NAME`: PostgreSQL database name.
    *   `DB_USER`: PostgreSQL database username.
    *   `DB_PASSWORD`: PostgreSQL database password.
    *   `DB_HOST`: Hostname of the PostgreSQL server (e.g., `localhost` if running PostgreSQL directly on host for development, or `url-db` which is the service name when using Docker Compose).
    *   `DB_PORT`: Port of the PostgreSQL server (e.g., `5432`).
    *   `TZ`: Timezone setting (e.g., `UTC`).
    *   `LOG_LEVEL`: Logging level (e.g., `INFO`, `DEBUG`).
    *   `JWT_SECRET_KEY`: **Crucial for security.** A strong, randomly generated secret key for JWT signing.
        To generate one, you can use:
        ```bash
        # From within the project root using Docker (recommended):
        docker exec url-backend python -c "import secrets; print(secrets.token_hex(32))"

        # Or using openssl if available on your host:
        # openssl rand -hex 32
        ```
    *   `JWT_ALGORITHM`: JWT signing algorithm (e.g., `HS256`).
    *   `ACCESS_TOKEN_EXPIRE_MINUTES`: Lifetime for access tokens.
    *   `REFRESH_TOKEN_EXPIRE_DAYS`: Lifetime for refresh tokens.
    *   `PASSWORD_RESET_TOKEN_EXPIRES_HOURS`: Expiry for password reset tokens.
    *   `EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS`: Expiry for email verification tokens.
    *   `DEFAULT_ROLE_ID`: Default role assigned to new users (e.g., `viewer`).

    Optional variables for email (SMTP) functionality if used:
    *   `SMTP_USER`
    *   `SMTP_PASSWORD`
    *   `SMTP_SERVER`
    *   `SMTP_PORT`

## Database Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) to manage database schema migrations. All Alembic commands **must** be run within the context of the running backend Docker container (`url-backend`). This ensures that migrations are executed with the correct database connection settings defined in the `.env` file (which is accessible to the container).

**Common Commands:**
(Run these from your project's root directory, where `docker-compose.yml` is located)

*   **View History**: See all migration revisions and the current revision.
    ```bash
    docker exec url-backend alembic history
    ```
*   **Check Current Revision**: Show the current database revision.
    ```bash
    docker exec url-backend alembic current
    ```
*   **Create a New Revision**: Generate a new empty revision file in `backend/alembic/versions/`. You will then need to edit this file to add your SQL changes for `upgrade()` and `downgrade()` functions.
    ```bash
    docker exec url-backend alembic revision -m "your_migration_message"
    ```
*   **Upgrade to Latest Revision**: Apply all pending migrations. This is the most common command to update your database schema.
    ```bash
    docker exec url-backend alembic upgrade head
    ```
*   **Upgrade to a Specific Revision**:
    ```bash
    docker exec url-backend alembic upgrade <revision_id>
    ```
*   **Downgrade by One Step**: Revert the last applied migration.
    ```bash
    docker exec url-backend alembic downgrade -1
    ```
*   **Downgrade to a Specific Revision**:
    ```bash
    docker exec url-backend alembic downgrade <revision_id>
    ```
*   **Stamp a Revision**: Mark a revision as applied without actually running the SQL. This is useful for initial setup if the schema already exists or for baseline management.
    ```bash
    docker exec url-backend alembic stamp head
    ```
Ensure your `backend/.env` file is correctly configured with database credentials before running migrations.

## Running the Backend Server

The backend server is designed to be run as a containerized service using Docker Compose, which manages the server, database, and other potential services.

**Primary Method (using Docker Compose):**
To start all services defined in the `docker-compose.template.yml` file (including the backend `url-backend`, database `url-db`, etc.), run the following command from the project's root directory:
```bash
# Make sure you have a .env file from .env.template in the root directory
# for docker-compose variable substitution if used there,
# and backend/.env for the application itself.
docker-compose -f docker-compose.template.yml up
# Or to run in detached mode (in the background):
# docker-compose -f docker-compose.template.yml up -d
```
The backend server (FastAPI with Uvicorn) will typically be available at `http://localhost:8000` (as per `docker-compose.template.yml` port mapping). The API documentation (Swagger UI) can be accessed at `http://localhost:8000/docs`.

**Directly (for development/debugging inside the container):**
If you need to run the server manually (e.g., after shelling into the running container or for specific debugging scenarios bypassing Docker Compose for the server process itself), you can use Uvicorn directly. From the `/app` directory (which is `backend/` on your host) inside the `url-backend` container:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
This method is generally for advanced development or debugging, not for standard operation.

## Authentication

Authentication is handled using JSON Web Tokens (JWT), providing secure and stateless user verification.

*   **Login**: Users authenticate via the `/auth/login` endpoint by providing their email and password (as form data: `username`=email, `password`=password).
*   **Tokens Issued**: Upon successful authentication, the backend issues two tokens:
    *   `access_token`: A short-lived token used to authorize access to protected API endpoints. It is sent in the `Authorization: Bearer <token>` header.
    *   `refresh_token`: A longer-lived token used to obtain a new `access_token` without requiring the user to re-enter credentials.
*   **Token Expiration**:
    *   Access tokens have role-based expiration times (e.g., shorter for 'Admin', longer for 'Viewer'), configured via environment variables (e.g., `ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES`, `VIEWER_ACCESS_TOKEN_EXPIRES_MINUTES`).
    *   Refresh tokens also have a defined expiration (e.g., `REFRESH_TOKEN_EXPIRE_DAYS`).
*   **Token Refresh**: The `/auth/refresh` endpoint accepts a valid `refresh_token` (in the request body) and returns a new `access_token`.
*   **Logout**: The `/auth/logout` endpoint (requires authentication) invalidates the user's session. It expects the `refresh_token` in the request body. Both the current access token (identified from the request) and the provided refresh token are added to a blacklist (`token_blacklist` table) to prevent their further use.
*   **Security**:
    *   The JWT secret key (`JWT_SECRET_KEY`) and algorithm (`JWT_ALGORITHM`) are critical security settings configured via `.env`.
    *   Passwords are hashed securely using `passlib` (bcrypt).
*   **Token Structure**: Tokens contain claims such as `sub` (subject, typically user email), `role`, `exp` (expiration time), and `jti` (JWT ID, unique identifier for blacklisting).
*   For a visual representation of these flows, refer to the [Authentication Flow Diagram](../flow_diagrams/auth_flow.md).

## Super Admin Management

A command-line utility is provided to create and manage the initial super admin user. This user will have the 'Admin' role and can subsequently manage other users through the application UI (once implemented).

The script is located at `backend/utils/create_super_admin.py` within the backend service.

**Prerequisites:**
*   The backend Docker services (especially `url-backend` and `url-db`) must be running.
*   Your `backend/.env` file must be correctly configured with database credentials, as the script running inside the container will use these settings.
*   Database migrations should have been applied so the `roles` and `users` tables exist (the 'Admin' role is typically created by an initial migration).

**Commands (run from your project's root directory):**

1.  **Create a Super Admin:**
    To create a new super admin user:
    ```bash
    docker exec -it url-backend python -m utils.create_super_admin create
    ```
    You will be prompted to enter the username, email, and password for the new super admin.

2.  **Update a Super Admin:**
    To update an existing super admin's username or password:
    ```bash
    docker exec -it url-backend python -m utils.create_super_admin update
    ```
    You will be prompted for the email of the admin user to update, and then for the new username and/or password. Press Enter to skip a field if no change is desired for that field.

This utility interacts directly with the database using the settings defined in `backend/.env`.
```
