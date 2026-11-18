SYSTEM_PROMPT = "You are DocuMind, an AI assistant helping a student understand documents."

def summarize_prompt(text):
    return f"Summarize the following text clearly and concisely:\n\n{text}"

def key_points_prompt(text):
    return f"Extract 5-8 key bullet points from the following document:\n\n{text}"

def generate_questions_prompt(text):
    return f"Generate 3-5 quiz questions with short answers based on this text. Format as Q: ... A: ...\n\n{text}"
