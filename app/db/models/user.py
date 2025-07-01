from app.db.db import db
from datetime import datetime
import enum


class RoleEnum(enum.Enum):
    athlete = 'athlete'
    organizer = 'organizer'
    admin = 'admin'
    organizer_adm = 'organizer-adm'


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cpf = db.Column(db.String(14), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(RoleEnum), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    birth_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(36), nullable=True)
    uniform_size = db.Column(db.String(10), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    nickname = db.Column(db.String(50), nullable=True)

    address_full = db.Column(db.String(255), nullable=True)
    district = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(2), nullable=True)
    team = db.Column(db.String(100), nullable=True)

    data_img = db.Column(db.LargeBinary, nullable=True)
    mime_type_img = db.Column(db.String(128), nullable=True)
    name_img = db.Column(db.String(256), nullable=True)
    
    payments = db.relationship("Payment", backref="user", foreign_keys="Payment.user_id")
