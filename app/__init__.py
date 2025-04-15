from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.models import Usuario

login = LoginManager()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__,template_folder='templates')
    @app.route("/")
    def home():
        return render_template('index.html')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    login.init_app(app)
    login.login_view = 'login'
    
    from app import models
    with app.app_context():
        db.create_all()
    
    
    return app

@login.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

