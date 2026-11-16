import os
import requests
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "").strip()

if not api_key:
    print("Error: API key missing.")
    exit()

print("Welcome to SkillMe Document Summarizer!")
print("---------------------------------------")

while True:
    file_path = input("\nEnter .txt file path or type 'quit' to exit: ")
    if file_path.lower() == 'quit':
        print("Bye!")
        break
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        if not text.strip():
            print("Error: File empty ga undi!")
            continue
            
        print("\nBypassing Google errors & scanning ALL models... Please wait.")
        
        # Step 1: Get all models
        models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        models_response = requests.get(models_url)
        
        if models_response.status_code != 200:
            print("API Key error or Network issue.")
            continue
            
        data = {"contents": [{"parts": [{"text": f"Summarise this in 3 bullet points:\n\n{text}"}]}]}
        headers = {'Content-Type': 'application/json'}
        success = False
        
        # Step 2: Loop through every model until one works!
        for m in models_response.json().get('models', []):
            model_name = m.get('name', '')
            if 'generateContent' in m.get('supportedGenerationMethods', []) and 'gemini' in model_name.lower():
                url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
                
                # Make the API Call
                res = requests.post(url, headers=headers, json=data)
                
                if res.status_code == 200:
                    print(f"\n[Success! Connected to working model: {model_name}]")
                    summary = res.json()['candidates'][0]['content']['parts'][0]['text']
                    print("\n--- Summary ---")
                    print(summary)
                    success = True
                    break # Stop looping once we get the result!
        
        if not success:
            print("\nError: No working models found in your Google account.")
            
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"Error: {e}")
