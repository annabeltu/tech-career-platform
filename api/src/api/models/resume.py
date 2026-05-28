from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from api.models.user import User


class Resume(SQLModel, table=True):
    __tablename__ = "resumes"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    file_url: str = Field(nullable=False)
    raw_text: str = Field(nullable=False)
    ai_feedback: Optional[str] = Field(default=None, nullable=True)
    ats_score: Optional[int] = Field(default=None, nullable=True)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user: Optional["User"] = Relationship(back_populates="resumes")