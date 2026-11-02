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
        pattern_bytes = await pattern_image.read()
        pattern_b64 = base64.b64encode(pattern_bytes).decode("utf-8")

        shape_bytes = await shape_image.read()
        shape_b64 = base64.b64encode(shape_bytes).decode("utf-8")

        prompt = """CRITICAL TASK: Shape transfer / morphing.

Image 1 = source pattern (flat boxer shorts with flamingos and flowers).
Image 2 = target shape and topology (volumetric blue boxer with strong 3D form and front pouch).

Warp and deform the exact pattern of Image 1 so that it perfectly follows the 3D topology, volume, fabric tension, and shape of Image 2.

Requirements:
- The front pouch must have the same pronounced rounded volume as Image 2
- The fabric must follow the same folds, seams, and 3D curvature as the reference
- Leg openings and waistband must match the shape of Image 2
- Keep the original pattern, colors, and branding 100% recognizable
- Result must look like a real product photo with strong volume, not a flat image
- Pure white background, soft studio lighting, subtle shadow
- Front view, high-end e-commerce quality"""

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
                        {"type": "image_url", "url": f"data:image/jpeg;base64,{pattern_b64}"},
                        {"type": "image_url", "url": f"data:image/jpeg;base64,{shape_b64}"}
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
