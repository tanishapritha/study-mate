from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import pdfplumber
import os
from dotenv import load_dotenv


load_dotenv()


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",          # OpenRouter
    api_key=os.getenv("OPENROUTER_API_KEY")           
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
    import io
    import pdfplumber

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
    if file:
        text = extract_text(file)
    response = client.chat.completions.create(
        model="gpt-4.1-mini",  
        messages=[
            {"role": "system", "content": "You are a helpful study assistant."},
            {"role": "user", "content": f"Summarize this text in 5 key points for study purposes:\n\n{text}"}
        ],
        temperature=0.5,
        max_tokens=300
    )
    return {"summary": response.choices[0].message.content}

# Flashcards
@app.post("/flashcards")
async def generate_flashcards(text: str = Form(...)):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a helpful study assistant."},
            {"role": "user", "content": f"Convert this text into 10 flashcards in question-answer format for study purposes:\n\n{text}"}
        ],
        temperature=0.5,
        max_tokens=500
    )
    return {"flashcards": response.choices[0].message.content}

# Q&A
@app.post("/qa")
async def ask_question(text: str = Form(...), question: str = Form(...)):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a helpful study assistant."},
            {"role": "user", "content": f"Answer the question based on the following notes:\n\n{text}\n\nQuestion: {question}"}
        ],
        temperature=0.5,
        max_tokens=300
    )
    return {"answer": response.choices[0].message.content}

# Quiz
@app.post("/quiz")
async def generate_quiz(text: str = Form(...)):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a helpful study assistant."},
            {"role": "user", "content": f"Create 5 multiple-choice questions based on the following notes. Provide 4 options each, mark the correct answer:\n\n{text}"}
        ],
        temperature=0.5,
        max_tokens=500
    )
    return {"quiz": response.choices[0].message.content}
