from datetime import datetime
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from api.database import get_session
from api.security import get_current_user, require_same_user
from api.models.user import User
from api.models.opportunity import Opportunity
from api.models.saved_opportunity import SavedOpportunity
from api.schemas import (
    SaveOpportunity,
    SaveOpportunityResponse,
    SavedOpportunityOut,
    SavedOpportunitiesResponse,
    OpportunitiesResponse,
    OpportunityDetailResponse,
    OpportunityOut,
    DeleteResponse,
)

router = APIRouter(tags=["Opportunities"])

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/waypoint/opportunities", response_model=OpportunitiesResponse)
def list_opportunities(
    session: SessionDep,
    current_user: CurrentUser,
    type: Optional[str] = Query(None),
    experience_required: Optional[str] = Query(None),
    eligibility: Optional[str] = Query(None),
    is_paid: Optional[bool] = Query(None),
    deadline_before: Optional[datetime] = Query(None),
):
    query = select(Opportunity).where(Opportunity.is_active == True)

    if type:
        query = query.where(Opportunity.type == type)
    if experience_required:
        query = query.where(Opportunity.experience_required == experience_required)
    if eligibility:
        query = query.where(Opportunity.eligibility == eligibility)
    if is_paid is not None:
        query = query.where(Opportunity.is_paid == is_paid)
    if deadline_before:
        query = query.where(Opportunity.deadline <= deadline_before)

    opportunities = session.exec(query).all()

    return OpportunitiesResponse(
        success=True,
        message="Opportunities retrieved.",
        count=len(opportunities),
        opportunities=[
            OpportunityOut(
                id=o.id,
                title=o.title,
                company=o.company,
                type=o.type,
                eligibility=o.eligibility,
                is_paid=o.is_paid,
                deadline=o.deadline,
                application_url=o.application_url,
            )
            for o in opportunities
        ],
    )


@router.get("/waypoint/opportunities/{opportunity_id}", response_model=OpportunityDetailResponse)
def get_opportunity(opportunity_id: int, session: SessionDep, current_user: CurrentUser):
    opp = session.get(Opportunity, opportunity_id)
    if not opp or not opp.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found.")

    return OpportunityDetailResponse(
        success=True,
        message="Opportunity retrieved.",
        id=opp.id,
        title=opp.title,
        company=opp.company,
        type=opp.type,
        description=opp.description,
        eligibility=opp.eligibility,
        experience_required=opp.experience_required,
        is_paid=opp.is_paid,
        deadline=opp.deadline,
        location=opp.location,
        application_url=opp.application_url,
    )


@router.post("/waypoint/users/{user_id}/saved-opportunities", response_model=SaveOpportunityResponse, status_code=status.HTTP_201_CREATED)
def save_opportunity(user_id: int, body: SaveOpportunity, session: SessionDep, current_user: CurrentUser):
    require_same_user(user_id, current_user)

    opp = session.get(Opportunity, body.opportunity_id)
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found.")

    already_saved = session.exec(
        select(SavedOpportunity)
        .where(SavedOpportunity.user_id == user_id)
        .where(SavedOpportunity.opportunity_id == body.opportunity_id)
    ).first()
    if already_saved:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Opportunity already saved.")

    saved = SavedOpportunity(
        user_id=user_id,
        opportunity_id=body.opportunity_id,
        deadline_reminder=body.deadline_reminder,
    )
    session.add(saved)
    session.commit()
    session.refresh(saved)

    return SaveOpportunityResponse(
        success=True,
        message="Opportunity saved.",
        user_id=user_id,
        opportunity_id=saved.opportunity_id,
        deadline_reminder=saved.deadline_reminder,
        saved_at=saved.saved_at,
    )


@router.get("/waypoint/users/{user_id}/saved-opportunities", response_model=SavedOpportunitiesResponse)
def get_saved_opportunities(user_id: int, session: SessionDep, current_user: CurrentUser):
    require_same_user(user_id, current_user)

    saved = session.exec(
        select(SavedOpportunity).where(SavedOpportunity.user_id == user_id)
    ).all()

    return SavedOpportunitiesResponse(
        success=True,
        message="Saved opportunities retrieved.",
        count=len(saved),
        saved_opportunities=[
            SavedOpportunityOut(
                id=s.id,
                opportunity_id=s.opportunity_id,
                saved_at=s.saved_at,
                deadline_reminder=s.deadline_reminder,
            )
            for s in saved
        ],
    )


@router.delete("/waypoint/users/{user_id}/saved-opportunities/{opportunity_id}", response_model=DeleteResponse)
def delete_saved_opportunity(user_id: int, opportunity_id: int, session: SessionDep, current_user: CurrentUser):
    require_same_user(user_id, current_user)

    saved = session.exec(
        select(SavedOpportunity)
        .where(SavedOpportunity.user_id == user_id)
        .where(SavedOpportunity.opportunity_id == opportunity_id)
    ).first()

    if not saved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved opportunity not found.")

    session.delete(saved)
    session.commit()

    return DeleteResponse(
        success=True,
        message="Opportunity removed from saved list.",
        opportunity_id=opportunity_id,
    )