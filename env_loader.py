import os
from dotenv import load_dotenv

def load_env():
    """Load environment variables from the backend/.env file"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the .env file in the backend directory
    env_path = os.path.join(script_dir, 'backend', '.env')
    
    # Load the environment variables from the .env file
    load_dotenv(env_path)
    
    # Print the API key (first few characters) to verify it's loaded
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        print(f"API key loaded successfully: {api_key[:10]}...")
        return True
    else:
        print("Failed to load API key from .env file")
        return False
