# 🚀 CodeReviewer AI

### AI-Powered Code Review & Pull Request Analysis Platform

CodeReviewer AI is a full-stack application that automatically analyzes GitHub repositories and pull requests using AI-driven review agents. It helps developers identify bugs, code smells, security concerns, and maintainability issues before merging code.

---

## ✨ Key Features

🔍 Automated Pull Request Analysis

🤖 AI-Powered Code Review Suggestions

📊 Repository Health & Review Dashboard

🔐 Secure Authentication System

⚡ FastAPI REST APIs

🧠 Multi-Agent Review Architecture

🔄 GitHub Webhook Integration

📈 Review Tracking & Management

---

## 🏗️ Architecture

```text id="xaqh4h"
GitHub Repository
        │
        ▼
 GitHub Webhook
        │
        ▼
 FastAPI Backend
        │
 ┌──────┼──────┐
 ▼      ▼      ▼
AI Agent Security Agent Quality Agent
        │
        ▼
 Review Engine
        │
        ▼
 React Dashboard
```

---

## 🛠️ Tech Stack

| Category    | Technologies            |
| ----------- | ----------------------- |
| Frontend    | React, Vite, JavaScript |
| Backend     | FastAPI, Python         |
| Database    | SQLAlchemy, Alembic     |
| AI Layer    | AI Review Agents        |
| Memory      | ChromaDB                |
| Async Tasks | Celery                  |
| DevOps      | Docker, GitHub Actions  |

---

## 📂 Project Structure

```text id="h8h8o6"
codereviewer
├── backend
├── frontend
├── migrations
└── .github/workflows
```

---

## 🚀 Getting Started

### Clone Repository

```bash id="zh9t7m"
git clone https://github.com/arundharwad-26/codereviewer.git
cd codereviewer
```

### Backend

```bash id="wz0e4g"
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash id="yfy4h7"
cd frontend
npm install
npm run dev
```

---

## 🎯 Future Enhancements

* AI Severity Scoring
* Code Quality Metrics
* Team Collaboration
* Cloud Deployment
* Advanced Security Analysis

---

## 👨‍💻 Author

**Arun B Dharwad**

GitHub: https://github.com/arundharwad-26
