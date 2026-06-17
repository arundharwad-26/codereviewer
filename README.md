# 🚀 CodeReviewer AI

<div align="center">

### Intelligent Pull Request Analysis & AI-Powered Code Review Platform

Analyze repositories, review pull requests, detect code quality issues, and generate actionable feedback using AI-driven review agents.

**FastAPI • React • ChromaDB • Celery • Docker • GitHub Actions**

</div>

---

## 🌟 Overview

CodeReviewer AI is a modern full-stack platform designed to automate code review workflows. The system integrates with GitHub repositories, analyzes pull requests, evaluates code quality, and generates intelligent review suggestions to help development teams improve software quality and reduce manual review effort.

### Why This Project?

Traditional code reviews are time-consuming and inconsistent. CodeReviewer AI introduces an automated review pipeline that assists developers by identifying:

* 🔍 Code Quality Issues
* 🛡️ Security Concerns
* ⚠️ Potential Bugs
* 📈 Maintainability Problems
* 💡 Improvement Suggestions

---

## ✨ Core Features

### 🤖 AI Review Engine

* Automated code analysis
* Intelligent review generation
* Multi-agent architecture

### 🔗 GitHub Integration

* Repository management
* Pull request tracking
* Webhook support

### 📊 Review Dashboard

* Review history
* Repository insights
* Status monitoring

### ⚡ Scalable Backend

* FastAPI REST APIs
* Async task processing with Celery
* Database migration support using Alembic

### 🎨 Modern Frontend

* React + Vite
* Responsive UI
* Interactive review experience

---

## 🏗️ System Architecture

```text
Developer Pushes Code
          │
          ▼
     GitHub Repo
          │
          ▼
    GitHub Webhook
          │
          ▼
     FastAPI Server
          │
 ┌────────┼────────┐
 │        │        │
 ▼        ▼        ▼
Code   Security  Quality
Agent   Agent     Agent
 │        │        │
 └────────┴────────┘
          │
          ▼
   Review Orchestrator
          │
          ▼
    Review Database
          │
          ▼
    React Dashboard
```

---

## 🛠️ Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* Celery
* ChromaDB

### Frontend

* React
* Vite
* JavaScript
* CSS

### DevOps

* Docker
* GitHub Actions
* CI/CD Pipelines

### Database & Storage

* SQL Database
* ChromaDB Vector Storage

---

## 📂 Project Structure

```text
codereviewer/
│
├── backend/
│   ├── app/
│   ├── migrations/
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── .github/
│   └── workflows/
│
└── README.md
```

---

## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/arundharwad-26/codereviewer.git
cd codereviewer
```

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 🎯 Future Enhancements

* AI Severity Scoring
* Advanced Security Review Agent
* Team Collaboration Features
* Cloud Deployment
* Real-Time Notifications
* Repository Analytics Dashboard

---

## 👨‍💻 Developer

### Arun B Dharwad

MCA Student | Python Developer | Data Science Enthusiast

* GitHub: https://github.com/arundharwad-26
* Interests: Python Development, AI, Machine Learning, Data Science

---

⭐ If you found this project useful, consider giving it a star.
