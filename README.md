# 🚑 Smart Health AI


AI-powered Symptom Checker & Medical Memory Platform
Multimodal input, intelligent diagnosis, and seamless patient history management.


✨ Features

Symptom Analysis: AI-powered, context-aware symptom checking using LLMs (OpenAI GPT-4, Google Gemini, etc.)
Medical Memory: Securely store and retrieve patient medical history using vector databases (FAISS).
Multimodal Input: Upload and analyze text, speech (voice-to-text), images, and PDF medical records.
Intelligent Diagnosis: Get probable diagnoses with confidence scores and actionable recommendations.
Document Management: Upload, view, and delete medical documents with a user-friendly dashboard.
Similar Case Search: Instantly find past cases similar to a query using semantic search (vector similarity).
Modern UI: Responsive, mobile-friendly React frontend.
RESTful API: FastAPI backend with clear, documented endpoints.


🏗️ System Architecture

image.png

---

## 🚀 Quickstart

flowchart TD
    A["React Frontend (User Interface)"]
    B["FastAPI Backend (API & Logic)"]
    C["AI Services (LLMs, Embeddings, OCR, Whisper)"]
    D["Vector DB (FAISS)"]
    E["File Storage (Uploads)"]
    F["JSON Data Storage (User, Docs, Diagnoses)"]

    A -- "REST API" --> B
    B -- "LLMs, Embeddings" --> C
    B -- "Vector Search" --> D
    B -- "File Uploads" --> E
    B -- "User/Doc Data" --> F


2. Backend Setup
* Python Version: 3.10 or 3.11 recommended (not 3.13)

* Create & Activate Virtual Environmen

git clone https://github.com/yourusername/smart-health-ai.git
cd smart-health-ai

* Install Dependencies:
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate

*Environment Variables:
Copy .env.example to .env and set your OpenAI/HuggingFace keys if needed.

*Run Backend:
  pip install -r requirements.txt

The backend will start at http://localhost:8000.

3. Frontend Setup
  python run_backend.py

The frontend will run at http://localhost:3000.

🧩 Key Technologies
Frontend: React, Material-UI, CSS Modules
Backend: FastAPI, Python, OpenAI, FAISS, PyMuPDF, Whisper, Tesseract OCR
Data: JSON storage, uploads folder for files
AI/ML: LLMs, Whisper (speech-to-text), OCR, vector search

🗂️ Project Structure

cd smart-health-frontend
npm install
npm start

 Usage
Register/Login: Create a user account.
Upload Documents: Add PDFs or images to your medical history.
Speech-to-Text: Record symptoms using your voice.
Symptom Checker: Get AI-powered health insights.
Delete Documents: Remove unwanted records from your dashboard.
Search Similar Cases: Find past cases similar to your query for better diagnosis and decision support.

📱 Mobile-Friendly UI
The dashboard and all components are fully responsive.
Optimized for both desktop and mobile devices.


🛠️ Troubleshooting
Python Version Issues:
Use Python 3.10 or 3.11 for best compatibility.
Dependency Conflicts:
If you see pip errors, check requirements.txt for pinned versions.
CORS/Proxy Issues:
The frontend uses a proxy to connect to the backend. Ensure "proxy": "http://localhost:8000" is set in smart-health-frontend/package.json.
File Upload/Deletion:
If files don't appear or delete, check backend logs and data/documents.json.
Tesseract Not Found:
Ensure Tesseract is installed and its path is added to your system's PATH variable.


⚠️ Challenges Faced
Dependency Conflicts:
Managing Python package versions (e.g., openai, huggingface_hub, PyMuPDF) to avoid incompatibilities.
File Handling:
Ensuring file pointers are reset after reading uploads to prevent "empty document" errors.
OCR Limitations:
Tesseract struggles with handwritten prescriptions; may require advanced OCR or preprocessing.
Speech-to-Text Accuracy:
Whisper model accuracy varies with audio quality; device compatibility and model loading required careful handling.
Frontend/Backend Integration:
CORS, proxy, and API path issues needed to be resolved for smooth communication.
Data Consistency:
Ensuring JSON storage is robust and concurrent-safe for user, document, and diagnosis data.


🚀 Future Enhancements
Cloud Database Integration:
Move from JSON files to a scalable database (e.g., PostgreSQL, MongoDB).
Advanced OCR:
Integrate handwriting-optimized OCR (e.g., EasyOCR, Google Vision API).
Role-Based Access:
Add admin/doctor/patient roles with different permissions.
Analytics Dashboard:
Visualize trends, outcomes, and usage statistics.
Internationalization:
Support for multiple languages.
Security Improvements:
OAuth2, JWT authentication, and encrypted storage.
API Documentation:
Add Swagger/OpenAPI docs for all endpoints.
Unit & Integration Tests:
Expand test coverage for reliability.

