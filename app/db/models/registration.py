# models/registration.py
from datetime import datetime
from app.db.db import db

class Registration(db.Model):
    __tablename__ = "registrations"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    athlete_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # novo campo


    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    athlete = db.relationship("User", foreign_keys=[athlete_id], backref="registrations_as_athlete")
    partner = db.relationship("User", foreign_keys=[partner_id], backref="registrations_as_partner")
    event = db.relationship("Event", backref="registrations")
    category = db.relationship("Category", backref="registrations")

