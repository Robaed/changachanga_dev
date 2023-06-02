from fastapi import APIRouter

from app.api.api_v1.endpoints import login, users, accounts, channels, payments

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(channels.router, prefix="/channels", tags=["channels"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])