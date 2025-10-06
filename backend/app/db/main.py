from sqlmodel import create_engine, text, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from backend.config import config
from backend.app.db.models.user_model import Users


engine = create_async_engine(
            url= config.DATABASE_URL,
            echo= True
        )
    

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        

async def get_session() -> AsyncSession:
    session = sessionmaker(
        bind= engine,
        class_ = AsyncSession,
        expire_on_commit= False
    )
    
    async with session() as sess:
        yield sess