import streamlit as st
import requests
import re

st.set_page_config(page_title="GitHub Tags Generator", page_icon="🏷️", layout="wide")

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    st.error("❌ GitHub token not found! Please add it to Streamlit secrets.")
    st.stop()

st.title("🏷️ GitHub Auto Tags Generator")

owner = st.text_input("🔑 GitHub Owner (username/org)")
repo = st.text_input("📂 Repository name")

def get_headers():
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {GITHUB_TOKEN}"
    }

def fetch_repo_data(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    resp = requests.get(url, headers=get_headers())
    if resp.status_code == 200:
        return resp.json()
    else:
        st.error(f"❌ Failed to fetch repo info: {resp.json().get('message','')}")
        return None

def fetch_issues_prs(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params = {"state": "all", "per_page": 100}
    resp = requests.get(url, headers=get_headers(), params=params)
    if resp.status_code == 200:
        return resp.json()
    return []

def generate_tags(repo_data, issues):
    text_data = (repo_data.get("description","") or "") + " "
    text_data += " ".join([i.get("title","") for i in issues])
    text_data = text_data.lower()

    # Extract potential keywords
    words = re.findall(r"[a-zA-Z0-9#\+\-]{3,}", text_data)
    ignore = {"the","and","for","with","this","that","from","your","into","have","are"}
    keywords = [w for w in words if w not in ignore]

    # Frequency count
    freq = {}
    for w in keywords:
        freq[w] = freq.get(w, 0) + 1

    # Top tags
    tags = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
    return [t[0] for t in tags]

if st.button("🚀 Generate Tags"):
    if not owner or not repo:
        st.error("❌ Please enter Owner and Repo.")
    else:
        with st.spinner("🔄 Analyzing repository..."):
            repo_data = fetch_repo_data(owner, repo)
            issues = fetch_issues_prs(owner, repo)
            if repo_data:
                tags = generate_tags(repo_data, issues)
                st.success("✅ Tags generated successfully!")
                st.write("### Suggested Tags:")
                st.write(", ".join(tags))
