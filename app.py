import streamlit as st
import openai
from dotenv import load_dotenv
import os
import PyPDF2
import pdfplumber

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")  # Or directly: openai.api_key = "YOUR_KEY"

st.title("📝 AI-Powered Study Assistant")
st.write("Upload notes (PDF or TXT) or paste text to generate summaries, flashcards, quizzes, and ask questions.")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])
user_text = ""

# Extract text from file
if uploaded_file:
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            pages = [page.extract_text() for page in pdf.pages]
            user_text = "\n".join(pages)
    elif uploaded_file.type == "text/plain":
        user_text = str(uploaded_file.read(), "utf-8")
    st.text_area("Extracted Text:", value=user_text, height=300)

# Also allow manual paste
manual_text = st.text_area("Or paste your notes here:", value="", height=150)
if manual_text.strip():
    user_text = manual_text

# -------------------- SUMMARY --------------------
if st.button("Generate Summary"):
    if user_text:
        with st.spinner("Generating summary..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful study assistant."},
                        {"role": "user", "content": f"Summarize this text in 5 key points for study purposes:\n\n{user_text}"}
                    ],
                    temperature=0.5,
                    max_tokens=300
                )
                summary = response['choices'][0]['message']['content']
                st.subheader("Summary:")
                st.markdown(f"<div style='background-color:#E0F7FA; padding:15px; border-radius:10px'>{summary}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please upload a file or enter some text!")

# -------------------- FLASHCARDS --------------------
if st.button("Generate Flashcards"):
    if user_text:
        with st.spinner("Generating flashcards..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful study assistant."},
                        {"role": "user", "content": f"Convert this text into 10 flashcards in question-answer format for study purposes:\n\n{user_text}"}
                    ],
                    temperature=0.5,
                    max_tokens=500
                )
                flashcards = response['choices'][0]['message']['content']
                st.subheader("Flashcards:")
                for card in flashcards.split("\n\n"):
                    if card.strip():
                        question = card.split("\n")[0]
                        answer = "\n".join(card.split("\n")[1:])
                        with st.expander(question):
                            st.write(answer)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please upload a file or enter some text!")

# -------------------- Q&A --------------------
st.subheader("Ask Questions About Your Notes")
user_question = st.text_input("Type your question here:")

if st.button("Get Answer"):
    if user_text and user_question.strip():
        with st.spinner("AI is thinking..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful study assistant."},
                        {"role": "user", "content": f"Answer the question based on the following notes:\n\nNotes:\n{user_text}\n\nQuestion: {user_question}"}
                    ],
                    temperature=0.5,
                    max_tokens=300
                )
                answer = response['choices'][0]['message']['content']
                st.subheader("Answer:")
                st.markdown(f"<div style='background-color:#E8F5E9; padding:15px; border-radius:10px'>{answer}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please upload notes and type a question!")

# -------------------- QUIZ --------------------
st.subheader("Generate Quiz (MCQs)")
if st.button("Create Quiz"):
    if user_text:
        with st.spinner("Generating quiz..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful study assistant."},
                        {"role": "user", "content": f"Create 5 multiple-choice questions based on the following notes. Provide 4 options each, mark the correct answer:\n\n{user_text}"}
                    ],
                    temperature=0.5,
                    max_tokens=500
                )
                quiz = response['choices'][0]['message']['content']
                st.subheader("Quiz:")
                for q in quiz.split("\n\n"):
                    if q.strip():
                        question_title = q.split("\n")[0]
                        options = "\n".join(q.split("\n")[1:])
                        with st.expander(question_title):
                            st.write(options)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please upload notes first!")
