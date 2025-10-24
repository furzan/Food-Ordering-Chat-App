from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import StreamingResponse
from backend.app.db.schemas import user, token
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.app.db.main import get_session
from backend.app.services.user_service import user_service
from backend.app.agents.main import agent_stream_generator
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

router = APIRouter()
userservice = user_service()

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/login")

@router.post('/register', status_code= status.HTTP_201_CREATED, response_model= user)
async def register_user(user_data: user, session: AsyncSession = Depends(get_session)) -> dict:
    new_user = await userservice.create_user(user_data, session)
    return new_user
    

@router.post('/login', status_code= status.HTTP_200_OK, response_model= token)
async def verify_login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)) -> dict:
    is_verified = await userservice.verify_password(form_data, session)
    if not is_verified:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return {"access_token": is_verified, "token_type": "bearer"}


class UserMessage(BaseModel):
    message: str

@router.post('/message', status_code= status.HTTP_200_OK)
async def response_message( username: str, inp: UserMessage) -> dict:
    # response = {"message": f"You said: {inp.message}"}
    return StreamingResponse(
        agent_stream_generator(inp.message, username),
        # Crucially, set the correct media type for a text stream
        media_type="text/plain" 
        # Note: If you wanted full SSE, you'd use 'text/event-stream' 
        # and format the yield output as 'data: <token>\n\n'
    )
    
@router.get('/chat', status_code= status.HTTP_200_OK)
async def get_chat_history( username: str, session: AsyncSession = Depends(get_session)):
    messages = await userservice.get_chat(username, session)
    return messages