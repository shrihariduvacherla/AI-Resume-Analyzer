import streamlit as st
from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills, get_skill_recommendations
from matcher import calculate_match, calculate_text_similarity, calculate_semantic_similarity, calculate_final_score, get_resume_tips
from database import init_db, save_analysis, get_all_analyses

# Make sure the database and table exist before the app runs
init_db()

# Basic page configuration
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")


def get_score_color(score):
    """
    Returns a color based on the score value, so higher scores look
    more positive (green) and lower scores look more cautionary (red).
    """
    if score >= 70:
        return "#2ECC71"
    elif score >= 40:
        return "#F39C12"
    else:
        return "#E74C3C"


def render_score_card(label, score):
    """
    Renders a single score as a colored card with a progress bar,
    instead of a plain number, for a more visual, professional look.
    """
    color = get_score_color(score)
    st.markdown(f"""
        <div style="padding: 12px; border-radius: 10px; background-color: #F8F9FA;
                    border-left: 6px solid {color}; margin-bottom: 10px;">
            <p style="margin: 0; font-size: 14px; color: #555;">{label}</p>
            <p style="margin: 0; font-size: 26px; font-weight: bold; color: {color};">{score}%</p>
        </div>
    """, unsafe_allow_html=True)
    st.progress(min(int(score), 100))


