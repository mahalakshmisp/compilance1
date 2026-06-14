import os
import json

print('Validating service account configuration...')
sa = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if not sa:
    print('GOOGLE_APPLICATION_CREDENTIALS is not set.')
    exit(2)
if not os.path.exists(sa):
    print(f'Service account file not found: {sa}')
    exit(3)

try:
    from google.oauth2 import service_account
    creds = service_account.Credentials.from_service_account_file(sa)
    print('Loaded service account JSON successfully.')
    # Print minimal info (project_id if present) but avoid printing keys
    try:
        with open(sa, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print('service_account_project_id:', data.get('project_id'))
    except Exception:
        pass
except Exception as e:
    print('Failed to load service account credentials:', e)
    exit(4)

# Optionally check for installed client library
try:
    import google.genai as genai
    print('google.genai available: you can migrate to the new client if desired.')
except Exception:
    try:
        import google.generativeai as genai
        print('google.generativeai available (deprecated).')
    except Exception:
        print('No Google Generative AI client installed.')

print('Validation complete.')
