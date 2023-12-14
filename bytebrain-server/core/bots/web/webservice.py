import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from structlog import getLogger

from config import load_config
from core.bots.web.dependencies import feedback_service
from core.bots.web.routers.auth import auth_router
from core.bots.web.routers.chat import chat_router
from core.bots.web.routers.projects import projects_router
from core.bots.web.routers.resources import resources_router
from core.dao.feedback_dao import Feedback

app = FastAPI()
app.include_router(auth_router)
app.include_router(resources_router)
app.include_router(projects_router)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
log = getLogger()

# Configuration setup
config = load_config()


@app.post("/feedback/", response_model=Feedback)
def create_feedback(feedback: Feedback):
    feedback_service.add_feedback(feedback)
    return JSONResponse(content={"message": "Feedback received"}, status_code=200)


# Main function
def main():
    uvicorn.run(app, host=config.webservice.host, port=config.webservice.port, reload=False)


if __name__ == "__main__":
    main()
