import os
import json
import asyncio
import time
from openai import OpenAI
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import google.generativeai as genai
import google.auth
import requests
import re

# Load environment variables
load_dotenv()

# Use uvicorn's error logger so messages appear alongside server logs
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)

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

# Approximate $/1k token rates for cost estimation (update as needed)
MODEL_RATES_USD = {
    ("openai", "gpt-4o", None): {"input": 0.005, "output": 0.015},
    ("openai", "gpt-5.1", None): {"input": 0.003, "output": 0.01},
    ("gemini", "gemini-3-pro-preview", None): {"input": 0.001, "output": 0.005},
    # Hugging Face OSS via providers (per-model, per-provider)
    ("huggingface", "openai/gpt-oss-120b", "groq"): {"input": 0.00027, "output": 0.00027},  # $0.27 / 1M
    ("huggingface", "deepseek-ai/deepseek-v3", "together"): {"input": 0.0003, "output": 0.0003},  # $0.20–0.40 / 1M
    ("huggingface", "deepseek-ai/deepseek-v3.1", "together"): {"input": 0.0003, "output": 0.0003},
    ("huggingface", "qwen/qwen3-235b-a22b", "fireworks-ai"): {"input": 0.00045, "output": 0.00045},  # $0.35–0.55 / 1M
}

MODEL_DISPLAY_NAMES = {
    "openai:gpt-4o": "GPT-4o",
    "openai:gpt-5.1": "GPT-5.1",
    "openai:gpt-5-preview": "GPT-5 Preview (if available)",
    "huggingface:deepseek-ai/DeepSeek-V3": "DeepSeek-V3.1",
    "huggingface:Qwen/Qwen3-235B-A22B": "Qwen3-235B-A22B",
    "huggingface:openai/gpt-oss-120b": "GPT-OSS-120B",
    "gemini:gemini-3-pro-preview": "Gemini 3 Pro Preview",
}

