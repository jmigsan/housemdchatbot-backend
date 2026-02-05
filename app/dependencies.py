from google import genai
from functools import cache
from openai import OpenAI
from app.config import get_settings
from pinecone import Pinecone

@cache
def get_gemini_client():
    settings = get_settings()
    client = genai.Client(api_key=settings.gemini_api_key)
    return client

@cache
def get_housemd_client():
    settings = get_settings()
    housemd_client = OpenAI(
        base_url=f"https://api.runpod.ai/v2/{settings.runpod_project_id}/openai/v1",
        api_key=settings.runpod_api_key
    )
    return housemd_client

@cache
def get_deepinfra_client():
    settings = get_settings()
    deepinfra_client = OpenAI(
        api_key=settings.deepinfra_api_key,
        base_url="https://api.deepinfra.com/v1/openai",
    )
    return deepinfra_client

@cache
def get_pinecone_index():
    settings = get_settings()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    pinecone_index = pc.Index(settings.pinecone_index_name)
    return pinecone_index
