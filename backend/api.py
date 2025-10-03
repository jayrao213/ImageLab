from io import BytesIO
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image as PILImage
from dotenv import load_dotenv
from pixel import Pixel
from image import Image
import os

load_dotenv()
app = FastAPI(title="Image API")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

def pil_to_internal(pil_img: PILImage.Image) -> Image:
    pil_img = pil_img.convert("RGB")
    width, height = pil_img.size
    data = []
    for r in range(height):
        y = height - 1 - r
        row = []
        for x in range(width):
            r8, g8, b8 = pil_img.getpixel((x, y))
            row.append(Pixel(r8, g8, b8))
        data.append(row)
    return Image(data, [3779, 3779])

def internal_to_pil(img: Image) -> PILImage.Image:
    h = len(img._data)
    w = len(img._data[0])
    pil = PILImage.new("RGB", (w, h))
    for r, row in enumerate(img._data):
        y = h - 1 - r
        for x, p in enumerate(row):
            pil.putpixel((x, y), (p._red, p._green, p._blue))
    return pil

@app.post("/apply")
async def apply(
    file: Optional[UploadFile] = File(None),
    action: str = Form(...),
    amount: Optional[float] = Form(None),
    factor: Optional[float] = Form(None),
    size: Optional[int] = Form(None),
    r: Optional[int] = Form(None),
    g: Optional[int] = Form(None),
    b: Optional[int] = Form(None),
    degrees: Optional[int] = Form(None),
    block: Optional[int] = Form(None),
    prompt: Optional[str] = Form(None),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None),
    resize_width: Optional[int] = Form(None),
    resize_height: Optional[int] = Form(None),
):
    if action == "ai_generate" and not file:
        pil_in = PILImage.new("RGB", (64, 64), color=(128, 128, 128))
    else:
        if not file:
            raise HTTPException(status_code=400, detail="Image file required for this action")
        try:
            raw = await file.read()
            pil_in = PILImage.open(BytesIO(raw))
        except Exception:
            raise HTTPException(status_code=400, detail="Could not read image")

    img = pil_to_internal(pil_in)

    if action == "ai_generate":
        if not prompt:
            raise HTTPException(status_code=400, detail="Missing prompt")
        try:
            img_width = width if width else 512
            img_height = height if height else 512
            img.ai_generate(prompt, width=img_width, height=img_height)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif action == "resize":
        if not resize_width or not resize_height:
            raise HTTPException(status_code=400, detail="Width and height required for resize")
        img.resize(int(resize_width), int(resize_height))
    elif action == "add_color":
        img.add_color(Pixel(int(r or 0), int(g or 0), int(b or 0)))
    elif action == "red_shift":
        img.red_shift(float(amount or 0))
    elif action == "green_shift":
        img.green_shift(float(amount or 0))
    elif action == "blue_shift":
        img.blue_shift(float(amount or 0))
    elif action == "shift_brightness":
        img.shift_brightness(float(factor or 1.0))
    elif action == "make_monochrome":
        img.make_monochrome()
    elif action == "mirror_horizontal":
        img.mirror_horizontal()
    elif action == "mirror_vertical":
        img.mirror_vertical()
    elif action == "tile":
        img.tile(int(size or 1))
    elif action == "blur":
        img.blur()
    elif action == "negative":
        img.negative()
    elif action == "sepia":
        img.sepia()
    elif action == "rotate":
        img.rotate(int(degrees or 90))
    elif action == "pixelate":
        img.pixelate(int(block or 8))
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action '{action}'")

    pil_out = internal_to_pil(img)
    buf = BytesIO()
    pil_out.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")