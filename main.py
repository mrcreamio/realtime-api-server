from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Apps Script Web App URL
GOOGLE_SCRIPT_URL_SHEET = "https://script.google.com/macros/s/AKfycbwHxa-MDtZCZo244bWc90AppFCa5oA7YT1ZYEaJbG90OViT109YtLjeMBstB7un7V8B/exec"
GOOGLE_SCRIPT_URL_CALENDAR = "https://script.google.com/macros/s/AKfycbwME7H5Fbxf0vSlK0uLkCGZrKTF3PhkdidhmrOvle2sVVq4LxM4lXdOOol3nNUmM7BCKA/exec"


class AppointmentData(BaseModel):
    name: str
    appointmentDate: str
    reason: str


@app.post("/send_appointment")
async def send_appointment(data: AppointmentData):
    # Send POST request to Google Apps Script with follow_redirects
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_SCRIPT_URL_SHEET, json=data.dict(), follow_redirects=True
        )

    # Check and log the response
    print("Response status:", response.status_code)
    print("Response content:", response.text)

    try:
        return response.json()
    except ValueError:
        return {
            "success": False,
            "error": "Invalid response from Google Apps Script",
            "content": response.text,
        }


@app.get("/get_appointments")
async def get_appointments(days: int = 1):
    # Send GET request to Google Apps Script to retrieve appointments
    params = {"days": days}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_SCRIPT_URL_CALENDAR, params=params, follow_redirects=True
        )

    # Check and log the response
    print("Response status:", response.status_code)
    print("Response content:", response.text)

    try:
        return response.json()
    except ValueError:
        return {
            "success": False,
            "error": "Invalid response from Google Apps Script",
            "content": response.text,
        }
