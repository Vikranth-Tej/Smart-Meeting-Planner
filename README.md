
# Smart Meeting Planner

This is a lightweight, full-stack FastAPI + HTML tool that helps you find and book **common meeting slots** for multiple users based on their busy schedules.

##  Features

-  Accepts multiple users with their busy times
-  Suggests 3 common available slots (30-min duration)
-  Allows booking one of the suggested slots
-  Reflects both busy and booked slots per user
-  Clean, minimal UI with instant feedback

---
##  How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the FastAPI server
uvicorn main:app --reload

# 3. Open in your browser
http://127.0.0.1:8000/
```

---

## Sample Input

Paste this JSON in the textarea:

```json
{
  "users": [
    { "id": 1, "busy": [["09:00", "10:30"], ["13:00", "14:00"]] },
    { "id": 2, "busy": [["11:00", "12:00"], ["15:00", "16:00"]] }
  ]
}

```
## Endpoints

Route -	Method - Description: 
- /slots - POST  -	Save busy slots for all users
- /suggest	- GET -	Return the first 3 common free 30-min slots
- /book	- POST -	Book one of the suggested slots for users
- /calendar/{id} - GET -	View both busy + booked slots for a single user

---
# Reflection

### 1. How exactly did you use AI while building this?
#### Tools Used:
- ChatGPT (GPT-4o) for full-stack scaffolding, API logic, HTML UX, debugging, and prompt driven iteration.
#### Prompts included:
- "Build me a FastAPI endpoint for slot suggestion"
- "edit the given code with much more logical efficiency"
- "Refactor this HTML to remove Submit and make Book smarter"
- "Make the UI  usable"
#### successes:
- Cut dev time by 70% while polishing frontend logic.
- Got clean backend API logic in one go.
#### Failures:
- Sometimes generated unnecessary extras (like keeping the Submit button after removing logic).
- Needed to guide AI to stick strictly to spec wording.


### 2.If given two more days, what would you refactor or add first, and why?
Planned Next:
- Calendar visualization for each user (GET /calendar/{id} → frontend).
- Duration input dropdown for customizable meeting lengths.
- A backend data store (e.g., SQLite) to persist slots beyond app restart.

These improve usability, realism and data persistence, making it more production grade.

