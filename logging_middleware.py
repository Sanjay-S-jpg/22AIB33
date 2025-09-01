import requests
import os

def log(level, package, message):
    log_url = 'http://20.244.56.144/evaluation-service/logs'
    bearer_token = os.environ.get('ACCESS_TOKEN', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJzYW5qYXlfMjJhaWIzM0BrZ2tpdGUuYWMuaW4iLCJleHAiOjE3NTY3MDUwMDcsImlhdCI6MTc1NjcwNDEwNywiaXNzIjoiQWZmb3JkIE1lZGljYWwgVGVjaG5vbG9naWVzIFByaXZhdGUgTGltaXRlZCIsImp0aSI6IjEwMThjODdlLTI0MjQtNDdkYi1iYjliLWYwNGYxN2JmNzQ3NSIsImxvY2FsZSI6ImVuLUlOIiwibmFtZSI6InNhbmpheSBzIiwic3ViIjoiOGRhMzM0NGMtMTA0OS00YWNiLTk2MDYtZGVkYzY3YTZmZGU4In0sImVtYWlsIjoic2FuamF5XzIyYWliMzNAa2draXRlLmFjLmluIiwibmFtZSI6InNhbmpheSBzIiwicm9sbE5vIjoiMjJhaWIzMyIsImFjY2Vzc0NvZGUiOiJkcVh1d1oiLCJjbGllbnRJRCI6IjhkYTMzNDRjLTEwNDktNGFjYi05NjA2LWRlZGM2N2E2ZmRlOCIsImNsaWVudFNlY3JldCI6Ik52eHRZQ1VmWEVURHNwZ0QifQ.IUXwLLsDIl6E2VFDp3k9_5KGQMMS_wg-6BmryqBBRtc')

    if not bearer_token:
        print('Logging Error: Access token not set.')
        return

    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        'stack': 'backend',
        'level': level.lower(),
        'package': package.lower(),
        'message': message
    }

    try:
        response = requests.post(log_url, headers=headers, json=payload, timeout=5)
        response.raise_for_status()
        print(f"Log sent successfully: {message}")
    except requests.exceptions.RequestException as request_error:
        print(f"Failed to send log: {request_error}")
        if hasattr(request_error, 'response') and request_error.response is not None:
            print(f"Response Body: {request_error.response.text}")
    except Exception as general_error:
        print(f"An unexpected error occurred while sending the log: {general_error}")
