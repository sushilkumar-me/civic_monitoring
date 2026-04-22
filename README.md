<div align="center">
  <h1>🏛️ Civic Monitoring System</h1>
  <p><i>An intelligent urban issue tracking platform powered by AI computer vision.</i></p>

  <!-- Badges -->
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white" alt="FastAPI"/></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/></a>
  <a href="https://ai.google.dev/"><img src="https://img.shields.io/badge/Gemini_AI-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini Vision"/></a>
  <a href="https://render.com/"><img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white" alt="Render"/></a>
</div>

<br/>

## 📖 Overview

The **Civic Monitoring System** bridges the gap between citizens, surveyors, and city engineers. By leveraging modern web frameworks and advanced AI (Google Gemini Vision + YOLOv8 fallback), the platform automates the detection, categorization, and prioritization of urban infrastructure hazards — from life-threatening open manholes to stray cattle on highways.

---

## ✨ Key Features

- **🤖 Automated AI Triage**: Upload an image of an issue, and our vision models instantly classify the hazard type, assess the severity (Low to Critical), and provide technical reasoning.
- **📍 Geolocation Routing**: Integrated GPS coordinates and Google Maps one-click navigation for engineers.
- **🔐 Secure Access**: Role-based access control (RBAC) with secure email OTP verification and encrypted passwords using `bcrypt`.
- **📊 Real-time Dashboard**: Live statistical breakdown for City Administrators to monitor ward-by-ward performance and resolution rates.
- **☁️ Cloud Ready**: One-click deployment instructions structured perfectly for Render's Infrastructure-as-Code ecosystem (`render.yaml`).

## 🛠️ Technology Stack

| Component | Technology |
| --- | --- |
| **Backend Framework** | FastAPI, Uvicorn, Gunicorn |
| **Database & ORM** | PostgreSQL, SQLAlchemy |
| **Frontend Rendering** | Jinja2 Templates, HTML5, Vanilla CSS |
| **AI Computer Vision** | Google Generative AI (Gemini 2.0 Flash), Ultralytics YOLOv8 |
| **Authentication** | Direct Bcrypt Hashing, Session Middleware, SMTP OTP |

---

## 👥 User Roles

The platform revolves around three core operational roles:

1. 📱 **Surveyor (`surveyor`)**: Operates in the field. Captures and uploads images of civic anomalies along with their GPS coordinates.
2. 🦺 **Engineer (`engineer`)**: Reviews assigned issues, utilizes GPS to navigate directly to the site, and uploads resolution "after" photos to close tickets.
3. 🛡️ **Administrator (`admin`)**: Accesses the global overview console capable of deleting fraudulent reports and viewing macro-resolution statistics.

---

## 🚀 Live Deployment to Render

This repository is built for instant cloud hosting using Render Blueprints. 

1. Ensure this codebase is pushed to your GitHub repository.
2. Log into [Render](https://dashboard.render.com/) and click **New > Blueprint**.
3. Connect your repository. Render will automatically provision:
   - A Managed **PostgreSQL Database**
   - A Python **Web Service**
4. Once deployed, add your private environment variables in the Render Dashboard:
   - `RENDER=true` (Forces HTTPS security)
   - `GEMINI_API_KEY=your_key` (Required for AI Vision)
   - `SMTP_EMAIL=your_email@gmail.com`
   - `SMTP_PASSWORD=your_16_digit_app_password`

> [!TIP]
> The database schema generates itself automatically! However, to create your first Administrator account, connect to the Render PostgreSQL instance using DBeaver or pgAdmin and execute the `INSERT` commands found in `DB.txt`.

---

## 💻 Local Development Setup

If you wish to run the civic monitoring system on your personal machine for development:

### 1. Database Setup
Create a local Postgres database named `civic_monitoring`. Execute the contents of `DB.txt` to inject the initial SQL schema. Verify that your connection string in `backend/database.py` matches your local credentials.

### 2. Environment Setup
Clone the repository and initialize a virtual environment:

```bash
# Initialize venv
python -m venv venv

# Activate venv (Windows)
venv\Scripts\activate
# Activate venv (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
Install the required packages. Note that we strictly enforce CPU-only PyTorch by default to prevent large GPU binaries from bloating the system unnecessarily on web servers.

```bash
pip install -r backend/requirements-deploy.txt
```

### 4. Run the Engine
Boot up the local Uvicorn server:

```bash
cd backend
uvicorn main:app --reload
```
Navigate to `http://127.0.0.1:8000` to access the portal!

---
<div align="center">
  <p>Built for a Better City 🌆</p>
</div>
