import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
import json
import os

# ── Gemini Vision API Configuration ──
# Set your API key as an environment variable: GEMINI_API_KEY
# Get a free key at: https://aistudio.google.com/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

_gemini_model = None

CIVIC_ISSUE_PROMPT = """You are a highly advanced Senior Urban Planner and AI Infrastructure Specialist.
Your task is to analyze civic monitoring imagery with extreme precision.

Step-by-Step Analysis Rubric:
1. IDENTIFY: List all visible objects related to urban infrastructure or public safety.
2. EVALUATE: Check for structural damage, safety hazards, environmental risks, or public obstruction.
3. CLASSIFY: Based on the "Issue Categories" below, choose the most accurate fit.
4. PRIORITIZE: Assign priority based on the immediate risk to citizens.

Issue Categories:
- Pothole (High risk for vehicles)
- Garbage Dump (Environmental hazard, health risk)
- Stray Cattle (Critical danger on roads)
- Open Manhole (Life-threatening critical hazard)
- Road Obstruction (Fallen markers, construction debris)
- Waterlogging (Poor drainage, vector risk)
- Broken Streetlight (Safety/security risk)
- Illegal Construction (Zoning violation)
- Damaged Road (Surface cracking, unevenness)
- Sewage Overflow (Health emergency)
- Fallen Tree (Emergency obstruction)
- Traffic Violation (Illegal parking, wrong-way)
- Unauthorized Parking (Sidewalk blockage)
- General Civic Issue (Anything else)

You MUST respond with ONLY a valid JSON object:
{
  "reasoning": "Briefly explain the visual evidence and logic used for classification.",
  "issue_type": "<one of the categories above>",
  "priority": "<Critical, High, Medium, Low>",
  "confidence": <0-100 float>
}
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
            temperature=0.1,
            max_output_tokens=500,
        ),
    )

    # Parse JSON response
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
        text = text.strip()

    result = json.loads(text)

    issue_type = result.get("issue_type", "General Civic Issue")
    priority = result.get("priority", "Medium")
    confidence = result.get("confidence", 0)
    reasoning = result.get("reasoning", "Standard visual analysis applied.")

    print(f"[Best AI - Gemini] {issue_type} ({confidence}% confidence)")
    print(f"[Reasoning] {reasoning}")

    return issue_type, priority, confidence, reasoning


# ── YOLO Fallback ──
_yolo_model = None

def _load_yolo():
    """Load YOLOv8 as fallback detector."""
    global _yolo_model
    if _yolo_model is None:
        from ultralytics import YOLO
        # Using a slightly larger model for the "best" local detection
        _yolo_model = YOLO("yolov8s.pt") 
    return _yolo_model


def _detect_with_yolo(image_path: str):
    """
    Advanced Fallback: Uses object density and common COCO classes to infer civic issues.
    """
    import cv2
    model = _load_yolo()
    img = cv2.imread(image_path)

    if img is None:
        return "Unknown Issue", "Normal", 0, "Image reading failed."

    results = model(img, conf=0.25, verbose=False) # More sensitive for fallback
    
    counts = {}
    detected_labels = []
    for r in results:
        for box in r.boxes:
            label = model.names[int(box.cls[0])].lower()
            counts[label] = counts.get(label, 0) + 1
            detected_labels.append(label)

    # 1. High Priority Safety Hazards
    if any(k in counts for k in ['cow', 'horse', 'sheep', 'elephant', 'bear']):
        return "Stray Animal/Cattle", "Critical", 85, f"Detected large animal ({', '.join(detected_labels)}) in transit zone."
    
    if counts.get('fire hydrant', 0) > 0:
        return "Infrastructure Leak/Obstruction", "High", 80, "Fire hydrant detected; possible water leakage or illegal parking."

    # 2. Traffic & Road Issues
    if counts.get('truck', 0) > 1 or counts.get('bus', 0) > 1:
        return "Heavy Vehicle Obstruction", "High", 75, f"Multiple heavy vehicles detected creating congestion."

    if counts.get('car', 0) > 4:
        return "Unauthorized Parking/Congestion", "Medium", 70, f"Detected clustered vehicles ({counts['car']}) in dense sector."

    if counts.get('traffic light', 0) > 0 or counts.get('stop sign', 0) > 0:
        return "Traffic Infrastructure Issue", "Medium", 65, "Detected traffic control elements; signaling check required."

    # 3. Public Space & Sanitation
    if counts.get('person', 0) > 10:
        return "Public Gathering/Crowd", "High", 60, f"Unusual density of {counts['person']} persons detected."

    if any(k in counts for k in ['bench', 'potted plant', 'bicycle', 'motorcycle']):
        return "Sidewalk Obstruction", "Low", 55, "Detected objects potentially blocking pedestrian pathways."

    if any(k in counts for k in ['bottle', 'cup', 'handbag', 'backpack']):
        return "Littering/Sanitation Issue", "Medium", 50, "Detected discarded items indicating potential sanitation cleanup."

    # 4. Final Fallback (If anything at all was found)
    if counts:
        main_obj = max(counts, key=counts.get)
        return "Infrastructure Monitoring", "Low", 45, f"Detected {main_obj} activity requiring standard review."

    return "General Civic Issue", "Low", 30, "No significant urban anomalies detected. Manual review recommended."


# ── Main Entry Point ──
def detect_issue(image_path: str):
    """
    Detect civic issue from image using the 'Best AI' strategy.
    Returns: (type, priority, confidence, reasoning)
    """
    if GEMINI_API_KEY:
        try:
            return _detect_with_gemini(image_path)
        except Exception as e:
            print(f"[Gemini AI] Error: {e}. Falling back to Expert YOLO...")

    # Fallback to Advanced YOLO
    return _detect_with_yolo(image_path)
