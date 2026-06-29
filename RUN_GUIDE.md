# SipSetu Local Execution & API Guide

Follow these instructions to run the SipSetu backend locally and call the matching APIs.

## 🚀 Setup & Startup

1. **Open Terminal**
   Ensure your shell is open in the project root:
   `c:\Users\Pujan\OneDrive\Documents\sipsetu worldcup\SipSetu`

2. **Activate Virtual Environment**
   ```powershell
   .venv\Scripts\activate
   ```

3. **Update Database Schema**
   Ensure your local PostgreSQL schema is fully up-to-date:
   ```powershell
   python update_db.py
   ```

4. **Run the Flask Server**
   ```powershell
   python run.py
   ```
   The API will listen at: `http://127.0.0.1:5000`

---

## 🛠️ testing your A2 Endpoints

### 1. Analyze Job Description
Extracts required skills from job description text.
* **Method:** `POST`
* **Route:** `/applicant/analyze-job`
* **Headers:** `Content-Type: application/json`
* **Payload:**
  ```json
  {
    "description": "Looking for a Software Engineer with Python, SQL, React and AWS skills."
  }
  ```

### 2. Match Resume & Job
Matches a candidate's latest resume against a posted job description.
* **Method:** `POST`
* **Route:** `/applicant/match`
* **Headers:** `Content-Type: application/json`
* **Payload:**
  ```json
  {
    "candidate_id": "YOUR_CANDIDATE_UUID",
    "job_id": "YOUR_JOB_UUID"
  }
  ```
* **Response format:**
  ```json
  {
    "candidate_id": "YOUR_CANDIDATE_UUID",
    "job_id": "YOUR_JOB_UUID",
    "score": 33,
    "matched_skills": ["sql"],
    "missing_skills": ["python", "aws"]
  }
  ```
