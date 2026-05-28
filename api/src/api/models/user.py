from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from api.models.profile import Profile
    from api.models.saved_opportunity import SavedOpportunity
    from api.models.conversation import Conversation
    from api.models.resume import Resume


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True, index=True)
    password_hash: str = Field(nullable=False)
    year_in_school: str = Field(nullable=False)
    major: str = Field(nullable=False)
    university: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    profile: Optional["Profile"] = Relationship(back_populates="user")
    saved_opportunities: list["SavedOpportunity"] = Relationship(back_populates="user")
    conversations: list["Conversation"] = Relationship(back_populates="user")
    resumes: list["Resume"] = Relationship(back_populates="user")