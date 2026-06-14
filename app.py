import os
import sys
from flask import Flask, render_template, request, jsonify, send_from_directory
from jinja2 import TemplateNotFound
try:
    import google.generativeai as genai
except ImportError:
    genai = None
import json


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)


app = Flask(__name__, template_folder=resource_path('templates'))

# Configure the real AI Engine
# Use GOOGLE_API_KEY from the environment if present, otherwise fall back to the provided API key.
DEFAULT_GOOGLE_API_KEY = 'AQ.Ab8RN6K_MSZalIpWCzI_Zy0zxkTRiUKlDtoOpf8GIb_Ct9EHGg'
DEFAULT_GOOGLE_MODEL = os.getenv('GOOGLE_MODEL', 'models/gemini-flash-latest')
if genai is not None:
    api_key = os.getenv('GOOGLE_API_KEY', DEFAULT_GOOGLE_API_KEY)
    if api_key:
        genai.configure(api_key=api_key)
        try:
            model = genai.GenerativeModel(DEFAULT_GOOGLE_MODEL)
        except Exception as e:
            print(f"WARNING: Could not load model {DEFAULT_GOOGLE_MODEL}: {e}")
            try:
                model = genai.GenerativeModel('models/gemini-2.5-flash')
                print('Loaded fallback model models/gemini-2.5-flash')
            except Exception as e2:
                print(f"WARNING: Could not load fallback model models/gemini-2.5-flash: {e2}")
                model = None
    else:
        print('WARNING: No Google AI API key is configured. /api/audit will return an error.')
        model = None
else:
    model = None

@app.route('/')
def home():
    # Serves the frontend dashboard
    try:
        return render_template('index.html')
    except TemplateNotFound:
        # Fallback when the template is missing (useful for lightweight runs)
        index_path = resource_path('index.html')
        if os.path.exists(index_path):
            return send_from_directory(os.path.dirname(index_path), 'index.html')
        return "<h1>BM FUTUROMIND AI Demo Server</h1><p>Frontend not installed. Visit /api/audit to use the API.</p>"

@app.route('/api/audit', methods=['POST'])
def run_audit():
    data = request.json
    evidence = data.get('evidence', '')
    control = data.get('control', 'A.9.2.1: User de-registration process must be implemented.')

    if model is None:
        return jsonify({"status": "Error", "reason": "AI model not configured. Install google.generativeai and set API key."}), 503

    # The Prompt Engineering
    prompt = f"""
    You are an expert ISO 27001 Compliance Auditor.
    Evaluate the provided evidence against the control.
    
    RULES:
    1. If the evidence satisfies the control, mark "Compliant". Otherwise, "Non-Compliant".
    2. Provide a concise, one-sentence reason.

    INPUT:
    Control: {control}
    Evidence: {evidence}

    OUTPUT FORMAT (Strict JSON):
    {{
      "status": "Compliant" | "Non-Compliant",
      "reason": "String explaining the decision"
    }}
    """

    try:
        response = model.generate_content(prompt)
        # Clean the response to ensure it is pure JSON
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        ai_decision = json.loads(clean_json)
        return jsonify(ai_decision)
    except Exception as e:
        return jsonify({"status": "Error", "reason": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('1', 'true', 'yes')
    print(f"Starting BM FUTUROMIND AI Demo Server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=debug)