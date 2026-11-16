SkillMe Document Summarizer
A simple Python command-line tool that reads a .txt file and generates a 3-bullet-point summary using the Google Gemini API.
It automatically scans the Gemini models available on your API key and uses the first one that works, so you don't have to worry about model names or quota errors on a specific model.
Features
Summarizes any plain-text (.txt) file in 3 bullet points
Auto-detects available Gemini models (generateContent supported)
Falls back to the next model if one fails
Loads the API key securely from a .env file
Interactive loop: summarize multiple files, type quit to exit
Handles missing files, empty files, and network/API errors
Requirements
Python 3.8 or higher
A Gemini API key (free from Google AI Studio)
Python packages:
requests
python-dotenv
Project Structure
skillme-summarizer/
├── app.py            # main script (your Python file)
├── .env              # your API key (do NOT commit this)
├── requirements.txt  # dependencies
└── README.md
How to Run
1. Clone or download the project
git clone <your-repo-url>
cd skillme-summarizer
2. (Optional) Create a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
3. Install the dependencies
pip install requests python-dotenv
Or, if you have a requirements.txt:
pip install -r requirements.txt
requirements.txt:
requests
python-dotenv
4. Add your API key
Create a file named .env in the project folder:
GEMINI_API_KEY=your_api_key_here
No quotes and no spaces around =.
5. Run the script
python app.py
6. Use it
Welcome to SkillMe Document Summarizer!
---------------------------------------

Enter .txt file path or type 'quit' to exit: notes.txt

[Success! Connected to working model: models/gemini-...]

--- Summary ---
* Point 1
* Point 2
* Point 3
Type quit to exit.
How It Works
Loads GEMINI_API_KEY from .env.
Asks for the path of a .txt file and reads it.
Fetches the list of models from the Gemini API.
Loops through every Gemini model that supports generateContent and sends the text with the prompt "Summarise this in 3 bullet points".
Prints the summary from the first model that responds successfully.
Troubleshooting
Problem
Fix
Error: API key missing.
Check that .env exists in the same folder and contains GEMINI_API_KEY=...
API Key error or Network issue.
Verify the key is valid and you have internet access
File not found.
Use the correct path (or full path) to your .txt file
Error: File empty
The file has no text, so add some content
No working models found
Your key may have hit its quota, or the models are not enabled. Try again later or create a new key
Security Notes
Never share or commit your API key.
Add .env to your .gitignore:
.env
venv/
__pycache__/
Limitations
Only supports plain .txt files (UTF-8 encoding).
Very large files may exceed the model's input limit.
Trying every model can be slow if the first few fail.
License
This project is for learning purposes. Feel free to use and modify it.
