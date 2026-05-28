from api.routes.auth import router as auth_router
from api.routes.profile import router as profile_router
from api.routes.roadmap import router as roadmap_router
from api.routes.opportunities import router as opportunities_router
from api.routes.resumes import router as resumes_router
from api.routes.conversations import router as conversations_router

API_ROUTERS = [
    auth_router,
    profile_router,
    roadmap_router,
    opportunities_router,
    resumes_router,
    conversations_router,
]