#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}vDrone Operations Coordinator AI - Setup${NC}"
echo "================================================"

# Check Python
echo -e "${YELLOW}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED} Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN} Python $PYTHON_VERSION found${NC}"

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${GREEN} Virtual environment created${NC}"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN} Dependencies installed${NC}"

# Check for .env file
echo -e "${YELLOW}Checking for .env file...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    echo "# OpenAI API Configuration" > .env
    echo "OPENAI_API_KEY=" >> .env
    echo -e "${YELLOW} Please add your OPENAI_API_KEY to .env file${NC}"
else
    echo -e "${GREEN}  .env file exists${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Next steps:"
echo "1. Add your OpenAI API key to .env (optional, app works without it)"
echo "2. Run: python app.py"
echo "3. Open: http://localhost:5000"
echo ""
echo "To activate the virtual environment in future sessions:"
echo "  source venv/bin/activate"
echo ""
