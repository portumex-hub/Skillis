# Free Voice Assistant

Full voice assistant pipeline: **speak → transcribe → LLM → speak back.**
100% free. No paid APIs.

| Component | Tool | Cost |
|-----------|------|------|
| Speech-to-Text | OpenAI Whisper (local) | $0 |
| LLM | Groq Llama 3.3 70B | $0 (14,400 req/day) |
| Text-to-Speech | pyttsx3 (local) | $0 |

## Setup

```bash
# macOS
brew install ffmpeg portaudio

# Linux
sudo apt install ffmpeg portaudio19-dev

pip install -r requirements.txt
export GROQ_API_KEY=your_key_here   # free at console.groq.com
python app.py
```

## Notes

- Whisper `base` model works well and is small. Swap for `medium` or `large` for better accuracy.
- First run downloads the Whisper model (~150MB, one-time).
- Speaks back using your OS's built-in TTS voices via pyttsx3.
