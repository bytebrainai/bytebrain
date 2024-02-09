# Copyright 2023-2024 ByteBrain AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fastapi import APIRouter

from core.bots.web.auth import *
from core.dao.user_dao import User

users_router = router = APIRouter()


@router.get("/users/me", response_model=User, tags=["Authentication"])
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user
