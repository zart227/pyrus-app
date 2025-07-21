# Pyrus-app

A web application to interact with the Pyrus API, built with a FastAPI backend and a Vue.js frontend. The application is containerized using Docker.

## Technologies Used

-   **Backend:** FastAPI
-   **Frontend:** Vue.js
-   **Web Server:** Nginx
-   **Containerization:** Docker, Docker Compose

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
    Now, edit the `.env` file with your credentials.

3.  **Build and run the containers**
    ```sh
    docker compose up --build -d
    ```
    The `-d` flag runs the containers in detached mode.

4.  **Access the application**

    Once the containers are running, you can access the application in your browser at:
    [http://localhost](http://localhost)

    -   The frontend is served directly.
    -   The FastAPI backend is available under the `/api` prefix (e.g., `http://localhost/api/docs`).

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