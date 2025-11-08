#!/bin/bash
# Arr Suite MCP Server Setup Script

set -e

echo "=================================="
echo "Arr Suite MCP Server Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo -e "${RED}Error: Python 3.10 or higher is required${NC}"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install package
echo "Installing arr-suite-mcp..."
pip install --upgrade pip
pip install -e .
echo -e "${GREEN}✓ Package installed${NC}"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env with your API keys and settings${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists${NC}"
fi
echo ""

# Create directories
echo "Creating directories..."
mkdir -p logs
mkdir -p backups
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Run tests
echo "Running tests..."
if pip install -e ".[dev]" 2>/dev/null; then
    if pytest tests/ 2>/dev/null; then
        echo -e "${GREEN}✓ All tests passed${NC}"
    else
        echo -e "${YELLOW}⚠ Some tests failed (this is okay for initial setup)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Dev dependencies not installed, skipping tests${NC}"
fi
echo ""

echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   ${YELLOW}nano .env${NC}"
echo ""
echo "2. Activate the virtual environment:"
echo "   ${YELLOW}source venv/bin/activate${NC}"
echo ""
echo "3. Run the server:"
echo "   ${YELLOW}arr-suite-mcp${NC}"
echo ""
echo "4. Configure Claude Desktop by editing:"
echo "   ${YELLOW}~/Library/Application Support/Claude/claude_desktop_config.json${NC}"
echo ""
echo "For detailed instructions, see INSTALL.md"
echo ""
