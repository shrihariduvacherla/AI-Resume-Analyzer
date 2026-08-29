import streamlit as st
from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills, get_skill_recommendations
from matcher import calculate_match, calculate_text_similarity, calculate_semantic_similarity, calculate_final_score, get_resume_tips
from database import init_db, save_analysis, get_all_analyses

# Make sure the database and table exist before the app runs
init_db()

# Basic page configuration
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.title("📄 AI Resume Analyzer")
    st.write("Upload your resume, paste a job description, and get an instant AI-powered match analysis.")
    st.markdown("---")
    st.caption("Built with Python, Streamlit, scikit-learn, and Sentence Transformers.")

# --- Main Title ---
st.title("AI-Powered Resume & Job Matching System")
st.write("Analyze how well your resume matches a job description using skill detection and AI semantic similarity.")

# --- Tabs for main navigation ---
tab1, tab2 = st.tabs(["🔍 Analyze", "🕘 History"])

with tab1:
    # --- Resume Upload Section ---
    st.header("1. Upload Your Resume")

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
            st.subheader("Skills Found in Your Resume:")
            st.write(resume_skills)
        except ValueError as e:
            st.error(f"❌ {e}")
            resume_text = ""

    # --- Job Description Section ---
    st.header("2. Paste Job Description")

    job_description = st.text_area("Paste the job description here:", height=250)

    job_skills = []
    if job_description:
        job_skills = extract_skills(job_description)
        st.subheader("Skills Found in Job Description:")
        st.write(job_skills)

    # --- Matching Section ---
    st.header("3. Match Analysis")

    if st.button("Analyze Match"):
        if not resume_skills:
            st.warning("⚠️ Please upload a resume first.")
        elif not job_skills:
            st.warning("⚠️ Please paste a job description first.")
        else:
            result = calculate_match(resume_skills, job_skills)
            text_similarity = calculate_text_similarity(resume_text, job_description)
            semantic_score = calculate_semantic_similarity(resume_text, job_description)
            final_score = calculate_final_score(result["match_percentage"], semantic_score)

            st.metric("🎯 Final Match Score", f"{final_score}%")

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Skill Match", f"{result['match_percentage']}%")
            with col_b:
                st.metric("TF-IDF Similarity", f"{text_similarity}%")
            with col_c:
                st.metric("Semantic (AI) Similarity", f"{semantic_score}%")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("✅ Matching Skills")
                st.write(result["matching_skills"])

            with col2:
                st.subheader("❌ Missing Skills")
                st.write(result["missing_skills"])

            # --- Recommendations Section ---
            st.header("4. Recommendations")

            if result["missing_skills"]:
                st.subheader("📚 Skills to Learn")
                skill_recs = get_skill_recommendations(result["missing_skills"])
                for rec in skill_recs:
                    st.write(f"**{rec['skill']}** ({rec['category']}) — {rec['suggestion']}")
            else:
                st.success("🎉 No missing skills detected — great match!")

            st.subheader("📝 Resume Improvement Tips")
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
    st.header("Analysis History")

    history = get_all_analyses()

    if history:
        for row in history:
            row_id, timestamp, final_score, skill_match, semantic_score, matching, missing = row
            with st.expander(f"Analysis on {timestamp} — Final Score: {final_score}%"):
                st.write(f"**Skill Match:** {skill_match}%")
                st.write(f"**Semantic Similarity:** {semantic_score}%")
                st.write(f"**Matching Skills:** {matching}")
                st.write(f"**Missing Skills:** {missing}")
    else:
        st.write("No analysis history yet. Run your first analysis in the Analyze tab!")