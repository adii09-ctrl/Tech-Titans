from flask import Flask, request, jsonify, render_template  # type: ignore
import os
import re
import firebase_admin  # type: ignore
from firebase_admin import credentials, storage, firestore  # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore
import pdfplumber  # type: ignore
from docx import Document  # type: ignore
from io import BytesIO

app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate("firebase_credentials.json")  # Ensure this file exists
firebase_admin.initialize_app(cred, {'storageBucket': 'your-firebase-bucket.appspot.com'})
db = firestore.client()  # Firestore database client

# Define upload folder (optional)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class ResumeScanner:
    def __init__(self, job_descriptions):
        self.job_descriptions = job_descriptions
        self.resumes = []
        self.candidates = []  # Store candidate details

    def add_resume(self, resume_text, candidate_info):
        """Adds a resume and candidate details to the scanner."""
        self.resumes.append(resume_text)
        self.candidates.append(candidate_info)

    def preprocess_text(self, text):
        """Cleans and normalizes text for better comparison."""
        text = text.lower()
        text = re.sub(r'\W+', ' ', text)
        return text.strip()

    def rank_candidates(self):
        """Ranks resumes based on similarity to job descriptions."""
        if not self.resumes:
            return []

        processed_descriptions = [self.preprocess_text(desc) for desc in self.job_descriptions]
        processed_resumes = [self.preprocess_text(resume) for resume in self.resumes]

        # Vectorization
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(processed_descriptions + processed_resumes)

        rankings = []
        for i in range(len(processed_descriptions)):
            cosine_similarities = cosine_similarity(vectors[i:i+1], vectors[len(processed_descriptions):]).flatten()
            ranked_candidates = sorted(
                enumerate(cosine_similarities), key=lambda x: x[1], reverse=True
            )
            rankings.append(ranked_candidates)

        return rankings

def extract_text_from_resume(file, file_ext):
    """Extracts text from uploaded resume (PDF, DOCX, or TXT)."""
    if file_ext == 'pdf':
        with pdfplumber.open(BytesIO(file.read())) as pdf:
            return " ".join([page.extract_text() or "" for page in pdf.pages])

    elif file_ext == 'docx':
        doc = Document(BytesIO(file.read()))
        return " ".join([para.text for para in doc.paragraphs])

    elif file_ext == 'txt':
        return file.read().decode('utf-8')

    return None

@app.route('/upload', methods=['POST'])
def upload_resume():
    """Handles resume uploads, stores them in Firebase & Firestore, and ranks candidates."""
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    allowed_extensions = {'pdf', 'doc', 'docx', 'txt'}
    file_ext = file.filename.split('.')[-1].lower()

    if file_ext not in allowed_extensions:
        return jsonify({'error': 'Invalid file type. Only PDF, DOC, DOCX, and TXT are allowed.'}), 400

    # Get candidate details
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    job_position = request.form.get('jobPosition')
    job_description = request.form.get('jobDescription')

    try:
        # Extract text from the resume
        resume_text = extract_text_from_resume(file, file_ext)
        if not resume_text:
            return jsonify({'error': 'Failed to extract text from the resume'}), 400

        # Upload file to Firebase Storage
        bucket = storage.bucket()
        blob = bucket.blob(f"resumes/{file.filename}")
        file.seek(0)  # Reset file pointer
        blob.upload_from_file(file)
        resume_url = blob.public_url  # Get public URL for access

        # Store resume in scanner
        candidate_info = {
            "name": name,
            "email": email,
            "phone": phone,
            "job_position": job_position,
            "job_description": job_description,
            "resume_url": resume_url
        }
        scanner.add_resume(resume_text, candidate_info)

        # Store metadata in Firestore
        db.collection("resumes").add(candidate_info)

        # Rank candidates dynamically
        rankings = scanner.rank_candidates()

        return jsonify({
            'message': 'Resume uploaded and processed successfully',
            'resume_url': resume_url,
            'rankings': rankings,
            'candidate_info': candidate_info
        }), 200

    except Exception as e:
        return jsonify({'error': f'An error occurred during upload: {str(e)}'}), 500

@app.route('/rankings', methods=['GET'])
def get_rankings():
    """Retrieves rankings dynamically."""
    rankings = scanner.rank_candidates()
    return jsonify({'rankings': rankings})

@app.route('/')
def home():
    return render_template('htmlfile.HTML')

@app.route('/signup')
def signup():
    return render_template('_signup.html')

if __name__ == "__main__":
    job_descs = [
        "Looking for a software engineer with experience in Python and machine learning.",
        "Seeking a data analyst with strong SQL skills."
    ]
    scanner = ResumeScanner(job_descs)

    print("Flask server running...")
    app.run(debug=True)
