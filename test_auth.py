import os, traceback
try:
    import google.generativeai as genai
except Exception as e:
    print('IMPORT_ERROR', e)
    raise
print('KEY_PRESENT', bool(os.getenv('GEMINI_API_KEY')))
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('models/gemini-flash-latest')
    print('MODEL_CREATED')
    try:
        resp = model.generate_content('Test authentication')
        print('RESPONSE_TEXT', getattr(resp, 'text', '')[:1000])
    except Exception:
        print('GENERATE_EXCEPTION')
        traceback.print_exc()
except Exception:
    print('CONFIG_EXCEPTION')
    traceback.print_exc()
