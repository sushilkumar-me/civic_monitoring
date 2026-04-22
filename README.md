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

## 📖 What is the Civic Monitoring System?

City administrators often struggle to track and prioritize urgent infrastructural issues like open manholes, severely damaged roads, or public hazards. The **Civic Monitoring System** is a full-stack web application designed to solve this problem by providing a direct pipeline between on-the-ground field surveyors, city resolution engineers, and global administrators.

Instead of relying solely on manual reporting, this platform utilizes **State-of-the-art Computer Vision** (Google Gemini 2.0 Flash and Ultralytics YOLOv8) to automatically analyze images uploaded from the field. It instantaneously identifies the issue type, evaluates the risk level, and flags critical dangers for immediate engineer dispatch.

---

## 🔄 How It Works (The Complete Workflow)

The system is built around a secure, role-based workflow designed for maximum efficiency:

1. **Field Reporting (Surveyor Role):**
   A Surveyor in the field encounters a problem (e.g., a massive pothole). They open the web app, take a picture, and upload it with their GPS coordinates. 

2. **AI Triage & Categorization (Backend):**
   The moment the image is uploaded, the backend sends the image to the **Gemini Vision AI Engine**. The AI analyzes the pixels, identifies the object ("Pothole"), gives a technical reasoning, and assigns a priority ("Critical"). *(If Gemini is unavailable, our internal `yolov8s` locally-hosted model acts as a fallback detector).*

3. **Task Assignment (Engineer Role):**
   City Engineers log into their dashboards and see a grid of all "Open" issues in their assigned wards. They can click **Navigate** to open Google Maps directly to the problem's exact GPS coordinates.

4. **Resolution Verification:**
   Once fixed, the Engineer uploads an "After" resolution photo. The system securely locks the ticket as "Closed".

5. **Macro Oversight (Admin Role):**
   City Administrators access a protected high-level overview detailing exactly how many issues are Open vs. Closed, which wards have the worst response times, and the total ratio of resolved hazards.

---

## ✨ Key Features & Architecture

- **🤖 Automated AI Triage**: Zero manual entry for issue types. The computer vision model determines the threat.
- **📍 Geolocation Routing**: Automatic generation of Google Maps navigation URLs based on latitude/longitude variables embedded in the surveyor's request.
- **🔐 Secure Lifecycle**: Employs Role-based Access Control (RBAC) with secure email OTP verification via SMTP and encrypted passwords using `bcrypt`.
- **📊 Interactive Glassmorphism UI**: The frontend utilizes modern UI standards featuring dynamic animated particles and glass-panel CSS (`/static/style.css`).

## 🛠️ Technology Breakdown

The codebase is strictly separated into a modular architecture:

| Tier | Technologies Used | Purpose |
| --- | --- | --- |
| **Frontend** | HTML5, CSS3, Jinja2 | Renders dynamic dashboards instantly from the server. Extensively utilizes Template context injection. |
| **Backend Core** | FastAPI, Uvicorn, Python 3.11 | Provides ultra-fast async HTTP routing. Connects AI logic to the user database. |
| **Database** | PostgreSQL, SQLAlchemy | Object-Relational Mapping (ORM) to handle `User` and `Issue` schemas robustly. |
| **AI Layer** | Gemini 2.0 API, OpenCV, YOLO | Generates the actual classification confidence ratios and safety hazard definitions. |

---

## 🚀 Live Deployment to Render

This repository is Infrastructure-as-Code (IaC) ready and can be instantly hosted in the cloud.

1. Ensure this codebase is pushed to your GitHub repository.
2. Log into [Render](https://dashboard.render.com/) and click **New > Blueprint**.
3. Connect your repository. Render will read the `render.yaml` file in the root folder and automatically provision:
   - A Managed **PostgreSQL Database**
   - A Python **Web Service** running Gunicorn and Uvicorn.
4. Once deployed, add your private environment variables in the Render Dashboard under your Web Service:
   - `RENDER=true` (Forces HTTPS secure cookies)
   - `GEMINI_API_KEY=your_key` (Required for AI Vision classification)
   - `SMTP_EMAIL=your_email@gmail.com` (Your system email address)
   - `SMTP_PASSWORD=your_16_digit_app_password` (Your generated app password)

> [!TIP]
> The database schema generates itself automatically. However, to create your first Administrator account, connect to the Render PostgreSQL instance using DBeaver or pgAdmin (using the Render connection URL) and execute the `INSERT` commands found in `DB.txt`.

---

## 💻 Local Developer Guide

If you wish to clone this system or contribute code, follow these steps:

### 1. Database Setup
Create a local Postgres database named `civic_monitoring`. Execute the contents of `DB.txt` to inject the initial SQL schema. Verify that your connection string in `backend/database.py` matches your local Postgres credentials.

### 2. Virtual Environment
Clone the repository and initialize a Python 3.11 virtual environment:

```bash
# Initialize venv
python -m venv venv

# Activate venv (Windows)
venv\Scripts\activate
# Activate venv (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
Install the required packages. Note that `requirements-deploy.txt` strictly enforces CPU-only PyTorch to prevent massive GPU binaries from crashing standard developer machines.

```bash
pip install -r backend/requirements-deploy.txt
```

### 4. Run the Engine
Boot up the local Uvicorn development server:

```bash
cd backend
uvicorn main:app --reload
```
Navigate your browser to `http://127.0.0.1:8000` to access the portal!

---
<div align="center">
  <p>Built for a Better City 🌆</p>
</div>
