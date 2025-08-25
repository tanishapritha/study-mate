let notesUploaded = false;
const BASE_URL = 'https://study-mate-ns25.onrender.com'; // Render backend URL

// Helper: Show creative error messages inside a container
function showCreativeError(containerId) {
    const messages = [
        "Oops! The brain gears got stuck 🧠⚙️. Try again!",
        "Uh-oh! The server seems to be napping 😴. Give it another shot!",
        "Whoops! Something went kaboom 💥. Let's retry!",
        "Hmm… the notes are playing hide and seek 🤔. Try once more!"
    ];
    const msg = messages[Math.floor(Math.random() * messages.length)];
    document.getElementById(containerId).innerText = msg;
}

// --- Section and Tab Handling (unchanged) ---
function showSection(sectionId){
    if(!notesUploaded && sectionId !== 'upload'){
        alert("Please upload your notes first!");
        return;
    }

    document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
}

function enableSections(){
    const text = document.getElementById('manualText').value;
    const file = document.getElementById('fileUpload').files[0];

    if(!text && !file){
        alert("Please paste notes or upload a file!");
        return;
    }

    notesUploaded = true;

    document.getElementById('contentSections').style.display = 'block';
    document.querySelectorAll('.sidebar-nav li.disabled').forEach(li => li.classList.remove('disabled'));

    showTab('summary');
}

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

// --- API Calls with error handling ---
async function generateSummary(){
    try {
        const text = document.getElementById('manualText').value;
        const formData = new FormData();
        formData.append('text', text);

        const res = await fetch(`${BASE_URL}/summary`, {method:'POST', body:formData});
        if(!res.ok) throw new Error("Network response not ok");
        const data = await res.json();
        document.getElementById('summaryResult').innerText = data.summary || "No summary returned.";
    } catch(err) {
        showCreativeError('summaryResult');
        console.error(err);
    }
}

async function generateFlashcards(){
    try {
        const text = document.getElementById('manualText').value;
        const formData = new FormData();
        formData.append('text', text);

        const res = await fetch(`${BASE_URL}/flashcards`, {method:'POST', body:formData});
        if(!res.ok) throw new Error("Network response not ok");
        const data = await res.json();

        const container = document.getElementById('flashcardsResult');
        container.innerHTML = '';
        (data.flashcards || "").split("\n\n").forEach(f => {
            if(f.trim()){
                const div = document.createElement('div');
                div.classList.add('card-item');
                div.innerText = f;
                container.appendChild(div);
            }
        });
        if(!data.flashcards) showCreativeError('flashcardsResult');
    } catch(err) {
        showCreativeError('flashcardsResult');
        console.error(err);
    }
}

async function askQuestion(){
    try {
        const text = document.getElementById('manualText').value;
        const question = document.getElementById('userQuestion').value;
        const formData = new FormData();
        formData.append('text', text);
        formData.append('question', question);

        const res = await fetch(`${BASE_URL}/qa`, {method:'POST', body:formData});
        if(!res.ok) throw new Error("Network response not ok");
        const data = await res.json();
        document.getElementById('qaResult').innerText = data.answer || "";
        if(!data.answer) showCreativeError('qaResult');
    } catch(err) {
        showCreativeError('qaResult');
        console.error(err);
    }
}

async function generateQuiz(){
    try {
        const text = document.getElementById('manualText').value;
        const formData = new FormData();
        formData.append('text', text);

        const res = await fetch(`${BASE_URL}/quiz`, {method:'POST', body:formData});
        if(!res.ok) throw new Error("Network response not ok");
        const data = await res.json();

        const container = document.getElementById('quizResult');
        container.innerHTML = '';
        (data.quiz || "").split("\n\n").forEach(q => {
            if(q.trim()){
                const div = document.createElement('div');
                div.classList.add('card-item');
                div.innerText = q;
                container.appendChild(div);
            }
        });
        if(!data.quiz) showCreativeError('quizResult');
    } catch(err) {
        showCreativeError('quizResult');
        console.error(err);
    }
}

// --- Download PDF (unchanged) ---
function downloadPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    const text = document.getElementById('manualText').value || "No notes available.";
    const lines = doc.splitTextToSize(text, 180);
    doc.text(lines, 15, 20);
    doc.save("StudyNotes.pdf");
}
