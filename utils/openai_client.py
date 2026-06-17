import os
from dotenv import load_dotenv
from openai import OpenAI

def get_openai_client() -> OpenAI:
    """
    Loads OPENAI_API_KEY from a .env file and returns an OpenAI client instance.
    Raises an error if the key is missing.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing from the environment. Please check your .env file.")
        
    return OpenAI(api_key=api_key)
