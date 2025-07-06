# Smart Health AI - Symptom Checker with Medical Memory

An AI-powered symptom checker system with medical memory, multimodal input support, and intelligent diagnosis suggestions.

# 🚀 Features


- **Symptom Analysis**: AI-powered symptom analysis using LLMs (OpenAI GPT-4, Google Gemini)
- **Medical Memory**: Store and retrieve patient medical history using vector databases
- **Multimodal Input**: Support for text, speech, images, and PDF medical records
- **Intelligent Diagnosis**: Probable diagnoses with confidence scores and recommendations
- **RESTful API**: FastAPI-based backend with comprehensive documentation

 # 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │───▶│  FastAPI Backend│───▶│  AI Services    │
│  (React/Web)    │    │                 │    │  (LLMs, Vector) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Medical Memory │
                       │  (Vector DB)    │
                       └─────────────────┘
```
# 📋 Prerequisites

- Python 3.8+
- Virtual environment (venv)
- API keys for OpenAI and/or Google Gemini (optional for development)




