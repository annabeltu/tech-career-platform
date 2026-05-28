from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ARRAY, TEXT

if TYPE_CHECKING:
    from api.models.user import User


class Profile(SQLModel, table=True):
    __tablename__ = "profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, unique=True, index=True)
    tech_interests: list[str] = Field(
        default=[], sa_column=Column(ARRAY(TEXT), nullable=False, default=[])
    )
    blind_spots: list[str] = Field(
        default=[], sa_column=Column(ARRAY(TEXT), nullable=False, default=[])
    )
    experience_level: str = Field(nullable=False)
    resume_url: Optional[str] = Field(default=None, nullable=True)
    linkedin_url: Optional[str] = Field(default=None, nullable=True)
    roadmap_stage: int = Field(default=1, nullable=False)
    profile_complete: bool = Field(default=False, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user: Optional["User"] = Relationship(back_populates="profile")