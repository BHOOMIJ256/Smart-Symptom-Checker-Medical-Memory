# 🚑 Smart Health AI

**AI-powered Symptom Checker & Medical Memory Platform**  
*Multimodal input, intelligent diagnosis, and seamless patient history management.*

---

## ✨ Features

- **Symptom Analysis:** AI-powered, context-aware symptom checking using LLMs (OpenAI GPT-4, Google Gemini, etc.)
- **Medical Memory:** Securely store and retrieve patient medical history using vector databases (FAISS).
- **Multimodal Input:** Upload and analyze text, speech (voice-to-text), images, and PDF medical records.
- **Intelligent Diagnosis:** Get probable diagnoses with confidence scores and actionable recommendations.
- **Document Management:** Upload, view, and delete medical documents with a user-friendly dashboard.
- **Modern UI:** Responsive, mobile-friendly React frontend.
- **RESTful API:** FastAPI backend with clear, documented endpoints.

---

## 🏗️ Architecture

```mermaid
flowchart LR
    A[React Frontend] -- REST API --> B[FastAPI Backend]
    B -- LLMs, Embeddings --> C[AI Services]
    B -- Vector Search --> D[Medical Memory (FAISS)]
    B -- File Storage --> E[Uploads]
```

---

## 🚀 Quickstart

### 1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/smart-health-ai.git
cd smart-health-ai
```

### 2. **Backend Setup**

- **Python Version:** 3.10 or 3.11 recommended (not 3.13)
- **Create & Activate Virtual Environment:**
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```
- **Install Dependencies:**
  ```bash
  pip install -r requirements.txt
  ```
- **Environment Variables:**  
  Copy `.env.example` to `.env` and set your OpenAI/HuggingFace keys if needed.

- **Run Backend:**
  ```bash
  python run_backend.py
  ```
  The backend will start at `http://localhost:8000`.

### 3. **Frontend Setup**

```bash
cd smart-health-frontend
npm install
npm start
```
The frontend will run at `http://localhost:3000`.

---

## 📱 Mobile-Friendly UI

- The dashboard and all components are fully responsive.
- Optimized for both desktop and mobile devices.

---

## 🧩 Key Technologies

- **Frontend:** React, CSS Modules, React Icons
- **Backend:** FastAPI, Python, OpenAI, FAISS, PyMuPDF, Whisper
- **Data:** JSON storage, uploads folder for files
- **AI/ML:** LLMs, Whisper (speech-to-text), OCR, vector search

---

## 🗂️ Project Structure

```
Smart_Health_AI/
  ├── backend/
  │   ├── main.py
  │   ├── services/
  │   └── models/
  ├── data/
  │   └── documents.json
  ├── uploads/
  ├── smart-health-frontend/
  │   ├── src/
  │   └── public/
  ├── requirements.txt
  └── README.md
```

---

**How to use:**  
- Replace `yourusername` and `your-email@example.com` with your actual GitHub username and contact email.
- Add a `LICENSE` file if you haven't already.

This README will make your project look professional, clear, and inviting on GitHub!  
Let me know if you want a custom badge, logo, or further tweaks.

---

## 📝 Usage

- **Register/Login:** Create a user account.
- **Upload Documents:** Add PDFs or images to your medical history.
- **Speech-to-Text:** Record symptoms using your voice.
- **Symptom Checker:** Get AI-powered health insights.
- **Delete Documents:** Remove unwanted records from your dashboard.

---

## 🛠️ Troubleshooting

- **Python Version Issues:**  
  Use Python 3.10 or 3.11 for best compatibility.
- **Dependency Conflicts:**  
  If you see pip errors, check `requirements.txt` for pinned versions.
- **CORS/Proxy Issues:**  
  The frontend uses a proxy to connect to the backend. Ensure `"proxy": "http://localhost:8000"` is set in `smart-health-frontend/package.json`.
- **File Upload/Deletion:**  
  If files don't appear or delete, check backend logs and `data/documents.json`.

---

## 🤝 Contributing

Pull requests are welcome!  
Please open an issue first to discuss major changes.

---

## 📄 License

[MIT License](LICENSE)

---

## 🙏 Acknowledgements

- OpenAI, HuggingFace, PyMuPDF, FAISS, FastAPI, React, and all open-source contributors.

---

## 📬 Contact

For questions, suggestions, or support, open an issue or contact [your-email@example.com](mailto:your-email@example.com).

---

*Made with ❤️ for better healthcare.*




