from fastapi import FastAPI, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List
from .db import get_db, engine
from . import schemas, models, crud
from sqlalchemy.orm import Session

import glob
import json
import os
from pydub import AudioSegment


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost.com",
    "https://localhost.com",
    "http://localhost:3000",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def main():
    return {"message": "Hello World"}


@app.post('/fetch_sound_for_strum')
def fetch_sound_for_strum(req: schemas.StrumInputSchema):
    strum_pattern = req.pattern
    strum_pattern = strum_pattern.replace('  ', ' ')

    existing_strum_sounds = os.listdir(f'./assets/sound/patterns')

    generatedFile = f"strum_pattern_sound_{strum_pattern}.wav"
    if generatedFile not in existing_strum_sounds:
        downStrum = AudioSegment.from_wav(f"./assets/sound/down-strum.wav")
        upStrum = AudioSegment.from_wav(f"./assets/sound/up-strum.wav")
        silence = AudioSegment.silent(duration=450)
        combined = AudioSegment.empty()
        for ch in strum_pattern:
            if ch.lower() == 'd':
                audiofilename = downStrum
            elif ch.lower() == 'u':
                audiofilename = upStrum
            elif ch == ' ':
                audiofilename = silence
            combined += audiofilename
        combined += silence

        combined.export(f"./assets/sound/patterns/" +
                        generatedFile, format="wav")
    return FileResponse(f"./assets/sound/patterns/" + generatedFile, media_type='audio/wav')


@app.post('/save_lyrics_and_chords')
async def save_lyrics_and_chords(req: schemas.NotesSchema, db: Session = Depends(get_db)):
    await crud.NotesCrud.create(db=db, item=req)
    return JSONResponse({"message": "success"}, status_code=200)


@app.get('/fetch_all_saved_chords', response_model=List[schemas.AllNotesSchema])
def fetch_all_saved_chords(db: Session = Depends(get_db)):
    """
    Get all the Items stored in database
    """
    items = crud.NotesCrud.fetch_all(db)
    return items

@app.get('/fetch_song_by_id', response_model=schemas.NotesSchema)
def fetch_song_by_id(id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get all the Items stored in database
    """
    items = []
    db_item = crud.NotesCrud.fetch_by_id(db, id)
    items.append(db_item)
    return items[0]
   