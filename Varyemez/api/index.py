from fastapi import FastAPI, Request, HTTPException
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from mangum import Mangum
import json
import os

app = FastAPI()
handler = Mangum(app)

PUBLIC_KEY = os.getenv("PUBLIC_KEY")

@app.post("/api/index")
async def handle_interactions(request: Request):
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")
    body = await request.body()

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    try:
        verify_key.verify(f'{timestamp}{body.decode()}'.encode(), bytes.fromhex(signature))
    except BadSignatureError:
        raise HTTPException(status_code=401, detail="Geçersiz imza")

    data = json.loads(body)
    if data["type"] == 1:
        return {"type": 1}

    if data["type"] == 2:
        if data["data"]["name"] == "kumar":
            sayi = float(data["data"]["options"][0]["value"])
            ucret = sayi * 0.05
            return {
                "type": 4,
                "data": {"content": f"💰 **Verilecek Ücret:** {ucret:.2f}"}
            }
    return {"type": 1}