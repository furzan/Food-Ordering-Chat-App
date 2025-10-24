from sqlmodel.ext.asyncio.session import AsyncSession
from backend.app.db.models.user_model import Users
from backend.app.db.models.conversation_msg_model import ConversationMessage
from sqlmodel import select, desc
from backend.app.db.schemas import user
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from jose import JWTError, jwt

bcrypt_context = CryptContext(schemes=["argon2"], deprecated="auto")


class user_service:

    async def create_user(self, user_data: user, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        print("\n\n", user_data_dict, "\n\n")

        raw_pw = user_data_dict.get("password")
        if raw_pw:
            user_data_dict["password"] = bcrypt_context.hash(raw_pw)

        new_user = Users(
            **user_data_dict
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    async def verify_password(self, login_user: user, session: AsyncSession):
        statement = select(Users).where(Users.username == login_user.username)
        result = await session.exec(statement)
        user = result.first()
        if not user:
            return False
        hashed_password = user.password
        plain_password = login_user.password
        if not bcrypt_context.verify(plain_password, hashed_password):
            return False
        
        encode = {'username': user.username}
        expires = datetime.now(timezone.utc) + timedelta(minutes=20)
        encode.update({"exp": expires})
        return jwt.encode(encode, "secret", algorithm="HS256")
    
    async def get_chat(self, username: str, session: AsyncSession):
        statement = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == username)
        )
        result = await session.exec(statement)
        messages = result.all()
        return messages
    