from flask import Flask
from app.config.config import get_config_by_name
from app.initialize_functions import initialize_jwt, initialize_route, initialize_db
from flask_cors import CORS


def create_app(config=None) -> Flask:
 
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    if config:
        app.config.from_object(get_config_by_name(config))

    # Initialize extensions
    initialize_db(app)
    initialize_jwt(app)
    # Register blueprints
    initialize_route(app)
    
   

    
    @app.after_request
    def after_request(response):
        print("--- HEADERS ENVIADOS NA RESPOSTA ---")
        print(response.headers)
        return response
  
    return app
