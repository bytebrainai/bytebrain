from typing import Dict

from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.main import BaseModel

from core.bots.web.auth import *
from core.dao.user_dao import UserInDB, UserDao, User

auth_router = router = APIRouter()


@router.get("/users/me/", response_model=User, tags=["Authentication"])
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@router.post("/register", response_model=Dict[str, str], tags=["Authentication"])
async def register(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_dao: Annotated[UserDao, Depends(UserDao)]
):
    existing_user = user_dao.get_user(form_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    hashed_password = get_password_hash(form_data.password)
    user_dao.save_user(UserInDB(username=form_data.username, hashed_password=hashed_password))

    return {"username": form_data.username}


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/token", response_model=Token, tags=['Authentication'])
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_dao: Annotated[UserDao, Depends(UserDao)]
):
    user = authenticate_user(form_data.username, form_data.password, user_dao)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
