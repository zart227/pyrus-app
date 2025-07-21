# Pyrus-app

A web application with a FastAPI backend and a Vue.js frontend, containerized using Docker.

## Technologies Used

-   **Backend:** FastAPI
-   **Frontend:** Vue.js
-   **Web Server:** Nginx
-   **Containerization:** Docker, Docker Compose

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1.  **Clone the repository**
    
    Replace `your-username` with your actual GitHub username.
    ```sh
    git clone https://github.com/your-username/Pyrus-app.git
    cd Pyrus-app
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

## Stopping the application
To stop the application, run:
```sh
docker compose down
``` 