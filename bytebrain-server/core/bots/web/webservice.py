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

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import load_config
from core.bots.web.routers.auth import auth_router
from core.bots.web.routers.users import users_router
from core.bots.web.routers.chat import chat_router
from core.bots.web.routers.feedbacks import feedbacks_router
from core.bots.web.routers.projects import projects_router
from core.bots.web.routers.resources import resources_router

app = FastAPI()
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(resources_router)
app.include_router(projects_router)
app.include_router(chat_router)
app.include_router(feedbacks_router)

origins = ['http://localhost:5173']

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    config = load_config()
    uvicorn.run(app, host=config.webservice.host, port=config.webservice.port, reload=False)


if __name__ == "__main__":
    main()
