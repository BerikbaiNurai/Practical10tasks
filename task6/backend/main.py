import os
import uuid
import aiofiles
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IMAGE_DIR = "static/images/"
os.makedirs(IMAGE_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

MAX_FILE_SIZE = 5 * 1024 * 1024 

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением.")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Файл слишком большой (максимум 5 МБ).")

    await file.seek(0)

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(IMAGE_DIR, unique_filename)

    try:
        async with aiofiles.open(file_path, mode='wb') as out_file:
            await out_file.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении файла: {e}")

    file_url = f"/static/images/{unique_filename}"
    return {"url": file_url}


@app.get("/api/images", response_model=List[str])
async def get_images():
    """Возвращает список URL всех изображений в папке."""
    try:
        files = os.listdir(IMAGE_DIR)
        return [f"/static/images/{f}" for f in files if os.path.isfile(os.path.join(IMAGE_DIR, f))]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при чтении директории: {e}")


@app.delete("/api/images/{filename}")
async def delete_image(filename: str):
    """Удаляет изображение по имени файла."""
    file_path = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    try:
        os.remove(file_path)
        return {"message": "Файл удалён"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении файла: {e}")