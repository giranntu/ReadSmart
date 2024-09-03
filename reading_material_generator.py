from vertexai.preview.generative_models import GenerativeModel

def generate_reading_material(model: GenerativeModel, reading_level: str, areas_for_improvement: list):
    prompt = f"""
    Generate a short, engaging reading passage suitable for a student at the following reading level:
    {reading_level}

    The passage should focus on improving these specific areas:
    {', '.join(areas_for_improvement)}

    The passage should be approximately 150-200 words long and include:
    1. Age-appropriate vocabulary
    2. Clear sentence structures
    3. Interesting content that encourages further reading
    4. Elements that address the specific areas for improvement

    Please provide only the generated passage without any additional explanations.
    """
    
    response = model.generate_content(prompt)
    
    return response.text