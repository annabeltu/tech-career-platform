from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    year_in_school: str
    major: str
    university: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    success: bool
    message: str
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    success: bool
    message: str
    id: int
    name: str
    email: str
    year_in_school: str
    created_at: datetime


# ── Profile ───────────────────────────────────────────────────────────────────

class ProfileCreate(BaseModel):
    tech_interests: list[str]
    blind_spots: list[str]
    experience_level: str


class ProfileUpdate(BaseModel):
    tech_interests: list[str]
    blind_spots: list[str]
    experience_level: str
    linkedin_url: Optional[str] = None


class ProfileResponse(BaseModel):
    success: bool
    message: str
    user_id: int
    tech_interests: list[str]
    blind_spots: list[str]
    experience_level: str
    roadmap_stage: int
    profile_complete: bool


class ProfileUpdateResponse(BaseModel):
    success: bool
    message: str
    user_id: int
    updated_at: datetime


# ── Roadmap ───────────────────────────────────────────────────────────────────

class RoadmapStageUpdate(BaseModel):
    roadmap_stage: int


class RoadmapActionOut(BaseModel):
    stage: int
    title: str
    description: str
    action_type: str
    completed: bool


class RoadmapResponse(BaseModel):
    success: bool
    message: str
    user_id: int
    current_stage: int
    actions: list[RoadmapActionOut]


class RoadmapStageResponse(BaseModel):
    success: bool
    message: str
    user_id: int
    roadmap_stage: int


# ── Opportunities ─────────────────────────────────────────────────────────────

class OpportunityOut(BaseModel):
    id: int
    title: str
    company: str
    type: str
    eligibility: str
    is_paid: bool
    deadline: Optional[datetime]
    application_url: str


class OpportunitiesResponse(BaseModel):
    success: bool
    message: str
    count: int
    opportunities: list[OpportunityOut]


class OpportunityDetailResponse(BaseModel):
    success: bool
    message: str
    id: int
    title: str
    company: str
    type: str
    description: str
    eligibility: str
    experience_required: str
    is_paid: bool
    deadline: Optional[datetime]
    location: Optional[str]
    application_url: str


# ── Saved Opportunities ───────────────────────────────────────────────────────

class SaveOpportunity(BaseModel):
    opportunity_id: int
    deadline_reminder: bool = False


class SaveOpportunityResponse(BaseModel):
    success: bool
    message: str
    user_id: int
    opportunity_id: int
    deadline_reminder: bool
    saved_at: datetime


class SavedOpportunityOut(BaseModel):
    id: int
    opportunity_id: int
    saved_at: datetime
    deadline_reminder: bool


class SavedOpportunitiesResponse(BaseModel):
    success: bool
    message: str
    count: int
    saved_opportunities: list[SavedOpportunityOut]


class DeleteResponse(BaseModel):
    success: bool
    message: str
    opportunity_id: Optional[int] = None
    conversation_id: Optional[int] = None


# ── Resumes ───────────────────────────────────────────────────────────────────

class ResumeUpload(BaseModel):
    raw_text: str


class ResumeUploadResponse(BaseModel):
    success: bool
    message: str
    id: int
    user_id: int
    file_url: str
    uploaded_at: datetime


class ResumeFeedbackResponse(BaseModel):
    success: bool
    message: str
    resume_id: int
    ats_score: int
    ai_feedback: str


class ResumeGetResponse(BaseModel):
    success: bool
    message: str
    id: int
    file_url: str
    ats_score: Optional[int]
    ai_feedback: Optional[str]
    uploaded_at: datetime


# ── Conversations ─────────────────────────────────────────────────────────────

class ConversationCreate(BaseModel):
    title: str


class ConversationOut(BaseModel):
    id: int
    title: str
    created_at: datetime


class ConversationResponse(BaseModel):
    success: bool
    message: str
    id: int
    user_id: int
    title: str
    created_at: datetime


class ConversationsListResponse(BaseModel):
    success: bool
    message: str
    conversations: list[ConversationOut]


# ── Messages ──────────────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime


class MessageResponse(BaseModel):
    success: bool
    message: str
    conversation_id: int
    user_message: str
    ai_response: str
    created_at: datetime


class MessagesListResponse(BaseModel):
    success: bool
    message: str
    conversation_id: int
    messages: list[MessageOut]