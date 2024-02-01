from pydantic import BaseModel
from typing import Union, List
from datetime import date


class StrumInputSchema(BaseModel):
    pattern: Union[str, None] = None

    class Config:
        orm_mode = True


class NotesSchema(BaseModel):
    id: Union[int, None] = None
    lyrics_chords: Union[str, None] = None
    title: Union[str, None] = None
    strum: Union[str, None] = None
    capo: Union[int, None] = None
    recording: Union[str, None] = None
    chords: Union[str, None] = None
    created_date: Union[date, None] = None
    user_id: Union[int, None] = None

    class Config:
        orm_mode = True


class AllNotesSchema(BaseModel):
    id: Union[int, None] = None
    title: Union[str, None] = None
    strum: Union[str, None] = None
    capo: Union[int, None] = None
    chords: Union[str, None] = None

    class Config:
        orm_mode = True

class UserSignupSchema(BaseModel):
    id: Union[int, None] = None
    email: Union[str, None] = None
    password: Union[str, None] = None
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    otp:  Union[str, None] = None
    class Config:
        orm_mode = True

class UserLoginSchema(BaseModel):
    email: Union[str, None] = None
    password: Union[str, None] = None

    
    class Config:
        orm_mode = True

class UserProfileSchema(BaseModel):
    id: Union[int, None] = None
    email: Union[str, None] = None
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    notes: NotesSchema = []

    class Config:
        orm_mode = True

class OtpTransactionSchema(BaseModel):
    id: Union[int, None] = None
    email: Union[str, None] = None
    otp:  Union[str, None] = None