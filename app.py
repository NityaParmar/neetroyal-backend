from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load environment variables from api.env file
load_dotenv('api.env')

# --- Flask Application Setup ---
app = Flask(__name__)
CORS(app)

# --- Google Gemini API Configuration ---
# Load API key from environment variable (more secure)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your api.env file.")

genai.configure(api_key=GEMINI_API_KEY)

# --- Routes ---
# Temporary route to list available Gemini models for debugging
@app.route('/list_models')
def list_gemini_models():
    try:
        # Get all available models
        models = genai.list_models()

        # Filter for models that support text generation (important for our use case)
        supported_models = [
            m.name for m in models if "generateContent" in m.supported_generation_methods
        ]

        return jsonify({"available_models": supported_models}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to list models: {e}"}), 500

# Home route: A simple endpoint to check if the server is running
@app.route('/')
def home():
    return "Hello from NEETROYAL AI Backend!"

# API endpoint to generate a single question
@app.route('/generate_question', methods=['POST'])
def generate_question():
    # Get the JSON data sent from the Node.js backend
    data = request.get_json()

    # Basic validation: Check if 'topic' and 'difficulty' are provided in the request
    if not data or 'topic' not in data or 'difficulty' not in data:
        # Return an error message if essential data is missing
        return jsonify({"error": "Missing 'topic' or 'difficulty' in request."}), 400

    topic = data['topic']
    difficulty = data['difficulty']

    # Create a generative model instance. 'gemini-pro' is suitable for text generation.
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # --- Crafting the Prompt for the AI ---
    # This is the most crucial part for getting good questions.
    # We instruct the AI to generate a specific type of question and format its output as JSON.
    prompt = f"""
    Generate a multiple-choice question for the NEET/JEE exam.
    Topic: "{topic}"
    Difficulty: "{difficulty}" (e.g., Easy, Medium, Hard)
    The question should have 4 options (A, B, C, D) and specify the single correct answer.
    Ensure the question is highly relevant to the NEET/JEE syllabus and standard.

    Output the question strictly in JSON format with the following keys:
    "question": "The question text here...",
    "options": ["A. Option A text", "B. Option B text", "C. Option C text", "D. Option D text"],
    "answer": "A. Option A text" (or B, C, D with the full option text)
    """

    try:
        # Generate content using the configured Gemini model
        # The `generate_content` method sends the prompt to the AI
        response = model.generate_content(prompt)

        # The AI's response is typically a text string.
        # It might sometimes include markdown code block wrappers (```json ... ```).
        generated_text = response.text.strip()

        # Clean possible markdown code block wrapper from the response
        if generated_text.startswith("```json"):
            generated_text = generated_text[len("```json"):].strip()
        if generated_text.endswith("```"):
            generated_text = generated_text[:-len("```")].strip()

        # Attempt to parse the cleaned text as JSON
        ai_generated_question = json.loads(generated_text)

        # Basic validation of the AI's response structure
        # Ensure the AI returned all the expected keys
        if not all(k in ai_generated_question for k in ["question", "options", "answer"]):
            # If keys are missing, raise an error to be caught by the except block
            raise ValueError("AI response missing required keys (question, options, answer).")

        # Return the AI-generated question as a JSON response
        return jsonify(ai_generated_question), 200 # 200 OK status

    except json.JSONDecodeError as e:
        # Handle cases where the AI's response is not valid JSON
        print(f"JSON parsing error: {e}. AI response was: {generated_text}")
        return jsonify({
            "error": "AI generated invalid JSON. Please try again or refine prompt.",
            "detail": str(e),
            "ai_raw_response": generated_text
        }), 500
    except Exception as e:
        # Catch any other unexpected errors during AI generation or processing
        print(f"Error generating question: {e}")
        return jsonify({
            "error": f"Failed to generate question due to an internal error: {e}",
            "detail": str(e),
            "ai_raw_response": generated_text if 'generated_text' in locals() else "N/A"
        }), 500

# API endpoint to generate a question bank (multiple questions)
@app.route('/generate_question_bank', methods=['POST'])
def generate_question_bank():
    # Get the JSON data sent from the frontend
    data = request.get_json()

    # Basic validation: Check if 'topic', 'difficulty', and 'count' are provided
    if not data or 'topic' not in data or 'difficulty' not in data:
        return jsonify({"error": "Missing 'topic' or 'difficulty' in request."}), 400
    
    # Get the number of questions to generate (default to 10, max 50)
    question_count = data.get('count', 10)
    if question_count > 50:
        question_count = 50
    elif question_count < 1:
        question_count = 1

    topic = data['topic']
    difficulty = data['difficulty']

    # Create a generative model instance
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # --- Crafting the Prompt for Multiple Questions ---
    prompt = f"""
    Generate {question_count} multiple-choice questions for the NEET/JEE exam.
    Topic: "{topic}"
    Difficulty: "{difficulty}" (e.g., Easy, Medium, Hard)
    
    Each question should have 4 options (A, B, C, D) and specify the single correct answer.
    Ensure all questions are highly relevant to the NEET/JEE syllabus and standard.
    Make sure each question is unique and covers different aspects of the topic.

    Output the questions strictly in JSON format as an array of objects with the following structure:
    [
        {{
            "question": "Question 1 text here...",
            "options": ["A. Option A text", "B. Option B text", "C. Option C text", "D. Option D text"],
            "answer": "A. Option A text" (or B, C, D with the full option text)
        }},
        {{
            "question": "Question 2 text here...",
            "options": ["A. Option A text", "B. Option B text", "C. Option C text", "D. Option D text"],
            "answer": "B. Option B text"
        }}
        // ... continue for all {question_count} questions
    ]
    """

    try:
        # Generate content using the configured Gemini model
        response = model.generate_content(prompt)
        generated_text = response.text.strip()

        # Clean possible markdown code block wrapper from the response
        if generated_text.startswith("```json"):
            generated_text = generated_text[len("```json"):].strip()
        if generated_text.endswith("```"):
            generated_text = generated_text[:-len("```")].strip()

        # Attempt to parse the cleaned text as JSON
        question_bank = json.loads(generated_text)

        # Validate that we got a list of questions
        if not isinstance(question_bank, list):
            raise ValueError("AI response is not a list of questions.")

        # Validate each question in the bank
        validated_questions = []
        for i, question in enumerate(question_bank):
            if not all(k in question for k in ["question", "options", "answer"]):
                print(f"Question {i+1} missing required keys, skipping...")
                continue
            validated_questions.append(question)

        if not validated_questions:
            raise ValueError("No valid questions found in AI response.")

        # Return the question bank as a JSON response
        return jsonify({
            "topic": topic,
            "difficulty": difficulty,
            "total_questions": len(validated_questions),
            "questions": validated_questions
        }), 200

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}. AI response was: {generated_text}")
        return jsonify({
            "error": "AI generated invalid JSON. Please try again or refine prompt.",
            "detail": str(e),
            "ai_raw_response": generated_text
        }), 500
    except Exception as e:
        print(f"Error generating question bank: {e}")
        return jsonify({
            "error": f"Failed to generate question bank due to an internal error: {e}",
            "detail": str(e),
            "ai_raw_response": generated_text if 'generated_text' in locals() else "N/A"
        }), 500

# This block ensures the Flask app runs only when the script is executed directly
if __name__ == '__main__':
    # Run the Flask app in debug mode.
    # Debug mode is great for development as it provides detailed error messages
    # and automatically reloads the server when you make code changes.
    # IMPORTANT: Set debug=False for production environments!
    app.run(debug=True)
