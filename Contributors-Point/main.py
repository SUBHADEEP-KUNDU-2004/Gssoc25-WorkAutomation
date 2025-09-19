import streamlit as st
import requests
import csv
import io
import re
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="GitHub Contributor Points", page_icon="📊", layout="wide")

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    st.error("❌ GitHub token not found! Please add it to Streamlit secrets.")
    st.stop()

st.title("📊 GitHub Contributors Points Calculator")

# --- Inputs ---
owner = st.text_input("🔑 GitHub Owner (username or org)")
repo = st.text_input("📂 Repository name")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=None)
with col2:
    end_date = st.date_input("End Date", value=None)

if st.checkbox("Set End Date to Today", value=True):
    end_date = datetime.today().date()

start_dt = datetime.combine(start_date, datetime.min.time()) if start_date else None
end_dt = datetime.combine(end_date, datetime.max.time()) if end_date else None

# --- Points Config ---
st.markdown("### 🎯 Points per Level")
POINTS_MAP = {
    "level 1": st.number_input("Points for Level 1", value=4, min_value=0),
    "level 2": st.number_input("Points for Level 2", value=7, min_value=0),
    "level 3": st.number_input("Points for Level 3", value=10, min_value=0),
}

st.markdown("## 📥 Upload Contributor Info CSV")
uploaded_file = st.file_uploader("Upload CSV: (full_name,email,github_url)", type=["csv"])

github_info_map = {}
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip().lower() for col in df.columns]

        if "github_url" not in df.columns:
            st.error("❌ CSV missing required column: github_url")
        else:
            def extract_username(url: str) -> str | None:
                if isinstance(url, str):
                    url = url.strip().rstrip("/")
                    match = re.search(r"github\.com/([^/]+)$", url)
                    return match.group(1).lower() if match else None
                return None

            df["github_username"] = df["github_url"].apply(extract_username)

            missing_url_count = df["github_username"].isna().sum()
            github_info_map = {
                row["github_username"]: {
                    "email": row.get("email", ""),
                    "full_name": row.get("full_name", "")
                }
                for _, row in df.dropna(subset=["github_username"]).iterrows()
            }

            st.success(f"✅ Loaded contributor info for {len(github_info_map)} users.")
            if missing_url_count:
                st.warning(f"⚠️ {missing_url_count} rows skipped due to invalid GitHub URL.")

    except Exception as e:
        st.error(f"❌ Failed to read CSV: {e}")


# --- Helpers ---
def get_headers() -> dict:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {GITHUB_TOKEN}"
    }

def fetch_merged_prs(owner: str, repo: str, start: datetime = None, end: datetime = None) -> list:
    """Fetch merged PRs with pagination"""
    prs, page = [], 1
    headers = get_headers()

    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = {"state": "closed", "per_page": 100, "page": page}
        resp = requests.get(url, headers=headers, params=params)

        if resp.status_code != 200:
            st.error(f"❌ Error fetching PRs: {resp.json().get('message', '')}")
            return []

        data = resp.json()
        if not data:
            break

        stop = False
        for pr in data:
            merged_at_str = pr.get("merged_at")
            if not merged_at_str:
                continue
            merged_at = datetime.strptime(merged_at_str, "%Y-%m-%dT%H:%M:%SZ")

            if end and merged_at > end:
                continue
            if start and merged_at < start:
                stop = True
                break

            prs.append(pr)

        if stop:
            break
        page += 1
    return prs

def calculate_points(prs: list, points_map: dict) -> dict:
    """Assign points based on PR labels"""
    points = {}
    for pr in prs:
        author = pr["user"]["login"].strip().lower()
        labels = [label["name"].lower() for label in pr.get("labels", [])]

        pr_points = max((points_map.get(lbl, 0) for lbl in labels), default=0)
        if pr_points > 0:
            points[author] = points.get(author, 0) + pr_points
    return points

def create_csv(points_dict: dict) -> str:
    """Generate CSV string"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["CONTRIBUTOR NAME", "CONTRIBUTOR EMAIL ID", "CONTRIBUTOR GITHUB LINK", "TOTAL POINTS"])
    
    for user, pts in sorted(points_dict.items(), key=lambda x: x[1], reverse=True):
        info = github_info_map.get(user, {})
        full_name = info.get("full_name") or user
        email = info.get("email", "")
        github_link = f"https://github.com/{user}"
        writer.writerow([full_name, email, github_link, pts])
    return output.getvalue()


# --- Main Action ---
if st.button("🚀 Fetch and Generate CSV"):
    if not owner or not repo:
        st.error("❌ Please enter Owner and Repo.")
    elif not github_info_map:
        st.error("❌ Please upload contributor info CSV first.")
    else:
        with st.spinner("🔄 Fetching merged PRs..."):
            prs = fetch_merged_prs(owner, repo, start=start_dt, end=end_dt)

        if prs:
            with st.spinner("⚡ Calculating points..."):
                points = calculate_points(prs, POINTS_MAP)

            contributors_in_prs = {pr["user"]["login"].strip().lower() for pr in prs}
            missing = contributors_in_prs - set(github_info_map.keys())
            if missing:
                st.warning(f"⚠️ Missing contributors in your CSV: {', '.join(sorted(missing))}")

            if points:
                csv_data = create_csv(points)
                st.success("✅ CSV generated successfully!")
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_data,
                    file_name=f"{owner}_{repo}_contributor_points.csv",
                    mime="text/csv"
                )
            else:
                st.info("ℹ️ No contributors found with matching level labels.")
        else:
            st.info("ℹ️ No merged PRs found in the given range.")

# --- Footer ---
st.markdown("---")
st.markdown("🔗 Built by [Ujjwal Saini](https://github.com/ujjwalsaini07)", unsafe_allow_html=True)
