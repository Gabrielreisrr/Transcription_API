from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import whisper
import shutil
import os

app = FastAPI()
model = whisper.load_model("small")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe")
async def transcribe_stream(file: UploadFile = File(...)):
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = model.transcribe(temp_file, language="pt", verbose=False)
    segments = []

    for seg in result["segments"]:
        segments.append({
            "time": f"{seg['start']:.2f} - {seg['end']:.2f}",
            "text": seg["text"].strip()
        })

    os.remove(temp_file)
    print(f"Processed file: {file.filename}")
    print(f"Transcription result: {result['text'].strip()}")
    print(f"Number of segments: {len(segments)}")
    print(f"Segments: {segments}")
    print("Transcription completed successfully.")
    return { "segments": segments }
