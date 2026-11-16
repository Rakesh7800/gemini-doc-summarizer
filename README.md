# SkillMe Document Summarizer

A simple Python command-line tool that reads a `.txt` file and generates a 3-bullet-point summary using the Google Gemini API. It automatically scans the Gemini models available on your API key and uses the first one that works, avoiding quota or model deprecation errors.

## Features
* Summarizes any plain-text (`.txt`) file in 3 bullet points.
* Auto-detects available Gemini models.
* Loads the API key securely from a `.env` file.
* Interactive loop: summarize multiple files, type `quit` to exit.
* Handles missing files, empty files, and network/API errors.

## Requirements
* Python 3.8 or higher
* A Gemini API key (free from Google AI Studio)
* Python packages: `requests`, `python-dotenv`

## Project Structure
```text
skillme-summarizer/
├── app.py           # main script
├── .env             # your API key (DO NOT commit this)
├── requirements.txt # dependencies
└── README.md
