# Development Setup Guide

Welcome to AetherLink development! This guide provides multiple ways to set up your development environment based on your preferences and tools.

## 🚀 Quick Start Options

Choose the method that works best for you:

1. **[VS Code Dev Container](#option-1-vs-code-dev-container-recommended)** - One-click setup ⭐ **Recommended**
2. **[Docker Compose](#option-2-docker-compose-development)** - Quick containerized setup
3. **[Local Development](#option-3-local-development)** - Traditional local setup

---

## Option 1: VS Code Dev Container (Recommended)

**Best for**: VS Code users, beginners, consistent environment

### Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Setup Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/ryanlong1004/aetherlink.git
   cd aetherlink
   ```

2. **Open in VS Code**

   ```bash
   code .
   ```

3. **Reopen in Container**

   - VS Code will detect the Dev Container configuration
   - Click "Reopen in Container" when prompted
   - Or: Press `F1` → Select "Dev Containers: Reopen in Container"

4. **Wait for setup** (first time only)

   - Container builds (~2-3 minutes)
   - Dependencies install automatically
   - Extensions install automatically

5. **Start developing!**

   ```bash
   # Terminal 1 - API
   cd api-service && ./start.sh

   # Terminal 2 - Frontend
   npm run dev
   ```

### Features

✅ Pre-configured Python & Node.js environment  
✅ All required VS Code extensions installed  
✅ Automatic port forwarding (3000, 8000)  
✅ Git configured  
✅ Network tools included  
✅ Same environment for all developers

---

## Option 2: Docker Compose Development

**Best for**: Docker users, quick setup, production-like environment

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine
- [Docker Compose](https://docs.docker.com/compose/install/)

### Setup Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/ryanlong1004/aetherlink.git
   cd aetherlink
   ```

2. **Start all services**

   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

3. **Access the application**

   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - API Health: http://localhost:8000/health

4. **Development workflow**
   - Code changes automatically reload (hot reload enabled)
   - Frontend: Changes reflect immediately
   - Backend: Uvicorn auto-reloads on file changes

### Useful Commands

```bash
# Start in background
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down

# Rebuild after dependency changes
docker-compose -f docker-compose.dev.yml up --build

# Access API container shell
docker-compose -f docker-compose.dev.yml exec api bash

# Access frontend container shell
docker-compose -f docker-compose.dev.yml exec frontend sh
```

---

## Option 3: Local Development

**Best for**: Experienced developers, full control, no Docker

### Prerequisites

Run the prerequisite checker:

```bash
./scripts/check-prerequisites.sh
```

**Required:**

- Python 3.10+ with pip
- Node.js 18+ with npm
- Git
- Network tools (arp, arp-scan)

### Automated Setup

Use our setup script for one-command installation:

```bash
./scripts/setup-dev.sh
```

This script will:

- Check all prerequisites
- Create Python virtual environment
- Install Python dependencies
- Install Node.js dependencies
- Create environment files
- Run health checks

### Manual Setup

If you prefer manual setup or the script fails:

#### 1. Setup Python Backend

```bash
# Create virtual environment
cd api-service
python3 -m venv ../.venv
source ../.venv/bin/activate  # On Windows: ..\.venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
API_HOST=0.0.0.0
API_PORT=8000
NETWORK_PREFIX=192.168.1
CORS_ORIGINS=http://localhost:3000
EOF

# Test the API
./start.sh
```

API should be running at http://localhost:8000

#### 2. Setup Frontend

```bash
# In project root
npm install

# Create .env file
cat > .env << EOF
NUXT_PUBLIC_API_BASE=http://localhost:8000
EOF

# Start development server
npm run dev
```

Frontend should be running at http://localhost:3000

---

## 🧪 Verifying Your Setup

### Quick Health Check

```bash
# Check API
curl http://localhost:8000/health

# Check network status
curl http://localhost:8000/api/network/status

# Visit frontend
open http://localhost:3000  # macOS
xdg-open http://localhost:3000  # Linux
```

### Expected Behavior

✅ API returns JSON at http://localhost:8000/health  
✅ Frontend loads at http://localhost:3000  
✅ Dashboard shows network devices  
✅ Real-time updates via WebSocket  
✅ No console errors

---

## 📁 Project Structure

```
aetherlink/
├── .devcontainer/          # VS Code Dev Container config
│   ├── devcontainer.json   # Container settings
│   ├── Dockerfile          # Dev container image
│   └── setup.sh            # Post-create setup
├── api-service/            # Python FastAPI backend
│   ├── app/
│   │   ├── main.py        # FastAPI application
│   │   ├── models/        # Pydantic models
│   │   ├── routers/       # API endpoints
│   │   └── services/      # Business logic
│   ├── Dockerfile         # Production image
│   ├── Dockerfile.dev     # Development image
│   └── requirements.txt   # Python dependencies
├── components/            # Vue components
├── pages/                 # Nuxt pages
├── scripts/               # Helper scripts
│   ├── check-prerequisites.sh
│   ├── setup-dev.sh
│   └── new-feature.sh
├── docker-compose.yml     # Production compose
├── docker-compose.dev.yml # Development compose
├── CONTRIBUTING.md        # Contribution workflow
└── DEVELOPMENT.md         # This file
```

---

## 🔧 Configuration

### Environment Variables

#### Frontend (`.env`)

```env
NUXT_PUBLIC_API_BASE=http://localhost:8000
```

#### Backend (`api-service/.env`)

```env
API_HOST=0.0.0.0
API_PORT=8000
NETWORK_PREFIX=192.168.1
CORS_ORIGINS=http://localhost:3000
```

### Network Scanning

The application scans your local network to discover devices. By default, it scans the `192.168.1.x` range. To change this:

1. Edit `api-service/.env`
2. Change `NETWORK_PREFIX=192.168.1` to your network prefix
3. Restart the API service

---

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use

**Problem**: `Address already in use` error

**Solution**:

```bash
# Find process using port 8000
lsof -i :8000
# or
netstat -ano | grep 8000

# Kill the process
kill -9 <PID>

# Or use different ports
# API: Change API_PORT in api-service/.env
# Frontend: npm run dev -- --port 3001
```

#### Python Version Issues

**Problem**: `python3: command not found` or version < 3.10

**Solution**:

```bash
# Ubuntu/Debian
sudo apt-get install python3.12 python3.12-venv

# macOS
brew install python@3.12

# Verify
python3 --version
```

#### Node.js Version Issues

**Problem**: Node.js version < 18

**Solution**:

```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20

# Or download from nodejs.org
```

#### Module Not Found Errors

**Problem**: `ModuleNotFoundError` or `Cannot find module`

**Solution**:

```bash
# Python
source .venv/bin/activate
pip install -r api-service/requirements.txt

# Node.js
rm -rf node_modules package-lock.json
npm install
```

#### Network Scanning Permission Denied

**Problem**: ARP scan fails with permission denied

**Solution**:

```bash
# Linux - install arp-scan
sudo apt-get install arp-scan

# Grant capabilities (safer than sudo)
sudo setcap cap_net_raw,cap_net_admin+eip $(which arp-scan)

# Or run API with sudo (not recommended for dev)
sudo ./start.sh
```

#### Docker Container Won't Start

**Problem**: Container exits immediately or fails to build

**Solution**:

```bash
# Clean Docker cache
docker-compose -f docker-compose.dev.yml down -v
docker system prune -a

# Rebuild from scratch
docker-compose -f docker-compose.dev.yml up --build --force-recreate
```

#### WebSocket Connection Failed

**Problem**: Frontend shows "Disconnected" status

**Solution**:

1. Verify API is running: `curl http://localhost:8000/health`
2. Check CORS settings in `api-service/.env`
3. Ensure `NUXT_PUBLIC_API_BASE` points to correct API URL
4. Check browser console for errors

---

## 🧰 Development Tools

### Recommended VS Code Extensions

Automatically installed in Dev Container, manual install for local dev:

- **Python**: `ms-python.python`
- **Pylance**: `ms-python.vscode-pylance`
- **Vue**: `Vue.volar`
- **ESLint**: `dbaeumer.vscode-eslint`
- **Prettier**: `esbenp.prettier-vscode`
- **GitLens**: `eamodio.gitlens`

### Code Formatting

```bash
# Python (Black)
cd api-service
black app/

# JavaScript/Vue (Prettier)
npm run format
```

### Linting

```bash
# Python (Flake8)
cd api-service
flake8 app/

# JavaScript (ESLint)
npm run lint
```

### Testing

```bash
# Python tests
cd api-service
pytest

# Frontend tests
npm run test
```

---

## 📚 Additional Resources

- [Contributing Guide](CONTRIBUTING.md) - Workflow for issues, branches, commits, PRs
- [README](README.md) - Project overview and features
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)
- [Nuxt Documentation](https://nuxt.com/docs) - Frontend framework
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Backend framework

---

## 🆘 Getting Help

If you encounter issues not covered here:

1. **Check existing issues**: [GitHub Issues](https://github.com/ryanlong1004/aetherlink/issues)
2. **Create a new issue**: Use the bug report template
3. **Ask in discussions**: [GitHub Discussions](https://github.com/ryanlong1004/aetherlink/discussions)

Include:

- Your setup method (Dev Container, Docker Compose, Local)
- Operating system and version
- Error messages and logs
- Steps to reproduce

---

**Happy coding! 🚀**
