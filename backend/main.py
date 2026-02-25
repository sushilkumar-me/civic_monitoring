from fastapi import FastAPI, UploadFile, Form, Depends, Request, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pathlib import Path
import shutil

from starlette.middleware.sessions import SessionMiddleware

from database import SessionLocal, engine
import models, crud
from ai_detector import detect_issue
from auth import hash_password, verify_password, generate_otp, otp_expiry, is_otp_valid, send_otp_email

from fastapi.templating import Jinja2Templates
from sqlalchemy import func


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "frontend" / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="civic-monitor-secret-key-2026-change-in-prod")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Auth Helpers ──

def get_current_user(request: Request, db: Session):
    """Get current logged-in user from session, or None."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(models.User).filter(models.User.id == user_id).first()

def require_login(request: Request):
    """Redirect to login if not authenticated."""
    if not request.session.get("user_id"):
        return RedirectResponse("/", status_code=302)
    return None


# ══════════════════════════════════════
#   AUTH ROUTES
# ══════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    # If already logged in, redirect to dashboard
    if request.session.get("user_id"):
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
def do_login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "No account found with this email"})

    if not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect password"})

    # Generate and send OTP
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expiry = otp_expiry()
    db.commit()

    email_sent = send_otp_email(user.email, otp)

    # Store pending user in session
    request.session["pending_user_id"] = user.id
    request.session["otp_email_sent"] = email_sent

    return RedirectResponse("/verify-otp", status_code=302)


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@app.post("/register")
def do_register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    ward: int = Form(...),
    db: Session = Depends(get_db)
):
    # Check if email exists
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Email already registered"})

    # Create user
    user = models.User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role,
        ward=ward,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate OTP
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expiry = otp_expiry()
    db.commit()

    email_sent = send_otp_email(user.email, otp)

    request.session["pending_user_id"] = user.id
    request.session["otp_email_sent"] = email_sent

    return RedirectResponse("/verify-otp", status_code=302)


@app.get("/verify-otp", response_class=HTMLResponse)
def verify_otp_page(request: Request, db: Session = Depends(get_db)):
    pending_id = request.session.get("pending_user_id")
    if not pending_id:
        return RedirectResponse("/", status_code=302)

    user = db.query(models.User).filter(models.User.id == pending_id).first()
    email_sent = request.session.get("otp_email_sent", False)

    # For demo: show OTP if email not configured
    demo_otp = user.otp_code if not email_sent else None

    return templates.TemplateResponse("verify_otp.html", {
        "request": request,
        "error": None,
        "email": user.email,
        "email_sent": email_sent,
        "demo_otp": demo_otp
    })

@app.post("/verify-otp")
def do_verify_otp(request: Request, otp: str = Form(...), db: Session = Depends(get_db)):
    pending_id = request.session.get("pending_user_id")
    if not pending_id:
        return RedirectResponse("/", status_code=302)

    user = db.query(models.User).filter(models.User.id == pending_id).first()

    if not user or user.otp_code != otp:
        email_sent = request.session.get("otp_email_sent", False)
        demo_otp = user.otp_code if not email_sent else None
        return templates.TemplateResponse("verify_otp.html", {
            "request": request,
            "error": "Invalid OTP. Please try again.",
            "email": user.email,
            "email_sent": email_sent,
            "demo_otp": demo_otp
        })

    if not is_otp_valid(user.otp_expiry):
        email_sent = request.session.get("otp_email_sent", False)
        demo_otp = user.otp_code if not email_sent else None
        return templates.TemplateResponse("verify_otp.html", {
            "request": request,
            "error": "OTP expired. Please resend.",
            "email": user.email,
            "email_sent": email_sent,
            "demo_otp": demo_otp
        })

    # Success — mark verified, log in
    user.is_verified = True
    user.otp_code = None
    user.otp_expiry = None
    db.commit()

    # Clear pending, set logged in
    request.session.pop("pending_user_id", None)
    request.session.pop("otp_email_sent", None)
    request.session["user_id"] = user.id
    request.session["user_role"] = user.role
    request.session["user_name"] = user.name

    return RedirectResponse("/dashboard", status_code=302)


@app.get("/resend-otp")
def resend_otp(request: Request, db: Session = Depends(get_db)):
    pending_id = request.session.get("pending_user_id")
    if not pending_id:
        return RedirectResponse("/", status_code=302)

    user = db.query(models.User).filter(models.User.id == pending_id).first()
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expiry = otp_expiry()
    db.commit()

    email_sent = send_otp_email(user.email, otp)
    request.session["otp_email_sent"] = email_sent

    return RedirectResponse("/verify-otp", status_code=302)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)


@app.get("/dashboard")
def dashboard(request: Request):
    role = request.session.get("user_role")
    if not role:
        return RedirectResponse("/", status_code=302)
    if role == "surveyor":
        return RedirectResponse("/surveyor", status_code=302)
    if role == "engineer":
        return RedirectResponse("/engineer", status_code=302)
    return RedirectResponse("/admin", status_code=302)


# ══════════════════════════════════════
#   PROTECTED ROUTES
# ══════════════════════════════════════

@app.get("/surveyor", response_class=HTMLResponse)
def surveyor(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    return (TEMPLATE_DIR / "surveyor.html").read_text(encoding="utf-8")

@app.post("/report")
def report_issue(
    request: Request,
    latitude: str = Form(None),
    longitude: str = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    redirect = require_login(request)
    if redirect:
        return redirect

    if not image.filename:
        return {"error": "No image uploaded"}, 400

    # Ensure coords are floats or default to a fixed point if invalid
    try:
        lat_f = float(latitude) if latitude else 22.30
        lon_f = float(longitude) if longitude else 70.80
    except (ValueError, TypeError):
        lat_f = 22.30
        lon_f = 70.80

    image_path = UPLOAD_DIR / image.filename
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    issue_type, priority, confidence, reasoning = detect_issue(str(image_path))
    ward = crud.detect_ward(lat_f, lon_f)

    issue = models.Issue(
        issue_type=issue_type,
        priority=priority,
        ward=ward,
        before_image=image.filename,
        latitude=lat_f,
        longitude=lon_f,
        ai_confidence=confidence,
        ai_reasoning=reasoning,
        status="OPEN"
    )

    db.add(issue)
    db.commit()

    return {"message": "Issue reported successfully"}

@app.get("/engineer", response_class=HTMLResponse)
def engineer(request: Request, db: Session = Depends(get_db)):
    redirect = require_login(request)
    if redirect:
        return redirect

    issues = db.query(models.Issue).filter(models.Issue.status != "CLOSED").all()

    html = (TEMPLATE_DIR / "engineer.html").read_text(encoding="utf-8")
    rows = ""

    for i in issues:
        if i.latitude is not None and i.longitude is not None:
            maps_link = f"https://www.google.com/maps/dir/?api=1&destination={i.latitude},{i.longitude}"
        else:
            maps_link = "#"

        if i.status == "OPEN":
            status_badge = '<span class="badge badge-open">🔓 Open</span>'
            action_html = f"""
            <form action="/start/{i.id}" method="post">
                <button class="btn btn-primary" style="width:100%;">▶ Start Work</button>
            </form>
            """
        elif i.status == "IN_PROGRESS":
            status_badge = '<span class="badge badge-progress">🔄 In Progress</span>'
            action_html = f"""
            <form action="/close/{i.id}" method="post" enctype="multipart/form-data">
                <div class="file-input-wrap">
                    <input type="file" name="image" required class="file-input">
                    <button class="btn btn-green" style="width:100%;">✅ Mark Resolved</button>
                </div>
            </form>
            """
        else:
            status_badge = '<span class="badge badge-closed">✅ Closed</span>'
            action_html = ""

        rows += f"""
        <div class="issue-card glass">
            <div class="issue-img-wrap">
                <img src="/static/uploads/{i.before_image}" class="issue-img" alt="Issue image">
                <div class="issue-img-overlay"></div>
            </div>
            <div class="issue-body">
                <div class="issue-header">
                    <span class="issue-type">{i.issue_type}</span>
                    {status_badge}
                </div>
                <span class="issue-ward">📍 Ward {i.ward}</span>
                <div class="issue-actions">
                    <a href="{maps_link}" target="_blank" class="btn btn-nav">📍 Navigate</a>
                </div>
                {action_html}
            </div>
        </div>
        """

    return html.replace("{{ROWS}}", rows)


@app.post("/close/{issue_id}")
def close_issue(request: Request, issue_id: int, image: UploadFile = Form(...), db: Session = Depends(get_db)):
    redirect = require_login(request)
    if redirect:
        return redirect

    image_path = UPLOAD_DIR / image.filename
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    issue = db.query(models.Issue).get(issue_id)
    issue.after_image = image.filename
    issue.status = "CLOSED"
    db.commit()

    return RedirectResponse("/engineer", 302)

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request, db: Session = Depends(get_db)):
    redirect = require_login(request)
    if redirect:
        return redirect

    issues = db.query(models.Issue).all()

    total = len(issues)
    open_count = sum(1 for i in issues if i.status == "OPEN")
    closed_count = sum(1 for i in issues if i.status == "CLOSED")
    critical_count = sum(
        1 for i in issues if i.issue_type in ["Stray Cattle", "Open Manhole"]
    )

    ward_stats = []
    wards = set(i.ward for i in issues)
    for w in wards:
        ward_issues = [i for i in issues if i.ward == w]
        ward_stats.append({
            "ward": w,
            "total": len(ward_issues),
            "open": sum(1 for i in ward_issues if i.status == "OPEN"),
            "closed": sum(1 for i in ward_issues if i.status == "CLOSED")
        })

    type_stats = {}
    for i in issues:
        type_stats[i.issue_type] = type_stats.get(i.issue_type, 0) + 1

    type_stats_list = [
        {"issue_type": k, "count": v} for k, v in type_stats.items()
    ]

    response = templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "total": total,
            "open_count": open_count,
            "closed_count": closed_count,
            "critical_count": critical_count,
            "ward_stats": ward_stats,
            "type_stats": type_stats_list,
            "issues": issues
        }
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.post("/start/{issue_id}")
def start_issue(request: Request, issue_id: int, db: Session = Depends(get_db)):
    redirect = require_login(request)
    if redirect:
        return redirect

    issue = db.query(models.Issue).get(issue_id)
    issue.status = "IN_PROGRESS"
    db.commit()
    return RedirectResponse("/engineer", 302)

@app.post("/delete_issue/{issue_id}")
def delete_issue(request: Request, issue_id: int, db: Session = Depends(get_db)):
    redirect = require_login(request)
    if redirect:
        return redirect

    user = get_current_user(request, db)
    user_name = user.name if user else "Unknown"
    
    # Use direct query to ensure deletion and get affected rows
    query = db.query(models.Issue).filter(models.Issue.id == issue_id)
    affected_rows = query.delete(synchronize_session='fetch')
    db.commit()
    
    print(f"DEBUG: Admin {user_name} (ID: {request.session.get('user_id')}) attempted to delete Issue ID {issue_id}. Affected rows: {affected_rows}")

    if affected_rows > 0:
        return {"message": f"Issue #{issue_id} deleted successfully"}
    
    return JSONResponse(status_code=404, content={"error": f"Issue #{issue_id} not found"})
