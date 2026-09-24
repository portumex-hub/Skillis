#!/bin/bash
# One-click Ollama setup: installs Ollama and pulls Llama 3.2

set -e

echo "🦙 Setting up Ollama (Local LLM — runs 100% offline)..."
echo ""

OS="$(uname -s)"

if [ "$OS" = "Darwin" ]; then
    if command -v brew &> /dev/null; then
        brew install ollama --quiet
    else
        curl -fsSL https://ollama.com/install.sh | sh
    fi
elif [ "$OS" = "Linux" ]; then
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "❌ Windows detected. Download Ollama from: https://ollama.com/download"
    exit 1
fi

echo "✅ Ollama installed"
echo ""

# Start Ollama service in background
ollama serve &>/dev/null &
sleep 2

# Pull model
echo "📦 Downloading Llama 3.2 (2GB — runs on 8GB RAM)..."
ollama pull llama3.2

echo ""
echo "✅ All done! Starting interactive chat..."
echo "   Type /bye to exit"
echo ""
ollama run llama3.2
