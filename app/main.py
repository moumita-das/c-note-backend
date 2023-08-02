from fastapi import FastAPI, APIRouter
from routers import (songs)

app = FastAPI()
router = APIRouter(prefix='/api')


@app.get('/')
async def root():
    return {'message': 'Hello World'}
app.include_router(router)
app.include_router(songs.router)
