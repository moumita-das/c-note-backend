from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from .db import Base


class NotesModel(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    lyrics_chords = Column(String, nullable=False)
    strum = Column(String(100))
    capo = Column(Integer)
    recording = Column(String)
