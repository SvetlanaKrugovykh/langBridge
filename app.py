# app.py
import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langbridge_transformers.opus_mt_en_ru import translate as translate_en_ru
from langbridge_transformers.opus_mt_en_uk import translate as translate_en_uk
from langbridge_transformers.opus_mt_en_de import translate as translate_en_de

from langbridge_transformers.opus_mt_de_en import translate as translate_de_en
from langbridge_transformers.opus_mt_pl_en import translate as translate_pl_en
from langbridge_transformers.opus_mt_ru_en import translate as translate_ru_en
from langbridge_transformers.opus_mt_uk_en import translate as translate_uk_en

app = FastAPI()

class TranslationRequest(BaseModel):
    text: str
    direction: str

# Mapping of directions to translation functions
TRANSLATION_MAP: Dict[str, callable] = {
    "en_ru": translate_en_ru,
    "en_uk": translate_en_uk,
    "en_de": translate_en_de,
    "de_en": translate_de_en,
    "pl_en": translate_pl_en,
    "ru_en": translate_ru_en,
    "uk_en": translate_uk_en,
}

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
    uvicorn.run(app, host="0.0.0.0", port=8000)