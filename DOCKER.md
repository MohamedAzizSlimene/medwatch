# MedWatch Docker Quick Start

## What It Does

Your backend is a **FastAPI + Uvicorn** application. This Docker setup containerizes it.

## Prerequisites

- Docker Desktop installed
- ~5GB disk space

## Quick Start

### 1. Build the Docker image
```bash
docker-compose build
```

### 2. Start the container
```bash
docker-compose up -d
```

### 3. Access your backend
- **API Docs**: http://localhost:8000/docs
- **WebSocket Stream**: ws://localhost:8000/ws/stream

### 4. View logs
```bash
docker-compose logs -f
```

### 5. Stop the container
```bash
docker-compose down
```

---

## How It Runs

When you run the container:

1. Docker builds an image from the `Dockerfile`
2. Copies all your code and installs dependencies
3. Runs: `python main.py`
4. Your `main.py` starts **Uvicorn** on `0.0.0.0:8000`

This is the same as running:
```bash
python main.py
```

But inside a container with all dependencies pre-installed.

---

## File Structure

```
medwatch/
├── Dockerfile              # How to build the image
├── docker-compose.yml      # How to run the container
├── .dockerignore           # Files to skip when building
└── .env.docker             # Configuration template
```

---

## Common Commands

```bash
# Build
docker-compose build

# Start in background
docker-compose up -d

# Start and see logs
docker-compose up

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Run a command inside container
docker-compose exec medwatch python -c "import torch; print(torch.cuda.is_available())"

# Open a shell inside container
docker-compose exec medwatch /bin/bash

# Check status
docker-compose ps

# Resource usage
docker stats
```

---

## Configuration

Copy `.env.docker` to `.env` if you want custom settings:

```bash
cp .env.docker .env
```

Edit `.env` for:
- `LOG_LEVEL`: DEBUG or INFO
- `DEBUG`: true or false

---

## Troubleshooting

### Port already in use
Change port in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

### Models not found
Make sure `./models/` directory exists with your model files.

### Out of memory
Reduce the container memory allocation or close other applications.

### Check logs
```bash
docker-compose logs -f medwatch
```

---

That's it! Your FastAPI app now runs in Docker. 🐋
