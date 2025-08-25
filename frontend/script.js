let notesUploaded = false;

// Show main section (via sidebar)
function showSection(sectionId){
    if(!notesUploaded && sectionId !== 'upload'){
        alert("Please upload your notes first!");
        return;
    }

    document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
}

// Enable other sections after mandatory upload
function enableSections(){
    const text = document.getElementById('manualText').value;
    const file = document.getElementById('fileUpload').files[0];

    if(!text && !file){
        alert("Please paste notes or upload a file!");
        return;
    }

    notesUploaded = true;

    // Show all tabbed sections inside main content
    document.getElementById('contentSections').style.display = 'block';

    // Remove disabled class from sidebar items
    document.querySelectorAll('.sidebar-nav li.disabled').forEach(li => li.classList.remove('disabled'));

    // Automatically switch to Summary section instead of alert
    document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
    document.getElementById('summary').classList.add('active');
}


// Tab switching inside main content
function showTab(tabId){
    if(!notesUploaded){
        alert("Please upload your notes first!");
        return;
    }

    document.querySelectorAll('.tab-section').forEach(sec => sec.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');

    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`.tab-btn[onclick="showTab('${tabId}')"]`).classList.add('active');
}

// API Calls
async function generateSummary(){
    const text = document.getElementById('manualText').value;
    const formData = new FormData();
    formData.append('text', text);

    const res = await fetch('http://localhost:8000/summary', {method:'POST', body:formData});
    const data = await res.json();
    document.getElementById('summaryResult').innerText = data.summary;
}

async function generateFlashcards(){
    const text = document.getElementById('manualText').value;
    const formData = new FormData();
    formData.append('text', text);

    const res = await fetch('http://localhost:8000/flashcards', {method:'POST', body:formData});
    const data = await res.json();

    const container = document.getElementById('flashcardsResult');
    container.innerHTML = '';
    data.flashcards.split("\n\n").forEach(f => {
        if(f.trim()){
            const div = document.createElement('div');
            div.classList.add('card-item');
            div.innerText = f;
            container.appendChild(div);
        }
    });
}

async function askQuestion(){
    const text = document.getElementById('manualText').value;
    const question = document.getElementById('userQuestion').value;
    const formData = new FormData();
    formData.append('text', text);
    formData.append('question', question);

    const res = await fetch('http://localhost:8000/qa', {method:'POST', body:formData});
    const data = await res.json();
    document.getElementById('qaResult').innerText = data.answer;
}

async function generateQuiz(){
    const text = document.getElementById('manualText').value;
    const formData = new FormData();
    formData.append('text', text);

    const res = await fetch('http://localhost:8000/quiz', {method:'POST', body:formData});
    const data = await res.json();

    const container = document.getElementById('quizResult');
    container.innerHTML = '';
    data.quiz.split("\n\n").forEach(q => {
        if(q.trim()){
            const div = document.createElement('div');
            div.classList.add('card-item');
            div.innerText = q;
            container.appendChild(div);
        }
    });
}


function downloadPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    // Get the text from the notes textarea
    const text = document.getElementById('manualText').value || "No notes available.";

    // Split text into lines for PDF
    const lines = doc.splitTextToSize(text, 180); // 180mm page width approx
    doc.text(lines, 15, 20); // starting at x=15, y=20

    // Save the PDF
    doc.save("StudyNotes.pdf");
}
