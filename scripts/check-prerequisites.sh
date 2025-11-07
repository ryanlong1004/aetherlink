#!/bin/bash
# Check if all required prerequisites are installed

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

MISSING_DEPS=0

check_command() {
    local cmd=$1
    local version_flag=$2
    local install_msg=$3
    local is_optional=$4
    
    if command -v $cmd &> /dev/null; then
        echo -e "${GREEN}✓${NC} $cmd is installed"
        if [ ! -z "$version_flag" ]; then
            VERSION=$($cmd $version_flag 2>&1 | head -n 1)
            echo -e "  Version: $VERSION"
        fi
        return 0
    else
        echo -e "${RED}✗${NC} $cmd is not installed"
        if [ ! -z "$install_msg" ]; then
            echo -e "  Install: $install_msg"
        fi
        if [ "$is_optional" != "optional" ]; then
            MISSING_DEPS=1
        fi
        return 1
    fi
}

check_python_version() {
    if command -v python3 &> /dev/null; then
        VERSION=$(python3 --version | cut -d' ' -f2)
        MAJOR=$(echo $VERSION | cut -d'.' -f1)
        MINOR=$(echo $VERSION | cut -d'.' -f2)
        
        if [ $MAJOR -ge 3 ] && [ $MINOR -ge 10 ]; then
            echo -e "${GREEN}✓${NC} Python $VERSION (meets requirement >=3.10)"
            return 0
        else
            echo -e "${RED}✗${NC} Python $VERSION (requires >=3.10)"
            MISSING_DEPS=1
            return 1
        fi
    else
        echo -e "${RED}✗${NC} Python 3 is not installed"
        MISSING_DEPS=1
        return 1
    fi
}

check_node_version() {
    if command -v node &> /dev/null; then
        VERSION=$(node --version | sed 's/v//')
        MAJOR=$(echo $VERSION | cut -d'.' -f1)
        
        if [ $MAJOR -ge 18 ]; then
            echo -e "${GREEN}✓${NC} Node.js $VERSION (meets requirement >=18)"
            return 0
        else
            echo -e "${RED}✗${NC} Node.js $VERSION (requires >=18)"
            echo -e "  Install: https://nodejs.org/"
            MISSING_DEPS=1
            return 1
        fi
    else
        echo -e "${RED}✗${NC} Node.js is not installed"
        echo -e "  Install: https://nodejs.org/"
        MISSING_DEPS=1
        return 1
    fi
}

echo "Checking prerequisites..."
echo ""

# Required for development
echo "Core Requirements:"
check_python_version
check_node_version
check_command npm "--version"
check_command git "--version"

echo ""
echo "Network Tools (for ARP scanning):"
check_command arp "--help" "Usually pre-installed on Linux/macOS"
if [ "$(uname)" = "Linux" ]; then
    check_command arp-scan "--version" "apt-get install arp-scan (Debian/Ubuntu) or yum install arp-scan (RHEL/CentOS)"
fi

echo ""
echo "Optional but Recommended:"
check_command docker "--version" "https://docs.docker.com/get-docker/" "optional" || true
check_command docker-compose "--version" "https://docs.docker.com/compose/install/" "optional" || true

echo ""

if [ $MISSING_DEPS -eq 1 ]; then
    echo -e "${RED}Some required dependencies are missing.${NC}"
    echo -e "Please install them before continuing."
    echo ""
    echo "Quick install commands:"
    echo ""
    if [ "$(uname)" = "Linux" ]; then
        echo "Ubuntu/Debian:"
        echo "  sudo apt-get update"
        echo "  sudo apt-get install python3 python3-venv python3-pip nodejs npm git arp-scan"
        echo ""
        echo "RHEL/CentOS/Fedora:"
        echo "  sudo dnf install python3 python3-pip nodejs npm git"
    elif [ "$(uname)" = "Darwin" ]; then
        echo "macOS (using Homebrew):"
        echo "  brew install python node git"
    fi
    exit 1
else
    echo -e "${GREEN}All required prerequisites are installed!${NC}"
    exit 0
fi
