import os
from app.models import Dataset, Proyecto, Usuario
from  app.forms import FormularioDataset, FormularioProyecto, FormularioRegistro,FormularioLogin
from flask import app, current_app, flash, redirect,render_template,Blueprint, url_for
from flask_login import login_required, login_user,current_user
from app.extensions import login,db
from werkzeug.utils import secure_filename


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
        return redirect (url_for('main.dashboard'))
    
    
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

@bp.route("/dashboard")
@login_required
def dashboard():
    proyectos_usuario = Proyecto.query.filter_by(usuario_id=current_user.id).order_by(Proyecto.fecha.desc())
    
    return render_template("dashboard.html",user = current_user.nombre,lista_proyectos = proyectos_usuario)

@bp.route("/crear-proyecto",methods=['GET','POST'])
@login_required
def nuevo_proyecto():
    form_registro= FormularioProyecto()
    
    if form_registro.validate_on_submit():
        nuevo_proyecto = Proyecto(
            nombre=form_registro.nombre.data,
            tipo=form_registro.tipo.data,
            usuario_id=  current_user.id,)
        db.session.add(nuevo_proyecto)
        db.session.commit()
        return redirect (url_for('main.dashboard'))
    else:
        flash('Por favor Completa todos los campos corectamente')
        
        
    return render_template('proyecto_form.html',form=form_registro)

@bp.route("/subir-archivo/<int:proyecto_id>", methods=['GET', 'POST'])
@login_required
def subir_archivo(proyecto_id):
    form_archivo = FormularioDataset()
    if form_archivo.validate_on_submit():
        archivo = form_archivo.archivo.data
        dir_segura = secure_filename(archivo.filename)
        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], dir_segura)
        archivo.save(ruta)
        
        nuevo_archvivo = Dataset(
            nombre_archivo = form_archivo.nombre.data,
            ruta_archivo = dir_segura,
            proyecto_id = proyecto_id
        )
        
        db.session.add(nuevo_archvivo)
        db.session.commit()
        return redirect (url_for('main.dashboard'))
    else:
        flash('Por favor introduce valores correctos')
    
    return render_template('archivo_form.html',form=form_archivo)

