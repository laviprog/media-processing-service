# Media Processing Service

Media Processing Service is an API for embedding subtitles into video files.

## 🛠️ Getting Started

Follow the steps below to set up and run the Media Processing Service using Docker.

### ⚙️ Configure Environment Variables

Copy the example environment file and fill in the necessary values:

```bash
cp .env.example .env
```

Edit the `.env` file to set your environment variables. You can use the default values or customize
them as needed.

### 🐳 Build and Run the Docker Container

Start the Docker container with the following command:

```bash
docker compose up --build -d
```

This command will build the Docker image and start the container.

Then, API will be available at `http://localhost:8000/api/v1`.

Documentation will be available at `http://localhost:8000/api/v1/docs`.
