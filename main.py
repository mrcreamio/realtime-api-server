from fastapi import FastAPI
from pydantic import BaseModel
import httpx

app = FastAPI()

# Google Apps Script Web App URL
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwHxa-MDtZCZo244bWc90AppFCa5oA7YT1ZYEaJbG90OViT109YtLjeMBstB7un7V8B/exec"


class AppointmentData(BaseModel):
    name: str
    appointmentDate: str
    reason: str


@app.post("/send_appointment/")
async def send_appointment(data: AppointmentData):
    # Send POST request to Google Apps Script with follow_redirects
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_SCRIPT_URL, json=data.dict(), follow_redirects=True
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
