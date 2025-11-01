#!/bin/bash

# 🌙 Moon Dev Environment Setup Script
# Installs all required Python dependencies for running agents and tests

echo "🚀 Setting up Moon Dev environment..."
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Core dependencies
PACKAGES=(
    "python-dotenv"
    "anthropic"
    "termcolor"
    "pandas"
    "requests"
    "openai"
)

echo "📦 Installing required packages..."
pip install --break-system-packages "${PACKAGES[@]}"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "🎯 You can now run:"
    echo "   python3 test_ai_consultation.py"
    echo ""
else
    echo ""
    echo "❌ Installation failed!"
    exit 1
fi
