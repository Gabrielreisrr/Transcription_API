# Whisper API - Audio Transcription Service

This application is a REST API built with FastAPI that uses OpenAI's Whisper model to transcribe audio files in Portuguese. The application is containerized with Docker and can be deployed in swarm mode for high availability.

## Application Architecture

### Main Components

1. **FastAPI**: Web framework for creating the REST API
2. **Whisper**: OpenAI's AI model for audio transcription
3. **Docker**: Application containerization
4. **Docker Swarm**: Orchestration for multiple replicas

## Project Structure

```
project/
├── docker-compose.yml    # Docker Swarm configuration
├── Dockerfile           # Image build instructions
├── whisper_api.py      # Main API code
└── requirements.txt      # Python dependencies
```

## How It Works

### Step-by-Step Process

1. **Client uploads audio file** via POST request to `/transcribe` endpoint
2. **API receives file** and saves it temporarily to disk
3. **Whisper model processes** the audio file with Portuguese language settings
4. **Transcription segments** are extracted with timestamps
5. **Results returned** as JSON with text segments and timing information
6. **Temporary file cleaned up** from disk

## Dockerfile Explanation

### Line-by-Line Analysis

```dockerfile
FROM python:3.12-slim AS base
```
**Purpose**: Uses Python 3.12 slim base image to reduce container size while maintaining necessary Python runtime.

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libsndfile1 && \
    rm -rf /var/lib/apt/lists/*
```
**Purpose**: Installs system dependencies required by Whisper:
- `ffmpeg`: Audio/video processing library for format conversion
- `libsndfile1`: Audio file reading/writing library
- Cleans package cache to reduce image size

```dockerfile
WORKDIR /app
```
**Purpose**: Sets `/app` as the working directory inside the container.

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
**Purpose**: Copies Python dependencies file and installs packages without pip cache to reduce image size.

```dockerfile
COPY . .
```
**Purpose**: Copies all application files to the container's working directory.

```dockerfile
RUN useradd -m appuser
USER appuser
```
**Purpose**: Creates a non-root user for security best practices and switches to it.

```dockerfile
EXPOSE 8000
```
**Purpose**: Documents that the container listens on port 8000 (doesn't actually open the port).

```dockerfile
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
```
**Purpose**: Defines health check by calling the `/health` endpoint to verify service availability.

```dockerfile
CMD ["uvicorn", "whisper_api:app", "--host", "0.0.0.0", "--port", "8000"]
```
**Purpose**: Starts the FastAPI application using Uvicorn ASGI server, binding to all interfaces on port 8000.

## Docker Compose Configuration

### Service Definition Analysis

```yaml
version: "3.9"
```
**Purpose**: Specifies Docker Compose file format version for compatibility.

```yaml
services:
  whisper-api:
    image: whisper-api
```
**Purpose**: Defines the service name and specifies the Docker image to use.

```yaml
    ports:
      - "8000:8000"
```
**Purpose**: Maps host port 8000 to container port 8000, making the API accessible externally.

```yaml
    deploy:
      replicas: 2
```
**Purpose**: Runs 2 instances of the service for load distribution and high availability.

```yaml
      restart_policy:
        condition: on-failure
```
**Purpose**: Automatically restarts containers only when they fail (not on manual stops).

```yaml
    networks:
      - whisper-net
```
**Purpose**: Connects the service to a custom network for inter-service communication.

```yaml
networks:
  whisper-net:
    driver: overlay
```
**Purpose**: Creates an overlay network that spans multiple Docker hosts in swarm mode.

## API Endpoints

### Health Check
```
GET /health
```
Returns service status for monitoring and load balancer health checks.

### Audio Transcription
```
POST /transcribe
```
Accepts audio file upload and returns transcription with timestamps.

**Request**: Multipart form data with audio file
**Response**: JSON with segments containing text and timing information

## FastAPI Application Details

### Key Features

**CORS Middleware**: Enables cross-origin requests from web browsers
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Whisper Model Loading**: Loads the "small" model for balance between speed and accuracy
```python
model = whisper.load_model("small")
```

**Portuguese Language Configuration**: Optimized transcription settings for Portuguese
```python
transcribe_options = {
    "language": "pt",
    "verbose": True,
    "fp16": False,
    "no_speech_threshold": 0.3,
    "logprob_threshold": -2.0,
    "condition_on_previous_text": False,
    "temperature": 0.0,
}
```

## Deployment Commands

### Building the Image
```bash
docker build -t whisper-api .
```

### Initialize Docker Swarm (if not already done)
```bash
docker swarm init
```

### Deploy the Stack
```bash
docker stack deploy -c docker-compose.yaml whisper
```

### Check Service Status
```bash
docker service ls
docker service ps whisper_whisper-api
```

### Remove the Stack
```bash
docker stack rm whisper
```

### View Logs
```bash
docker service logs whisper-stack_whisper-api
```

## Development Commands

### Run Locally (without Docker)
```bash
pip install -r requirements.txt
uvicorn whisper_api:app --reload --host 0.0.0.0 --port 8000
```

### Test the API
```bash
# Health check
curl http://localhost:8000/health

# Upload audio file for transcription
curl -X POST "http://localhost:8000/transcribe" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your-audio-file.wav"
```

## Monitoring and Troubleshooting

### Check Container Health
```bash
docker ps
docker inspect <container_id>
```

### Access Container Logs
```bash
docker logs <container_id>
```

### Execute Commands in Running Container
```bash
docker exec -it <container_id> /bin/bash
```

## Performance Considerations

- **Model Size**: Uses "small" Whisper model for faster processing
- **Replicas**: Configured for 2 replicas to handle concurrent requests
- **File Cleanup**: Temporary files are automatically removed after processing
- **Memory**: Each replica loads the Whisper model into memory (~244MB for small model)

## Security Features

- Non-root user execution inside containers
- Temporary file cleanup to prevent disk space issues
- Health checks for service monitoring
- Restart policy for service resilience