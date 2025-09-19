import streamlit as st
import requests

st.set_page_config(page_title="GitHub Auto Thank Contributors", page_icon="🙏", layout="wide")

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    st.error("❌ GitHub token not found! Please add it to Streamlit secrets.")
    st.stop()

st.title("🙏 Auto Thank Contributors")

owner = st.text_input("🔑 GitHub Owner (username/org)")
repo = st.text_input("📂 Repository name")

thank_message = st.text_area(
    "✍️ Thank You Message",
    "🙏 Thank you for your valuable contribution! The repo owner/mentors will review your issue/PR soon."
)

def get_headers():
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {GITHUB_TOKEN}"
    }

def fetch_open_contributions(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params = {"state": "open", "per_page": 50}
    resp = requests.get(url, headers=get_headers(), params=params)
    if resp.status_code == 200:
        return resp.json()
    return []

def post_comment(owner, repo, issue_number, message):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    resp = requests.post(url, headers=get_headers(), json={"body": message})
    return resp.status_code == 201

if st.button("🚀 Auto-Thank Contributors"):
    if not owner or not repo:
        st.error("❌ Please enter Owner and Repo.")
    else:
        with st.spinner("🔄 Fetching open issues & PRs..."):
            contributions = fetch_open_contributions(owner, repo)

        if contributions:
            count = 0
            for c in contributions:
                issue_number = c["number"]
                user = c["user"]["login"]

                msg = f"Hi @{user},\n\n{thank_message}"
                if post_comment(owner, repo, issue_number, msg):
                    count += 1

            st.success(f"✅ Thanked {count} contributors automatically!")
        else:
            st.info("ℹ️ No open issues/PRs found.")
