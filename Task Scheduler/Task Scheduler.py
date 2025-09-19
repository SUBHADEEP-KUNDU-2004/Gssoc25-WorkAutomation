import requests
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = "UjjwalSaini07"
REPO = "Bharat-Bhakti-Yatra"

def get_headers():
    return {"Authorization": f"token {GITHUB_TOKEN}"}

def fetch_open(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    resp = requests.get(url, headers=get_headers(), params={"state": "open"})
    return resp.json() if resp.status_code == 200 else []

def post_comment(owner, repo, issue_number, message):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    resp = requests.post(url, headers=get_headers(), json={"body": message})
    return resp.status_code == 201

def run():
    contributions = fetch_open(OWNER, REPO)
    for c in contributions:
        num = c["number"]
        user = c["user"]["login"]
        message = f"Hi @{user} 👋\n\n🙏 Thanks for contributing! A mentor will review this soon."
        if post_comment(OWNER, REPO, num, message):
            print(f"✅ Commented on #{num}")

if __name__ == "__main__":
    run()
