import os
import sys
from flask import Flask, render_template, request, jsonify, send_from_directory
try:
    from jinja2 import TemplateNotFound
except ImportError:
    TemplateNotFound = None
# Prefer the newer `google.genai` client if available, otherwise fall back
try:
    import google.genai as genai
    genai_client_label = 'google.genai'
except Exception:
    try:
        import google.generativeai as genai
        genai_client_label = 'google.generativeai (deprecated)'
    except Exception:
        genai = None
        genai_client_label = None
try:
    # Load local .env file if present (keeps secrets out of repo)
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
# Optionally load a local, untracked Python file `secret_config.py` that defines
# `GOOGLE_API_KEY` or `GEMINI_API_KEY` variables. This file should be listed in
# .gitignore and never committed. See `secret_config.example.py` for the format.
try:
    import secret_config
    # If env var not already set, copy from secret_config
    if not os.getenv('GOOGLE_API_KEY') and hasattr(secret_config, 'GOOGLE_API_KEY'):
        os.environ['GOOGLE_API_KEY'] = secret_config.GOOGLE_API_KEY
    if not os.getenv('GEMINI_API_KEY') and hasattr(secret_config, 'GEMINI_API_KEY'):
        os.environ['GEMINI_API_KEY'] = secret_config.GEMINI_API_KEY
except Exception:
    pass
try:
    from google.oauth2 import service_account
except ImportError:
    service_account = None
import json


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)


app = Flask(__name__, template_folder=resource_path('templates'))

# Configure the real AI Engine
# Use GOOGLE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS from the environment
DEFAULT_GOOGLE_MODEL = os.getenv('GOOGLE_MODEL', 'models/gemini-flash-latest')
model = None
if genai is not None:
    api_key = os.getenv('GEMINI_API_KEY')
    credentials = None
    if api_key:
        genai.configure(api_key=api_key)
        auth_source = 'Gemini API key'
    else:
        sa_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if sa_path:
            if service_account is None:
                print('WARNING: google.oauth2.service_account is not available; cannot load service account credentials.')
            elif not os.path.exists(sa_path):
                print(f'WARNING: Service account credentials file not found: {sa_path}')
            else:
                try:
                    credentials = service_account.Credentials.from_service_account_file(sa_path)
                    genai.configure(credentials=credentials)
                    auth_source = 'Google service account'
                except Exception as e:
                    print(f'WARNING: Could not load service account credentials from {sa_path}: {e}')
        else:
            auth_source = None
    if api_key or credentials:
        try:
            model = genai.GenerativeModel(DEFAULT_GOOGLE_MODEL)
            print(f'Google AI model configured using {auth_source}.')
        except Exception as e:
            print(f"WARNING: Could not load model {DEFAULT_GOOGLE_MODEL}: {e}")
            try:
                model = genai.GenerativeModel('models/gemini-2.5-flash')
                print('Loaded fallback model models/gemini-2.5-flash')
            except Exception as e2:
                print(f"WARNING: Could not load fallback model models/gemini-2.5-flash: {e2}")
                model = None
    else:
        print('WARNING: No Google AI auth configured. Set GOOGLE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS.')
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

    def mock_audit(evidence_text, control_text):
        """Produce a conservative deterministic mock audit result when no AI model is available."""
        lower = (evidence_text or '').lower()
        # simple heuristics: look for words that indicate removal/deactivation
        positive_keywords = ['delete', 'deleted', 'remov', 'removed', 'deactivate', 'deactivated', 'terminated', 'revoke']
        for kw in positive_keywords:
            if kw in lower:
                return {"status": "Compliant", "reason": "Evidence shows removal/deactivation which satisfies the control."}
        # if evidence is very short or obviously unrelated, mark non-compliant
        if not evidence_text or len(evidence_text.strip()) < 20:
            return {"status": "Non-Compliant", "reason": "Insufficient evidence provided to show the control is satisfied."}
        # default heuristic: non-compliant but with neutral reason
        return {"status": "Non-Compliant", "reason": "Evidence does not clearly demonstrate the required control is implemented."}

    if model is None:
        # Use the mock fallback so the endpoint remains usable without live API keys
        return jsonify(mock_audit(evidence, control))

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