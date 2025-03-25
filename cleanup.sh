#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}  YouTube Downloader Cleanup Script ${NC}"
echo -e "${BLUE}===================================${NC}"

# Remove Python cache files
echo -e "\n${BLUE}Removing Python cache files...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
echo -e "${GREEN}Python cache files removed.${NC}"

# Remove node_modules if requested
echo -e "\n${YELLOW}Do you want to remove node_modules? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${BLUE}Removing node_modules...${NC}"
    rm -rf client/node_modules
    echo -e "${GREEN}node_modules removed.${NC}"
fi

# Remove virtual environment if requested
echo -e "\n${YELLOW}Do you want to remove the Python virtual environment (venv)? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${BLUE}Removing virtual environment...${NC}"
    rm -rf venv
    echo -e "${GREEN}Virtual environment removed.${NC}"
fi

# Clean downloads folder if requested
echo -e "\n${YELLOW}Do you want to clean the downloads folder? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${BLUE}Cleaning downloads folder...${NC}"
    rm -rf downloads/*
    echo -e "${GREEN}Downloads folder cleaned.${NC}"
fi

echo -e "\n${GREEN}Cleanup complete!${NC}" 