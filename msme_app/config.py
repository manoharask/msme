import os

import neo4j
import openai
import streamlit as st


def _get_secret(key: str) -> str:
    """Read from Streamlit Secrets first, fall back to environment variable."""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key)


def load_config():
    openai.api_key = _get_secret("OPENAI_API_KEY")
    return {
        "NEO4J_URI":      _get_secret("NEO4J_URI"),
        "NEO4J_USER":     _get_secret("NEO4J_USERNAME"),
        "NEO4J_PASSWORD": _get_secret("NEO4J_PASSWORD"),
    }


def get_driver(config):
    return neo4j.GraphDatabase.driver(
        config["NEO4J_URI"],
        auth=(config["NEO4J_USER"], config["NEO4J_PASSWORD"]),
    )
