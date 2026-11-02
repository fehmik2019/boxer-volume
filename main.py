from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import base64
import httpx
import os

app = FastAPI()

XAI_API_KEY = os.getenv("XAI_API_KEY")

@app.post("/process")
async def process_image(file: UploadFile = File(...)):
    if not XAI_API_KEY:
        return JSONResponse(status_code=500, content={"error": "XAI_API_KEY manquante"})

    try:
        contents = await file.read()
        base64_image = base64.b64encode(contents).decode("utf-8")

        prompt = """Transform this flat-laid boxer shorts into a professional 3D product photography mockup with realistic volume and form. 
Give it a shaped front pouch with volume, natural fabric draping and folds, defined leg openings, and a slightly curved waistband. 
Keep the exact pattern, colors, and waistband branding. 
Pure white background, soft studio lighting, subtle shadow underneath, high-end product photo style, front view."""

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
                    "response_format": "b64_json",
                    "image": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "type": "image_url"
                    }
                }
            )

            data = response.json()

            if response.status_code != 200 or "data" not in data:
                return JSONResponse(
                    status_code=response.status_code or 500,
                    content={"error": data}
                )

            # On renvoie le base64 directement
            b64 = data["data"][0]["b64_json"]
            return {"image": f"data:image/jpeg;base64,{b64}"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r") as f:
        return f.read()
