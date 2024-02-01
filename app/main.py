from fastapi import FastAPI, Body, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List
from typing_extensions import Annotated
from .db import get_db, engine
from . import schemas, models, crud
from .auth import auth_handler, auth_bearer

from sqlalchemy.orm import Session

import glob
import json
import os
import traceback
import re
from pydub import AudioSegment
import smtplib
import random
from datetime import datetime as dt
from email.mime.text import MIMEText
from dotenv import load_dotenv, find_dotenv

load_dotenv()
print(os.path.join(os.getcwd(), 'app', '.env'))

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

async def get_current_active_user(request: Request, db: Session = Depends(get_db)):
    token= await auth_bearer.JWTBearer().__call__(request)
    decodedToken = auth_handler.decodeJWT(token)
    current_user = crud.UsersCrud.find_user_by_id(db, decodedToken['user_id'])
    return current_user if current_user is not None else {} 


@app.post('/fetch_sound_for_strum', tags=['Songs'])
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


@app.post('/save_lyrics_and_chords', tags=['Songs'],dependencies = [Depends(auth_bearer.JWTBearer())])
async def save_lyrics_and_chords(current_user: Annotated[schemas.UserProfileSchema, Depends(get_current_active_user)], req: schemas.NotesSchema,  db: Session = Depends(get_db)):
    req.chords = ",".join(find_chords_in_song(req.lyrics_chords))
    print(current_user)
    req.user_id = current_user.id
    req.created_date = dt.now()
    await crud.NotesCrud.create(db=db, item=req)
    return JSONResponse({"message": "success"}, status_code=200)


@app.get('/fetch_all_saved_chords', tags=['Songs'], response_model=List[schemas.AllNotesSchema])
def fetch_all_saved_chords(db: Session = Depends(get_db)):
    """
    Get all the Items stored in database
    """
    items = crud.NotesCrud.fetch_all(db)
    return items


@app.get('/fetch_song_by_id', tags=['Songs'], response_model=schemas.NotesSchema)
def fetch_song_by_id(id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get all the Items stored in database
    """
    items = []
    db_item = crud.NotesCrud.fetch_by_id(db, id)
    items.append(db_item)
    return items[0]


def find_chords_in_song(lyrics, tags=['Songs']):
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


@app.post('/signup_user', tags=['Authentication'])
def signup_user(req: schemas.UserSignupSchema):
    pass


@app.post('/send_otp', tags=['Authentication'])
async def send_otp(req: schemas.UserSignupSchema, db: Session = Depends(get_db)):
    user_email = req.email
    existing_user = crud.UsersCrud.find_user_by_email(db, user_email)
    if existing_user:
        return JSONResponse({"message": "failed", "desc": "Account is already registered"}, status_code=400)
    sender_email = os.environ.get("GMAIL_USERNAME")
    sender_password = os.getenv("GMAIL_PASSWORD")
    recipient_email = user_email
    subject = "Hello from High-Notes"
    otp = random.randint(100000, 999999)
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
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, html_message.as_string())
        await crud.UsersCrud.record_otp(db, email=recipient_email, otp=otp)
        return JSONResponse({"message": "success"}, status_code=200)
    except:
        print(traceback.format_exc())
        return JSONResponse({"message": "failed", "desc": "We have run into an error. Please try later."}, status_code=500)


@app.post('/verify_otp', tags=['Authentication'])
def verify_otp(req: schemas.OtpTransactionSchema, db: Session = Depends(get_db)):
    user_email = req.email
    otp = req.otp
    db_item = crud.UsersCrud.verify_otp(db, user_email, otp)
    try:
        if db_item is not None:
            return JSONResponse({"message": "success"}, status_code=200)
        else:
            return JSONResponse({"message": "failed", 'desc': "OTP verification failed"}, status_code=400)
    except:
        return JSONResponse({"message": "failed", "desc": "We have run into an error. Please try later"}, status_code=500)


@app.post('/create_account', tags=['Authentication'])
async def create_account(req: schemas.UserSignupSchema, db: Session = Depends(get_db)):
    existing_user = crud.UsersCrud.find_user_by_email(db, req.email)
    if existing_user:
        return JSONResponse({"message": "failed", "desc": "Account is already registered"}, status_code=400)

    item = await crud.UsersCrud.signup(db, req)
    response = auth_handler.signJWT(item.id)
    if 'status_code' in response and response["status_code"] == 403:
        return JSONResponse({"message": "failed", "desc": response.detail}, status_code=response["status_code"])
    else:
        return JSONResponse({"message": "success", "desc": response}, status_code=200)


@app.post('/login', tags=['Authentication'])
async def login(req: schemas.UserLoginSchema, db: Session = Depends(get_db)):
    existing_user = crud.UsersCrud.check_user(db, req.email, req.password)
    if existing_user:
        return JSONResponse({"message": "success", "desc": auth_handler.signJWT(existing_user.id)}, status_code=200)
    else:
        return JSONResponse({"message": "failed", "desc": "Invalid credentials"}, status_code=400)



@app.get('/fetch_user_details', tags=['Profile'],dependencies = [Depends(auth_bearer.JWTBearer())], response_model=schemas.UserProfileSchema)
def fetch_user_details(current_user: Annotated[schemas.UserProfileSchema, Depends(get_current_active_user)]):
    return current_user

# https://github.com/testdrivenio/fastapi-jwt/blob/main/app/api.py
# https://blog.logrocket.com/handling-user-authentication-redux-toolkit/