# --- Custom CSS Styling (Gemini-inspired) ---
# --- Custom CSS Styling (Gemini-inspired, theme-aware) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');

        * {
            font-family: 'Roboto', 'Google Sans', sans-serif;
        }

        /* Gradient title text - works in both light and dark mode */
        h1 {
            background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            font-size: 2.2rem !important;
        }

        /* Buttons - fully rounded "pill" shape, same in both themes */
        .stButton > button {
            background: linear-gradient(90deg, #4285F4, #9B72CB);
            color: white !important;
            border-radius: 24px;
            border: none;
            padding: 12px 28px;
            font-weight: 500;
            font-size: 15px;
            transition: all 0.25s ease-in-out;
            box-shadow: 0 1px 3px rgba(0,0,0,0.15);
        }
        .stButton > button:hover {
            box-shadow: 0 4px 14px rgba(66, 133, 244, 0.35);
            transform: translateY(-1px);
        }

        /* Containers - use theme's own background/border, just add rounding + shadow */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 20px !important;
            box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
        }

        /* Text areas - rounded, but let theme control colors */
        textarea, .stTextArea textarea {
            border-radius: 18px !important;
        }

        section[data-testid="stFileUploaderDropzone"] {
            border-radius: 18px !important;
            border: 1.5px dashed rgba(128, 128, 128, 0.4) !important;
        }

        /* Expander - just rounding, no forced colors */
        .streamlit-expanderHeader {
            border-radius: 12px;
            font-weight: 500;
        }

        button[data-baseweb="tab"] {
            font-weight: 500;
            font-size: 15px;
        }

        /* Progress bars - gradient fill (looks good in both themes) */
        .stProgress > div > div {
            background: linear-gradient(90deg, #4285F4, #9B72CB) !important;
        }

        div[data-testid="stAlert"] {
            border-radius: 16px;
        }
    </style>
""", unsafe_allow_html=True)


# --- Sidebar ---
with st.sidebar:
    st.title("📄 AI Resume Analyzer")
    st.write("Upload your resume, paste a job description, and get an instant AI-powered match analysis.")
    st.markdown("---")
    st.caption("Built with Python, Streamlit, scikit-learn, and Sentence Transformers.")

# --- Main Title ---
st.title("🚀 AI-Powered Resume & Job Matching System")
st.write("Analyze how well your resume matches a job description using skill detection and AI semantic similarity.")
st.divider()

# --- Tabs for main navigation ---
tab1, tab2 = st.tabs(["🔍 Analyze", "🕘 History"])

with tab1:
    # --- Resume Upload Section ---
    with st.container(border=True):
        st.subheader("1️⃣ Upload Your Resume")

        uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

        resume_skills = []
        resume_text = ""
        if uploaded_file is not None:
            try:
                resume_text = extract_text_from_pdf(uploaded_file)
                st.success("✅ Resume uploaded and text extracted!")

                with st.expander("View Extracted Resume Text"):
                    st.text_area("Extracted Text", resume_text, height=300)

                resume_skills = extract_skills(resume_text)
                st.markdown("**🧩 Skills Found in Your Resume:**")
                st.write(resume_skills)
            except ValueError as e:
                st.error(f"❌ {e}")
                resume_text = ""

    st.write("")

    # --- Job Description Section ---
    with st.container(border=True):
        st.subheader("2️⃣ Paste Job Description")

        job_description = st.text_area("Paste the job description here:", height=200)

        job_skills = []
        if job_description:
            job_skills = extract_skills(job_description)
            st.markdown("**🧩 Skills Found in Job Description:**")
            st.write(job_skills)

    st.write("")

    # --- Matching Section ---
    analyze_clicked = st.button("🔍 Analyze Match", use_container_width=True)

    if analyze_clicked:
        if not resume_skills:
            st.warning("⚠️ Please upload a resume first.")
        elif not job_skills:
            st.warning("⚠️ Please paste a job description first.")
        else:
            with st.spinner("🤖 Running AI analysis... this may take a few seconds"):
                result = calculate_match(resume_skills, job_skills)
                text_similarity = calculate_text_similarity(resume_text, job_description)
                semantic_score = calculate_semantic_similarity(resume_text, job_description)
                final_score = calculate_final_score(result["match_percentage"], semantic_score)

            st.divider()

            with st.container(border=True):
                st.subheader("3️⃣ Match Analysis")
                render_score_card("🎯 Final Match Score", final_score)

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    render_score_card("Skill Match", result['match_percentage'])
                with col_b:
                    render_score_card("TF-IDF Similarity", text_similarity)
                with col_c:
                    render_score_card("Semantic (AI) Similarity", semantic_score)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**✅ Matching Skills**")
                    st.write(result["matching_skills"])
                with col2:
                    st.markdown("**❌ Missing Skills**")
                    st.write(result["missing_skills"])

            st.write("")

            # --- Recommendations Section ---
            with st.container(border=True):
                st.subheader("4️⃣ Recommendations")

                if result["missing_skills"]:
                    st.markdown("**📚 Skills to Learn**")
                    skill_recs = get_skill_recommendations(result["missing_skills"])
                    for rec in skill_recs:
                        st.write(f"**{rec['skill']}** ({rec['category']}) — {rec['suggestion']}")
                else:
                    st.success("🎉 No missing skills detected — great match!")

                st.markdown("**📝 Resume Improvement Tips**")
                resume_tips = get_resume_tips(resume_text)
                for tip in resume_tips:
                    st.write(f"- {tip}")

            # Save this analysis to the database
            save_analysis(
                final_score,
                result["match_percentage"],
                semantic_score,
                result["matching_skills"],
                result["missing_skills"]
            )
            st.info("💾 This analysis has been saved to your history.")

with tab2:
    st.subheader("Analysis History")

    history = get_all_analyses()

    if history:
        for row in history:
            row_id, timestamp, final_score, skill_match, semantic_score, matching, missing = row
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"🕒 **{timestamp}**")
                with col2:
                    color = get_score_color(final_score)
                    st.markdown(f"<span style='color:{color}; font-weight:bold; font-size:18px;'>{final_score}%</span>", unsafe_allow_html=True)

                with st.expander("View details"):
                    st.write(f"**Skill Match:** {skill_match}%")
                    st.write(f"**Semantic Similarity:** {semantic_score}%")
                    st.write(f"**Matching Skills:** {matching}")
                    st.write(f"**Missing Skills:** {missing}")
    else:
        st.write("No analysis history yet. Run your first analysis in the Analyze tab!")