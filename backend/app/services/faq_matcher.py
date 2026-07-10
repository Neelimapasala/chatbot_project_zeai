from sqlalchemy.orm import Session
from app import models


def find_faq_match(db: Session, user_query: str):
    query_words = set(w.strip().lower() for w in user_query.split() if len(w) > 3)

    if not query_words:
        return None

    faqs = db.query(models.FAQ).filter(models.FAQ.status == "active").all()

    best_match = None
    best_score = 0

    for faq in faqs:
        question_words = set(faq.question.lower().split())
        score = len(query_words & question_words)
        if score > best_score:
            best_score = score
            best_match = faq

    return best_match if best_score >= 2 else None