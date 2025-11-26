from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
import asyncio
import os
from dotenv import load_dotenv

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from parsers.text_extractor import extract_text_from_file
from parsers.resume_parser import parse_with_model, parse_model_specs
from models.resume_models import ParseResponse, ModelError

load_dotenv()

app = FastAPI(title="Resume Parser API")

# CORS middleware - allow all origins in production, specific in dev
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Resume Parser API"}

@app.post("/api/parse", response_model=ParseResponse)
async def parse_resume_endpoint(
    file: UploadFile = File(...),
    models: Optional[str] = Query(
        None,
        description="Comma-separated list of provider:model (e.g., openai:gpt-4o,gemini:gemini-1.5-pro-latest)",
    ),
):
    """
    Parse a resume file and extract structured data
    """
    # Validate file type
    allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract text from file
        text = extract_text_from_file(temp_path, file_ext)
        
        if not text or len(text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from the file. File may be corrupted or empty."
            )
        
        # Determine model specs
        try:
            model_specs = parse_model_specs(models)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Parse resume using all requested models concurrently
        parse_tasks = [parse_with_model(text, spec) for spec in model_specs]
        responses = await asyncio.gather(*parse_tasks, return_exceptions=True)

        results = []
        errors = []
        for spec, result in zip(model_specs, responses):
            if isinstance(result, Exception):
                errors.append(
                    ModelError(
                        provider=spec.provider,
                        model_name=spec.model_name,
                        message=str(result),
                    )
                )
            else:
                results.append(result)

        if not results:
            raise HTTPException(
                status_code=500,
                detail="All model calls failed. Check API keys and model availability.",
            )
        
        # Clean up temp file
        os.remove(temp_path)
        
        return ParseResponse(results=results, errors=errors)
        
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

