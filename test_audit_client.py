import json
import threading
from app import app


def run_tests():
    client = app.test_client()

    samples = [
        {
            'evidence': 'The user account was deleted from the system on 2026-06-01 and all access tokens revoked.',
            'control': 'A.9.2.1: User de-registration process must be implemented.'
        },
        {
            'evidence': 'User requested account closure but no deletion recorded.',
            'control': 'A.9.2.1: User de-registration process must be implemented.'
        },
        {
            'evidence': '',
            'control': 'A.9.2.1: User de-registration process must be implemented.'
        }
    ]

    for i, sample in enumerate(samples, start=1):
        resp = None
        error = None
        
        def make_request():
            nonlocal resp, error
            try:
                resp = client.post('/api/audit', json=sample)
            except Exception as e:
                error = e
        
        thread = threading.Thread(target=make_request, daemon=True)
        thread.start()
        thread.join(timeout=10)
        
        if thread.is_alive():
            print(f"Test #{i} - TIMEOUT (10s) - API call hung; likely auth issue or network timeout")
            continue
        
        if error:
            print(f"Test #{i} - ERROR: {error}")
            continue
        
        print(f"Test #{i} - status_code: {resp.status_code}")
        try:
            print(json.dumps(resp.get_json(), indent=2))
        except Exception:
            print('Non-JSON response:', resp.data.decode())


if __name__ == '__main__':
    run_tests()
