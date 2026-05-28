from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from api.database import get_session
from api.security import get_current_user, require_same_user
from api.models.user import User
from api.models.resume import Resume
from api.models.profile import Profile
from api.schemas import (
    ResumeUpload,
    ResumeUploadResponse,
    ResumeFeedbackResponse,
    ResumeGetResponse,
)
from core.config import get_settings

router = APIRouter(prefix="/waypoint/users", tags=["Resumes"])

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
settings = get_settings()


@router.post("/{user_id}/resumes", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_resume(user_id: int, body: ResumeUpload, session: SessionDep, current_user: CurrentUser):
    require_same_user(user_id, current_user)

    resume = Resume(
        user_id=user_id,
        file_url=f"/resumes/{user_id}/latest.pdf",
        raw_text=body.raw_text,
    )
    session.add(resume)
    session.commit()
    session.refresh(resume)

    profile = session.exec(select(Profile).where(Profile.user_id == user_id)).first()
    if profile:
        profile.resume_url = resume.file_url
        session.add(profile)
        session.commit()

    return ResumeUploadResponse(
        success=True,
        message="Resume uploaded successfully.",
        id=resume.id,
        user_id=user_id,
        file_url=resume.file_url,
        uploaded_at=resume.uploaded_at,
    )


@router.post("/{user_id}/resumes/{resume_id}/feedback", response_model=ResumeFeedbackResponse)
def generate_feedback(user_id: int, resume_id: int, session: SessionDep, current_user: CurrentUser):
    require_same_user(user_id, current_user)

    resume = session.get(Resume, resume_id)
    if not resume or resume.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

    profile = session.exec(select(Profile).where(Profile.user_id == user_id)).first()
    experience_level = profile.experience_level if profile else "No Experience"

    feedback, ats_score = _call_openai_for_feedback(
        resume.raw_text, experience_level, current_user.year_in_school
    )

    resume.ai_feedback = feedback
    resume.ats_score = ats_score
    session.add(resume)
    session.commit()

    return ResumeFeedbackResponse(
        success=True,
        message="Resume feedback generated.",
        resume_id=resume_id,
        ats_score=ats_score,
        ai_feedback=feedback,
    )


@router.get("/{user_id}/resumes/{resume_id}", response_model=ResumeGetResponse)
def get_resume(user_id: int, resume_id: int, session: SessionDep, current_user: CurrentUser):
    require_same_user(user_id, current_user)

    resume = session.get(Resume, resume_id)
    if not resume or resume.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

    return ResumeGetResponse(
        success=True,
        message="Resume retrieved.",
        id=resume.id,
        file_url=resume.file_url,
        ats_score=resume.ats_score,
        ai_feedback=resume.ai_feedback,
        uploaded_at=resume.uploaded_at,
    )


def _call_openai_for_feedback(raw_text: str, experience_level: str, year: str) -> tuple[str, int]:
    import json
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)

    system_prompt = (
        f"You are Waypoint's AI career mentor specializing in helping {year}s "
        f"with {experience_level} break into tech. Review the resume and return "
        "JSON with two keys: 'feedback' (string) and 'ats_score' (int 0-100)."
    )

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Review this resume:\n\n{raw_text}"},
        ],
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return result.get("feedback", ""), int(result.get("ats_score", 0))