# Pyrus-app

A web application to interact with the Pyrus API, built with a FastAPI backend and a Vue.js frontend. The application supports multiple users with authentication and is containerized using Docker.

## Technologies Used

-   **Backend:** FastAPI, SQLAlchemy, JWT Authentication
-   **Frontend:** Vue.js, Element Plus, Pinia
-   **Database:** PostgreSQL (Docker) / SQLite (fallback)
-   **Web Server:** Nginx
-   **Containerization:** Docker, Docker Compose
-   **Migrations:** Alembic

## Features

- **Multi-user authentication** with JWT tokens and cookies
- **User registration** with Pyrus API credentials validation
- **Session management** with automatic token refresh
- **Task management** with user-specific access
- **Responsive UI** with modern design

## Getting Started with Docker

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1.  **Clone the repository**
    ```sh
    git clone https://github.com/zart227/pyrus-app.git
    cd pyrus-app
    ```

2.  **Create and configure the environment file**

    Copy the example environment file and fill in the required values.
    ```sh
    cp .env.example .env
    ```
    Now, edit the `.env` file with your credentials:
    ```
    PYRUS_LOGIN=your-email@example.com
    PYRUS_SECURITY_KEY=your-pyrus-security-key
    SECRET_KEY=your-super-secret-jwt-key-change-in-production-12345
    ```

3.  **Build and run the containers**
    ```sh
    docker compose up --build -d
    ```
    The `-d` flag runs the containers in detached mode.

4.  **Initialize the first user (optional)**
    
    If you want to migrate your existing single-user setup to the new multi-user system:
    ```sh
    docker compose exec backend python init_user.py
    ```

5.  **Access the application**

    Once the containers are running, you can access the application in your browser at:
    - **Main application (Nginx):** [http://localhost:8082](http://localhost:8082)
    - **Frontend only:** [http://localhost:8081](http://localhost:8081)
    - **Backend API:** [http://localhost:8000](http://localhost:8000)
    - **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
    - **PostgreSQL Database:** localhost:5433

### Stopping the application
To stop the application, run:
```sh
docker compose down
```

## Local Development (Without Docker)

Follow these instructions to run the application on your local machine without Docker.

### Prerequisites

-   [Python 3](https://www.python.org/downloads/)
-   [Node.js](https://nodejs.org/) (which includes `npm`)

### Installation and Setup

1.  **Clone the repository**
    ```sh
    git clone https://github.com/zart227/pyrus-app.git
    cd pyrus-app
    ```

2.  **Create and configure the environment file**

    Copy the example environment file and fill in the required values for the backend.
    ```sh
    cp .env.example .env
    ```
    Now, edit the `.env` file with your credentials.

3.  **Run the setup script**

    This script will prepare your environment by creating a Python virtual environment and installing all backend and frontend dependencies.

    -   **On Windows:**
        ```cmd
        setup.bat
        ```

    -   **On Linux or macOS:**
        First, make the script executable:
        ```sh
        chmod +x setup.sh
        ```
        Then run it:
        ```sh
        ./setup.sh
        ```

4.  **Initialize the first user (optional)**
    
    If you want to migrate your existing single-user setup to the new multi-user system:
    ```sh
    python init_user.py
    ```

### Running the Application

After setup is complete, run the start script for your operating system. This will launch both the backend and frontend servers.

-   **On Windows:**
    ```cmd
    start.bat
    ```

-   **On Linux or macOS:**
    First, make the script executable:
    ```sh
    chmod +x start.sh
    ```
    Then run it:
    ```sh
    ./start.sh
    ```

Once running, you can access:
-   **Frontend:** `http://localhost:5173` (check the terminal for the exact address)
-   **Backend API:** `http://127.0.0.1:8000`

### Stopping the Application

To stop both servers, return to the terminal where the start script is running and press `Ctrl+C`.

## User Management

### Registration

New users can register by providing their Pyrus API credentials (login and security key). The system validates these credentials against the Pyrus API before creating the user account.

### Authentication

Users authenticate using their Pyrus credentials. The system uses JWT tokens stored in HTTP-only cookies for session management.

### Multiple Users

The application now supports multiple users, each with their own Pyrus API credentials. Users can only access their own tasks and data.

## API Documentation

Once the application is running, you can access the interactive API documentation at:
- **Swagger UI:** `http://localhost/api/docs`
- **ReDoc:** `http://localhost/api/redoc`

## Security Notes

- JWT tokens are stored in HTTP-only cookies for security
- User credentials are validated against the Pyrus API during registration
- All API endpoints require authentication except for login/register
- CORS is configured for development; update origins for production 