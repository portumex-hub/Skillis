#!/bin/bash
# One-click Groq setup: installs SDK and runs a test query

set -e

echo "🚀 Setting up Groq (Free LLM API — 14,400 req/day)..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Install it from https://python.org"
    exit 1
fi

# Install SDK
pip install groq --quiet
echo "✅ Groq SDK installed"

# Prompt for key
echo ""
echo "👉 Get your free API key at: https://console.groq.com"
echo ""
read -p "Paste your Groq API key here: " GROQ_KEY

if [ -z "$GROQ_KEY" ]; then
    echo "❌ No key provided. Exiting."
    exit 1
fi

# Export for this session
export GROQ_API_KEY="$GROQ_KEY"

# Save to shell profile
SHELL_RC="$HOME/.zshrc"
[ -f "$HOME/.bashrc" ] && SHELL_RC="$HOME/.bashrc"
echo "export GROQ_API_KEY=\"$GROQ_KEY\"" >> "$SHELL_RC"
echo "✅ Key saved to $SHELL_RC"

# Test it
echo ""
echo "🧪 Running test query..."
python3 - <<'EOF'
import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Say 'Groq setup successful!' and nothing else."}]
)
print("")
print("🎉", response.choices[0].message.content)
print("")
print("You are now running Llama 3.3 70B for FREE. Happy building!")
EOF
