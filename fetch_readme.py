import requests

url = "https://api.github.com/repos/Samson-Mathai/UniAssist-RAG/events"
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    events = response.json()
    
    for event in events:
        if event["type"] == "PushEvent":
            commits = event.get("payload", {}).get("commits", [])
            for commit in commits:
                msg = commit.get("message", "")
                if "README" in msg or "Create" in msg or "readme" in msg.lower():
                    print(f"FOUND COMMIT: {commit['sha']}")
                    print(f"Message: {msg}")
                    
                    raw_url = f"https://raw.githubusercontent.com/Samson-Mathai/UniAssist-RAG/{commit['sha']}/README.md"
                    raw_resp = requests.get(raw_url)
                    if raw_resp.status_code == 200:
                        print("--- ORIGINAL README CONTENT ---")
                        print(raw_resp.text)
                        print("-------------------------------")
except Exception as e:
    print(f"Error: {e}")
