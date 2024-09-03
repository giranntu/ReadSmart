import os
import logging
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Vertex AI
PROJECT_ID = "meat-ry"
LOCATION = "us-central1"
aiplatform.init(project=PROJECT_ID, location=LOCATION)

# Initialize the Gemini 1.5 Pro model
model = GenerativeModel("gemini-1.5-pro-001")

# Initialize Text-to-Speech client
tts_client = texttospeech.TextToSpeechClient()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class Student(BaseModel):
    student_id: str
    grade_level: int

class SentenceExplanationRequest(BaseModel):
    sentence: str
    context: str
    grade_level: int

class QuizGenerationRequest(BaseModel):
    student_id: str
    text: str
    explained_sentences: List[str]

class ChatMessage(BaseModel):
    student_id: str
    message: str

class TTSRequest(BaseModel):
    text: str

# In-memory storage for demo purposes
students = {}
chat_sessions = {}

@app.get("/", response_class=HTMLResponse)
async def get_home():
    with open("static/index.html", "r") as file:
        return file.read()

@app.post("/login")
async def login(student: Student):
    if student.student_id not in students:
        students[student.student_id] = {
            "grade_level": student.grade_level,
            "explained_sentences": [],
            "progress": [random.randint(50, 80)],  # Start with a random progress
            "achievements": []
        }
    # Initialize chat session for the student
    chat_sessions[student.student_id] = model.start_chat(
        history=[
            Content(
                role="user",
                parts=[Part.from_text(f"You are a helpful Reading Buddy for a grade {student.grade_level} student. The student's ID is {student.student_id}. Please provide friendly and educational responses to help the student with their reading.")],
            ),
            Content(role="model", parts=[Part.from_text("Understood. I'm here to help the student with their reading. I'll provide friendly and educational responses tailored to their grade level.")]),
        ]
    )
    return {"status": "success", "message": "Logged in successfully"}

@app.get("/student/{student_id}")
async def get_student_info(student_id: str):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    return students[student_id]

@app.post("/explain_sentence")
async def explain_sentence(request: SentenceExplanationRequest):
    try:
        logger.info(f"Explaining sentence: {request.sentence[:50]}..., Grade: {request.grade_level}")
        logger.info(f"Context: {request.context[:100]}...")  # Log first 100 characters of context

        prompt = f"""
        Explain the following sentence for a {request.grade_level}th grade student:
        "{request.sentence}"

        Context:
        {request.context}

        Provide:
        1. A clear, simple explanation of the sentence's meaning
        2. Highlight any important vocabulary or grammar points
        3. If relevant, explain how this sentence relates to the broader context

        Format your response in Markdown.
        Be direct and avoid unnecessary phrases.
        """

        logger.info(f"Sending prompt to Gemini: {prompt[:100]}...")  # Log first 100 characters of prompt
        response = model.generate_content(prompt)
        logger.info(f"Raw Gemini response: {response.text}")

        return {"explanation": response.text}

    except Exception as e:
        logger.error(f"Error in explain_sentence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_quiz")
