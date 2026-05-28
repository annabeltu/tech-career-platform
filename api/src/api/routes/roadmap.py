from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from api.database import get_session
from api.security import get_current_user, require_same_user
from api.models.user import User
from api.models.profile import Profile
from api.models.roadmap_action import RoadmapAction
from api.schemas import (
    RoadmapStageUpdate,
    RoadmapActionOut,
    RoadmapResponse,
    RoadmapStageResponse,
)

router = APIRouter(prefix="/waypoint/users", tags=["Roadmap"])

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/{user_id}/roadmap", response_model=RoadmapResponse)
def get_roadmap(user_id: int, session: SessionDep, current_user: CurrentUser):
    require_same_user(user_id, current_user)

    profile = session.exec(select(Profile).where(Profile.user_id == user_id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found. Complete onboarding first.")

    all_actions = session.exec(select(RoadmapAction)).all()

    actions_out = [
        RoadmapActionOut(
            stage=a.stage,
            title=a.title,
            description=a.description,
            action_type=a.action_type,
            completed=a.stage < profile.roadmap_stage,
        )
        for a in sorted(all_actions, key=lambda x: x.stage)
        if current_user.year_in_school.strip().capitalize() in a.applicable_years
    ]

    return RoadmapResponse(
        success=True,
        message="Roadmap retrieved.",
        user_id=user_id,
        current_stage=profile.roadmap_stage,
        actions=actions_out,
    )


@router.put("/{user_id}/roadmap/stage", response_model=RoadmapStageResponse)
def update_roadmap_stage(user_id: int, body: RoadmapStageUpdate, session: SessionDep, current_user: CurrentUser):
    require_same_user(user_id, current_user)

    profile = session.exec(select(Profile).where(Profile.user_id == user_id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

    if body.roadmap_stage < profile.roadmap_stage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot move to a previous stage.")

    profile.roadmap_stage = body.roadmap_stage
    session.add(profile)
    session.commit()

    return RoadmapStageResponse(
        success=True,
        message="Roadmap stage updated.",
        user_id=user_id,
        roadmap_stage=profile.roadmap_stage,
    )