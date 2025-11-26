import os
import json
import asyncio
import time
from openai import OpenAI
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from models.resume_models import (
    ResumeData,
    ContactInfo,
    Education,
    Experience,
    Certification,
    Award,
    Project,
    Patent,
    Skill,
    ModelSpec,
    ModelProvider,
    ParsedModelResult,
    ModelError,
)
from dateutil import parser as date_parser
import re

# Initialize OpenAI client (will use OPENAI_API_KEY from env)
client = None

DEFAULT_MODEL_STRINGS = [
    "openai:gpt-4o",
    "openai:gpt-5.1",
]

MODEL_DISPLAY_NAMES = {
    "openai:gpt-4o": "GPT-4o",
    "openai:gpt-5.1": "GPT-5.1",
    "openai:gpt-5-preview": "GPT-5 Preview (if available)",
}

def get_client():
    """Lazy initialization of OpenAI client"""
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            raise ValueError("OPENAI_API_KEY not set. Please set it in backend/.env file")
        # Initialize client with explicit parameters to avoid proxy issues
        client = OpenAI(
            api_key=api_key,
            timeout=60.0,
            max_retries=3
        )
    return client


def parse_model_string(model_str: str) -> ModelSpec:
    """
    Parse strings like 'openai:gpt-4o' into ModelSpec.
    Defaults to OpenAI if provider omitted.
    """
    if not model_str:
        raise ValueError("Empty model spec")
    parts = model_str.split(":", 1)
    if len(parts) == 1:
        provider = ModelProvider.OPENAI
        model_name = parts[0]
    else:
        provider_part, model_name = parts
        provider = ModelProvider(provider_part.strip().lower())
    display = MODEL_DISPLAY_NAMES.get(model_str.lower()) or model_name
    return ModelSpec(provider=provider, model_name=model_name.strip(), display_name=display)


def parse_model_specs(models_param: Optional[str]) -> List[ModelSpec]:
    """
    Convert comma-separated string into ModelSpec list.
    """
    if models_param:
        raw_specs = [m.strip() for m in models_param.split(",") if m.strip()]
    else:
        raw_specs = DEFAULT_MODEL_STRINGS

    specs: List[ModelSpec] = []
    for raw in raw_specs:
        specs.append(parse_model_string(raw))
    return specs

# System prompt for structured extraction
EXTRACTION_PROMPT = """You are an expert resume parser. Extract structured information from the following resume text.

Extract the following information:
1. Contact Information: name, phone, email, city
2. Total Experience: calculate total years and months of work experience
3. Education: all degrees, institutions, graduation years, fields of study
4. Experience: all work experiences with company, position, dates, and contributions
5. Certifications: all certifications with issuer and dates
6. Awards: any awards or recognitions
7. Projects: projects with descriptions and technologies
8. Patents: any patents with numbers and dates
9. Skills: technical and soft skills
10. Summary/Objective: professional summary or objective
11. Languages: languages known
12. References: if mentioned

For dates, use YYYY-MM format when possible, or YYYY if only year is available.
For experience, calculate total years and months across all positions.
Extract achievements and contributions for each experience.

Return ONLY valid JSON matching this structure:
{
  "contact_info": {
    "name": "string or null",
    "phone": "string or null",
    "email": "string or null",
    "city": "string or null"
  },
  "total_experience_years": number or null,
  "total_experience_months": number or null,
  "education": [
    {
      "degree": "string or null",
      "field_of_study": "string or null",
      "institution": "string or null",
      "graduation_year": number or null,
      "gpa": "string or null",
      "location": "string or null"
    }
  ],
  "experience": [
    {
      "company": "string or null",
      "position": "string or null",
      "start_date": "string or null",
      "end_date": "string or null",
      "is_current": boolean,
      "summary": "string or null",
      "achievements": ["string"] or null
    }
  ],
  "certifications": [
    {
      "name": "string or null",
      "issuer": "string or null",
      "issue_date": "string or null",
      "expiry_date": "string or null",
      "credential_id": "string or null"
    }
  ],
  "awards": [
    {
      "title": "string or null",
      "issuer": "string or null",
      "date": "string or null",
      "description": "string or null"
    }
  ],
  "projects": [
    {
      "name": "string or null",
      "description": "string or null",
      "technologies": ["string"] or null,
      "start_date": "string or null",
      "end_date": "string or null",
      "url": "string or null"
    }
  ],
  "patents": [
    {
      "title": "string or null",
      "patent_number": "string or null",
      "issue_date": "string or null",
      "inventors": ["string"] or null,
      "description": "string or null"
    }
  ],
  "skills": [
    {
      "name": "string",
      "category": "string or null",
      "proficiency": "string or null"
    }
  ],
  "summary": "string or null",
  "objective": "string or null",
  "languages": ["string"] or null,
  "references": ["string"] or null
}

Return ONLY the JSON object, no additional text or markdown formatting."""

def _strip_code_fences(content: str) -> str:
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()


def _json_to_resume(parsed_json: Dict[str, Any]) -> ResumeData:
    resume_data = ResumeData(**parsed_json)
    # Ensure confidence score is populated
    if not resume_data.confidence_score:
        resume_data.confidence_score = calculate_confidence_score(resume_data)
    return resume_data


