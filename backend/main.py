from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid
from translator import DiagramTranslator

app = FastAPI(title="Diagram Translate API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Determine the frontend directory (works both locally and in Docker)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /app
FRONTEND_DIR = BASE_DIR  # index.html is in /app

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "translated")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.post("/translate")
async def translate_document(
    file: UploadFile = File(...),
    target_lang: str = Form("es"),
    precision_mode: str = Form("schematic")
):
    file_id = str(uuid.uuid4())
    # Handle filenames with no extension
    filename = file.filename or "document.pdf"
    ext = os.path.splitext(filename)[1].lower() or ".pdf"

    input_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    output_path = os.path.join(OUTPUT_DIR, f"translated_{file_id}{ext}")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # target_lang should be lowercase (e.g. "es", "en", "de")
    translator = DiagramTranslator(target_lang=target_lang.lower())

    try:
        if ext == ".pdf":
            translator.process_pdf(input_path, output_path)
        else:
            shutil.copy(input_path, output_path)

        return {
            "status": "success",
            "download_url": f"/download/{file_id}{ext}",
            "filename": f"translated_{filename}"
        }
    except Exception as e:
        print(f"Translation error: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/download/{file_id_ext}")
async def download_file(file_id_ext: str):
    path = os.path.join(OUTPUT_DIR, f"translated_{file_id_ext}")
    if os.path.exists(path):
        return FileResponse(
            path,
            media_type="application/octet-stream",
            filename=f"translated_{file_id_ext}"
        )
    return {"error": "File not found"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Serve the frontend static files — MUST be mounted last so API routes take priority
if os.path.exists(os.path.join(FRONTEND_DIR, "index.html")):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
else:
    @app.get("/")
    async def root():
        return HTMLResponse("<h1>Diagram Translate API is running.</h1><p>Frontend not found.</p>")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Diagram Translate server on port {port}")
    print(f"Frontend directory: {FRONTEND_DIR}")
    print(f"Frontend exists: {os.path.exists(os.path.join(FRONTEND_DIR, 'index.html'))}")
    uvicorn.run(app, host="0.0.0.0", port=port)
