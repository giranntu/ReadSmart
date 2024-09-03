from vertexai.preview.generative_models import GenerativeModel

def analyze_reading_level(model: GenerativeModel, student_text: str, grade_level: int):
    prompt = f"""
    As an expert reading tutor, analyze the following text read by a grade {grade_level} student:
    
    {student_text}
    
    Provide a detailed analysis including:
    1. Reading level assessment (below, at, or above grade level)
    2. Identified areas for improvement (e.g., vocabulary, comprehension, fluency)
    3. Specific suggestions for improvement
    4. Positive reinforcement for areas of strength
    
    Format the response as a Python dictionary with keys: 
    'reading_level', 'areas_for_improvement', 'suggestions', 'strengths'
    """
    
    response = model.generate_content(prompt)
    
    # Convert the response to a Python dictionary
    analysis = eval(response.text)
    
    return analysis

def generate_personalized_feedback(model: GenerativeModel, analysis: dict, grade_level: int):
    prompt = f"""
    Based on the following analysis of a grade {grade_level} student's reading:
    
    {analysis}
    
    Generate a personalized, encouraging feedback message for the student. 
    The message should:
    1. Acknowledge their strengths
    2. Provide constructive feedback on areas for improvement
    3. Offer specific, actionable suggestions for enhancing their reading skills
    4. End with an motivational statement

    Keep the tone positive and supportive throughout the message.
    """
    
    response = model.generate_content(prompt)
    
    return response.text