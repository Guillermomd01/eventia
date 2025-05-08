from dotenv import load_dotenv
import os

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

from flask import Flask ,Blueprint

from app.models import Usuario
from app.extensions import db, login


def create_app():
    app = Flask(__name__,template_folder='templates')
    
    # Define el directorio base
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Configura la carpeta de subidas
    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
    
    #configura la clave secreta
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave_segura')
    
    #configura la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
    db.init_app(app)
    login.init_app(app)
    login.login_view = 'main.login'
    
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app import models
    with app.app_context():
        db.create_all()

    return app

@login.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))



