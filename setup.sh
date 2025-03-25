#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================${NC}"
echo -e "${BLUE}  YouTube Downloader Setup Script   ${NC}"
echo -e "${BLUE}====================================${NC}"

# Check if Python is installed
echo -e "\n${BLUE}Checking for Python...${NC}"
if command -v python3 >/dev/null 2>&1; then
    echo -e "${GREEN}Python is installed!${NC}"
else
    echo -e "${RED}Python is not installed. Please install Python 3.6+ and try again.${NC}"
    exit 1
fi

# Check if Node.js and npm are installed
echo -e "\n${BLUE}Checking for Node.js and npm...${NC}"
if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
    echo -e "${GREEN}Node.js and npm are installed!${NC}"
    NODE_VERSION=$(node -v)
    NPM_VERSION=$(npm -v)
    echo -e "Node.js version: ${NODE_VERSION}"
    echo -e "npm version: ${NPM_VERSION}"
else
    echo -e "${RED}Node.js and/or npm are not installed. Please install Node.js 14+ and npm 6+ and try again.${NC}"
    exit 1
fi

# Create virtual environment
echo -e "\n${BLUE}Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo -e "\n${BLUE}Installing backend dependencies...${NC}"
pip install -r requirements.txt

# Install frontend dependencies
echo -e "\n${BLUE}Installing frontend dependencies...${NC}"
cd client && npm install
cd ..

# Create downloads directory if it doesn't exist
echo -e "\n${BLUE}Creating downloads directory...${NC}"
mkdir -p downloads

# Download assets
echo -e "\n${BLUE}Downloading assets (sounds and favicon)...${NC}"
chmod +x download_assets.sh
./download_assets.sh

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "\n${BLUE}To run the application:${NC}"
echo -e "1. Activate the virtual environment: ${GREEN}source venv/bin/activate${NC}"
echo -e "2. Start the application: ${GREEN}python app.py${NC}"
echo -e "   - Or use the start_app.sh script: ${GREEN}chmod +x start_app.sh && ./start_app.sh${NC}"
echo -e "\nThe application will be available at: ${GREEN}http://localhost:5000${NC}" 