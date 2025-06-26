from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import whisper
import shutil
import os

app = FastAPI()
model = whisper.load_model("medium")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe")
async def transcribe_stream(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        verbose_output = True
        fp16_setting = False

        transcribe_options = {
            "language": "pt",
            "verbose": verbose_output,
            "fp16": fp16_setting,
            "no_speech_threshold": 0.3,  # torna mais tolerante a silêncios
            "logprob_threshold": -2.0,   # permite transcrição com menor confiança
            "condition_on_previous_text": False,  # evita repetir ou travar
            "temperature": 0.0,     
        }

        print(f"Transcribing with options: {transcribe_options}")
        result = model.transcribe(temp_file_path, **transcribe_options)

        segments = []
        if result and "segments" in result and isinstance(result["segments"], list):
            for seg in result["segments"]:
                segments.append({
                    "time": f"{seg.get('start', 0.0):.2f} - {seg.get('end', 0.0):.2f}",
                    "text": seg.get('text', '').strip()
                })

        transcribed_text = result['text'].strip() if result and 'text' in result else "No transcription text found."
        
        print(f"Processed file: {file.filename}")
        print(f"Transcription result: {transcribed_text}")
        print(f"Number of segments: {len(segments)}")
        return { "segments": segments }

    except Exception as e:
        print(f"Error during transcription: {e}")
        return {
            "error": str(e),
            "message": "An error occurred during transcription.",
            "segments": []
        }
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
