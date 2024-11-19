from flask import Flask
from app.routes.nutrition_routes import nutrition_bp
from app.routes.page_routes import page_bp
from app.handlers.error_handlers import register_error_handlers

def create_app():
    app = Flask(__name__)
    
    app.register_blueprint(page_bp)
    app.register_blueprint(nutrition_bp)
    
    register_error_handlers(app)
    
    return app

app = create_app()