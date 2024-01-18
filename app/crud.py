from sqlalchemy.orm import Session
from sqlalchemy import and_
from . import models, schemas


class NotesCrud:
    async def create(db: Session, item: schemas.NotesSchema):
        db_item = models.NotesModel(title=item.title, lyrics_chords=item.lyrics_chords,
                                    strum=item.strum, capo=item.capo, recording=item.recording, chords=item.chords)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    def fetch_by_id(db: Session, _id):
        return db.query(models.NotesModel).filter(models.NotesModel.id == _id).first()

    def fetch_by_title(db: Session, title):
        return db.query(models.NotesModel).filter(models.NotesModel.name == title).first()

    def fetch_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.NotesModel).all()

class UsersCrud:
    async def record_otp(db: Session, email, otp):
        db_item = models.OtpTransaction(email = email, otp = otp)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    
    def verify_otp(db:Session, email,otp):
        print(email)
        db_item = db.query(models.OtpTransaction).filter(and_((models.OtpTransaction.email == email),(models.OtpTransaction.otp == otp))).first()
        print('+++++')
        print(db_item)
        print('-----')

    async def signup(db: Session, item: schemas.UserSignupSchema):
        db_item = models.UserModel(email = item.email, password = item.password, first_name = item.first_name, last_name = item.last_name)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item