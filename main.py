import os
import logging
import base64
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict
import json
import random
from google.cloud import aiplatform, texttospeech
from vertexai.preview.generative_models import GenerativeModel, Content, Part
from json_repair import repair_json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Vertex AI
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "us-central1")
aiplatform.init(project=PROJECT_ID, location=LOCATION)

# Initialize the Gemini 1.5 Pro model
model = GenerativeModel("gemini-1.5-pro-001")

# Initialize Text-to-Speech client
tts_client = texttospeech.TextToSpeechClient()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ... (rest of the code remains the same)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))