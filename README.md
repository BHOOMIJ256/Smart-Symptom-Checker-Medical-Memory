# Smart Health AI


AI-powered Symptom Checker & Medical Memory Platform
Multimodal input, intelligent diagnosis, and seamless patient history management.


## Features

1. **Symptom Analysis**: AI-powered, context-aware symptom checking using LLMs (OpenAI GPT-4, Google Gemini, etc).

2. **Medical Memory**: Securely store and retrieve patient medical history using vector databases (FAISS).

3. **Multimodal Input**: Upload and analyze text, speech (voice-to-text), images, and PDF medical records.

4. **Intelligent Diagnosis**: Get probable diagnoses with confidence scores and actionable recommendations.

5. **Document Management**: Upload, view, and delete medical documents with a user-friendly dashboard.

6. **Similar Case Search**: Instantly find past cases similar to a query using semantic search (vector similarity).

7. **Modern UI**:  Responsive, mobile-friendly React frontend.

8. **RESTful API**: FastAPI backend with clear, documented endpoints.


## System Architecture

<img width="915" height="284" alt="image" src="https://github.com/user-attachments/assets/2c18dcbc-898e-4385-9a3b-d8e75e4523b4" />

<img width="905" height="271" alt="image" src="https://github.com/user-attachments/assets/ba3699d1-445e-42e5-a60d-21af59e91d6e" />



---

## Quickstart

### 1. Backend Setup

*  **Python Version:** 3.10 or 3.11 recommended (not 3.13)

*  Create & Activate Virtual Environment: 

        git clone https://github.com/BHOOMIJ256/Smart-Symptom-Checker-Medical-Memory.git
        cd smart-health-ai

* **Install Dependencies**:

  
      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate

*  **Environment Variables**:

   Copy .env.example to .env and set your OpenAI/HuggingFace keys if needed.

* **Run Backend**:
  
      pip install -r requirements.txt

The backend will start at http://localhost:8000.

### 2. Frontend Setup

* python run_backend.py

* The frontend will run at http://localhost:3000.

## 🧩 Key Technologies

**1. Frontend**: React, Material-UI, CSS Modules

**2. Backend**: FastAPI, Python, OpenAI, FAISS, PyMuPDF, Whisper, Tesseract OCR

**3. Data:** JSON storage, uploads folder for files

**4. AI/ML**: LLMs, Whisper (speech-to-text), OCR, vector search

## 🗂️ Project Structure

    cd smart-health-frontend
    npm install
    npm start

## Usage

*  **Register/Login**: Create a user account.

*  **Upload Documents**: Add PDFs or images to your medical history.

*  **Speech-to-Text**: Record symptoms using your voice.

*  **Symptom Checker** : Get AI-powered health insights.

*  **Delete Documents**: Remove unwanted records from your dashboard.

*  **Search Similar Cases**: Find past cases similar to your query for better diagnosis and decision support.

*  **API Documentation:** Swagger/OpenAPI docs for all endpoints.

## Mobile-Friendly UI

*  The dashboard and all components are fully responsive.

*  Optimized for both desktop and mobile devices.


## 🛠️ Troubleshooting


**1. Python Version Issues**:

Use Python 3.10 or 3.11 for best compatibility.

**2. Dependency Conflicts**:

If you see pip errors, check requirements.txt for pinned versions.

**3. CORS/Proxy Issues**:

The frontend uses a proxy to connect to the backend. Ensure "proxy": "http://localhost:8000" is set in smart-health-frontend/package.json.

**4. File Upload/Deletion**:

If files don't appear or delete, check backend logs and data/documents.json.

**5. Tesseract Not Found:**

Ensure Tesseract is installed and its path is added to your system's PATH variable.


## Challenges Faced

**1. Dependency Conflicts:**
Managing Python package versions (e.g., openai, huggingface_hub, PyMuPDF) to avoid incompatibilities.

**2. File Handling:**
Ensuring file pointers are reset after reading uploads to prevent "empty document" errors.

**3. OCR Limitations:**
Tesseract struggles with handwritten prescriptions; may require advanced OCR or preprocessing.

**4. Speech-to-Text Accuracy:**
Whisper model accuracy varies with audio quality; device compatibility and model loading required careful handling.

**5. Frontend/Backend Integration:**
CORS, proxy, and API path issues needed to be resolved for smooth communication.

**6. Data Consistency:**
Ensuring JSON storage is robust and concurrent-safe for user, document, and diagnosis data.


## Future Enhancements

> **Cloud Database Integration:**
Move from JSON files to a scalable database (e.g., PostgreSQL, MongoDB).

> **Advanced OCR:**
Integrate handwriting-optimized OCR (e.g., EasyOCR, Google Vision API).

> **Role-Based Access:**
Add admin/doctor/patient roles with different permissions.

> **Analytics Dashboard:**
Visualize trends, outcomes, and usage statistics.

> **Internationalization:**
Support for multiple languages.

> **Security Improvements:**
OAuth2, JWT authentication, and encrypted storage.

> **Unit & Integration Tests:**
Expand test coverage for reliability.


## Demo Video
<video width="100%" controls>
  <source src="https://github.com/BHOOMIJ256/Smart-Symptom-Checker-Medical-Memory/blob/main/Demo_comp.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>


