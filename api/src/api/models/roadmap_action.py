from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ARRAY, TEXT


class RoadmapAction(SQLModel, table=True):
    __tablename__ = "roadmap_actions"

    id: Optional[int] = Field(default=None, primary_key=True)
    stage: int = Field(nullable=False, index=True)
    title: str = Field(nullable=False)
    description: str = Field(nullable=False)
    action_type: str = Field(nullable=False)
    applicable_years: list[str] = Field(
        default=[], sa_column=Column(ARRAY(TEXT), nullable=False, default=[])
    )