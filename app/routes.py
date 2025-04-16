from app.models import Usuario
from  app.forms import FormularioRegistro,FormularioLogin
from flask import app, flash, redirect,render_template,Blueprint
from flask_login import login_user

bp = Blueprint('main',__name__)

@bp.route("/")
def home():
    return render_template('index.html')
    
@bp.route("/registro",methods=['GET','POST'])
def registro():
    form_registro = FormularioRegistro()
    if form_registro.validate_on_submit():
        nuevo_usuario = Usuario(nombre=form_registro.nombre.data ,email=form_registro.email.data, rol= form_registro.rol.data)
        nuevo_usuario.set_password(form_registro.password.data)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect('/dashboard')
    
    
    return render_template("registro_form.html",form= form_registro)
    
@bp.route("/login",methods=['GET','POST'])
def login():
    form_login = FormularioLogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario:
            if usuario.check_password(form_login.password.data):
                login_user(usuario) 
                return redirect('/dashboard')
            else:
                flash('Contraseña incorrecta')
        else:
            flash('Email incorrecto')
    
    return render_template("login_form.html",form= form_login)

from app import login
@login.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))