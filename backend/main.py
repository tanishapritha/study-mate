from fastapi import FastAPI, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAI
import pdfplumber
import os
from dotenv import load_dotenv
import io

load_dotenv()

# Initialize OpenAI client for OpenRouter
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

app = FastAPI(title="AI Study Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text(file: UploadFile) -> str:
    try:
        file.file.seek(0)
        if file.content_type == "application/pdf":
            pdf = pdfplumber.open(io.BytesIO(file.file.read()))
            text = "\n".join([page.extract_text() or "" for page in pdf.pages])
            return text
        elif file.content_type == "text/plain":
            return file.file.read().decode("utf-8")
        else:
            return ""
    except Exception as e:
        print(f"Error reading file: {e}")
        return ""

def generate_response(prompt: str, max_tokens: int = 500):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful study assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

@app.post("/summary")
async def generate_summary(text: str = Form(...), file: UploadFile = File(None)):
    if file:
        text = extract_text(file)
    result = generate_response(f"Summarize this text in 5 key points:\n\n{text}", max_tokens=300)
    if result is None:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"error": "Failed to generate summary."})
    return {"summary": result}

@app.post("/flashcards")
async def generate_flashcards(text: str = Form(...)):
    result = generate_response(f"Convert this text into 10 flashcards in question-answer format:\n\n{text}", max_tokens=500)
    if result is None:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"error": "Failed to generate flashcards."})
    return {"flashcards": result}

@app.post("/qa")
async def ask_question(text: str = Form(...), question: str = Form(...)):
    result = generate_response(f"Answer the question based on these notes:\n\n{text}\n\nQuestion: {question}", max_tokens=300)
    if result is None:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"error": "Failed to answer question."})
    return {"answer": result}

@app.post("/quiz")
async def generate_quiz(text: str = Form(...)):
    result = generate_response(f"Create 5 multiple-choice questions based on these notes. Provide 4 options each, mark the correct answer:\n\n{text}", max_tokens=500)
    if result is None:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"error": "Failed to generate quiz."})
    return {"quiz": result}
