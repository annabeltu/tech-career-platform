from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from api.database import get_session
from api.security import get_current_user, require_same_user
from api.models.user import User
from api.models.profile import Profile
from api.models.conversation import Conversation
from api.models.message import Message
from api.schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationsListResponse,
    ConversationOut,
    MessageCreate,
    MessageResponse,
    MessagesListResponse,
    MessageOut,
    DeleteResponse,
)
from core.config import get_settings

router = APIRouter(prefix="/waypoint/users", tags=["AI Mentor"])

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
settings = get_settings()


@router.post("/{user_id}/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def start_conversation(user_id: int, body: ConversationCreate, session: SessionDep, current_user: CurrentUser):
    require_same_user(user_id, current_user)

    convo = Conversation(user_id=user_id, title=body.title)
    session.add(convo)
    session.commit()
    session.refresh(convo)

    return ConversationResponse(
        success=True,
        message="Conversation started.",
        id=convo.id,
        user_id=user_id,
        title=convo.title,
        created_at=convo.created_at,
    )


@router.post("/{user_id}/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    user_id: int,
    conversation_id: int,
    body: MessageCreate,
    session: SessionDep,
    current_user: CurrentUser,
):
    require_same_user(user_id, current_user)

    convo = session.get(Conversation, conversation_id)
    if not convo or convo.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    user_msg = Message(conversation_id=conversation_id, role="user", content=body.content)
    session.add(user_msg)
    session.commit()
    session.refresh(user_msg)

    history = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    ).all()

    profile = session.exec(select(Profile).where(Profile.user_id == user_id)).first()
    ai_response = _call_openai_mentor(current_user, profile, history)

    ai_msg = Message(conversation_id=conversation_id, role="assistant", content=ai_response)
    session.add(ai_msg)
    session.commit()
    session.refresh(ai_msg)

    return MessageResponse(
        success=True,
        message="Message sent.",
        conversation_id=conversation_id,
        user_message=body.content,
        ai_response=ai_response,
        created_at=ai_msg.created_at,
    )


@router.get("/{user_id}/conversations", response_model=ConversationsListResponse)
def list_conversations(user_id: int, session: SessionDep, current_user: CurrentUser):
    require_same_user(user_id, current_user)

    convos = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
    ).all()

    return ConversationsListResponse(
        success=True,
        message="Conversations retrieved.",
        conversations=[ConversationOut(id=c.id, title=c.title, created_at=c.created_at) for c in convos],
    )


@router.get("/{user_id}/conversations/{conversation_id}/messages", response_model=MessagesListResponse)
def get_messages(user_id: int, conversation_id: int, session: SessionDep, current_user: CurrentUser):
    require_same_user(user_id, current_user)

    convo = session.get(Conversation, conversation_id)
    if not convo or convo.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    ).all()

    return MessagesListResponse(
        success=True,
        message="Messages retrieved.",
        conversation_id=conversation_id,
        messages=[MessageOut(id=m.id, role=m.role, content=m.content, created_at=m.created_at) for m in messages],
    )


@router.delete("/{user_id}/conversations/{conversation_id}", response_model=DeleteResponse)
def delete_conversation(user_id: int, conversation_id: int, session: SessionDep, current_user: CurrentUser):
    require_same_user(user_id, current_user)

    convo = session.get(Conversation, conversation_id)
    if not convo or convo.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    messages = session.exec(select(Message).where(Message.conversation_id == conversation_id)).all()
    for m in messages:
        session.delete(m)
    session.delete(convo)
    session.commit()

    return DeleteResponse(
        success=True,
        message="Conversation deleted.",
        conversation_id=conversation_id,
    )


def _call_openai_mentor(user: User, profile: Profile | None, history: list[Message]) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)

    interests = ", ".join(profile.tech_interests) if profile else "not specified"
    blind_spots = ", ".join(profile.blind_spots) if profile else "not specified"
    experience = profile.experience_level if profile else "No Experience"

    system_prompt = (
        "You are Waypoint, an AI career mentor for college students breaking into tech. "
        "You speak plainly and tailor advice to where the student actually is.\n\n"
        f"Student profile:\n"
        f"- Name: {user.name}\n"
        f"- Year: {user.year_in_school} at {user.university}\n"
        f"- Major: {user.major}\n"
        f"- Tech interests: {interests}\n"
        f"- Experience level: {experience}\n"
        f"- Blind spots: {blind_spots}\n\n"
        "Give direct, honest answers appropriate for their stage. "
        "Never assume they already know how recruiting works."
    )

    openai_messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        openai_messages.append({"role": msg.role, "content": msg.content})

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=openai_messages,
    )

    return response.choices[0].message.content