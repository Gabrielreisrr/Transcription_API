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


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/transcribe")
async def transcribe_stream(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        transcribe_options = {
            "language": "pt",
            "verbose": True,
            "fp16": False,
            "no_speech_threshold": 0.3,
            "logprob_threshold": -2.0,
            "condition_on_previous_text": False,
            "temperature": 0.0,
        }

        result = model.transcribe(temp_file_path, **transcribe_options)

        segments = [
            {
                "time": f"{seg.get('start', 0.0):.2f} - {seg.get('end', 0.0):.2f}",
                "text": seg.get("text", "").strip(),
            }
            for seg in result.get("segments", [])
            if isinstance(result.get("segments"), list)
        ]

        return {"segments": segments}

    except Exception as e:
        return {
            "error": str(e),
            "message": "An error occurred during transcription.",
            "segments": [],
        }
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
