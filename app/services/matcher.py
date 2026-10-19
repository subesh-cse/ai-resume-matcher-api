import os
import re
import httpx
import numpy as np
from typing import Set, Dict, Any, List, Optional

COMMON_SKILLS = {
    # Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "sql", "html", "css",
    # Frameworks & Libraries
    "fastapi", "flask", "django", "react", "nextjs", "vue", "angular", "node", "express",
    "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy",
    # Databases & Storage
    "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
    # Cloud & DevOps
    "docker", "kubernetes", "aws", "gcp", "azure", "git", "github", "ci/cd", "linux", "rest", "graphql"
}

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_URL = "https://api.openai.com/v1/embeddings"


class HybridScoringEngine:

    @staticmethod
    async def get_embeddings(texts: List[str]) -> List[List[float]]:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        cleaned_texts = [t[:8000] for t in texts]

        payload = {
            "model": "text-embedding-3-small",
            "input": cleaned_texts
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(OPENAI_EMBEDDING_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        a = np.array(vec1, dtype=np.float32)
        b = np.array(vec2, dtype=np.float32)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))

    @staticmethod
    def extract_skills(text: str) -> Set[str]:
        found_skills = set()
        text_lower = text.lower()
        
        for skill in COMMON_SKILLS:
            pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        return found_skills

    @classmethod
    async def calculate_match(
        cls,
        resume_text: str,
        job_text: str,
        resume_embedding: Optional[List[float]] = None,
        job_embedding: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        if not resume_embedding:
            res_emb = await cls.get_embeddings([resume_text])
            resume_embedding = res_emb[0]

        if not job_embedding:
            jb_emb = await cls.get_embeddings([job_text])
            job_embedding = jb_emb[0]

        cos_sim = cls.cosine_similarity(resume_embedding, job_embedding)
        semantic_score = max(0.0, min(1.0, float(cos_sim)))

        resume_skills = cls.extract_skills(resume_text)
        job_skills = cls.extract_skills(job_text)

        matched_skills = sorted(list(resume_skills.intersection(job_skills)))
        missing_skills = sorted(list(job_skills - resume_skills))

        if len(job_skills) > 0:
            skill_score = len(matched_skills) / len(job_skills)
        else:
            skill_score = semantic_score

        final_score = (0.6 * semantic_score) + (0.4 * skill_score)
        match_percentage = round(final_score * 100, 2)

        if match_percentage >= 75:
            summary = "Excellent match. The candidate possesses the majority of required technical competencies and domain context."
        elif match_percentage >= 50:
            summary = "Moderate fit. Solid foundational overlap, but important target skills are missing."
        else:
            summary = "Low match. Significant gap between candidate experience and required job qualifications."

        return {
            "match_score": match_percentage,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "summary": summary
        }