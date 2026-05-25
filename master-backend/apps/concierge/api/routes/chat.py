from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from apps.concierge.db.session import get_db
from apps.concierge.db.models.conversation import Conversation, Message
from apps.concierge.api.schemas.chat import ChatRequest, ChatResponse, ConversationOut
from apps.concierge.ai.concierge import generate_response
from apps.concierge.utils.logger import get_logger

router = APIRouter(prefix="/chat", tags=["chat"])
logger = get_logger(__name__)

JOIN_URL = "https://www.pharmacist.com/join"
RENEW_URL = "https://www.pharmacist.com/renew"


def get_or_create_conversation(session_token: str, db: Session, page_url: str = None) -> Conversation:
    conv = db.query(Conversation).filter(Conversation.session_token == session_token).first()
    if not conv:
        conv = Conversation(session_token=session_token, page_url=page_url)
        db.add(conv)
        db.commit()
        db.refresh(conv)
    return conv


@router.post("/", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    conv = get_or_create_conversation(req.session_token, db, req.page_url)

    history = db.query(Message).filter(
        Message.conversation_id == conv.id
    ).order_by(Message.created_at).all()
    history_dicts = [{"role": m.role, "content": m.content} for m in history]

    result = generate_response(
        conversation_history=history_dicts,
        user_message=req.message,
        turn_count=conv.turn_count,
        lead_captured=conv.lead_captured,
    )

    db.add(Message(
        conversation_id=conv.id,
        role="user",
        content=req.message,
        intent=result["intent"],
    ))
    db.add(Message(
        conversation_id=conv.id,
        role="assistant",
        content=result["response"],
        retrieved_chunks=result["chunks_used"],
    ))

    conv.turn_count += 1
    conv.detected_intent = result["intent"]
    if result["tier_recommendation"]:
        conv.recommended_tier = result["tier_recommendation"]
    db.commit()

    join_url = None
    if result["intent"] == "renew":
        join_url = RENEW_URL
    elif result["intent"] == "join" or conv.turn_count >= 4:
        join_url = JOIN_URL

    return ChatResponse(
        session_token=req.session_token,
        response=result["response"],
        intent=result["intent"],
        turn_count=conv.turn_count,
        should_capture_lead=result["should_capture_lead"],
        tier_recommendation=result["tier_recommendation"],
        join_url=join_url,
    )


@router.get("/session/{session_token}", response_model=ConversationOut)
def get_conversation(session_token: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.session_token == session_token).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = db.query(Message).filter(
        Message.conversation_id == conv.id
    ).order_by(Message.created_at).all()
    out = ConversationOut.model_validate(conv)
    out.messages = [m for m in messages]
    return out
