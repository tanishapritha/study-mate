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
    api_key=os.getenv("OPENROUTER_API_KEY"),     # Do NOT pass proxies
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

def extract_text(file: UploadFile):
    if file.content_type == "application/pdf":
        file_bytes = file.file.read()
        pdf = pdfplumber.open(io.BytesIO(file_bytes))
        text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        return text
    elif file.content_type == "text/plain":
        file.file.seek(0)
        return file.file.read().decode("utf-8")
    return ""

# Summary
@app.post("/summary")
async def generate_summary(text: str = Form(...), file: UploadFile = File(None)):
    try:
        if file:
            text = extract_text(file)
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful study assistant."},
                {"role": "user", "content": f"Summarize this text in 5 key points:\n\n{text}"}
            ],
            temperature=0.5,
            max_tokens=300
        )
        return {"summary": response.choices[0].message.content}
    except Exception as e:
        print("Error generating summary:", str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to generate summary. Please try again later."}
        )

# Flashcards
@app.post("/flashcards")
async def generate_flashcards(text: str = Form(...)):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful study assistant."},
                {"role": "user", "content": f"Convert this text into 10 flashcards in question-answer format:\n\n{text}"}
            ],
            temperature=0.5,
            max_tokens=500
        )
        return {"flashcards": response.choices[0].message.content}
    except Exception as e:
        print("Error generating flashcards:", str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to generate flashcards. Please try again later."}
        )

# Q&A
@app.post("/qa")
async def ask_question(text: str = Form(...), question: str = Form(...)):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful study assistant."},
                {"role": "user", "content": f"Answer the question based on these notes:\n\n{text}\n\nQuestion: {question}"}
            ],
            temperature=0.5,
            max_tokens=300
        )
        return {"answer": response.choices[0].message.content}
    except Exception as e:
        print("Error answering question:", str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to answer question. Please try again later."}
        )

# Quiz
@app.post("/quiz")
async def generate_quiz(text: str = Form(...)):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful study assistant."},
                {"role": "user", "content": f"Create 5 multiple-choice questions based on these notes. Provide 4 options each, mark the correct answer:\n\n{text}"}
            ],
            temperature=0.5,
            max_tokens=500
        )
        return {"quiz": response.choices[0].message.content}
    except Exception as e:
        print("Error generating quiz:", str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to generate quiz. Please try again later."}
        )
