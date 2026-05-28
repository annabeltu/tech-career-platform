from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from api.models.saved_opportunity import SavedOpportunity


class Opportunity(SQLModel, table=True):
    __tablename__ = "opportunities"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    company: str = Field(nullable=False)
    type: str = Field(nullable=False)
    description: str = Field(nullable=False)
    eligibility: str = Field(nullable=False)
    experience_required: str = Field(nullable=False)
    is_paid: bool = Field(nullable=False)
    deadline: Optional[datetime] = Field(default=None, nullable=True)
    location: Optional[str] = Field(default=None, nullable=True)
    application_url: str = Field(nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    saved_opportunities: list["SavedOpportunity"] = Relationship(back_populates="opportunity")