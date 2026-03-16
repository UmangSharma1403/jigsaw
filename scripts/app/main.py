from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import uuid
import json
import os

import base64
from io import BytesIO

from .processor import process_image
from .palette import BEAD_PALETTE

app = FastAPI(title="Bead Grid API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.post("/generate")
async def generate_bead_grid(file: UploadFile = File(...)):
    contents = await file.read()
    img = Image.open(BytesIO(contents))

    output_img, grid_labels = process_image(img)

    # --- convert image to base64 ---
    buf = BytesIO()
    output_img.save(buf, format="PNG")
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return {
        "width": grid_labels.shape[1],
        "height": grid_labels.shape[0],
        "palette": [{"r": r, "g": g, "b": b} for r, g, b in BEAD_PALETTE],
        "grid": grid_labels.tolist(),
        "image_base64": img_base64,
    }