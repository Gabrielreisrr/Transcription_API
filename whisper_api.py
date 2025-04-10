# whisper_api.py
from fastapi import FastAPI, File, UploadFile
import whisper
import shutil

app = FastAPI()
model = whisper.load_model("small")

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    result = model.transcribe(temp_file, language="pt")
    return {"transcription": result["text"]}
