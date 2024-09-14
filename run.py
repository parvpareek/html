import asyncio
from dotenv import load_dotenv
import os
import ngrok
load_dotenv()

ngrok_token = os.getenv("NGROK_AUTH_TOKEN")

if not ngrok_token:
    raise ValueError("NGROK_AUTH_TOKEN is not set in the environment variables")

ngrok.set_auth_token(ngrok_token)


async def setup_ngrok():
    public_url = await ngrok.connect(8000)  # Assuming FastAPI runs on port 8000
    print(f"Public URL: {public_url}")
    return public_url

# Run the ngrok setup
loop = asyncio.get_event_loop()
public_url = loop.run_until_complete(setup_ngrok())

# ... rest of your FastAPI app code ...
