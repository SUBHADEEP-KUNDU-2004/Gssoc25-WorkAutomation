import streamlit as st
import requests
import csv
import io
import re
from datetime import datetime
import pandas as pd

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    st.error("GitHub token not found! Please add it to your .env file.")
    st.stop()

st.title("GitHub Contributors Points Calculator")

owner = st.text_input("GitHub Owner (username or org)")
repo = st.text_input("Repository name")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=None)
with col2:
    end_date = st.date_input("End Date", value=None)

till_now = st.checkbox("Set End Date to Today", value=True)
if till_now:
    end_date = datetime.today().date()

start_dt = datetime.combine(start_date, datetime.min.time()) if start_date else None
end_dt = datetime.combine(end_date, datetime.max.time()) if end_date else None

st.markdown("### Points per Level Tag")
level1_points = st.number_input("Points for Level 1", value=4, min_value=0)
level2_points = st.number_input("Points for Level 2", value=7, min_value=0)
level3_points = st.number_input("Points for Level 3", value=10, min_value=0)

POINTS_MAP = {
    "level 1": level1_points,
    "level 2": level2_points,
    "level 3": level3_points,
}

github_info_map = {}

st.markdown("## Upload Contributor Info CSV")

df = None  # initialize

uploaded_file = st.file_uploader("Upload CSV: Contributor Info (full_name,email,github_url)", type=["csv"])
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        df = None

if df is not None:
    def extract_username(url):
        if isinstance(url, str):
            url = url.strip().rstrip('/')
            match = re.search(r"github\.com/([^/]+)$", url)
            if match:
                return match.group(1).lower()
        return None

    df.columns = [col.strip() for col in df.columns]
    if 'github_url' not in df.columns:
        st.error("CSV missing required column: github_url")
    else:
        df['github_username'] = df['github_url'].apply(extract_username)

        github_info_map = {}
        missing_url_count = 0
        for _, row in df.iterrows():
            username = row.get('github_username')
            if username:
                github_info_map[username] = {
                    "email": row.get('email', ''),
                    "full_name": row.get('full_name', '')
                }
            else:
                missing_url_count += 1

        st.success(f"Loaded contributor info for {len(github_info_map)} users.")
        if missing_url_count:
            st.warning(f"{missing_url_count} rows skipped due to invalid or missing GitHub URL.")

def get_user_info(username):
    info = github_info_map.get(username, {})
    email = info.get("email", "")
    full_name = info.get("full_name", "")
    return full_name, email

def get_headers():
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {GITHUB_TOKEN}"
    }

def fetch_merged_prs(owner, repo, start=None, end=None):
    prs = []
    page = 1
    headers = get_headers()
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = {
            "state": "closed",
            "per_page": 100,
            "page": page
        }
        r = requests.get(url, headers=headers, params=params)
        if r.status_code != 200:
            st.error(f"Error fetching PRs: {r.json().get('message', '')}")
            return None
        data = r.json()
        if not data:
            break

        stop_fetching = False
        for pr in data:
            merged_at_str = pr.get("merged_at")
            if merged_at_str:
                merged_at = datetime.strptime(merged_at_str, "%Y-%m-%dT%H:%M:%SZ")
                if end and merged_at > end:
                    # Skip PRs merged after the end date
                    continue
                if start and merged_at < start:
                    # Reached PRs older than start date — stop paging
                    stop_fetching = True
                    break
                prs.append(pr)
            else:
                # Not merged, ignore
                pass

        if stop_fetching:
            break
        page += 1
    return prs

def calculate_points(prs, points_map):
    points_per_contributor = {}
    for pr in prs:
        author = pr["user"]["login"].strip().lower()
        labels = [label["name"].lower() for label in pr.get("labels", [])]

        pr_points = 0
        for level_label, pts in points_map.items():
            if level_label in labels:
                pr_points = max(pr_points, pts)
        if pr_points == 0:
            continue
        points_per_contributor[author] = points_per_contributor.get(author, 0) + pr_points
    return points_per_contributor

def create_csv(points_dict):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["CONTRIBUTOR NAME", "CONTRIBUTOR EMAIL ID", "CONTRIBUTOR GITHUB LINK", "TOTAL POINTS"])
    for contributor, pts in sorted(points_dict.items(), key=lambda x: x[1], reverse=True):
        full_name, email = get_user_info(contributor)
        if not full_name:
            full_name = contributor  # fallback
        github_link = f"https://github.com/{contributor}"
        writer.writerow([full_name, email, github_link, pts])
    return output.getvalue()

if st.button("Fetch and Generate CSV"):
    if not owner or not repo:
        st.error("Please enter Owner and Repo.")
    elif not github_info_map:
        st.error("Please upload contributor info CSV first.")
    else:
        with st.spinner("Fetching merged PRs..."):
            prs = fetch_merged_prs(owner, repo, start=start_dt, end=end_dt)

        if prs is not None:
            with st.spinner("Calculating points..."):
                points = calculate_points(prs, POINTS_MAP)

            all_contributors = set(pr["user"]["login"].strip().lower() for pr in prs)
            mapped_contributors = set(github_info_map.keys())
            missing = all_contributors - mapped_contributors
            if missing:
                st.warning(f"Contributors missing in your CSV mapping: {', '.join(sorted(missing))}")

            if points:
                csv_data = create_csv(points)
                st.success("CSV generated successfully!")
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"{owner}_{repo}_contributor_points.csv",
                    mime="text/csv"
                )
            else:
                st.info("No contributors found with specified level labels in this time range.")


# --- Footer ---
st.markdown("---")
st.markdown(
    'Built by [Ujjwal Saini](https://github.com/ujjwalsaini07)',
    unsafe_allow_html=True
)