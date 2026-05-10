from fastapi import FastAPI, Request, HTTPException
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from mangum import Mangum
import json
import os

app = FastAPI()
handler = Mangum(app)

# Vercel Settings -> Environment Variables kısmına eklediğin Public Key
PUBLIC_KEY = os.getenv("PUBLIC_KEY")

@app.post("/api/index")
async def handle_interactions(request: Request):
    # Güvenlik doğrulaması
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")
    body = await request.body()

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    try:
        verify_key.verify(f'{timestamp}{body.decode()}'.encode(), bytes.fromhex(signature))
    except BadSignatureError:
        raise HTTPException(status_code=401, detail="Geçersiz imza")

    data = json.loads(body)

    # Discord Ping kontrolü
    if data["type"] == 1:
        return {"type": 1}

    # Komut kontrolü
    if data["type"] == 2:
        if data["data"]["name"] == "kumar":
            # Kullanıcının yazdığı sayı
            yazilan_sayi = float(data["data"]["options"][0]["value"])
            
            # Hesaplama: Yazılan Sayı - (Yazılan Sayı * 0.05)
            # int() kullanarak küsuratları ( .00 ) siliyoruz
            net_sonuc = int(yazilan_sayi - (yazilan_sayi * 0.05))
            
            return {
                "type": 4,
                "data": {
                    "content": f"Verilecek Ücret: {net_sonuc}"
                }
            }

    return {"type": 1}
