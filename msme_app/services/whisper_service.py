import streamlit as st
import whisper


@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")


def transcribe_audio(model, audio_path, language=None):
    if language == "auto" or not language:
        result = model.transcribe(audio_path)
    else:
        result = model.transcribe(audio_path, language=language)
    return result["text"].strip()
