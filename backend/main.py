from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "translated"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/translate")
async def translate_document(
    file: UploadFile = File(...),
    target_lang: str = Form("es"),
    precision_mode: str = Form("schematic")
):
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    output_path = os.path.join(OUTPUT_DIR, f"translated_{file_id}{ext}")
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    translator = DiagramTranslator(target_lang=target_lang.upper())
    
    try:
        if ext.lower() == ".pdf":
            translator.process_pdf(input_path, output_path)
        else:
            shutil.copy(input_path, output_path) 
            
        return {
            "status": "success",
            "download_url": f"/download/{file_id}{ext}",
            "filename": f"translated_{file.filename}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/download/{file_id_ext}")
async def download_file(file_id_ext: str):
    path = os.path.join(OUTPUT_DIR, f"translated_{file_id_ext}")
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "File not found"}

# Serve Frontend - Move this to the end so it doesn't override API routes
# We assume the frontend files are in a folder named 'frontend' or root
# For the unified deployment, we will put everything in the root or a 'public' folder
if os.path.exists("../index.html"):
    app.mount("/", StaticFiles(directory="../", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Use port from environment variable for deployment (default 8000)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
