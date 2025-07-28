from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import google.generativeai as genai
from fpdf import FPDF
import uuid
import os

# Configure Gemini API
genai.configure(api_key="AIzaSyBegl0hIl3E2cXT5yFr8y-UcwCZCGGDZjk")
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

# FastAPI app
app = FastAPI()

# Pydantic model for mood log
class MoodEntry(BaseModel):
    moodIndex: int
    moodLabel: str
    note: str
    timestamp: str

class MoodLog(BaseModel):
    logs: list[MoodEntry]

# PDF Generator class
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Monthly Mood & Wellness Report", ln=True, align="C")
        self.ln(10)

    def add_body(self, text):
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, text)

# API endpoint to generate report
@app.post("/generate-pdf")
async def generate_pdf(mood_log: MoodLog):
    try:
        # Generate Gemini response
        prompt = f"""
        You are a helpful wellness assistant.

        A user has been logging their daily moods using the following structure:
        - moodIndex (0-4 where 0 = Very Sad and 4 = Very Happy)
        - moodLabel (a string like "Happy", "Sad", etc.)
        - note (user's personal comment)
        - timestamp (datetime)

        Using this JSON data, write a monthly mood and wellness report in a structured, professional tone, suitable for PDF export. 
        Ensure the report includes:
        - Title
        - Introductory summary
        - Mood trend and pattern analysis
        - Key highlights from notes (as bullet points)
        - A motivational closing paragraph

        Respond in plain text only, no Markdown or emojis.

        JSON logs:
        {mood_log.dict()}
        """

        response = model.generate_content(prompt)

        # Generate unique filename
        filename = f"mood_report_{uuid.uuid4().hex[:8]}.pdf"
        filepath = f"./{filename}"

        # Create PDF
        pdf = PDF()
        pdf.add_page()
        pdf.add_body(response.text)
        pdf.output(filepath)

        return FileResponse(path=filepath, filename=filename, media_type='application/pdf')

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))