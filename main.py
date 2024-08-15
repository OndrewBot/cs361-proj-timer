from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for timer state
timer_data = {
    "duration": 0,      # Total time in seconds
    "start_time": None, # Start timestamp
    "paused_time": None, # Time left when paused
    "is_running": False,
}

class TimerSettings(BaseModel):
    hours: int = 0
    minutes: int = 0
    seconds: int = 0

@app.post("/start-timer")
def start_timer(settings: TimerSettings):
    if timer_data["is_running"]:
        raise HTTPException(status_code=400, detail="Timer is already running.")

    # Convert hours, minutes, and seconds to total seconds
    total_seconds = settings.hours * 3600 + settings.minutes * 60 + settings.seconds
    
    timer_data["duration"] = total_seconds
    timer_data["start_time"] = time.time()
    timer_data["paused_time"] = None
    timer_data["is_running"] = True

    return {"message": "Timer started", "duration": total_seconds}

@app.post("/pause-timer")
def pause_timer():
    if not timer_data["is_running"]:
        raise HTTPException(status_code=400, detail="Timer is not running.")

    # Calculate remaining time
    elapsed = time.time() - timer_data["start_time"]
    remaining_time = timer_data["duration"] - elapsed
    
    timer_data["paused_time"] = remaining_time
    timer_data["is_running"] = False

    return {"message": "Timer paused", "remaining_time": remaining_time}

@app.post("/reset-timer")
def reset_timer():
    timer_data["duration"] = 0
    timer_data["start_time"] = None
    timer_data["paused_time"] = None
    timer_data["is_running"] = False

    return {"message": "Timer reset"}

@app.get("/status")
def get_status():
    if timer_data["is_running"]:
        elapsed = time.time() - timer_data["start_time"]
        remaining_time = timer_data["duration"] - elapsed
        return {"remaining_time": remaining_time, "is_running": True}
    elif timer_data["paused_time"] is not None:
        return {"remaining_time": timer_data["paused_time"], "is_running": False}
    else:
        return {"remaining_time": timer_data["duration"], "is_running": False}
