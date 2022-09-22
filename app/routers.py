
from fastapi import APIRouter
from endpoints import main_router

api_router = APIRouter()
api_router.include_router(main_router,  tags=["main"])
