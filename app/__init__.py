from flask import Flask, app ,Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


login = LoginManager()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__,template_folder='templates')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   
    db.init_app(app)
    login.init_app(app)
    login.login_view = 'login'
    
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app import models
    with app.app_context():
        db.create_all()

    return app



