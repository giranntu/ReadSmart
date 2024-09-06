# Personalized Reading Support System

This project uses Gemini 1.5 Pro to provide an interactive and engaging personalized reading support experience for students. It analyzes student reading submissions, provides feedback, generates tailored reading materials, and includes gamification elements to motivate students.

## Features

- Reading level analysis using Gemini 1.5 Pro
- Personalized feedback generation
- Student progress tracking with a database
- Adaptive reading material generation
- Gamification with points and achievements
- Interactive chat with an AI reading tutor
- Text-to-speech functionality for feedback
- Real-time progress visualization

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/giranntu/ReamSmart.git
   cd ReamSmart
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your Google Cloud Project and enable the following APIs:
   - Vertex AI API
   - Text-to-Speech API

5. Create a `.env` file in the project root and add your Google Cloud credentials:
   ```
   GCP_PROJECT_ID=your-project-id
   GCP_LOCATION=us-central1
   GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
   ```

## Running the Application

1. Start the FastAPI server:
   ```
   uvicorn main:app --reload
   ```

2. Open a web browser and navigate to `http://localhost:8000`.

3. Use the interactive web interface to submit reading samples, receive feedback, and engage with the AI tutor.

## Using the Application

1. Enter your student ID and grade level.
2. Paste or type a reading sample into the text area.
3. Click "Submit" to receive an analysis of your reading.
4. View your reading level, areas for improvement, and strengths.
5. Read the personalized feedback and listen to it using text-to-speech.
6. Check out the next recommended reading material.
7. Track your progress using the interactive chart.
8. Chat with the AI reading tutor for additional help or questions.

## API Endpoints

- `POST /analyze_reading`: Submit a reading sample for analysis
- `POST /text_to_speech`: Convert text to speech
- `WebSocket /ws/chat`: Real-time chat with AI tutor

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Acknowledgements

- This project uses the Gemini 1.5 Pro model from Google's Vertex AI.
- The frontend is built using HTML, JavaScript, and Tailwind CSS.
- Charts are created using Chart.js.

Happy reading and learning!
