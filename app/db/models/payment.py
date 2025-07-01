# models/payment.py

from datetime import datetime

from app.db.db import db

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # ou nullable=False, se quiser forçar parceiro sempre
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    payment_id = db.Column(db.String, nullable=False)
    reference_id = db.Column(db.String(255), unique=True, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    qr_code_text = db.Column(db.Text)
    qr_code_image_url = db.Column(db.Text)
    status = db.Column(db.String(50), default="PENDING")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=True)
    coupon = db.relationship("Coupon", backref="payments")
