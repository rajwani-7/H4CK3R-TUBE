#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting YouTube Downloader Application...${NC}"

# Check if we have a virtual environment
if [ -d "venv" ]; then
    echo -e "${GREEN}Using virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${BLUE}No virtual environment found, using system Python...${NC}"
fi

# Run the application
python app.py

# Check if there was an error
if [ $? -ne 0 ]; then
    echo
    echo -e "${RED}There was an error starting the application.${NC}"
    echo -e "${BLUE}Please check if you have installed all required dependencies.${NC}"
    echo -e "${BLUE}Try running setup.sh first or check the README for instructions.${NC}"
    read -p "Press Enter to continue..."
fi 