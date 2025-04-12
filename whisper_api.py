from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import whisper
import shutil

app = FastAPI()
model = whisper.load_model("small")

@app.post("/transcribe")
async def transcribe_stream(file: UploadFile = File(...)):
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    def generate_chunks():
        result = model.transcribe(temp_file, language="pt", verbose=False, word_timestamps=True)
        for segment in result["segments"]:
            yield segment["text"] + " "

    return StreamingResponse(generate_chunks(), media_type="text/plain")
