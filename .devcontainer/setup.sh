#!/bin/bash
# Post-create setup script for Dev Container

set -e

echo "🚀 Setting up AetherLink development environment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd /workspace/api-service
python3 -m venv /workspace/.venv
source /workspace/.venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd /workspace
npm install

# Create .env file if it doesn't exist
if [ ! -f /workspace/.env ]; then
    echo "📝 Creating .env file..."
    cat > /workspace/.env << EOF
NUXT_PUBLIC_API_BASE=http://localhost:8000
EOF
fi

if [ ! -f /workspace/api-service/.env ]; then
    echo "📝 Creating API .env file..."
    cat > /workspace/api-service/.env << EOF
API_HOST=0.0.0.0
API_PORT=8000
NETWORK_PREFIX=192.168.1
CORS_ORIGINS=http://localhost:3000
EOF
fi

echo "✅ Development environment setup complete!"
echo ""
echo "Quick start commands:"
echo "  Start API:      cd api-service && ./start.sh"
echo "  Start Frontend: npm run dev"
echo ""
echo "Or use the integrated terminal tasks in VS Code!"
