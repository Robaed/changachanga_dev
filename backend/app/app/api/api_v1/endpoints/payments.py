import logging

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/notification")
async def mpesa_express_checkout_callback(
        *,
        apiKey: str = Depends(deps.get_api_key),
        data: dict,
        db: AsyncSession = Depends(deps.get_db),
):
    print("received data %s" % data)
    raise HTTPException(500, detail="Method not implemented")
