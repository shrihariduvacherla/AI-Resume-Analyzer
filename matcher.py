from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_match(resume_skills, job_skills):
    """
    Compares resume skills against job description skills.
    Returns match percentage, matching skills, and missing skills.
    """
    # Convert lists to sets for easy comparison (removes duplicates too)
    resume_set = set(resume_skills)
    job_set = set(job_skills)

    # Skills that appear in both lists
    matching_skills = resume_set.intersection(job_set)

    # Skills the job wants but the resume doesn't have
    missing_skills = job_set.difference(resume_set)

    # Avoid dividing by zero if job description has no detected skills
    if len(job_set) == 0:
        match_percentage = 0
    else:
        match_percentage = (len(matching_skills) / len(job_set)) * 100

    return {
        "match_percentage": round(match_percentage, 1),
        "matching_skills": sorted(matching_skills),
        "missing_skills": sorted(missing_skills)
    }


def calculate_text_similarity(resume_text, job_text):
    """
    Compares the overall text content of the resume and job description
    using TF-IDF and cosine similarity. Returns a similarity score
    between 0 and 1 (higher means more similar in content).
    """
    # TfidfVectorizer converts text into numeric vectors based on word importance
    vectorizer = TfidfVectorizer(stop_words="english")

    # Combine both texts into one list so they're compared on the same vocabulary
    documents = [resume_text, job_text]

    # This creates the TF-IDF number representation for both documents at once
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Compare document 0 (resume) against document 1 (job description)
    similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    # cosine_similarity returns a 2D array like [[0.34]], so we extract the number
    return round(similarity_score[0][0] * 100, 1)

from sentence_transformers import SentenceTransformer, util

# Load the pre-trained model once when the app starts.
# "all-MiniLM-L6-v2" is small, fast, and free — great for this kind of task.
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_semantic_similarity(resume_text, job_text):
    """
    Compares the MEANING of the resume and job description using
    Sentence Transformers, not just exact word overlap.
    Returns a similarity score between 0 and 100.
    """
    # Convert both texts into embeddings (meaning-vectors)
    resume_embedding = semantic_model.encode(resume_text, convert_to_tensor=True)
    job_embedding = semantic_model.encode(job_text, convert_to_tensor=True)

    # Compare the two embeddings using cosine similarity
    similarity_score = util.cos_sim(resume_embedding, job_embedding)

    # similarity_score is a tensor like [[0.45]], so we extract the number
    return round(similarity_score.item() * 100, 1)


def calculate_final_score(skill_match_percentage, semantic_score):
    """
    Combines the skill-keyword match percentage with the semantic
    similarity score into one final, balanced score.
    We weight skill match slightly higher since exact skills matter
    a lot for job fit, but semantic similarity adds valuable context.
    """
    final_score = (skill_match_percentage * 0.6) + (semantic_score * 0.4)
    return round(final_score, 1)

def get_resume_tips(resume_text):
    """
    Gives basic, general suggestions for improving a resume based on
    simple, observable characteristics of the text. These are general
    best-practice tips, not a definitive judgment of resume quality.
    """
    tips = []

    word_count = len(resume_text.split())

    if word_count < 150:
        tips.append("Your resume seems quite short. Consider adding more detail "
                     "about your projects, skills, or achievements.")

    if word_count > 1000:
        tips.append("Your resume is quite long. Consider trimming it to focus "
                     "on your most relevant and recent experience.")

    resume_lower = resume_text.lower()

    if "objective" not in resume_lower and "summary" not in resume_lower:
        tips.append("Consider adding a brief career objective or summary at "
                     "the top of your resume to quickly convey your goals.")

    if "project" not in resume_lower:
        tips.append("Consider adding a Projects section — hands-on projects "
                     "are a strong way to demonstrate practical skills.")

    if not tips:
        tips.append("Your resume covers the basics well. Consider tailoring "
                     "specific keywords to each job you apply for.")

    return tips