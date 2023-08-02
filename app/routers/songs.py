from fastapi import APIRouter

router = APIRouter(prefix='/songs')

@router.get('/')
async def get_song_list():
    return {
        'song_list':'all songs'
    }
    
@router.post('/upload')
async def upload_song():
    return None