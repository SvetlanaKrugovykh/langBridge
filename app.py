import sys
import os
import netifaces
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langbridge_transformers.opus_mt_en_es import translate as translate_en_es
from langbridge_transformers.opus_mt_en_fr import translate as translate_en_fr
from langbridge_transformers.opus_mt_en_ru import translate as translate_en_ru
from langbridge_transformers.opus_mt_en_uk import translate as translate_en_uk
from langbridge_transformers.opus_mt_en_de import translate as translate_en_de

from langbridge_transformers.opus_mt_de_en import translate as translate_de_en
from langbridge_transformers.opus_mt_es_en import translate as translate_es_en
from langbridge_transformers.opus_mt_fr_en import translate as translate_fr_en
from langbridge_transformers.opus_mt_pl_en import translate as translate_pl_en
from langbridge_transformers.opus_mt_ru_en import translate as translate_ru_en
from langbridge_transformers.opus_mt_uk_en import translate as translate_uk_en

app = FastAPI()
class TranslationRequest(BaseModel):
    text: str
    direction: str

# Mapping of directions to translation functions
TRANSLATION_MAP: Dict[str, callable] = {
    "en_ru": translate_en_es,
    "en_ru": translate_en_fr,
    "en_ru": translate_en_ru,
    "en_uk": translate_en_uk,
    "en_de": translate_en_de,
    "de_en": translate_de_en,
    "es_en": translate_es_en,
    "fr_en": translate_fr_en,
    "pl_en": translate_pl_en,
    "ru_en": translate_ru_en,
    "uk_en": translate_uk_en,
}

def get_local_ips():
    local_ips = set()
    for interface in netifaces.interfaces():
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            for addr_info in addresses[netifaces.AF_INET]:
                local_ips.add(addr_info['addr'])
    return local_ips

local_ips = get_local_ips()
print(f"Local IPs: {local_ips}")

@app.middleware("http")
async def check_request_origin(request: Request, call_next):
    client_host = request.client.host
    if client_host not in local_ips:
        raise HTTPException(status_code=403, detail="Forbidden: requests from this host are not allowed")
    response = await call_next(request)
    return response

@app.post("/translate/")
async def translate_text(request: TranslationRequest):
    translate_function = TRANSLATION_MAP.get(request.direction)
    print(f"Request direction: {request.direction}")
    print(f"Translation function: {translate_function}")

    if not translate_function:
        raise HTTPException(status_code=400, detail="Invalid translation direction")

    translated_text = translate_function(request.text)
    return {"translated_text": translated_text}

if __name__ == "__main__":
    import uvicorn
    PORT = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
