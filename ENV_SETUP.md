# Environment Setup

## Backend Setup

1. Create a `.env` file in the `backend` directory:
```bash
cd backend
touch .env
```

2. Add your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
# Optional: unlock Gemini comparison
GEMINI_API_KEY=your_gemini_api_key_here
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
cd backend
python main.py
```

Or from project root:
```bash
python -m backend.main
```

## Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

## Running the Application

1. Start the backend server (port 8000)
2. Start the frontend server (port 3000)
3. Open http://localhost:3000 in your browser
4. Choose which models to run (GPT-4o, GPT-5 preview, Gemini 3) via the checkboxes
5. Upload a resume file (PDF, DOC, DOCX, or TXT)




