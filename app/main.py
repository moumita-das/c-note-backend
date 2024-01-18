from fastapi import FastAPI, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List
from .db import get_db, engine
from . import schemas, models, crud
from sqlalchemy.orm import Session

import glob
import json
import os, traceback
import re
from pydub import AudioSegment
import smtplib
import random
from email.mime.text import MIMEText
from dotenv import load_dotenv, find_dotenv

load_dotenv()
print(os.path.join(os.getcwd(),'app','.env'))

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost.com",
    "https://localhost.com",
    "http://localhost:3000",
    "http://localhost:3001",
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
    req.chords = ",".join(find_chords_in_song(req.lyrics_chords))
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


def find_chords_in_song(lyrics):
    lyrics = json.loads(lyrics)
    known_chords = ["C", "C7", "Cm", "Cm7", "Cdim", "Caug", "C6", "Cmaj7", "C9",
                    "Db", "Db7", "Dbm", "Dbm7", "Dbdim", "Dbaug", "Db6", "Dbmaj7", "Db9",
                    "D", "D7", "Dm", "Dm7", "Ddim", "Daug", "D6", "Dmaj7", "D9",
                    "Eb", "Eb7", "Ebm", "Ebm7", "Ebdim", "Ebaug", "Eb6", "Ebmaj7", "Eb9",
                    "E", "E7", "Em", "Em7", "Edim", "Eaug", "E6", "Emaj7", "E9",
                    "F", "F7", "Fm", "Fm7", "Fdim", "Faug", "F6", "Fmaj7", "F9",
                    "Gb", "Gb7", "Gbm", "Gbm7", "Gbdim", "Gbaug", "Gb6", "Gbmaj7", "Gb9",
                    "G", "G7", "Gm", "Gm7", "Gdim", "Gaug", "G6", "Gmaj7", "G9",
                    "Ab", "Ab7", "Abm", "Abm7", "Abdim", "Abaug", "Ab6", "Abmaj7", "Ab9",
                    "A", "A7", "Am", "Am7", "Adim", "Aaug", "A6", "Amaj7", "A9",
                    "Bb", "Bb7", "Bbm", "Bbm7", "Bbdim", "Bbaug", "Bb6", "Bbmaj7", "Bb9",
                    "B", "B7", "Bm", "Bm7", "Bdim", "Baug", "B6", "Bmaj7", "B9"]
    chords_arr = []
    for line in lyrics:
        line = line['text']
        # check if the format of the lyrics is of 1st type
        total_length = len(line)
        total_characters = len(line.replace(" ", ""))
        total_spaces = total_length - total_characters
        if total_spaces > total_characters:
            chords_in_line = line.split(" ")
            for chord in chords_in_line:
                if chord in known_chords and chord not in chords_arr:
                    chords_arr.append(chord)
        else:
            # check for second type, ie with brackets
            line = line.replace('[', '(').replace(']', ')').replace(
                '{', '(').replace('}', ')')
            matches = re.findall(r'\(.*?\)', line)
            if len(matches) > 0:
                for chord in matches:
                    chord = chord[1:len(chord)-1]
                    if chord in known_chords and chord not in chords_arr:
                        chords_arr.append(chord)
    return chords_arr


@app.post('/signup_user')
def signup_user(req: schemas.UserSignupSchema):
    pass

@app.post('/send_otp')
def send_otp(req: schemas.UserSignupSchema, db: Session = Depends(get_db)):
    user_email = req.email
    sender_email = os.environ.get("GMAIL_USERNAME")
    sender_password=os.getenv("GMAIL_PASSWORD")
    recipient_email = user_email
    subject = "Hello from High-Notes"
    otp = random.randint(100000,999999)
    print(otp)
    body = """
    <html>
        <body>
            <p>Hi there, you are almost done with the signup process.</p>
            <p>Please enter the below OTP to verify yourself in the website.</p>
            <p>{otp}</p>
        </body>
    </html>
    """.format(otp=otp)
    try:
        html_message = MIMEText(body, 'html')
        html_message['Subject'] = subject
        html_message['From'] = sender_email
        html_message['To'] = recipient_email    
        # with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        #     server.login(sender_email, sender_password)
        #     server.sendmail(sender_email, recipient_email, html_message.as_string())
        crud.UsersCrud.record_otp(db, email=recipient_email, otp=otp)
        return JSONResponse({"message": "success"}, status_code=200)
    except:
        print(traceback.format_exc())
        return JSONResponse({"message": "failed"}, status_code=500)
    
@app.post('/verify_otp')
def verify_otp(req: schemas.OtpTransactionSchema, db: Session = Depends(get_db)):
    user_email = req.email
    otp = req.otp
    print(user_email, otp)
    db_item = crud.UsersCrud.verify_otp(db,user_email, otp)
    print(db_item)
    

    