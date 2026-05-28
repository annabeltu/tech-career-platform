from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from api.database import get_session
from api.security import get_current_user, require_same_user
from api.models.user import User
from api.models.profile import Profile
from api.schemas import (
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
    ProfileUpdateResponse,
)

router = APIRouter(prefix="/waypoint/users", tags=["Profile"])

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/{user_id}/profile", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(user_id: int, body: ProfileCreate, session: SessionDep, current_user: CurrentUser):
    require_same_user(user_id, current_user)

    existing = session.exec(select(Profile).where(Profile.user_id == user_id)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile already exists. Use PUT to update.")

    profile = Profile(
        user_id=user_id,
        tech_interests=body.tech_interests,
        blind_spots=body.blind_spots,
        experience_level=body.experience_level,
    )
    session.add(profile)
    session.commit()
    session.refresh(profile)

    return ProfileResponse(
        success=True,
        message="Profile created successfully.",
        user_id=user_id,
        tech_interests=profile.tech_interests,
        blind_spots=profile.blind_spots,
        experience_level=profile.experience_level,
        roadmap_stage=profile.roadmap_stage,
        profile_complete=profile.profile_complete,
    )


@router.get("/{user_id}/profile", response_model=ProfileResponse)
def get_profile(user_id: int, session: SessionDep, current_user: CurrentUser):
    require_same_user(user_id, current_user)

    profile = session.exec(select(Profile).where(Profile.user_id == user_id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

    return ProfileResponse(
        success=True,
        message="Profile retrieved.",
        user_id=user_id,
        tech_interests=profile.tech_interests,
        blind_spots=profile.blind_spots,
        experience_level=profile.experience_level,
        roadmap_stage=profile.roadmap_stage,
        profile_complete=profile.profile_complete,
    )


@router.put("/{user_id}/profile", response_model=ProfileUpdateResponse)
def update_profile(user_id: int, body: ProfileUpdate, session: SessionDep, current_user: CurrentUser):
    require_same_user(user_id, current_user)

    profile = session.exec(select(Profile).where(Profile.user_id == user_id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found. Create it first.")

    profile.tech_interests = body.tech_interests
    profile.blind_spots = body.blind_spots
    profile.experience_level = body.experience_level
    if body.linkedin_url is not None:
        profile.linkedin_url = body.linkedin_url
    profile.updated_at = datetime.utcnow()

    session.add(profile)
    session.commit()

    return ProfileUpdateResponse(
        success=True,
        message="Profile updated successfully.",
        user_id=user_id,
        updated_at=profile.updated_at,
    )