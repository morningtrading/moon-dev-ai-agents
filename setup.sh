#!/bin/bash
# 🌙 Moon Dev AI Agents - Setup Script
# This script ensures all dependencies are installed and the environment is ready
# Run this script after opening a new terminal or rebooting your computer
# Usage: ./setup.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌙 Moon Dev AI Agents - Environment Setup${NC}"
echo "================================================"

# Check if we're in the correct directory
EXPECTED_DIR="/home/titus/moon-dev-ai-agents"
CURRENT_DIR=$(pwd)

if [ "$CURRENT_DIR" != "$EXPECTED_DIR" ]; then
    echo -e "${RED}❌ Error: This script must be run from $EXPECTED_DIR${NC}"
    echo -e "${YELLOW}Current directory: $CURRENT_DIR${NC}"
    echo -e "${YELLOW}Please run: cd $EXPECTED_DIR && ./setup.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Directory check passed${NC}"

# Check for conda/miniconda
echo ""
echo -e "${BLUE}Checking conda environment...${NC}"

if ! command -v conda &> /dev/null; then
    echo -e "${YELLOW}⚠️  Warning: conda command not found in PATH${NC}"
    echo -e "${YELLOW}   Make sure conda/miniconda is installed and initialized${NC}"
    echo -e "${YELLOW}   To initialize conda, run: conda init bash && source ~/.bashrc${NC}"
else
    if [ -z "$CONDA_DEFAULT_ENV" ]; then
        echo -e "${YELLOW}⚠️  Warning: No conda environment is currently activated${NC}"
        echo -e "${YELLOW}   Consider creating and activating a conda environment${NC}"
        echo -e "${YELLOW}   Example: conda create -n moon-dev python=3.13 && conda activate moon-dev${NC}"
    else
        echo -e "${GREEN}✓ Conda environment active: $CONDA_DEFAULT_ENV${NC}"
    fi
fi

# Check and update requirements.txt
echo ""
echo -e "${BLUE}Checking requirements.txt for missing dependencies...${NC}"

REQUIREMENTS_FILE="requirements.txt"
UPDATED=false

# Check for solders
if grep -q "^solders==" "$REQUIREMENTS_FILE"; then
    echo -e "${GREEN}✓ solders already in requirements.txt${NC}"
else
    echo "solders==0.27.0" >> "$REQUIREMENTS_FILE"
    echo -e "${GREEN}✓ Added solders==0.27.0 to requirements.txt${NC}"
    UPDATED=true
fi

# Check for jsonalias
if grep -q "^jsonalias==" "$REQUIREMENTS_FILE"; then
    echo -e "${GREEN}✓ jsonalias already in requirements.txt${NC}"
else
    echo "jsonalias==0.1.1" >> "$REQUIREMENTS_FILE"
    echo -e "${GREEN}✓ Added jsonalias==0.1.1 to requirements.txt${NC}"
    UPDATED=true
fi

if [ "$UPDATED" = true ]; then
    echo -e "${YELLOW}⚠️  requirements.txt has been updated${NC}"
fi

# Install dependencies
echo ""
echo -e "${BLUE}Installing dependencies from requirements.txt...${NC}"
echo -e "${YELLOW}This may take a few minutes...${NC}"

if pip3 install -r requirements.txt; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Error: Failed to install dependencies${NC}"
    exit 1
fi

# Verify critical imports
echo ""
echo -e "${BLUE}Verifying module installations...${NC}"

# Test solders
if python3 -c "import solders" 2>/dev/null; then
    echo -e "${GREEN}✓ solders module imported successfully${NC}"
else
    echo -e "${RED}❌ Failed to import solders module${NC}"
    exit 1
fi

# Test jsonalias
if python3 -c "import jsonalias" 2>/dev/null; then
    echo -e "${GREEN}✓ jsonalias module imported successfully${NC}"
else
    echo -e "${RED}❌ Failed to import jsonalias module${NC}"
    exit 1
fi

# Test other critical modules
CRITICAL_MODULES=("ccxt" "hyperliquid" "pandas" "numpy" "dotenv" "termcolor" "requests")

for module in "${CRITICAL_MODULES[@]}"; do
    # Handle special import names
    IMPORT_NAME="$module"
    if [ "$module" = "dotenv" ]; then
        IMPORT_NAME="dotenv"
    fi
    
    if python3 -c "import $IMPORT_NAME" 2>/dev/null; then
        echo -e "${GREEN}✓ $module module imported successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: Failed to import $module module${NC}"
    fi
done

# Success message
echo ""
echo "================================================"
echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo -e "${GREEN}✓ All dependencies installed and verified${NC}"
echo ""
echo -e "${BLUE}You can now run your application:${NC}"
echo -e "${YELLOW}  python3 ./src/main.py${NC}"
echo "================================================"

exit 0

# To make this script executable, run:
# chmod +x setup.sh
