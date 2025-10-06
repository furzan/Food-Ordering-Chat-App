from fastapi import APIRouter, status, Depends, HTTPException
from backend.app.db.schemas import user, token
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.app.db.main import get_session
from backend.app.services.user_service import user_service
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

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