from pydantic import BaseModel
from typing import Union


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

    class Config:
        orm_mode = True

class AllNotesSchema(BaseModel):
    id: Union[int, None] = None
    title: Union[str, None] = None
    strum: Union[str, None] = None
    capo: Union[int, None] = None
    class Config:
        orm_mode = True
