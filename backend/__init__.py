from fastapi import FastAPI
from backend.app.api.user_routes import router 
from contextlib import asynccontextmanager
from backend.app.db.main import init_db

@asynccontextmanager
async def life_span(app: FastAPI):
    await init_db()
    print('server is starting=================|')
    yield
    print('server has been stoped=================|')

version  = 'v1'
app = FastAPI(
    title= "Food app",
    description= "rest api for food ordering system", 
    version= version,
    lifespan= life_span
) 

app.include_router(router, prefix=f"/api/{version}/user")