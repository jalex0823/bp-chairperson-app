import sys
import time
import requests

BASE = "http://127.0.0.1:5000"

# Public endpoints to test
ENDPOINTS = [
    "/",
    "/calendar",
    "/calendar/display",
    "/calendar.ics",
    "/meetings/today",
    "/chair-resources",
    "/register",
    "/login",
    # Static assets
    "/static/img/favicon.ico",
    "/static/img/favicon-16x16.png",
    "/static/img/favicon-32x32.png",
    "/static/img/apple-touch-icon.png",
    "/static/img/backporch-logo.png",
]

TIMEOUT = 10

def check(path):
    url = BASE + path
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        status = resp.status_code
        final_url = resp.url
        print(f"{status}\t{path}\t-> {final_url}")
        return status, path, final_url
    except requests.RequestException as e:
        print(f"ERR\t{path}\t{e}")
        return None, path, str(e)

if __name__ == "__main__":
    # Allow server time to start (optional delay if needed)
    time.sleep(0.5)
    failures = []
    for ep in ENDPOINTS:
        status, path, info = check(ep)
        if status is None or status >= 400:
            failures.append((path, info))
    print("\nSummary:")
    if failures:
        for path, info in failures:
            print(f"FAIL\t{path}\t{info}")
        sys.exit(1)
    else:
        print("All endpoints returned < 400 status.")
        sys.exit(0)
