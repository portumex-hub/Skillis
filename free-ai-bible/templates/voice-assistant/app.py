"""
Free voice assistant: Whisper (STT) + Groq LLM + pyttsx3 (TTS).
Entirely free. Runs locally for STT and TTS. Groq for LLM (14,400 req/day free).

Prerequisites:
  - pip install -r requirements.txt
  - export GROQ_API_KEY=your_key   # get free at console.groq.com
  - brew install ffmpeg (macOS) or apt install ffmpeg (Linux)
"""

import os
import tempfile
import whisper
import pyttsx3
import sounddevice as sd
import soundfile as sf
import numpy as np
from groq import Groq

SAMPLE_RATE = 16000
RECORD_SECONDS = 5
WHISPER_MODEL = "base"
GROQ_MODEL = "llama-3.3-70b-versatile"

groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
stt_model = whisper.load_model(WHISPER_MODEL)
tts_engine = pyttsx3.init()

history = []


def record_audio() -> np.ndarray:
    print(f"🎙️  Listening for {RECORD_SECONDS} seconds...")
    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    return audio.flatten()


def transcribe(audio: np.ndarray) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, audio, SAMPLE_RATE)
        result = stt_model.transcribe(f.name)
    return result["text"].strip()


def ask_llm(text: str) -> str:
    history.append({"role": "user", "content": text})
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "system", "content": "You are a helpful voice assistant. Keep answers short — under 3 sentences."}] + history,
    )
    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    return reply


def speak(text: str) -> None:
    tts_engine.say(text)
    tts_engine.runAndWait()


def main():
    print("🤖 Free Voice Assistant")
    print("   Whisper (STT) + Groq Llama 70B (LLM) + pyttsx3 (TTS)")
    print("   Press Ctrl+C to quit\n")

    while True:
        audio = record_audio()
        transcript = transcribe(audio)
        if not transcript:
            continue
        print(f"You: {transcript}")

        reply = ask_llm(transcript)
        print(f"Assistant: {reply}\n")
        speak(reply)


if __name__ == "__main__":
    main()
