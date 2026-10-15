from app.services.matcher import HybridScoringEngine


def test_extract_skills_boundary_matching():
    """
    Test that regex accurately captures whole skills and prevents
    false positives (e.g., 'c' inside 'docker', 'go' inside 'mongodb').
    """
    sample_text = (
        "Experienced Backend Developer proficient in Python, FastAPI, and Docker. "
        "Worked with PostgreSQL, Redis, and Git. Some knowledge of C++ and Go."
    )
    extracted = HybridScoringEngine.extract_skills(sample_text)

    # Must find the real skills
    assert "python" in extracted
    assert "fastapi" in extracted
    assert "docker" in extracted
    assert "postgresql" in extracted
    assert "redis" in extracted
    assert "git" in extracted
    assert "c++" in extracted
    assert "go" in extracted


def test_calculate_match_high_overlap():
    """
    Test that identical or highly aligned text produces a high match score (> 70)
    and populates matched_skills correctly.
    """
    resume = "Python FastAPI PostgreSQL Docker Git REST CI/CD Redis developer."
    job = "Looking for a Python developer with FastAPI, PostgreSQL, Docker, and Git experience."

    result = HybridScoringEngine.calculate_match(resume_text=resume, job_text=job)

    # 1. Structure assertions (matches the exact keys returned by the engine)
    assert "match_score" in result
    assert "matched_skills" in result
    assert "missing_skills" in result
    assert "summary" in result

    # 2. Value assertions
    assert result["match_score"] >= 70.0
    assert "python" in result["matched_skills"]
    assert "fastapi" in result["matched_skills"]
    assert "docker" in result["matched_skills"]
    assert len(result["missing_skills"]) == 0
    assert "Excellent match" in result["summary"]


def test_calculate_match_disjoint_skills():
    """
    Test that completely unrelated skillsets produce missing skills and low score.
    """
    resume = "Nurse with extensive clinical care, hospital triage, and patient monitoring."
    job = "Senior Python engineer with Kubernetes, AWS, Docker, and PostgreSQL experience."

    result = HybridScoringEngine.calculate_match(resume_text=resume, job_text=job)

    assert result["match_score"] < 50.0
    assert len(result["matched_skills"]) == 0
    assert "kubernetes" in result["missing_skills"]
    assert "aws" in result["missing_skills"]
    assert "Low match" in result["summary"]