import os
import requests
from dotenv import load_dotenv
import prompts
import re
def split_sections(text):
    # Rendu blank lines (paragraphs) daggara text ni cut chestundi
    sections = re.split(r'\n\s*\n', text)
    # Empty ga unna sections ni theesestundi
    sections = [sec.strip() for sec in sections if sec.strip()]
    print(f"Document ni {len(sections)} sections ga split chesam.")
    return sections
def call_gemini(prompt_text, api_key):
    import time
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt_text}]}]}
    
    for attempt in range(3): # 3 times try chestundi
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            elif response.status_code == 503:
                print("\nGoogle server busy (503), 3 seconds aagi malli try chestundi...")
                time.sleep(3)
                continue
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Network Error: {e}"
            
    return "Error: Google server inka busy gane undi, kasepu aagi run chey."

def summarize_document(sections, api_key):
    print(f"\nTotal {len(sections)} sections ni summarize chestunna...")
    section_summaries = []
    
    # Prathi section ni okkokkatiga pampadam
    for i, sec in enumerate(sections):
        print(f"Section {i+1} processing...")
        prompt = prompts.summarize_prompt(sec)
        result = call_gemini(prompt, api_key)
        section_summaries.append(result)
        
    # Anni summaries ni okkela kalapadam
    combined_text = "\n\n".join(section_summaries)
    
    print("Anni sections kalipi final summary create chestunna...")
    final_prompt = prompts.summarize_prompt(combined_text)
    return call_gemini(final_prompt, api_key)
def get_key_points(text, api_key):
    print("\nKey points extract chestunna...")
    prompt = prompts.key_points_prompt(text)
    return call_gemini(prompt, api_key)

def generate_quiz(text, api_key):
    print("\nQuiz questions generate chestunna...")
    prompt = prompts.generate_questions_prompt(text)
    return call_gemini(prompt, api_key)
class Conversation:
    def __init__(self, context_summary):
        self.context = context_summary

    def ask_question(self, question, api_key):
        print("\nThinking...")
        prompt = f"System: {prompts.SYSTEM_PROMPT}\n\nHere is the document summary for context:\n{self.context}\n\nUser Question: {question}\n\nPlease answer the user's question based ONLY on the summary provided."
        return call_gemini(prompt, api_key)

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "").strip()

if not api_key:
    print("Error: API key missing.")
    exit()

print("---------------------------------------")

print("\nWelcome to DocuMind Week 2!")
print("-----------------------------------")

while True:
    file_path = input("\nEnter .txt file path (or 'quit' to exit): ")
    if file_path.lower() == 'quit':
        print("Bye!")
        break
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        if not text.strip():
            print("Error: File empty ga undi!")
            continue
            
        # 1. Split text and get summary
        sections = split_sections(text)
        final_summary = summarize_document(sections, api_key)
        print("\n--- FINAL SUMMARY ---\n" + final_summary)
        
        # 2. Setup Conversation with the summary
        conv = Conversation(final_summary)
        
        # 3. Inner loop for new commands
        while True:
            cmd = input("\nEnter command (key_points, quiz_me, ask, next, quit): ").strip().lower()
            
            if cmd == 'quit':
                print("Bye!")
                exit()
            elif cmd == 'next':
                break  # Goes back to ask for a new file
            elif cmd == 'key_points':
                print("\n" + get_key_points(text, api_key))
            elif cmd == 'quiz_me':
                print("\n" + generate_quiz(text, api_key))
            elif cmd == 'ask':
                question = input("\nEnter your question: ")
                print("\n" + conv.ask_question(question, api_key))
            else:
                print("Invalid command. Please try again.")
                
    except FileNotFoundError:
        print("Error: File not found. Path check chey.")
    except Exception as e:
        print(f"Error: {e}")
