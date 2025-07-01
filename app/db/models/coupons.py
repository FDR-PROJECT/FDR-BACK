# app/db/models/coupon.py
from app.db.db import db
from datetime import datetime

class Coupon(db.Model):
    __tablename__ = "coupons"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_type = db.Column(db.String(10), nullable=False)  # 'percent' ou 'value'
    amount = db.Column(db.Float, nullable=False)  # ex: 10.0 ou 20.0%
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=True)