async def generate_quiz(request: QuizGenerationRequest):
    try:
        student = students.get(request.student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        prompt = f"""
        Generate a quiz based on the following text and explained sentences for a {student['grade_level']}th grade student:

        Text: {request.text}

        Explained sentences: {', '.join(request.explained_sentences)}

        Create a quiz with the following:
        1. 5 multiple-choice questions
        2. 3 true/false questions
        3. 2 short answer questions

        Ensure the questions cover both the content of the text and the explained sentences.
        Format the response as a JSON object with 'multiple_choice', 'true_false', and 'short_answer' keys.
        For multiple-choice questions, include 4 options for each question and indicate the correct answer.

        Example format:
        {{
            "multiple_choice": [
                {{
                    "question": "What is the capital of France?",
                    "options": ["London", "Berlin", "Paris", "Madrid"],
                    "correct_answer": "Paris"
                }},
                ...
            ],
            "true_false": [
                {{
                    "question": "The Earth is flat.",
                    "correct_answer": false
                }},
                ...
            ],
            "short_answer": [
                {{
                    "question": "What is the largest planet in our solar system?",
                    "answer": "Jupiter"
                }},
                ...
            ]
        }}
        """

        logger.info(f"Sending quiz generation prompt to Gemini: {prompt[:100]}...")
        response = model.generate_content(prompt)
        logger.info(f"Raw Gemini response for quiz generation: {response.text}")

        # Repair and parse JSON
        repaired_json = repair_json(response.text)
        quiz = json.loads(repaired_json)

        logger.info(f"Repaired and parsed quiz: {json.dumps(quiz, indent=2)}")

        # Update student progress
        new_progress = min(student['progress'][-1] + random.randint(5, 15), 100)
        student['progress'].append(new_progress)

        # Check for achievements
        if new_progress >= 90 and "Outstanding Student" not in student['achievements']:
            student['achievements'].append("Outstanding Student")
        elif new_progress >= 75 and "Super Star" not in student['achievements']:
            student['achievements'].append("Super Star")
        elif new_progress >= 60 and "Super Student" not in student['achievements']:
            student['achievements'].append("Super Student")

        return quiz

    except Exception as e:
        logger.error(f"Error in generate_quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(message: ChatMessage):
    try:
        logger.info(f"Received chat message from student {message.student_id}: {message.message}")
        
        if message.student_id not in chat_sessions:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        chat_session = chat_sessions[message.student_id]
        response = chat_session.send_message(message.message)
        
        logger.info(f"Sent chat response: {response.text}")
        
        return {"response": response.text}
    
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/text-to-speech")
async def text_to_speech(request: TTSRequest):
    try:
        synthesis_input = texttospeech.SynthesisInput(text=request.text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-SG",
            name="en-SG-Standard-A",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        return {"audio_content": response.audio_content.decode('utf-8')}

    except Exception as e:
        logger.error(f"Error in text-to-speech: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sample_readings")
async def get_sample_readings():
    samples = [
        {
            "title": "The Lion and the Mouse",
            "text": """# The Lion and the Mouse

Once upon a time, in the heart of the **African savanna**, a mighty lion was taking a nap under the shade of a large acacia tree. The hot sun beat down on the golden grass, and the air was filled with the sounds of various animals going about their day.

Suddenly, a tiny mouse, scurrying through the grass in search of food, accidentally ran across the lion's massive paw. The lion's eyes snapped open, and with lightning-quick reflexes, he caught the mouse in his giant paw.

The little mouse, trembling with fear, squeaked, "Oh, please, Mr. Lion, don't eat me! I'm so small, I wouldn't even make a tasty snack for you. If you let me go, I promise I'll help you someday!"

The lion, amused by the mouse's bold claim, laughed heartily. "You? Help me? How could such a tiny creature ever help the king of the jungle?" But feeling generous, he decided to let the mouse go.

A few days later, the lion was prowling through the jungle when he suddenly found himself trapped in a hunter's net. He roared and thrashed, but the more he struggled, the tighter the net became. His powerful roars echoed through the forest.

The little mouse, hearing the lion's cries, came running. He recognized the lion's voice and remembered his promise. Without hesitation, the mouse began gnawing at the thick ropes of the net with his sharp teeth.

Bit by bit, the mouse chewed through the ropes until finally, the lion was able to break free. The lion, amazed and grateful, turned to the mouse and said, "I was wrong to doubt you, little one. You have saved my life, and I will never forget your kindness."

From that day on, the lion and the mouse became the best of friends, proving that:

1. Even the smallest creatures can make a big difference.
2. Kindness is always worth giving.
3. True friendship knows no boundaries.

**The End**""",
            "grade_level": 2
        },
        {
            "title": "The Water Cycle",
            "text": """# The Amazing Water Cycle

Water is one of the most important substances on Earth. It's constantly moving and changing form in a never-ending cycle called the **water cycle**. Let's explore the four main stages of this fascinating process!

## 1. Evaporation

- The sun heats up water in oceans, lakes, and rivers.
- Water turns into an invisible gas called water vapor.
- This vapor rises into the air.

## 2. Condensation

- As water vapor rises, it cools down.
- Tiny water droplets form and gather together.
- These droplets create clouds in the sky.

## 3. Precipitation

- When the water droplets in clouds get too heavy, they fall back to Earth.
- This can be in the form of:
  - Rain
  - Snow
  - Sleet
  - Hail

## 4. Collection

- Fallen water collects in various places:
  - Oceans
  - Lakes
  - Rivers
  - Underground aquifers

And then the cycle starts all over again!

### Why is the Water Cycle Important?

1. It provides fresh water for plants and animals.
2. It helps regulate Earth's temperature.
3. It shapes our landscapes through erosion and deposition.

**Fun Fact**: The water you drink today might have been the same water a dinosaur drank millions of years ago!

Remember, every time you see a cloud or feel a raindrop, you're witnessing the amazing water cycle in action!""",
            "grade_level": 4
        },
        {
            "title": "The Invention of the Telephone",
            "text": """# The Invention of the Telephone: Connecting the World

## Background

The telephone, one of the most revolutionary inventions in human history, was created by **Alexander Graham Bell** in 1876. This invention would go on to change the way people communicate across the globe.

## Alexander Graham Bell

- Born: March 3, 1847, in Edinburgh, Scotland
- Moved to Canada in 1870 and later to the United States
- Worked as a teacher for the deaf
- Married Mabel Hubbard, who was deaf

## The Path to Invention

1. Bell was fascinated by the idea of transmitting speech electrically.
2. He worked with Thomas Watson, a skilled electrician, to develop his ideas.
3. They experimented with various designs and materials.

## The Breakthrough

On **March 10, 1876**, Bell made the first successful telephone call to Watson, who was in the next room. He famously said:

> "Mr. Watson, come here, I want to see you."

This simple sentence marked the birth of the telephone.

## Impact and Legacy

1. Initially seen as a novelty, the telephone quickly became essential for:
   - Business communication
   - Personal connections
   - Emergency services

2. Bell's invention led to the formation of the Bell Telephone Company, which later became AT&T.

3. The telephone revolutionized long-distance communication, making it instant and personal.

4. It paved the way for future technologies like:
   - Mobile phones
   - The internet
   - Video calling

## Fun Facts

- Bell refused to have a telephone in his study, considering it a distraction.
- The first transcontinental telephone call was made in 1915, from New York to San Francisco.

## Conclusion

The invention of the telephone by Alexander Graham Bell was a pivotal moment in history. It brought people closer together, revolutionized business, and laid the foundation for the interconnected world we live in today.

**Question for Thought**: How do you think our world would be different if the telephone had never been invented?""",
            "grade_level": 6
        }
    ]
    return JSONResponse(content=samples)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)