def _call_openai(text: str, model_name: str) -> Dict[str, Any]:
    client = get_client()
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": f"Parse this resume:\n\n{text}"},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    content = _strip_code_fences(content)
    parsed_json = json.loads(content)
    return parsed_json


async def parse_with_model(text: str, spec: ModelSpec) -> ParsedModelResult:
    """
    Run parsing for a single model/provider pair.
    """
    started = time.perf_counter()
    loop = asyncio.get_running_loop()

    def _caller():
        if spec.provider == ModelProvider.OPENAI:
            return _call_openai(text, spec.model_name)
        else:
            raise ValueError(f"Unsupported provider {spec.provider}")

    parsed_json = await loop.run_in_executor(None, _caller)
    resume = _json_to_resume(parsed_json)
    latency_ms = int((time.perf_counter() - started) * 1000)

    return ParsedModelResult(
        provider=spec.provider,
        model_name=spec.model_name,
        resume=resume,
        confidence=resume.confidence_score,
        latency_ms=latency_ms,
        raw_response=parsed_json,
    )


async def parse_resume(text: str, model_str: str = "openai:gpt-4o") -> ResumeData:
    """
    Backwards-compatible single-model parser (defaults to GPT-4o).
    """
    spec = parse_model_string(model_str)
    result = await parse_with_model(text, spec)
    return result.resume

def calculate_confidence_score(resume_data: ResumeData) -> float:
    """
    Calculate a confidence score based on extracted data completeness and quality
    """
    score = 0.0
    max_score = 10.0
    
    # Core Contact info (2.5 points - most important)
    contact_score = 0.0
    if resume_data.contact_info.name:
        contact_score += 0.8  # Name is critical
    if resume_data.contact_info.email:
        contact_score += 0.8  # Email is critical
    if resume_data.contact_info.phone:
        contact_score += 0.5  # Phone is nice to have
    if resume_data.contact_info.city:
        contact_score += 0.4  # City is optional
    score += min(contact_score, 2.5)
    
    # Experience (2.5 points - very important)
    experience_score = 0.0
    if resume_data.experience and len(resume_data.experience) > 0:
        experience_score += 1.5
        # Bonus for multiple experiences
        if len(resume_data.experience) > 1:
            experience_score += 0.3
        # Bonus for detailed experience (with summary/achievements)
        detailed_experiences = sum(1 for exp in resume_data.experience if exp.summary or (exp.achievements and len(exp.achievements) > 0))
        if detailed_experiences > 0:
            experience_score += 0.2
    if resume_data.total_experience_years:
        experience_score += 0.5
    score += min(experience_score, 2.5)
    
    # Education (1.5 points - important)
    if resume_data.education and len(resume_data.education) > 0:
        score += 1.0
        # Bonus for multiple degrees
        if len(resume_data.education) > 1:
            score += 0.3
        # Bonus for complete education info
        complete_edu = sum(1 for edu in resume_data.education if edu.degree and edu.institution)
        if complete_edu > 0:
            score += 0.2
    score = min(score, max_score * 0.4)  # Cap at 40% for core fields
    
    # Skills (1.5 points - important)
    if resume_data.skills and len(resume_data.skills) > 0:
        score += 1.0
        # Bonus for multiple skills
        if len(resume_data.skills) > 5:
            score += 0.3
        if len(resume_data.skills) > 10:
            score += 0.2
    score = min(score, max_score * 0.55)  # Cap at 55% with skills
    
    # Summary/Objective (0.5 points - nice to have)
    if resume_data.summary or resume_data.objective:
        score += 0.5
    
    # Additional sections (bonus points, up to 2.0 total)
    bonus_score = 0.0
    if resume_data.certifications and len(resume_data.certifications) > 0:
        bonus_score += 0.3
    if resume_data.projects and len(resume_data.projects) > 0:
        bonus_score += 0.4
    if resume_data.awards and len(resume_data.awards) > 0:
        bonus_score += 0.2
    if resume_data.patents and len(resume_data.patents) > 0:
        bonus_score += 0.3
    if resume_data.languages and len(resume_data.languages) > 0:
        bonus_score += 0.2
    if resume_data.references and len(resume_data.references) > 0:
        bonus_score += 0.1
    
    # Add bonus (capped at 2.0) to reach up to 8.0, then normalize
    score += min(bonus_score, 2.0)
    
    # Normalize to 0-1 range, but adjust scale so good resumes score higher
    # A resume with core fields (contact, experience, education, skills) should score 60-70%
    # With additional sections, should score 80-90%
    normalized = min(score / max_score, 1.0)
    
    # Adjust scale: minimum 0.3 for any valid extraction, scale up from there
    if normalized < 0.3:
        normalized = 0.3  # Minimum confidence for any extraction
    elif normalized < 0.5:
        # Scale 0.3-0.5 to 0.4-0.7 (better scaling for basic resumes)
        normalized = 0.4 + (normalized - 0.3) * 1.5
    elif normalized < 0.7:
        # Scale 0.5-0.7 to 0.7-0.85
        normalized = 0.7 + (normalized - 0.5) * 0.75
    else:
        # Scale 0.7-1.0 to 0.85-1.0
        normalized = 0.85 + (normalized - 0.7) * 0.5
    
    return min(normalized, 1.0)

