import streamlit as st
import pandas as pd

CSV_URL = "https://docs.google.com/spreadsheets/d/12TYRJSwCimT8DIBT4UKKUGR7lrpG2lzTNK82Zc1LwO0/export?format=csv"

@st.cache_data
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()


st.set_page_config(page_title="Open Source Project Showcase", layout="wide")
st.markdown("""
<h1 style='color:#06b6d4; font-size:44px; font-weight:800; margin-bottom:5px;'>🚀 Gssoc'25 Open Source Project Showcase</h1>
<p style='color:#e0f7fa; font-size:18px; margin-top:0;'>
Explore innovative student-driven open-source projects, connect with passionate contributors, and dive into exciting tech stacks.
</p>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .big-title {
        font-size: 28px !important;
        font-weight: 700 !important;
        margin-bottom: 10px;
        color: #06b6d4; /* cyan-500 */
    }
    .section-title {
        font-size: 20px !important;
        font-weight: 600 !important;
        color: #06b6d4; /* cyan-500 */
        margin-top: 15px;
        margin-bottom: 5px;
    }
    .card {
        background-color: #1e1e1e;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.25);
        margin-bottom: 15px;
    }
    .tech-stack {
        background: #333333;
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 14px;
        margin-top: 3px;
        margin-right: 5px;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

search = st.text_input("🔍 Search projects by name or tech stack")

filtered_df = df.copy()
if search:
    mask = (
        df["Project name"].astype(str).str.contains(search, case=False, na=False) |
        df["Tech stack"].astype(str).str.contains(search, case=False, na=False)
    )
    filtered_df = df[mask]

cols = st.columns(3)  # 3 per row

for idx, row in enumerate(filtered_df.iterrows()):
    i, project = row
    with cols[idx % 3]:
        with st.expander(f"📌 {project['Project name']}"):
            # Description
            st.markdown(f"<div class='section-title'>📝 Description</div>", unsafe_allow_html=True)
            st.write(project['Project description'])

            # Project Link
            if pd.notna(project['Project link']):
                st.markdown(f"🔗 <a href='{project['Project link']}' target='_blank'><b>Visit Project</b></a>", unsafe_allow_html=True)

            # Project Admin
            st.markdown(f"<div class='section-title'>👨‍💻 Project Admin</div>", unsafe_allow_html=True)
            st.write(project['Project admin'])
            admin_links = []
            if pd.notna(project['Admin linkedin']):
                admin_links.append(f"<a href='{project['Admin linkedin']}' target='_blank'>💼 LinkedIn</a>")
            if pd.notna(project['Admin github']):
                admin_links.append(f"<a href='{project['Admin github']}' target='_blank'>🐙 GitHub</a>")
            if admin_links:
                st.markdown(" | ".join(admin_links), unsafe_allow_html=True)

            # Tech Stack
            if pd.notna(project['Tech stack']):
                st.markdown(f"<div class='section-title'>⚙️ Tech Stack</div>", unsafe_allow_html=True)
                techs = [f"<span class='tech-stack'>{t.strip()}</span>" for t in project['Tech stack'].split(",")]
                st.markdown(" ".join(techs), unsafe_allow_html=True)

            # Mentors
            mentor_list = []
            for j in range(1, 6):
                mentor = project.get(f"mentor {j}")
                if pd.notna(mentor):
                    links = []
                    if pd.notna(project.get(f"mentor {j} linkedin")):
                        links.append(f"<a href='{project[f'mentor {j} linkedin']}' target='_blank'>💼 LinkedIn</a>")
                    if pd.notna(project.get(f"mentor {j} github")):
                        links.append(f"<a href='{project[f'mentor {j} github']}' target='_blank'>🐙 GitHub</a>")
                    mentor_list.append(f"<li><b>{mentor}</b> {' | '.join(links)}</li>")

            if mentor_list:
                st.markdown(f"<div class='section-title'>👩‍🏫 Project Mentors</div>", unsafe_allow_html=True)
                st.markdown("<ul>" + "".join(mentor_list) + "</ul>", unsafe_allow_html=True)
