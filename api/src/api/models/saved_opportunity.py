from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from api.models.user import User
    from api.models.opportunity import Opportunity


class SavedOpportunity(SQLModel, table=True):
    __tablename__ = "saved_opportunities"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    opportunity_id: int = Field(foreign_key="opportunities.id", nullable=False, index=True)
    saved_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    deadline_reminder: bool = Field(default=False, nullable=False)

    user: Optional["User"] = Relationship(back_populates="saved_opportunities")
    opportunity: Optional["Opportunity"] = Relationship(back_populates="saved_opportunities")