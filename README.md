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

## Production Deployment on Corporate Network

### Deploy at `/pyrus` subpath

To make the application accessible within your corporate network at `http://server-address/pyrus/`, follow these steps:

#### Quick Start (3 steps)

1. **Install Nginx on the host:**
   ```bash
   sudo apt update && sudo apt install -y nginx
   ```

2. **Configure reverse proxy:**
   ```bash
   sudo cp nginx-host.conf /etc/nginx/sites-available/pyrus
   sudo ln -s /etc/nginx/sites-available/pyrus /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl restart nginx
   ```

3. **Start the application:**
   ```bash
   ./prod.sh up
   ```

Your application will be available at: `http://your-server-address/pyrus/`

#### Automated Setup

Alternatively, use the automated setup script:
```bash
sudo ./SETUP_COMMANDS.sh
./prod.sh up
```

#### Management Commands

```bash
./prod.sh up       # Start production mode
./prod.sh down     # Stop containers
./prod.sh logs     # View logs
./prod.sh ps       # Container status
./prod.sh restart  # Restart containers
./prod.sh rebuild  # Rebuild and restart
./prod.sh dev      # Switch to dev mode
```

#### Development vs Production

- **Development mode:** `./dev.sh up` - Hot reload, port 8081 (Vite dev server)
- **Production mode:** `./prod.sh up` - Optimized build, ready for corporate network

#### Documentation

- 📘 **Quick Start:** See `QUICKSTART.md`
- 📚 **Detailed Guide:** See `INSTALL.md` (includes troubleshooting, security, backup)
- 📝 **Changes Log:** See `CHANGES.md`

#### Architecture

```
Corporate Network → Nginx (host:80) → /pyrus → Docker Nginx (8082) → Backend/Frontend
```

#### Firewall Configuration

Open port 80 for your corporate network:
```bash
sudo ufw allow 80/tcp
```

Or for specific IP range:
```bash
sudo ufw allow from 192.168.0.0/16 to any port 80 proto tcp
``` 