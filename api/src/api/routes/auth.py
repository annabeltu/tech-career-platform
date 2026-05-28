from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from api.database import get_session
from api.security import hash_password, verify_password, create_access_token
from api.models.user import User
from api.schemas import UserRegister, RegisterResponse, UserLogin, TokenResponse

router = APIRouter(prefix="/waypoint/auth", tags=["Auth"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(body: UserRegister, session: SessionDep):
    existing = session.exec(select(User).where(User.email == body.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with that email already exists.",
        )

    user = User(
        name=body.name,
        email=body.email,
        password_hash=hash_password(body.password),
        year_in_school=body.year_in_school,
        major=body.major,
        university=body.university,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return RegisterResponse(
        success=True,
        message="Account created successfully.",
        id=user.id,
        name=user.name,
        email=user.email,
        year_in_school=user.year_in_school,
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse)
def login(body: UserLogin, session: SessionDep):
    user = session.exec(select(User).where(User.email == body.email)).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(user.id)
    return TokenResponse(
        success=True,
        message="Login successful.",
        access_token=token,
        token_type="bearer",
    )