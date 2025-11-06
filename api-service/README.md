# AetherLink API Service

Network monitoring API service built with FastAPI and Python.

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:

- Interactive API docs (Swagger UI): http://localhost:8000/docs
- Alternative API docs (ReDoc): http://localhost:8000/redoc

## Endpoints

### Network Status

- `GET /api/network/status` - Get complete network status including devices, stats, and activity

### Devices

- `GET /api/devices` - List all connected devices
- `GET /api/devices/{device_id}` - Get specific device details

### Stats

- `GET /api/stats` - Get network statistics (speed, uptime, data usage)

### Activities

- `GET /api/activities` - Get recent network activities

## Environment Variables

Create a `.env` file in the api-service directory:

```
API_HOST=0.0.0.0
API_PORT=8000
NETWORK_PREFIX=192.168.1
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Docker

Build and run with Docker:

```bash
docker build -t aetherlink-api .
docker run -p 8000:8000 aetherlink-api
```

Or use docker-compose from the root directory:

```bash
docker-compose up api-service
```
