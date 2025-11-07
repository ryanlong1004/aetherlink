#!/bin/bash
# Automated development environment setup script
# Compatible with Linux and macOS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}===================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

print_header "AetherLink Development Setup"

# Step 1: Check prerequisites
print_header "Step 1: Checking Prerequisites"

./scripts/check-prerequisites.sh
if [ $? -ne 0 ]; then
    print_error "Prerequisites check failed. Please install missing dependencies."
    exit 1
fi

# Step 2: Setup Python environment
print_header "Step 2: Setting Up Python Environment"

cd api-service

if [ ! -d "../.venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv ../.venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

print_info "Activating virtual environment..."
source ../.venv/bin/activate

print_info "Upgrading pip..."
pip install --upgrade pip --quiet

print_info "Installing Python dependencies..."
pip install -r requirements.txt --quiet
print_success "Python dependencies installed"

cd ..

# Step 3: Setup Node.js environment
print_header "Step 3: Setting Up Node.js Environment"

if [ ! -d "node_modules" ]; then
    print_info "Installing Node.js dependencies..."
    npm install
    print_success "Node.js dependencies installed"
else
    print_success "Node.js dependencies already installed"
fi

# Step 4: Create environment files
print_header "Step 4: Creating Environment Files"

if [ ! -f ".env" ]; then
    print_info "Creating frontend .env file..."
    cat > .env << EOF
NUXT_PUBLIC_API_BASE=http://localhost:8000
EOF
    print_success "Frontend .env created"
else
    print_success "Frontend .env already exists"
fi

if [ ! -f "api-service/.env" ]; then
    print_info "Creating API .env file..."
    cat > api-service/.env << EOF
API_HOST=0.0.0.0
API_PORT=8000
NETWORK_PREFIX=192.168.1
CORS_ORIGINS=http://localhost:3000
EOF
    print_success "API .env created"
else
    print_success "API .env already exists"
fi

# Step 5: Run health checks
print_header "Step 5: Running Health Checks"

print_info "Checking Python installation..."
python3 --version
print_success "Python is ready"

print_info "Checking Node.js installation..."
node --version
print_success "Node.js is ready"

print_info "Checking npm installation..."
npm --version
print_success "npm is ready"

print_info "Verifying Python packages..."
source .venv/bin/activate
python3 -c "import fastapi, uvicorn, pydantic; print('FastAPI:', fastapi.__version__); print('Uvicorn:', uvicorn.__version__)"
print_success "Python packages verified"

# Step 6: Setup git hooks
print_header "Step 6: Setting Up Git Hooks"

if [ ! -f ".git/hooks/pre-push" ]; then
    print_warning "Git pre-push hook not found. Workflow enforcement not active."
    print_info "The hook should be created automatically by the repository."
else
    print_success "Git hooks configured"
fi

# Final summary
print_header "Setup Complete! 🎉"

echo -e "${GREEN}Your development environment is ready!${NC}\n"
echo -e "Quick start commands:\n"
echo -e "  ${BLUE}Terminal 1 - Start API:${NC}"
echo -e "    cd api-service"
echo -e "    source ../.venv/bin/activate"
echo -e "    ./start.sh"
echo -e ""
echo -e "  ${BLUE}Terminal 2 - Start Frontend:${NC}"
echo -e "    npm run dev"
echo -e ""
echo -e "  ${BLUE}Or use Docker Compose:${NC}"
echo -e "    docker-compose -f docker-compose.dev.yml up --build"
echo -e ""
echo -e "Access the application:"
echo -e "  Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "  API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo -e ""
echo -e "For more information, see ${BLUE}DEVELOPMENT.md${NC}"
