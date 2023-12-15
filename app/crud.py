from sqlalchemy.orm import Session
from . import models, schemas


class NotesCrud:
    async def create(db: Session, item: schemas.NotesSchema):
        print(item)
        db_item = models.NotesModel(title=item.title, lyrics_chords=item.lyrics_chords,
                                    strum=item.strum, capo=item.capo, recording=item.recording)
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
