# Resume Parser

A comprehensive resume parser that extracts structured information from PDF, DOC, DOCX, and TXT files using AI-powered extraction.

## Features

- **Multi-format Support**: Parse PDF, DOC, DOCX, and TXT files
- **Structured Extraction**: Extracts contact info, experience, education, skills, certifications, awards, projects, patents, and more
- **AI-Powered**: Uses OpenAI GPT-4 for intelligent extraction
- **Multi-Model Comparison**: Run GPT-4o, GPT-5 preview, and Gemini 3 (1.5 Pro experimental) side-by-side
- **Validation**: Automatic validation of extracted data (emails, phone numbers, etc.)
- **Confidence Scoring**: Provides confidence scores for extraction quality
- **Modern UI**: Beautiful React-based interface to view parsed results
- **Export Options**: Export parsed data as JSON or CSV

## Project Structure

```
cursor-resume-parser/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── parsers/
│   │   ├── text_extractor.py   # File format parsers
│   │   └── resume_parser.py    # LLM-based extraction
│   └── models/
│       └── resume_models.py    # Pydantic data models
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   │       ├── FileUpload.jsx
│   │       └── ResumeDisplay.jsx
│   └── package.json
└── requirements.txt
```

## Setup

### Backend

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp backend/.env.example backend/.env
# Edit backend/.env and add your OPENAI_API_KEY
# Optional: add GEMINI_API_KEY for Google Gemini models
```

3. Run the backend server:
```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

- `POST /api/parse` - Upload and parse a resume file  
  - Optional `models` query param: `openai:gpt-4o,openai:gpt-5-preview,gemini:gemini-1.5-pro-exp-0827`
- `GET /api/health` - Health check endpoint

## Extracted Fields

- **Contact Information**: Name, phone, email, city
- **Experience**: Total years/months, detailed work history with companies, positions, dates, and achievements
- **Education**: Degrees, institutions, graduation years, fields of study, GPA
- **Skills**: Technical and soft skills with categories and proficiency levels
- **Certifications**: Names, issuers, dates, credential IDs
- **Awards**: Titles, issuers, dates, descriptions
- **Projects**: Names, descriptions, technologies, dates, URLs
- **Patents**: Titles, patent numbers, issue dates, inventors
- **Additional**: Summary, objective, languages, references

## Additional Features

- **Confidence Scoring**: Each extraction includes a confidence score
- **Data Validation**: Automatic validation of emails, phone numbers, and dates
- **Error Handling**: Comprehensive error handling for corrupted files and parsing failures
- **Progress Indicators**: Visual feedback during parsing
- **Model Comparison UI**: Interactive dashboard to compare OpenAI vs Gemini outputs with latency/confidence badges
- **Responsive Design**: Works on desktop and mobile devices

## Notes

- For `.doc` files, you may need to install additional libraries like `python-docx2txt` or convert them to `.docx` first
- The parser uses OpenAI GPT-4 by default. You can switch to GPT-3.5-turbo in `resume_parser.py` for faster/cheaper processing
- Make sure you have sufficient OpenAI API credits
- Gemini parsing requires a `GEMINI_API_KEY` from Google AI Studio. If absent, Gemini models will return an error while other models continue.
- Gemini 3 uses the `gemini-1.5-pro-exp-0827` identifier; swap this string if Google releases a newer Gemini 3 build.

## License

MIT




