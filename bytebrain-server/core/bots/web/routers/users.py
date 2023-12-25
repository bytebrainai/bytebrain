from fastapi import APIRouter

from core.bots.web.auth import *
from core.dao.user_dao import User

users_router = router = APIRouter()


@router.get("/users/me/", response_model=User, tags=["Authentication"])
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@router.get("/getUserData", tags=["Authorization"])
async def get_user_data(
        current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user
