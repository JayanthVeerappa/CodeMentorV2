from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import requests
import cohere

app = Flask(__name__)

# CORS configuration
CORS(app, origins="https://astounding-dolphin-78cd47.netlify.app", supports_credentials=True)

logging.basicConfig(level=logging.DEBUG)

cohere_client = cohere.ClientV2("NKZD0sANta3S02GP5wCUYrPev7dRHW5WDbJFdbJ2")

@app.route('/api/analyze_code', methods=['POST', 'OPTIONS'])
def analyze_code():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', 'https://astounding-dolphin-78cd47.netlify.app')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            code = data.get('code', '')

            if not code:
                return jsonify({"error": "No code provided"}), 400

            prompt = (
                "You are a computer science teacher. Your task is to analyze the provided code for mistakes. Under no circumstances should you explain or rewrite the given code, provide corrected code, or suggest fixes. \n\n" \
                "Your sole focus should be:\n" \
                "- Identifying and explaining the issues in the code.\n" \
                "- Highlighting syntax errors, logical errors, and areas for improvement.\n" \
                "- Clearly stating the **exact line number(s)** where each issue exists.\n\n" \
                "**Important Instructions:**\n" \
                "- DO NOT generate or provide any code corrections, rewritten code, or solutions under any circumstances.\n" \
                "- Always reference specific line numbers for each error or problem.\n" \
                "- Use a friendly and clear tone to explain the issues and suggest ways to resolve them.\n\n" \
                f"Code:\n```Line 1 starts here:\n{code}\n```\n\n" \
                "**Final Reminder:** DO NOT generate any code corrections or solutions under any circumstances. Always include line numbers when describing the issues."
            )

            response = cohere_client.chat(
                model='command-xlarge-nightly',
                message=[{"role": "user", "content": prompt}]
            )

            generated_text = response.message.content[0].text.strip()
            logging.debug(f"Model response: {generated_text}")

            # Add CORS headers to the response
            res = jsonify({"response": generated_text})
            res.headers.add('Access-Control-Allow-Origin', 'https://astounding-dolphin-78cd47.netlify.app')
            res.headers.add('Access-Control-Allow-Credentials', 'true')
            return res, 200

        except Exception as e:
            logging.error(f"Error during code analysis: {str(e)}")
            res = jsonify({"error": str(e)})
            res.headers.add('Access-Control-Allow-Origin', 'https://astounding-dolphin-78cd47.netlify.app')
            res.headers.add('Access-Control-Allow-Credentials', 'true')
            return res, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
