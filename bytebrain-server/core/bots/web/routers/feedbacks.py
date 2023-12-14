from fastapi import APIRouter
from starlette.responses import JSONResponse

from core.bots.web.dependencies import feedback_service
from core.dao.feedback_dao import Feedback

feedbacks_router = router = APIRouter()


@router.post("/feedbacks/", response_model=Feedback)
def create_feedback(feedback: Feedback):
    feedback_service.add_feedback(feedback)
    return JSONResponse(content={"message": "Feedback received"}, status_code=200)
