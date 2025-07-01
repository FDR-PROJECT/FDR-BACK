from flask_migrate import Migrate
from app.modules.payments.route import payments_bp
import os
from app.modules.registrations.route import registrations_bp
from app.modules.categories.route import categories_bp
from app.modules.events.route import events_bp
from app.modules.auth.route import auth_bp
from flask import Flask
from flask_jwt_extended import JWTManager
from app.modules.main.route import main_bp
from app.db.db import db, migrate

migrate = Migrate()
# Criar uma instância global do JWTManager
jwt = JWTManager()
# Armazena tokens bloqueados
jwt_blocklist = set()

def initialize_route(app: Flask):
    with app.app_context():
        app.register_blueprint(payments_bp, url_prefix='/api/v1/payments')
        app.register_blueprint(registrations_bp, url_prefix='/api/v1/registrations')
        app.register_blueprint(categories_bp, url_prefix='/api/v1/categories')
        app.register_blueprint(events_bp, url_prefix='/api/v1/events')
        app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
        app.register_blueprint(main_bp, url_prefix='/api/v1/main')


def initialize_jwt(app):
    """Inicializa o JWT Manager."""
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')  # Chave secreta
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))  # Token expira em 1 hora
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 86400))  # Refresh Token expira em 1 dia
    
    # Vincular o JWT à aplicação Flask
    jwt.init_app(app)
    
    # Configurar callback para verificar tokens bloqueados
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload["jti"] in jwt_blocklist

def initialize_db(app: Flask):
    with app.app_context():
        db.init_app(app)
        migrate.init_app(app, db)
        db.create_all()

