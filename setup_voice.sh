#!/bin/bash
# ============================================================================
# Voice Conversation Loop - Setup Script
# ============================================================================
# Run this once to install dependencies for CLI Gem voice conversation.
#
# Usage: chmod +x setup_voice.sh && ./setup_voice.sh
# ============================================================================

echo "💎 Setting up CLI Gem Voice Conversation..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install it first."
    exit 1
fi

echo "✅ Python 3 found"

# Install system dependencies for PyAudio (Linux)
echo ""
echo "[Installing system dependencies...]"
if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y portaudio19-dev python3-pyaudio ffmpeg
elif command -v dnf &> /dev/null; then
    sudo dnf install -y portaudio-devel ffmpeg
elif command -v pacman &> /dev/null; then
    sudo pacman -S portaudio ffmpeg
else
    echo "⚠️  Unknown package manager. Install portaudio manually."
fi

# Install Python packages
echo ""
echo "[Installing Python packages into venv...]"
zion-engine/venv/bin/pip install --upgrade pip
zion-engine/venv/bin/pip install SpeechRecognition pyaudio google-generativeai

# Optional: Install gTTS as fallback
zion-engine/venv/bin/pip install gTTS

# Optional: Install newer google-genai for TTS
zion-engine/venv/bin/pip install google-genai

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "============================================"
echo "NEXT STEPS:"
echo "============================================"
echo ""
echo "1. Set your Gemini API key:"
echo "   export GEMINI_API_KEY='your-key-here'"
echo ""
echo "2. Run the voice loop:"
echo "   python voice_conversation_loop.py"
echo ""
echo "3. Or test without mic first:"
echo "   python voice_conversation_loop.py --test"
echo ""
echo "💎 Gem is waiting for you."
