from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from typing import Optional
from datetime import datetime, timedelta
import pytz

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
GOOGLE_SCRIPT_URL_SHEET = "https://script.google.com/macros/s/AKfycbyHtzFow7AGolUqkf9S2eK6TcAGD_9-H_8IGVUicvH9qqcivxSZGx9Bu5toIviWqbyg/exec"
GOOGLE_SCRIPT_URL_CALENDAR = "https://script.google.com/macros/s/AKfycbxDOAox60T2aekE-8E6VuTDTypooxDh0tDbP3MFNag2A-CGo8cz3zYLAHmKs7SzLb2eGQ/exec"
# GOOGLE_SCRIPT_URL_CALENDAR = "https://script.google.com/macros/s/AKfycbzADEAp_0Rge4ET7g4O5dTFJwquBHrZwxT83aLhSN5zkUFdzxyd86vtwev96mgpN582/exec"


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
    params = {"days": days}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_SCRIPT_URL_CALENDAR, params=params, follow_redirects=True
        )

    # Log the response for debugging
    print("Response status:", response.status_code)
    print("Response content:", response.text)

    if response.status_code == 200:
        try:
            # Ensure we return a list
            data = response.json()
            if isinstance(data, list):
                return data
            else:
                return {
                    "success": False,
                    "error": "Expected a list of appointments",
                    "content": data,
                }
        except ValueError:
            return {
                "success": False,
                "error": "Invalid JSON response from Google Apps Script",
                "content": response.text,
            }
    else:
        return {
            "success": False,
            "error": f"Failed to fetch appointments. Status code: {response.status_code}",
            "content": response.text,
        }


class EventData(BaseModel):
    title: str
    startTime: str  # In ISO format
    endTime: Optional[str] = None  # In ISO format, optional
    location: Optional[str] = "No location"
    description: Optional[str] = "No description"


@app.post("/create_calendar_event")
async def create_calendar_event(data: EventData):
    # Use GMT+1 timezone
    timezone = pytz.timezone('Etc/GMT-1')  # Or use 'Europe/Paris'

    # Parse startTime and make it timezone-aware
    start_datetime = datetime.fromisoformat(data.startTime)
    start_datetime = timezone.localize(start_datetime)

    # If endTime is not provided, assume a 30-minute event
    if not data.endTime:
        end_datetime = start_datetime + timedelta(minutes=30)
        data.endTime = end_datetime.isoformat()
    else:
        # Parse endTime and make it timezone-aware
        end_datetime = datetime.fromisoformat(data.endTime)
        end_datetime = timezone.localize(end_datetime)
        data.endTime = end_datetime.isoformat()

    # Update the data object
    data.startTime = start_datetime.isoformat()
    data.endTime = end_datetime.isoformat()

    # Prepare the data to send
    event_data = data.dict()

    # Send POST request to Google Apps Script to create calendar event
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_SCRIPT_URL_CALENDAR, json=event_data, follow_redirects=True
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
