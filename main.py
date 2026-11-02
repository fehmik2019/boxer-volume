from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import base64
import httpx
import os

app = FastAPI()

XAI_API_KEY = os.getenv("XAI_API_KEY")

@app.post("/process")
async def process_image(
    pattern_image: UploadFile = File(...),
    shape_image: UploadFile = File(...)
):
    if not XAI_API_KEY:
        return JSONResponse(status_code=500, content={"error": "XAI_API_KEY manquante"})

    try:
        # Image A (motif)
        pattern_bytes = await pattern_image.read()
        pattern_b64 = base64.b64encode(pattern_bytes).decode("utf-8")

        # Image B (forme / volume)
        shape_bytes = await shape_image.read()
        shape_b64 = base64.b64encode(shape_bytes).decode("utf-8")

        prompt = """Take the exact pattern, colors, and branding from the first image (the flat boxer shorts).
Apply the realistic 3D volume, shape, front pouch, fabric draping, and overall form from the second image (the blue volumetric reference).
Create a professional product photo of the patterned boxer with the same strong volume and shaping as the reference.
Keep the original pattern perfectly recognizable.
Pure white background, soft studio lighting, subtle shadow underneath, front view, high-end e-commerce style."""

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                "https://api.x.ai/v1/images/edits",
                headers={
                    "Authorization": f"Bearer {XAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-imagine-image-2.0",
                    "prompt": prompt,
                    "images": [
                        {
                            "url": f"data:image/jpeg;base64,{pattern_b64}",
                            "type": "image_url"
                        },
                        {
                            "url": f"data:image/jpeg;base64,{shape_b64}",
                            "type": "image_url"
                        }
                    ]
                }
            )

            data = response.json()

            if response.status_code != 200 or "data" not in data:
                return JSONResponse(
                    status_code=response.status_code or 500,
                    content={"error": data}
                )

            return {"url": data["data"][0]["url"]}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r") as f:
        return f.read()
