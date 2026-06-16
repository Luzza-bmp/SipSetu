
import re
from typing import Optional
 
 
# ── Section-heading patterns ────────────────────────────────────────────────
# Matches lines like: "SKILLS", "Skills:", "TECHNICAL SKILLS", "Key Skills" etc.
_SKILLS_HEADER = re.compile(
    r"^(?:technical\s+)?skills(?:\s+summary)?[:\s]*$",
    re.IGNORECASE | re.MULTILINE,
)
 
# Matches "Experience", "Work Experience", "Professional Experience", "Employment"
_EXPERIENCE_HEADER = re.compile(
    r"^(?:work\s+|professional\s+|relevant\s+)?(?:experience|employment|history)[:\s]*$",
    re.IGNORECASE | re.MULTILINE,
)
 
# Any known major section that signals the end of a previous one
_ANY_SECTION_HEADER = re.compile(
    r"^(?:education|projects?|certifications?|awards?|publications?|"
    r"languages?|interests?|references?|summary|objective|profile|"
    r"technical\s+skills|skills|work\s+experience|experience|employment)[:\s]*$",
    re.IGNORECASE | re.MULTILINE,
)
 
# Patterns for extracting years of experience from free text
# Matches: "5 years", "3+ years", "2-4 years", "over 6 years"
_YEARS_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:\+|–|-|to)?\s*(?:\d+\s+)?year[s]?",
    re.IGNORECASE,
)
 
 
def _extract_section(text: str, header_pattern: re.Pattern) -> str:
    """Return the text body immediately following the first matched header."""
    match = header_pattern.search(text)
    if not match:
        return ""
 
    # Find where this section ends — the next major heading after the match
    remainder = text[match.end():]
    end_match = _ANY_SECTION_HEADER.search(remainder)
    if end_match:
        return remainder[: end_match.start()].strip()
    return remainder.strip()
 
 
def _extract_skill_names(skills_text: str) -> list[str]:
    """
    Turn a raw skills block into a clean list of skill tokens.
    Handles bullet lists, comma-separated, line-separated formats.
    """
    # Replace bullets / pipes / semicolons with commas, then split
    normalised = re.sub(r"[•·▪\-|;/]", ",", skills_text)
    tokens = [t.strip() for t in re.split(r"[,\n\r]+", normalised)]
    # Drop empty strings and very long tokens (likely sentences, not skill names)
    return [t for t in tokens if 1 < len(t) < 60]
 
 
def _estimate_experience_years(experience_text: str) -> float:
    """
    Heuristic: sum all year-spans found in the experience section.
    E.g. "3 years at Foo" + "2 years at Bar" → 5.0
 
    Falls back to counting distinct date-range years if no explicit mentions.
    """
    explicit = _YEARS_PATTERN.findall(experience_text)
    if explicit:
        # Cap individual tenures at 20 to avoid "20+ years experience" inflating total
        return min(sum(float(y) for y in explicit), 40.0)
 
    # Fallback: count 4-digit years that look like job dates (1990-2030)
    years_found = re.findall(r"\b(19[89]\d|20[012]\d)\b", experience_text)
    if len(years_found) >= 2:
        years_ints = sorted(set(int(y) for y in years_found))
        return float(years_ints[-1] - years_ints[0])
 
    return 0.0
 
 
def parse_resume(full_text: str) -> dict:
    """
    Parse a resume's raw text and return a structured dict:
 
    {
        "skills_text":        str,   # raw skills section body
        "skills_list":        list,  # ["Python", "Django", ...]
        "experience_text":    str,   # raw experience section body
        "experience_years":   float, # estimated total years
        "embedding_input":    str,   # text sent to the embedder (anti-gaming)
    }
    """
    skills_text     = _extract_section(full_text, _SKILLS_HEADER)
    experience_text = _extract_section(full_text, _EXPERIENCE_HEADER)
    skills_list     = _extract_skill_names(skills_text)
    experience_years = _estimate_experience_years(experience_text)
 
    # The embedding is built ONLY from these two sections.
    # Any content outside (including hidden keyword-stuffing) is excluded.
    embedding_input = f"Skills: {skills_text}\n\nExperience: {experience_text}"
 
    return {
        "skills_text":      skills_text,
        "skills_list":      skills_list,
        "experience_text":  experience_text,
        "experience_years": experience_years,
        "embedding_input":  embedding_input,
    }