import os
import uuid
from typing import Dict

import httpx
from fastapi import APIRouter
from fastapi import Query
from fastapi.param_functions import Form
from pydantic.main import BaseModel

from core.bots.web.auth import *
from core.dao.user_dao import UserInDB, UserDao

auth_router = router = APIRouter()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

USER_ID_NAMESPACE = uuid.UUID('9890c20b-f752-4807-a8ea-8b05fa466d6a')


class OAuth2PasswordRequestForm:
    def __init__(
            self,
            grant_type: str = Form(default=None, regex="password"),
            username: str = Form(),
            password: str = Form(),
            full_name: Optional[str] = Form(default=None),
            scope: str = Form(default=""),
            client_id: Optional[str] = Form(default=None),
            client_secret: Optional[str] = Form(default=None),
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.full_name = full_name
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


@router.post("/auth/signup", response_model=Dict[str, str], tags=["Authentication"])
async def register(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_dao: Annotated[UserDao, Depends(UserDao)]
):
    existing_user = user_dao.get_user(form_data.username)  # TODO: use email instead of username
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user is already registered",
        )

    hashed_password = get_password_hash(form_data.password)
    user_dao.save_user(
        UserInDB(
            id=str(uuid.uuid4()),
            email=form_data.username,  # TODO: use email instead of username
            full_name=form_data.full_name,
            enabled=False,
            hashed_password=hashed_password
        )
    )
    return create_access_token_by_email(form_data.username)


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/auth/access_token", response_model=Token, tags=['Authentication'])
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_dao: Annotated[UserDao, Depends(UserDao)]
):
    user = authenticate_user(
        form_data.username,  # TODO: use email instead of username
        form_data.password,
        user_dao
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_access_token_by_email(user.email)


@router.get("/auth/github/access_token", tags=["Authorization"])
async def get_access_token(
        user_dao: Annotated[UserDao, Depends(UserDao)],
        code: str = Query(...),
):
    github_access_token = await get_github_access_token(code)
    github_user = await get_user_data_from_github(f"Bearer {github_access_token}")
    email = github_user['email']
    user = user_dao.get_user(email)
    if user is None:
        user_dao.save_user(
            UserInDB(
                id=str(uuid.uuid5(namespace=USER_ID_NAMESPACE, name=email)),
                email=email,
                full_name=github_user['name'],
                enabled=True,
                hashed_password=None
            )
        )
    return create_access_token_by_email(email)


async def get_user_data_from_github(authorization: str):
    url = f"https://api.github.com/user"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers={
            "Authorization": authorization
        })
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error calling API: {response.status_code}")


async def get_github_access_token(code: str) -> str:
    url = f"https://github.com/login/oauth/access_token"
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, headers={
            "Accept": "application/json"
        })
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            raise Exception(f"Error calling Github API: {response.status_code}")
