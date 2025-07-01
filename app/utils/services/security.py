import bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode())

def create_jwt_token(user):
    return create_access_token(
        identity=str(user.id),  # 👈 precisa ser string
        additional_claims={
            "email": user.email,
            "role": user.role.value
        },
        expires_delta=timedelta(hours=24)
    )
