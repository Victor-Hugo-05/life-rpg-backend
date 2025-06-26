from flask import Flask
from models import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///character_data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializa o db com o app
    db.init_app(app)
    
    from .views import bp
    app.register_blueprint(bp)
    
    with app.app_context():
        db.create_all()
    
    return app