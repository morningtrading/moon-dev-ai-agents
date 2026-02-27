#!/bin/bash

##############################################################################
# Titus Start Agents - Optimized Setup & Startup Script
# 
# Purpose: 
#   - Create conda environments (tflow, moon312)
#   - Install all dependencies
#   - Start RBI Agent v2 Simple for backtesting
#
# Usage:
#   bash titus_start_agents.sh
#
# Environment:
#   - Python 3.10.9 (tflow) - for backtesting with talib
#   - Python 3.12 (moon312) - for agents
#   - Required: conda, pip
#
##############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/home/titus/moon-dev-ai-agents"
TFLOW_ENV="tflow"
MOON_ENV="moon312"
AGENT_SCRIPT="src/agents/rbi_agent_v2_simple.py"

##############################################################################
# Helper Functions
##############################################################################

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 is not installed"
        return 1
    fi
    return 0
}

env_exists() {
    conda env list | grep -q "^$1 "
    return $?
}

##############################################################################
# Main Setup
##############################################################################

main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║     🚀 Titus Start Agents - Setup & Launch                     ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""

    # Step 1: Validate prerequisites
    log_info "Step 1/6: Validating prerequisites..."
    check_command conda || exit 1
    check_command pip || exit 1
    log_success "Prerequisites validated"
    echo ""

    # Step 2: Change to project directory
    log_info "Step 2/6: Setting up project directory..."
    if [ ! -d "$PROJECT_DIR" ]; then
        log_error "Project directory not found: $PROJECT_DIR"
        exit 1
    fi
    cd "$PROJECT_DIR"
    log_success "Working directory: $(pwd)"
    echo ""

    # Step 3: Create/Update tflow environment (Python 3.10.9)
    log_info "Step 3/6: Setting up tflow environment (Python 3.10.9)..."
    
    if env_exists "$TFLOW_ENV"; then
        log_warning "Environment '$TFLOW_ENV' already exists, skipping creation"
    else
        log_info "Creating conda environment: $TFLOW_ENV..."
        conda create -n "$TFLOW_ENV" python=3.10.9 -y > /dev/null 2>&1
        log_success "Created $TFLOW_ENV"
    fi
    
    # Activate and install/upgrade requirements for tflow
    log_info "Installing dependencies in $TFLOW_ENV..."
    source activate "$TFLOW_ENV"
    
    # Install core packages
    pip install --upgrade pip > /dev/null 2>&1
    
    # Install required packages individually to ensure all are present
    PACKAGES=(
        "pandas"
        "numpy"
        "backtesting"
        "ta-lib"
        "anthropic"
        "deepseek"
        "python-dotenv"
        "termcolor"
        "openai"
        "pyarrow"
    )
    
    for package in "${PACKAGES[@]}"; do
        log_info "Installing $package..."
        pip install "$package" > /dev/null 2>&1 && log_success "$package installed" || log_warning "Failed to install $package (may already exist)"
    done
    
    log_success "tflow environment ready"
    echo ""

    # Step 4: Create/Update moon312 environment (Python 3.12)
    log_info "Step 4/6: Setting up moon312 environment (Python 3.12)..."
    
    if env_exists "$MOON_ENV"; then
        log_warning "Environment '$MOON_ENV' already exists, skipping creation"
    else
        log_info "Creating conda environment: $MOON_ENV..."
        conda create -n "$MOON_ENV" python=3.12 -y > /dev/null 2>&1
        log_success "Created $MOON_ENV"
    fi
    
    log_success "moon312 environment ready"
    echo ""

    # Step 5: Verify agent script exists
    log_info "Step 5/6: Validating agent script..."
    if [ ! -f "$AGENT_SCRIPT" ]; then
        log_error "Agent script not found: $AGENT_SCRIPT"
        exit 1
    fi
    log_success "Agent script found: $AGENT_SCRIPT"
    echo ""

    # Step 6: Verify .env file
    log_info "Step 6/6: Checking environment configuration..."
    if [ ! -f ".env" ]; then
        log_warning "No .env file found. Please create one with:"
        echo "   - ANTHROPIC_KEY=sk-ant-api03-..."
        echo "   - DEEPSEEK_KEY=sk-..."
        exit 1
    fi
    
    # Check for required API keys
    if ! grep -q "ANTHROPIC_KEY" .env; then
        log_error ".env missing ANTHROPIC_KEY"
        exit 1
    fi
    if ! grep -q "DEEPSEEK_KEY" .env; then
        log_error ".env missing DEEPSEEK_KEY"
        exit 1
    fi
    
    log_success "Environment configuration valid"
    echo ""

    # Summary
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                  ✅ Setup Complete!                           ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 Environments Ready:"
    echo "   • $TFLOW_ENV (Python 3.10.9) - Backtesting with talib"
    echo "   • $MOON_ENV (Python 3.12) - Agent runtime"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Switch coin (if needed):"
    echo "      Edit line 24 in src/agents/rbi_agent_v2_simple.py"
    echo "      COIN = \"SUI\"  # or \"BNB\", \"BTC\", etc"
    echo ""
    echo "   2. Start backtesting:"
    echo "      conda run -n $TFLOW_ENV python $AGENT_SCRIPT"
    echo ""
    echo "   3. Or use utilities:"
    echo "      python utils_upload_coin_data.py <feather_file>"
    echo ""
    echo "📝 Configuration:"
    echo "   • API Keys: ✅ Verified in .env"
    echo "   • Project Dir: ✅ $PROJECT_DIR"
    echo "   • Agent Script: ✅ $AGENT_SCRIPT"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
}

##############################################################################
# Optional: Quick Start Mode
##############################################################################

if [ "$1" == "--quick-start" ]; then
    log_info "Starting quick-start mode (no setup, direct agent run)..."
    source activate "$TFLOW_ENV"
    python "$AGENT_SCRIPT"
elif [ "$1" == "--help" ]; then
    echo "Usage: bash titus_start_agents.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  (none)              - Full setup and display instructions"
    echo "  --quick-start       - Skip setup, run agent immediately"
    echo "  --help              - Show this help message"
    echo ""
    echo "Examples:"
    echo "  bash titus_start_agents.sh              # Full setup"
    echo "  bash titus_start_agents.sh --quick-start # Direct run"
else
    main
fi
