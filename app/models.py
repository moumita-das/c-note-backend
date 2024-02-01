from sqlalchemy import Column, ForeignKey, Integer, String, Date
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
    chords = Column(String)
    created_date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserModel", back_populates = "notes")


class UserModel(Base):
    __tablename__='users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100))
    password = Column(String(100))
    first_name = Column(String(50))
    last_name = Column(String(50))
    notes = relationship(
        "NotesModel",
        cascade="all, delete-orphan",
        back_populates="user",
        uselist=True,
        lazy='subquery'
    )

class OtpTransaction(Base):
    __tablename__='otp_transactions'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100))
    otp = Column(String(7))