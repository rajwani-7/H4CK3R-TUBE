#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Downloading sound effects and favicon...${NC}"

# Create directories if they don't exist
mkdir -p static/sounds

# Download sound effects
echo -e "${BLUE}Downloading click sound...${NC}"
curl -L "https://www.soundjay.com/buttons/sounds/button-21.mp3" -o static/sounds/click.mp3

echo -e "${BLUE}Downloading success sound...${NC}"
curl -L "https://www.soundjay.com/buttons/sounds/button-35.mp3" -o static/sounds/success.mp3

echo -e "${BLUE}Downloading error sound...${NC}"
curl -L "https://www.soundjay.com/buttons/sounds/button-10.mp3" -o static/sounds/error.mp3

echo -e "${BLUE}Downloading typing sound...${NC}"
curl -L "https://www.soundjay.com/mechanical/sounds/typewriter-key-1.mp3" -o static/sounds/typing.mp3

# Download favicon
echo -e "${BLUE}Downloading favicon...${NC}"
curl -L "https://www.iconarchive.com/download/i103365/paomedia/small-n-flat/device-desktop.ico" -o static/favicon.ico

echo -e "${GREEN}Assets downloaded successfully!${NC}" 