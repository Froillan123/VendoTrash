# VendoTrash Deployment Guide

Complete deployment guide for local development and cloud deployment (Google Cloud Run).

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Data Flow Diagram](#data-flow-diagram)
3. [Local Deployment](#local-deployment)
4. [Cloud Deployment (Google Cloud Run)](#cloud-deployment-google-cloud-run)
5. [Reliability Considerations](#reliability-considerations)
6. [Docker Setup](#docker-setup)

---

## 🏗️ Architecture Overview

```
┌─────────────┐
│   Client    │  React + Vite (Port 5175)
│  (Browser)  │
└──────┬──────┘
       │ HTTP/WebSocket
       │
┌──────▼──────────────────────────────────────┐
│         FastAPI Server                      │
│      (Port 8000 / Cloud Run)               │
│  - Computer Vision Processing               │
│  - API Endpoints                            │
│  - Database (PostgreSQL)                   │
└──────┬──────────────────────────────────────┘
       │ HTTP Request
       │
┌──────▼──────┐
│   ESP32     │  WiFi Bridge (Port 80)
│  (Bridge)   │
└──────┬──────┘
       │ Serial/UART (9600 baud)
       │
┌──────▼──────┐
│  Arduino   │  Motor Control
│  (Hardware)│  - Servos
│            │  - Sensors
└────────────┘
```

---

## 🔄 Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Client as React Client<br/>(Port 5175)
    participant Server as FastAPI Server<br/>(Port 8000 / Cloud)
    participant Camera as Camera Module
    participant ESP32 as ESP32 Bridge<br/>(WiFi)
    participant Arduino as Arduino<br/>(Hardware)
    participant DB as PostgreSQL

    User->>Client: Interact with UI
    Client->>Server: HTTP Request<br/>(POST /api/vendo/command)
    
    Note over Server,Camera: Computer Vision Processing
    Server->>Camera: Capture Image
    Camera-->>Server: Image Data
    Server->>Server: Process Image<br/>(Classify: PLASTIC/NON_PLASTIC)
    Server->>DB: Log Transaction
    
    Server->>ESP32: HTTP POST<br/>(Command: SORT:PLASTIC)
    ESP32->>Arduino: Serial Command<br/>("SORT:PLASTIC\n")
    
    Arduino->>Arduino: Execute Servo Movement
    Arduino-->>ESP32: Serial Response<br/>("DONE\n")
    ESP32-->>Server: HTTP Response<br/>(Status: OK)
    Server-->>Client: JSON Response<br/>(Success)
    Client-->>User: Display Result
```

---

## 🖥️ Local Deployment

### Prerequisites

- Docker & Docker Compose installed
- Node.js 18+ (for local client development)
- Python 3.8+ (for local server development)
- Arduino IDE (for Arduino code)

### Step 1: Clone and Setup

```bash
git clone <your-repo>
cd VendoTrash
```

### Step 2: Environment Variables

Create `.env` files:

**Server/.env:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/vendotrash
DEBUG=True
SECRET_KEY=your-secret-key-here
ESP32_IP=192.168.1.100
ESP32_PORT=80
```

**Client/.env:**
```env
VITE_API_URL=http://localhost:8000
```

### Step 3: Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Step 4: Access Services

- **Client**: http://localhost:5175
- **Server API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

---

## ☁️ Cloud Deployment (Google Cloud Run)

### Why Cloud Run?

✅ **Serverless** - Pay only for what you use  
✅ **Auto-scaling** - Handles traffic spikes automatically  
✅ **HTTPS** - Built-in SSL certificates  
✅ **Easy deployment** - Just drag and drop your code!  

### Step 1: Setup Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable **Cloud Run API** (it will prompt you automatically)

### Step 2: Deploy Server (Drag & Drop Method)

**Super Simple Method:**

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click **Create Service**
3. Choose **Deploy one revision from a source repository** or **Deploy from container image**
4. **For Source Deployment:**
   - Upload your `Server/` folder (or ZIP it first)
   - Cloud Run will automatically detect it's Python and build it
5. **Or use gcloud CLI (one command):**
   ```bash
   gcloud run deploy vendotrash-server --source ./Server --region asia-southeast1
   ```
6. Set **Service name**: `vendotrash-server`
7. Set **Region**: `asia-southeast1` (or your preferred region)
8. Set **Port**: `8000`
9. Add environment variables:
   - `DATABASE_URL` = your database URL
   - `SECRET_KEY` = your secret key
10. Click **Deploy** or **Create**

That's it! Cloud Run will build and deploy automatically.

### Step 3: Deploy Client (Same Simple Method)

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click **Create Service**
3. Upload your `Client/` folder (or ZIP it first)
4. Set **Service name**: `vendotrash-client`
5. Set **Region**: Same as server
6. Set **Port**: `80`
7. Add environment variable:
   - `VITE_API_URL` = your server URL (from Step 2)
8. Click **Deploy**

**Or use gcloud CLI:**
```bash
gcloud run deploy vendotrash-client --source ./Client --region asia-southeast1
```

Done! Both services are now deployed.

### Step 4: Update ESP32 Configuration

After deployment, you'll get URLs like:
- Server: `https://vendotrash-server-xxxxx.run.app`
- Client: `https://vendotrash-client-xxxxx.run.app`

Update your ESP32 code with the server URL:
```cpp
const char* serverURL = "https://vendotrash-server-xxxxx.run.app";
```

### Step 5: Setup Database (Optional - if using Cloud SQL)

If you want to use Cloud SQL instead of local database:

1. Go to [Cloud SQL Console](https://console.cloud.google.com/sql)
2. Click **Create Instance**
3. Choose **PostgreSQL**
4. Set instance ID: `vendotrash-db`
5. Set region: Same as Cloud Run
6. Click **Create**
7. Create database and user
8. Update `DATABASE_URL` in Cloud Run service environment variables

---

## 🐳 Docker Setup

### Server Dockerfile

**Server/Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Client Dockerfile

**Client/Dockerfile:**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Client Nginx Config

**Client/nginx.conf:**
```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://vendotrash-server:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker Compose

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: vendouser
      POSTGRES_PASSWORD: vendopass
      POSTGRES_DB: vendotrash
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U vendouser"]
      interval: 10s
      timeout: 5s
      retries: 5

  server:
    build: ./Server
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://vendouser:vendopass@postgres:5432/vendotrash
      DEBUG: "True"
      SECRET_KEY: dev-secret-key
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./Server:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  client:
    build: ./Client
    ports:
      - "5175:80"
    environment:
      VITE_API_URL: http://localhost:8000
    depends_on:
      - server

volumes:
  postgres_data:
```

---

## 🔒 Reliability Considerations

### Advantages of Cloud Run:
1. **High Availability**: 99.95% uptime SLA
2. **Auto-scaling**: Handles traffic automatically
3. **Health Checks**: Built-in monitoring
4. **Zero-downtime**: Rolling updates
5. **HTTPS**: Free SSL certificates

### Challenges & Solutions:

| Challenge | Solution |
|-----------|----------|
| **ESP32 Connection** | Use static IP or dynamic DNS (DuckDNS) |
| **Network Latency** | Deploy in same region as ESP32 |
| **Cold Starts** | Set min instances > 0 (optional) |
| **Database** | Use Cloud SQL or external database |

### 1. Network Reliability

**Problem**: ESP32 may lose connection to cloud server

**Solutions**:
- Implement retry logic in ESP32
- Use message queue (Pub/Sub) for commands
- Add local fallback mode (sensor-based when offline)

### 2. Database Connection Pooling

**Problem**: Too many database connections

**Solution**: Use connection pooling
```python
# In db.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### 3. Error Handling

**Problem**: Unhandled errors crash the system

**Solution**: Comprehensive error handling
```python
# In routes/vendo.py
try:
    # Send command to ESP32
    response = await client.post(...)
except httpx.TimeoutException:
    logger.error("ESP32 timeout")
    return {"status": "error", "message": "Device unreachable"}
except Exception as e:
    logger.error(f"Error: {e}")
    return {"status": "error", "message": str(e)}
```

### 4. Health Checks

**Problem**: Service may be down but not detected

**Solution**: Implement health checks
```python
@app.get("/health")
async def health_check():
    checks = {
        "server": "healthy",
        "database": await check_db(),
        "esp32": await check_esp32()
    }
    return checks
```

### 5. Monitoring & Logging

**Problem**: No visibility into system issues

**Solution**: Use Cloud Logging and Monitoring
```python
import logging
from google.cloud import logging as cloud_logging

# Setup cloud logging
client = cloud_logging.Client()
client.setup_logging()

logger = logging.getLogger(__name__)
logger.info("Server started")
```

---

## 📊 System Architecture Diagram

```mermaid
graph TB
    subgraph "User Layer"
        Browser[Web Browser]
    end
    
    subgraph "Application Layer"
        Client[React Client<br/>Cloud Run]
        Server[FastAPI Server<br/>Cloud Run]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL<br/>Cloud SQL)]
        Storage[Cloud Storage<br/>Images/Logs]
    end
    
    subgraph "IoT Layer"
        ESP32[ESP32 Bridge<br/>WiFi]
        Arduino[Arduino<br/>Hardware]
    end
    
    subgraph "Services"
        Vision[Computer Vision<br/>Processing]
        Queue[Pub/Sub<br/>Message Queue]
    end
    
    Browser -->|HTTPS| Client
    Client -->|REST API| Server
    Server -->|SQL| DB
    Server -->|Store| Storage
    Server -->|HTTP| ESP32
    Server -->|Process| Vision
    Server -->|Publish| Queue
    Queue -->|Subscribe| ESP32
    ESP32 -->|Serial| Arduino
    
    style Client fill:#61dafb
    style Server fill:#009688
    style DB fill:#336791
    style ESP32 fill:#e7352b
    style Arduino fill:#00979d
```

---

## 🚀 Quick Start Commands

### Local Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f server

# Stop services
docker-compose down
```

### Cloud Deployment (Super Simple)

**Just drag and drop your folders!**

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click **Create Service**
3. Upload your `Server/` or `Client/` folder (or ZIP)
4. Set port and environment variables
5. Click **Deploy**

**Or use one command:**
```bash
gcloud run deploy vendotrash-server --source ./Server --region asia-southeast1
gcloud run deploy vendotrash-client --source ./Client --region asia-southeast1
```

Cloud Run handles everything automatically - no Docker commands needed!

---

## 📝 Notes

- **ESP32 IP**: Use static IP or dynamic DNS for reliable connection
- **Database**: Use Cloud SQL Proxy for secure connections
- **Monitoring**: Set up Cloud Monitoring alerts
- **Backup**: Regular database backups via Cloud SQL
- **Security**: Use service accounts, not user credentials

---

## 🔗 Useful Links

- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Cloud SQL Connection](https://cloud.google.com/sql/docs/postgres/connect-run)

