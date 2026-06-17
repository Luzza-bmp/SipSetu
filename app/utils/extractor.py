import re

SKILLS_DB = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "php", "ruby",
    "flask", "django", "react", "node.js", "express", "angular", "vue", "svelte", "fastapi",
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "graphql", "rest api",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github", "gitlab",
    "html", "css", "tailwind", "bootstrap", "sass", "webpack", "vite",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
    "design", "figma", "ui", "ux", "product", "agile", "scrum", "jira",
    "communication", "leadership", "teamwork", "problem solving", "critical thinking"
]

def extract_skills(text):
    if not text:
        return []
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in SKILLS_DB:
        # Generate regex patterns that handle special characters and word boundaries
        if skill == 'c++':
            pattern = r'\bc\+\+(?:\b|[^\w+])'
        elif skill == 'c#':
            pattern = r'\bc\#(?:\b|[^\w#])'
        elif skill == 'node.js':
            pattern = r'\bnode\.js\b'
        elif '.' in skill:
            pattern = r'\b' + re.escape(skill) + r'\b'
        else:
            pattern = r'\b' + re.escape(skill) + r'\b'
            
        if re.search(pattern, text_lower):
            found_skills.append(skill)
            
    return found_skills
