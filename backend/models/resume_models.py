from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import re

class ContactInfo(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-\(\)\.]', '', v)
        # Check if it looks like a phone number (at least 10 digits)
        if not re.match(r'^\+?\d{10,15}$', cleaned):
            return None  # Return None for invalid phone numbers
        return v

class Education(BaseModel):
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[str] = None
    location: Optional[str] = None

class Experience(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = False
    summary: Optional[str] = None
    achievements: Optional[List[str]] = None

class Certification(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None

class Award(BaseModel):
    title: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None

class Project(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    url: Optional[str] = None

class Patent(BaseModel):
    title: Optional[str] = None
    patent_number: Optional[str] = None
    issue_date: Optional[str] = None
    inventors: Optional[List[str]] = None
    description: Optional[str] = None

class Skill(BaseModel):
    name: str
    category: Optional[str] = None  # e.g., "Technical", "Soft", "Language"
    proficiency: Optional[str] = None  # e.g., "Beginner", "Intermediate", "Advanced", "Expert"

class ResumeData(BaseModel):
    contact_info: ContactInfo
    total_experience_years: Optional[float] = None
    total_experience_months: Optional[int] = None
    education: List[Education] = []
    experience: List[Experience] = []
    certifications: List[Certification] = []
    awards: List[Award] = []
    projects: List[Project] = []
    patents: List[Patent] = []
    skills: Optional[List[Skill]] = []
    summary: Optional[str] = None
    objective: Optional[str] = None
    languages: Optional[List[str]] = []
    references: Optional[List[str]] = []
    
    # Metadata
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    extraction_notes: Optional[str] = None


class ModelProvider(str, Enum):
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    GEMINI = "gemini"


class ModelSpec(BaseModel):
    provider: ModelProvider
    model_name: str
    display_name: Optional[str] = None
    # For Hugging Face models, optionally specify the inference provider (e.g., groq, together, fireworks)
    inference_provider: Optional[str] = None


class ParsedModelResult(BaseModel):
    provider: ModelProvider
    model_name: str
    resume: ResumeData
    confidence: Optional[float] = None
    latency_ms: Optional[int] = None  # end-to-end parse latency
    api_latency_ms: Optional[int] = None  # model API call latency only
    cost_usd: Optional[float] = None
    raw_response: Optional[Dict[str, Any]] = None


class ModelError(BaseModel):
    provider: Optional[ModelProvider] = None
    model_name: Optional[str] = None
    message: str


class ParseResponse(BaseModel):
    results: List[ParsedModelResult] = []
    errors: List[ModelError] = []
