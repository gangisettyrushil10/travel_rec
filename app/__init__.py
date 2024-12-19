from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()  # Create tables
    
    # Register blueprints
    from app.api.routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    
    from app.api.recommendations import recommendations_bp
    app.register_blueprint(recommendations_bp)  # Remove url_prefix
    
    return app
from app import models

