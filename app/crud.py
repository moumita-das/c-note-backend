from sqlalchemy.orm import Session
from sqlalchemy import and_
from . import models, schemas


class NotesCrud:
    async def create(db: Session, item: schemas.NotesSchema):
        db_item = models.NotesModel(title=item.title, lyrics_chords=item.lyrics_chords,
                                    strum=item.strum, capo=item.capo, recording=item.recording, 
                                    chords=item.chords, created_date=item.created_date, user_id=item.user_id)
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
        db_item = models.OtpTransaction(email=email, otp=otp)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        db.close()
        return db_item

    def verify_otp(db: Session, email, otp):
        db_item = db.query(models.OtpTransaction).filter(and_(
            (models.OtpTransaction.email == email), (models.OtpTransaction.otp == otp))).first()
        db.close()
        return db_item

    async def signup(db: Session, item: schemas.UserSignupSchema):
        db_item = models.UserModel(email=item.email, password=item.password,
                                   first_name=item.first_name, last_name=item.last_name)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        db.close()
        return db_item

    def find_user_by_email(db: Session, email):
        db_item = db.query(models.UserModel).filter(
            models.UserModel.email == email).first()
        db.close()
        return db_item
    
    def find_user_by_id(db: Session, id):
        db_item = db.query(models.UserModel).filter(
            models.UserModel.id == id).first()
        db.close()
        print(db_item)
        return db_item
    
    def check_user(db: Session, email, password):
        db_item = db.query(models.UserModel).filter(and_((email==models.UserModel.email),(password==models.UserModel.password))).first()
        db.close()
        return db_item
