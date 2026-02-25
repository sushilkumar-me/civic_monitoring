# Civic Monitoring System

A civic issue tracking system built with FastAPI, PostgreSQL, and YOLOv8 for automated issue detection.

## Prerequisites

- Python 3.8+
- PostgreSQL
- Internet connection (for initial YOLO model download)

## Setup Instructions

### 1. Database Setup
1. Create a PostgreSQL database named `civic_monitoring`.
2. Open the `DB.txt` file in the root directory.
3. Execute the SQL commands in `DB.txt` using your PostgreSQL tool (e.g., pgAdmin, psql) to create the tables and insert initial users.
4. **Important**: Verify the database connection string in `backend/database.py`.
   - Current: `postgresql://postgres:1234@localhost/civic_monitoring`
   - Update `postgres` and `1234` with your PostgreSQL username and password if different.

### 2. Backend Setup
1. Open a terminal in the project root.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

### 3. Running the Application
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
3. The application will be available at `http://127.0.0.1:8000`.

## User Roles and Login

You can log in using the IDs provided in `DB.txt`:

| Role     | User Name | ID | Description |
|----------|-----------|----|-------------|
| Surveyor | Amit      | 1  | Reports civic issues with location and images. |
| Engineer | Rahul     | 2  | Views reported issues, navigates to location, and closes them. |
| Admin    | Admin     | 3  | Views dashboard with statistics and ward-wise summaries. |

## Features
- **AI detection**: Automatically detects "Stray Cattle" or "Road Obstructions" from uploaded images using YOLOv8.
- **Navigation**: Integrated Google Maps links for engineers to navigate to reported issues.
- **Reporting**: Surveyor captures images and GPS coordinates to report issues.
- **Dashboard**: Admin view for monitoring overall civic health.