# Some hosted models require a specific provider on Hugging Face Inference
MODEL_PROVIDER_HINTS = {
    "deepseek-ai/deepseek-v3": "together",
    "deepseek-ai/deepseek-v3.1": "together",
    "qwen/qwen3-235b-a22b": "fireworks-ai",
    "qwen/qwen2.5-72b-instruct": "fireworks-ai",
    "openai/gpt-oss-120b": "groq",
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


def _normalize_provider_name(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    return PROVIDER_ALIASES.get(name.lower(), name)


def get_hf_client(inference_provider: Optional[str] = None):
    """
    Build a fresh Hugging Face Inference client per call.
    Some providers are not thread-safe, so we avoid sharing a global client across concurrent requests.
    """
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key or api_key == "your_huggingface_token_here":
        raise ValueError("HUGGINGFACE_API_KEY not set. Please set it in backend/.env file")

    provider = _normalize_provider_name(inference_provider or os.getenv("HUGGINGFACE_PROVIDER"))
    client_kwargs: Dict[str, Any] = {"token": api_key}
    if provider:
        client_kwargs["provider"] = provider

    logger.info("Initializing Hugging Face InferenceClient with provider=%s", provider or "default")
    try:
        return InferenceClient(**client_kwargs)
    except Exception as e:
        logger.exception("Failed to initialize Hugging Face InferenceClient: %s", e)
        raise


def parse_model_string(model_str: str) -> ModelSpec:
    """
    Parse strings like 'openai:gpt-4o' into ModelSpec.
    Defaults to OpenAI if provider omitted.
    You can specify a Hugging Face inference provider with 'huggingface+groq:model'.
    """
    if not model_str:
        raise ValueError("Empty model spec")
    parts = model_str.split(":", 1)
    if len(parts) == 1:
        provider = ModelProvider.OPENAI
        model_name = parts[0]
        inference_provider = None
    else:
        provider_part, model_name = parts
        provider_part = provider_part.strip().lower()
        inference_provider = None
        if provider_part.startswith("huggingface+"):
            provider_part, inference_provider = provider_part.split("+", 1)
            inference_provider = inference_provider.strip() or None
        provider = ModelProvider(provider_part)

    display = MODEL_DISPLAY_NAMES.get(model_str.lower()) or model_name
    return ModelSpec(
        provider=provider,
        model_name=model_name.strip(),
        display_name=display,
        inference_provider=inference_provider,
    )


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


def _estimate_tokens_from_text(text: str) -> int:
    # Rough heuristic: ~4 characters per token
    return max(1, int(len(text) / 4))


LIST_FIELDS = [
    "education",
    "experience",
    "certifications",
    "awards",
    "projects",
    "patents",
    "skills",
    "languages",
    "references",
]


PROVIDER_ALIASES = {
    "fireworks": "fireworks-ai",
    "fireworks_ai": "fireworks-ai",
    "fireworks-ai": "fireworks-ai",
    "hf": "hf-inference",
    "huggingface": "hf-inference",
}

DEFAULT_HF_PROVIDER_PRIORITY = ["groq", "together", "fireworks-ai", "hf-inference"]


def _normalize_parsed_json(parsed_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Guard against providers returning null/atoms for list fields by coercing to lists.
    This avoids pydantic validation errors when multiple model results are aggregated.
    """
    for field in LIST_FIELDS:
        if field not in parsed_json or parsed_json[field] is None:
            parsed_json[field] = []
        elif not isinstance(parsed_json[field], list):
            parsed_json[field] = [parsed_json[field]]
    return parsed_json


def _json_to_resume(parsed_json: Dict[str, Any]) -> ResumeData:
    parsed_json = _normalize_parsed_json(parsed_json)
    resume_data = ResumeData(**parsed_json)
    # Ensure confidence score is populated
    if not resume_data.confidence_score:
        resume_data.confidence_score = calculate_confidence_score(resume_data)
    return resume_data


def _estimate_cost(provider: str, model_name: str, inference_provider: Optional[str], prompt_text: str, parsed_json: Dict[str, Any]) -> Optional[float]:
    key = (provider.lower(), model_name.lower(), inference_provider.lower() if inference_provider else None)
    rates = MODEL_RATES_USD.get(key)
    if not rates:
        return None
    input_tokens = _estimate_tokens_from_text(prompt_text)
    output_tokens = _estimate_tokens_from_text(json.dumps(parsed_json))
    cost = (input_tokens / 1000.0) * rates["input"] + (output_tokens / 1000.0) * rates["output"]
    return round(cost, 6)


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


def _hf_chat_completion(text: str, model_name: str, provider_for_call: Optional[str]) -> Dict[str, Any]:
    """Single chat completion attempt against a specific provider."""
    logger.info("Calling Hugging Face model '%s' (provider=%s)", model_name, provider_for_call or "default")
    hf_client = get_hf_client(inference_provider=provider_for_call)

    full_prompt = f"{EXTRACTION_PROMPT}\n\nParse this resume:\n\n{text}"
    supports_chat = (
        hasattr(hf_client, "chat")
        and hasattr(hf_client.chat, "completions")
        and hasattr(getattr(hf_client.chat, "completions"), "create")
    )

    try:
        if not supports_chat:
            raise ValueError(
                "Hugging Face chat API is unavailable in this environment. "
                "Upgrade huggingface_hub to >=0.23 and ensure the InferenceClient exposes chat.completions."
            )

        response = hf_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": f"Parse this resume:\n\n{text}"},
            ],
            temperature=0.1,
            max_tokens=4000,
            response_format={"type": "json_object"},
        )
        logger.info("Hugging Face chat completion received for model '%s'", model_name)
    except Exception as e:
        msg = str(e)
        hint = None
        lowered = model_name.lower()
        for key, provider_hint in MODEL_PROVIDER_HINTS.items():
            if lowered.startswith(key):
                hint = provider_hint
                break

        # Provide a clearer hint when a provider is required (e.g., Together/Fireworks)
        if "provider" in msg.lower() or "not available on inference" in msg.lower() or hint:
            suggestion = ""
            if hint:
                suggestion = f" Try setting HUGGINGFACE_PROVIDER='{hint}' for {model_name}."
            logger.exception("Hugging Face call failed for model '%s': %s%s", model_name, msg, suggestion)
            raise ValueError(
                f"Hugging Face chat completion failed: {msg}. "
                "Set HUGGINGFACE_PROVIDER to a supported provider (e.g., 'together', 'fireworks')."
                + suggestion
            ) from e
        logger.exception("Hugging Face call failed for model '%s': %s", model_name, msg)
        raise ValueError(f"Hugging Face chat completion failed: {msg}") from e

    content = response.choices[0].message.content

    if isinstance(content, list):
        # Providers may return a list of content parts; join text portions only
        content = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)

    if not isinstance(content, str):
        raise ValueError(f"Unexpected Hugging Face response format: {content}")

    content = _strip_code_fences(content)

    try:
        parsed_json = json.loads(content)
    except json.JSONDecodeError as e:
        # Try to recover by extracting the first JSON object in the text
        logger.warning("JSON parse failed for Hugging Face response from '%s'; attempting to recover", model_name)
        # Remove think blocks that some models prepend
        content_no_think = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
        if content_no_think != content:
            try:
                parsed_json = json.loads(content_no_think)
                logger.info("Recovered JSON from Hugging Face response for model '%s' after stripping <think>", model_name)
                return parsed_json
            except json.JSONDecodeError:
                content = content_no_think
        # Strategy 1: take the substring from first '{' to last '}' (helps if trailing text is appended)
        first = content.find("{")
        last = content.rfind("}")
        if first != -1 and last != -1 and last > first:
            candidate = content[first : last + 1]
            try:
                parsed_json = json.loads(candidate)
                logger.info("Recovered JSON from Hugging Face response for model '%s' using bracket slice", model_name)
                return parsed_json
            except json.JSONDecodeError:
                pass

        # Strategy 2: regex for the first JSON-like object
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                parsed_json = json.loads(match.group(0))
                logger.info("Recovered JSON from Hugging Face response for model '%s' using regex extract", model_name)
                return parsed_json
            except json.JSONDecodeError:
                pass
        raise ValueError(
            f"Failed to parse JSON from Hugging Face response. Raw content (truncated): {content[:500]}"
        ) from e

    return parsed_json


def _call_gemini(text: str, model_name: str) -> Dict[str, Any]:
    def _parse_content_text(content: str, source: str) -> Dict[str, Any]:
        content = content or ""
        content_clean = _strip_code_fences(content)
        if not content_clean:
            raise ValueError(f"Empty response from Gemini ({source})")
        try:
            return json.loads(content_clean)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse JSON from Gemini response ({source}). Raw content (truncated): {content_clean[:500]}"
            ) from e

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY not set. Please set it in backend/.env file")

    logger.info("Gemini API key call to %s via Vertex REST", model_name)
    try:
        endpoint = f"https://aiplatform.googleapis.com/v1/publishers/google/models/{model_name}:generateContent"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"Parse this resume:\n\n{text}"}],
                }
            ],
            "system_instruction": {"parts": [{"text": EXTRACTION_PROMPT}]},
            "generation_config": {
                "temperature": 0.1,
                "response_mime_type": "application/json",
            },
        }
        resp = requests.post(
            f"{endpoint}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=120,
        )
        logger.info("Gemini API key call status: %s", resp.status_code)
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates") or []
        if not candidates:
            raise ValueError(f"Empty candidates from Gemini ({data})")
        text_parts = candidates[0].get("content", {}).get("parts", [])
        combined = "".join(p.get("text", "") for p in text_parts if isinstance(p, dict))
        return _parse_content_text(combined, "api-key")
    except Exception as e:
        logger.exception("Gemini API key call failed for model %s: %s", model_name, e)
        raise ValueError(f"Gemini chat completion failed: {str(e)}") from e


def _call_huggingface(text: str, model_name: str, inference_provider: Optional[str] = None) -> Dict[str, Any]:
    """
    Call Hugging Face Inference Client chat completions API with provider priority fallback.
    Based on: https://huggingface.co/docs/inference-providers/en/tasks/chat-completion
    """
    candidates: List[Optional[str]] = []

    def _add_candidate(p: Optional[str]):
        p_norm = _normalize_provider_name(p)
        if p_norm not in candidates:
            candidates.append(p_norm)

    # 1) Explicit provider from model string goes first
    _add_candidate(inference_provider)

    lowered = model_name.lower()
    for key, provider_hint in MODEL_PROVIDER_HINTS.items():
        if lowered.startswith(key):
            _add_candidate(provider_hint)
            break

    # 3) Explicit env override for first pick
    _add_candidate(os.getenv("HUGGINGFACE_PROVIDER"))

    env_priority = os.getenv("HUGGINGFACE_PROVIDER_PRIORITY")
    if env_priority:
        for p in env_priority.split(","):
            _add_candidate(p.strip())
    else:
        for p in DEFAULT_HF_PROVIDER_PRIORITY:
            _add_candidate(p)

    _add_candidate(None)

    errors: List[str] = []
    for provider in candidates:
        try:
            return _hf_chat_completion(text, model_name, provider)
        except ValueError as e:
            errors.append(f"{provider or 'auto'}: {e}")
            continue

    raise ValueError(
        f"All Hugging Face provider attempts failed for {model_name}. "
        f"Tried: {', '.join(str(p or 'auto') for p in candidates)}. "
        f"Errors: {' | '.join(errors)}"
    )


async def parse_with_model(text: str, spec: ModelSpec) -> ParsedModelResult:
    """
    Run parsing for a single model/provider pair.
    """
    started = time.perf_counter()
    loop = asyncio.get_running_loop()

    def _caller():
        if spec.provider == ModelProvider.OPENAI:
            return _call_openai(text, spec.model_name)
        elif spec.provider == ModelProvider.HUGGINGFACE:
            return _call_huggingface(text, spec.model_name, spec.inference_provider)
        elif spec.provider == ModelProvider.GEMINI:
            return _call_gemini(text, spec.model_name)
        else:
            raise ValueError(f"Unsupported provider {spec.provider}")

    api_start = time.perf_counter()
    parsed_json = await loop.run_in_executor(None, _caller)
    api_latency_ms = int((time.perf_counter() - api_start) * 1000)

    resume = _json_to_resume(parsed_json)
    total_latency_ms = int((time.perf_counter() - started) * 1000)

    # Estimate cost when rates are known
    prompt_text = f"{EXTRACTION_PROMPT}\n\nParse this resume:\n\n{text}"
    cost_usd = _estimate_cost(spec.provider.value, spec.model_name, spec.inference_provider, prompt_text, parsed_json)

    return ParsedModelResult(
        provider=spec.provider,
        model_name=spec.model_name,
        resume=resume,
        confidence=resume.confidence_score,
        latency_ms=total_latency_ms,
        api_latency_ms=api_latency_ms,
        cost_usd=cost_usd,
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
