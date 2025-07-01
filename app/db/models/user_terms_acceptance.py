# models/user_terms_acceptance.py
from datetime import datetime
from app.db.db import db


class UserTermsAcceptance(db.Model):
    __tablename__ = "user_terms_acceptance"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, nullable=False)
    accepted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # (opcional) evitar duplicidade de aceite por usuário por evento
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='_user_event_uc'),)
