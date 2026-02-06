import os

import neo4j
import openai
from dotenv import load_dotenv


def load_config():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    return {
        "NEO4J_URI": os.getenv("NEO4J_URI"),
        "NEO4J_USER": os.getenv("NEO4J_USERNAME"),
        "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"),
    }


def get_driver(config):
    return neo4j.GraphDatabase.driver(
        config["NEO4J_URI"],
        auth=(config["NEO4J_USER"], config["NEO4J_PASSWORD"]),
    )
