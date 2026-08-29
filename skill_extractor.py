import re

# A starter list of common tech/data-science skills.
# We'll keep this simple for now — we can expand it later.
SKILL_KEYWORDS = [
    "python", "java", "c++", "javascript", "html", "css",
    "sql", "mysql", "postgresql", "mongodb",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "power bi", "tableau", "excel", "data visualization",
    "machine learning", "deep learning", "nlp",
    "data analysis", "data structures", "algorithms",
    "react", "reactjs", "node.js", "flask", "django",
    "git", "github", "docker", "aws", "azure", "gcp",
    "streamlit", "api", "rest api"
]


def extract_skills(text):
    """
    Takes a block of text and returns a list of skills found in it,
    based on our SKILL_KEYWORDS list. Uses word-boundary matching so
    "java" doesn't incorrectly match inside "javascript".
    """
    text_lower = text.lower()  # make matching case-insensitive

    found_skills = []
    for skill in SKILL_KEYWORDS:
        # \b means "word boundary" - so the skill must appear as a
        # whole word/phrase, not just as a substring inside another word.
        # re.escape() handles skills with special characters like "c++".
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return found_skills
# Maps each skill to a general category, so we can give more useful
# recommendations than just "learn this skill."
SKILL_CATEGORIES = {
    "python": "Programming Language",
    "java": "Programming Language",
    "c++": "Programming Language",
    "javascript": "Programming Language",
    "html": "Web Development",
    "css": "Web Development",
    "sql": "Database",
    "mysql": "Database",
    "postgresql": "Database",
    "mongodb": "Database",
    "pandas": "Data Analysis Library",
    "numpy": "Data Analysis Library",
    "scikit-learn": "Machine Learning Library",
    "tensorflow": "Machine Learning Library",
    "pytorch": "Machine Learning Library",
    "power bi": "Data Visualization Tool",
    "tableau": "Data Visualization Tool",
    "excel": "Data Analysis Tool",
    "data visualization": "Data Visualization Skill",
    "machine learning": "Machine Learning Concept",
    "deep learning": "Machine Learning Concept",
    "nlp": "Machine Learning Concept",
    "data analysis": "Data Skill",
    "data structures": "Computer Science Fundamentals",
    "algorithms": "Computer Science Fundamentals",
    "react": "Web Development Framework",
    "reactjs": "Web Development Framework",
    "node.js": "Web Development Framework",
    "flask": "Web Development Framework",
    "django": "Web Development Framework",
    "git": "Version Control",
    "github": "Version Control",
    "docker": "DevOps Tool",
    "aws": "Cloud Platform",
    "azure": "Cloud Platform",
    "gcp": "Cloud Platform",
    "streamlit": "Web App Framework",
    "api": "Software Development Concept",
    "rest api": "Software Development Concept",
}


def get_skill_recommendations(missing_skills):
    """
    Takes a list of missing skills and returns a list of recommendation
    dictionaries, each containing the skill, its category, and a general
    suggestion for where to start learning it.
    """
    recommendations = []

    for skill in missing_skills:
        category = SKILL_CATEGORIES.get(skill, "General Skill")

        recommendations.append({
            "skill": skill,
            "category": category,
            "suggestion": f"Consider exploring free resources like the official "
                           f"documentation, YouTube tutorials, or freeCodeCamp to "
                           f"build familiarity with {skill} ({category})."
        })

    return recommendations