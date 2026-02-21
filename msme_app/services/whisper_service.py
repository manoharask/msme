import os
import streamlit as st
from openai import OpenAI


@st.cache_resource
def load_whisper_model():
    """Returns an OpenAI client — kept for API compatibility with callers."""
    return OpenAI(api_key=st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY"))


def transcribe_audio(client, audio_path, language=None):
    """Transcribe audio using OpenAI Whisper API (cloud-safe, no local model)."""
    lang = None if (not language or language == "auto") else language
    with open(audio_path, "rb") as f:
        kwargs = {"model": "whisper-1", "file": f}
        if lang:
            kwargs["language"] = lang
        result = client.audio.transcriptions.create(**kwargs)
    return result.text.strip()
