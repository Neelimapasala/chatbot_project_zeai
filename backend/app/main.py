import uuid
from fastapi import FastAPI, Depends, HTTPException, status
from app.auth import verify_password, create_access_token, get_current_admin
from sqlalchemy.orm import Session
from app.database import get_db
from sqlalchemy import func
from typing import List
from app import models, schemas
from fastapi.middleware.cors import CORSMiddleware
from app.services.faq_matcher import find_faq_match
from app.services.rag_placeholder import get_rag_response

app = FastAPI(title="ZeAI Soft Chatbot API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "ZeAI Soft Chatbot API is running"}


@app.get("/faqs")
def get_faqs(db: Session = Depends(get_db)):
    faqs = db.query(models.FAQ).filter(models.FAQ.status == "active").all()
    return [
        {
            "faq_id": faq.faq_id,
            "question": faq.question,
            "answer": faq.answer,
            "category_id": faq.category_id,
        }
        for faq in faqs
    ]
@app.post("/session/start", response_model=schemas.SessionStartResponse)
def start_session(db: Session = Depends(get_db)):
    new_session = models.UserSession(
        session_token=str(uuid.uuid4()),
        status="active",
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return {
        "session_id": new_session.session_id,
        "session_token": new_session.session_token,
    }
@app.post("/admin/login", response_model=schemas.LoginResponse)
def admin_login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.email == request.email).first()

    if not admin or not verify_password(request.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if admin.status != "active":
        raise HTTPException(status_code=403, detail="Admin account is inactive")

    token = create_access_token({"sub": str(admin.admin_id), "role": admin.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "admin_name": admin.name,
    }
@app.post("/admin/faqs", response_model=schemas.FAQResponse)
def create_faq(
    faq: schemas.FAQCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    new_faq = models.FAQ(
        category_id=faq.category_id,
        question=faq.question,
        answer=faq.answer,
        keywords=faq.keywords,
        display_order=faq.display_order,
        created_by=current_admin.admin_id,
    )
    db.add(new_faq)
    db.commit()
    db.refresh(new_faq)
    return new_faq
@app.put("/admin/faqs/{faq_id}", response_model=schemas.FAQResponse)
def update_faq(
    faq_id: int,
    faq_update: schemas.FAQUpdate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    faq = db.query(models.FAQ).filter(models.FAQ.faq_id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    update_data = faq_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(faq, field, value)

    db.commit()
    db.refresh(faq)
    return faq
@app.get("/admin/me")
def get_my_profile(current_admin: models.Admin = Depends(get_current_admin)):
    return {
        "admin_id": current_admin.admin_id,
        "name": current_admin.name,
        "email": current_admin.email,
        "role": current_admin.role,
    }
@app.post("/chat", response_model=schemas.ChatResponse)
def chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    matched_faq = find_faq_match(db, request.query)

    if matched_faq:
        answer = matched_faq.answer
        source = "FAQ"
        source_reference_id = matched_faq.faq_id
    else:
        answer = get_rag_response(request.query)
        source = "RAG"
        source_reference_id = None

    chat_log = models.ChatHistory(
        session_id=request.session_id,
        category_id=matched_faq.category_id if matched_faq else None,
        user_question=request.query,
        bot_response=answer,
        source_type=source,
        source_reference_id=source_reference_id,
        status="resolved",
    )
    db.add(chat_log)
    db.commit()

    return {"response": answer, "source": source}
@app.delete("/admin/faqs/{faq_id}")
def delete_faq(
    faq_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    faq = db.query(models.FAQ).filter(models.FAQ.faq_id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    faq.status = "inactive"
    db.commit()
    return {"message": f"FAQ {faq_id} marked as inactive"}
@app.get("/admin/analytics/summary", response_model=schemas.AnalyticsSummary)
def analytics_summary(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    total = db.query(models.ChatHistory).count()
    faq_count = db.query(models.ChatHistory).filter(models.ChatHistory.source_type == "FAQ").count()
    rag_count = db.query(models.ChatHistory).filter(models.ChatHistory.source_type == "RAG").count()
    fallback_count = db.query(models.ChatHistory).filter(models.ChatHistory.status == "fallback").count()
    resolved_count = db.query(models.ChatHistory).filter(models.ChatHistory.status == "resolved").count()
    escalated_count = db.query(models.ChatHistory).filter(models.ChatHistory.status == "escalated").count()

    return {
        "total_chats": total,
        "faq_count": faq_count,
        "rag_count": rag_count,
        "fallback_count": fallback_count,
        "resolved_count": resolved_count,
        "escalated_count": escalated_count,
    }


@app.get("/admin/analytics/top-questions", response_model=List[schemas.TopQuestion])
def top_questions(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    results = (
        db.query(
            models.ChatHistory.user_question,
            func.count(models.ChatHistory.chat_id).label("times_asked"),
        )
        .group_by(models.ChatHistory.user_question)
        .order_by(func.count(models.ChatHistory.chat_id).desc())
        .limit(limit)
        .all()
    )
    return [{"user_question": q, "times_asked": c} for q, c in results]


@app.get("/admin/analytics/daily-volume", response_model=List[schemas.DailyVolume])
def daily_volume(
    days: int = 7,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    results = (
        db.query(
            func.date(models.ChatHistory.created_at).label("date"),
            func.count(models.ChatHistory.chat_id).label("count"),
        )
        .group_by(func.date(models.ChatHistory.created_at))
        .order_by(func.date(models.ChatHistory.created_at).desc())
        .limit(days)
        .all()
    )
    return [{"date": str(d), "count": c} for d, c in results]
@app.get("/admin/chat-history")
def get_chat_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    logs = (
        db.query(models.ChatHistory)
        .order_by(models.ChatHistory.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "chat_id": log.chat_id,
            "session_id": log.session_id,
            "user_question": log.user_question,
            "bot_response": log.bot_response,
            "source_type": log.source_type,
            "status": log.status,
            "created_at": log.created_at,
        }
        for log in logs
    ]
