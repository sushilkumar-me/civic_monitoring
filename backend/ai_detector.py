import google.generativeai as genai
from pathlib import Path
import json
import os

# ── Gemini Vision API Configuration ──
# Set your API key as an environment variable: GEMINI_API_KEY
# Get a free key at: https://aistudio.google.com/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

_gemini_model = None

CIVIC_ISSUE_PROMPT = """You are an expert AI system for civic infrastructure monitoring.
Analyze this image and classify the civic issue shown.

You MUST respond with ONLY a valid JSON object (no markdown, no extra text):

{
  "issue_type": "<one of: Pothole, Garbage Dump, Stray Cattle, Open Manhole, Road Obstruction, Waterlogging, Broken Streetlight, Illegal Construction, Damaged Road, Sewage Overflow, Fallen Tree, Traffic Violation, Unauthorized Parking, General Civic Issue>",
  "priority": "<one of: Critical, High, Medium, Low>",
  "confidence": <0-100>,
  "description": "<brief 1-line description of what you see>"
}

Priority guide:
- Critical: Immediate danger to life (Open Manhole, Stray Cattle on road, Sewage Overflow)
- High: Major inconvenience or safety risk (Pothole, Road Obstruction, Waterlogging, Fallen Tree)
- Medium: Moderate issue (Garbage Dump, Damaged Road, Unauthorized Parking)
- Low: Minor issue (Broken Streetlight, General Civic Issue)

Be accurate. If the image does not show a clear civic issue, classify as "General Civic Issue" with Low priority.
"""


def _get_gemini_model():
    """Lazy-load and cache the Gemini model."""
    global _gemini_model
    if _gemini_model is None:
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel("gemini-2.0-flash")
    return _gemini_model


def _detect_with_gemini(image_path: str):
    """Use Gemini Vision API for high-accuracy civic issue detection."""
    model = _get_gemini_model()

    # Upload image to Gemini
    img_file = genai.upload_file(image_path)

    # Generate classification
    response = model.generate_content(
        [CIVIC_ISSUE_PROMPT, img_file],
        generation_config=genai.types.GenerationConfig(
            temperature=0.1,  # Low temperature for consistent classification
            max_output_tokens=300,
        ),
    )

    # Parse JSON response
    text = response.text.strip()
    # Handle potential markdown code block wrapping
    if text.startswith("```"):
        text = text.split("\n", 1)[1]  # Remove first line (```json)
        text = text.rsplit("```", 1)[0]  # Remove last ```
        text = text.strip()

    result = json.loads(text)

    issue_type = result.get("issue_type", "General Civic Issue")
    priority = result.get("priority", "Medium")
    confidence = result.get("confidence", 0)
    description = result.get("description", "")

    print(f"[Gemini AI] Detected: {issue_type} | Priority: {priority} | "
          f"Confidence: {confidence}% | {description}")

    return issue_type, priority


# ── YOLO Fallback ──
_yolo_model = None

def _load_yolo():
    """Load YOLOv8 as fallback detector."""
    global _yolo_model
    if _yolo_model is None:
        from ultralytics import YOLO
        _yolo_model = YOLO("yolov8n.pt")
    return _yolo_model


def _detect_with_yolo(image_path: str):
    """Fallback: basic YOLO detection for when Gemini is unavailable."""
    import cv2
    model = _load_yolo()
    img = cv2.imread(image_path)

    if img is None:
        return "Unknown Issue", "Normal"

    results = model(img, conf=0.4, verbose=False)

    for r in results:
        for box in r.boxes:
            label = model.names[int(box.cls[0])].lower()
            if "cow" in label or "horse" in label or "sheep" in label:
                return "Stray Cattle", "Critical"
            if "car" in label or "truck" in label or "bus" in label:
                return "Road Obstruction", "High"
            if "dog" in label or "cat" in label:
                return "Stray Animal", "Medium"

    return "General Civic Issue", "Medium"


# ── Main Entry Point ──
def detect_issue(image_path: str):
    """
    Detect civic issue from image using Gemini Vision API.
    Falls back to YOLO if Gemini is unavailable or API key is not set.
    """
    # Try Gemini first (high accuracy)
    if GEMINI_API_KEY:
        try:
            return _detect_with_gemini(image_path)
        except Exception as e:
            print(f"[Gemini AI] Error: {e}. Falling back to YOLO...")

    # Fallback to YOLO
    print("[AI Detector] Using YOLO fallback (set GEMINI_API_KEY for better accuracy)")
    return _detect_with_yolo(image_path)
