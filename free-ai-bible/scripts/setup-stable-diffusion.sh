#!/bin/bash
# One-click Stable Diffusion setup via diffusers

set -e

echo "🎨 Setting up local image generation (Stable Diffusion)..."
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Install it from https://python.org"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies (this may take a few minutes)..."
pip install diffusers transformers accelerate torch --quiet
echo "✅ Dependencies installed"

read -p "Enter your image prompt: " PROMPT

if [ -z "$PROMPT" ]; then
    PROMPT="a futuristic developer workspace with holographic screens"
fi

echo ""
echo "🖼️ Generating: \"$PROMPT\""
echo "   (First run downloads the model — ~4GB, one-time only)"
echo ""

python3 - <<EOF
from diffusers import StableDiffusionPipeline
import torch

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float32
)

print("⏳ Generating image...")
image = pipe("$PROMPT").images[0]
image.save("output.png")
print("")
print("✅ Image saved to: output.png")
print("   Open it with: open output.png")
EOF

# Try to open the image
if command -v open &> /dev/null; then
    open output.png
elif command -v xdg-open &> /dev/null; then
    xdg-open output.png
fi
