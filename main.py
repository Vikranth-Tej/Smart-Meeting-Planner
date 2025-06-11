from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Tuple, Dict
from functools import reduce
import os

app = FastAPI()

# In-memory storage
user_busy_slots: Dict[int, List[Tuple[str, str]]] = {}
booked_slots: List[Tuple[List[int], Tuple[str, str]]] = []

# Utility functions
def to_minutes(time_str: str) -> int:
    hours, minutes = map(int, time_str.split(":"))
    return hours * 60 + minutes

def to_time_str(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"

# Pydantic models
class UserBusySlot(BaseModel):
    id: int
    busy: List[Tuple[str, str]]

class UsersPayload(BaseModel):
    users: List[UserBusySlot]

class BookRequest(BaseModel):
    users: List[int]
    slot: Tuple[str, str]

# Endpoint: Save busy slots
@app.post("/slots")
def save_slots(payload: UsersPayload):
    for user in payload.users:
        user_busy_slots[user.id] = user.busy
    return {"message": "Slots saved successfully"}

# Find free time slots for each user
def get_free_slots(busy: List[Tuple[str, str]], start="09:00", end="18:00") -> List[Tuple[int, int]]:
    busy_minutes = sorted([[to_minutes(s), to_minutes(e)] for s, e in busy])
    free_slots = []
    current = to_minutes(start)
    end_time = to_minutes(end)

    for s, e in busy_minutes:
        if s > current:
            free_slots.append([current, s])
        current = max(current, e)

    if current < end_time:
        free_slots.append([current, end_time])

    return free_slots

# Find common slots across all users
def intersect_slots(a: List[Tuple[int, int]], b: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    i = j = 0
    result = []
    while i < len(a) and j < len(b):
        s1, e1 = a[i]
        s2, e2 = b[j]
        start = max(s1, s2)
        end = min(e1, e2)
        if end - start >= 0:
            result.append([start, end])
        if e1 < e2:
            i += 1
        else:
            j += 1
    return result

# Endpoint: Suggest common free slots
@app.get("/suggest")
def suggest_slots(duration: int = 30):
    all_free_slots = []

    for user_id, busy in user_busy_slots.items():
        booked = [slot for users, slot in booked_slots if user_id in users]
        combined = busy + booked
        free = get_free_slots(combined)
        all_free_slots.append(free)

    if not all_free_slots:
        return []

    common_slots = reduce(intersect_slots, all_free_slots)
    suggestions = []

    for start, end in common_slots:
        while end - start >= duration:
            suggestions.append([to_time_str(start), to_time_str(start + duration)])
            start += duration
            if len(suggestions) >= 3:
                return suggestions

    return suggestions


# Endpoint: Book a selected slot
@app.post("/book")
def book_slot(request: BookRequest):
    new_start, new_end = to_minutes(request.slot[0]), to_minutes(request.slot[1])

    for user_id in request.users:
        busy = user_busy_slots.get(user_id, [])
        booked = [slot for users, slot in booked_slots if user_id in users]
        all_occupied = busy + booked

        for s, e in all_occupied:
            s1, e1 = to_minutes(s), to_minutes(e)
            if not (new_end <= s1 or new_start >= e1):
                raise HTTPException(status_code=409, detail=f"User {user_id} has a conflict with [{s}, {e}]")

    booked_slots.append((request.users, request.slot))
    return {"message": f"Slot {request.slot} booked for users {request.users}"}

# Endpoint: Get calendar view for a user
@app.get("/calendar/{user_id}")
def get_user_calendar(user_id: int):
    busy = user_busy_slots.get(user_id, [])
    booked = [slot for users, slot in booked_slots if user_id in users]
    return {
        "user_id": user_id,
        "busy": busy + booked
    }


# Serve static HTML
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join("static", "index.html"))
