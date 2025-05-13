import os

from app.machine_learning.anomalias import detectar_anomalias
from app.machine_learning.prediccion import prediccion
from app.machine_learning.sentimiento import analisis_sentimientos
from app.models import Dataset, Proyecto, Usuario
from  app.forms import FormularioDataset, FormularioProyecto, FormularioRegistro,FormularioLogin, FormularionVerificacion
from app.extensions import login,db

from flask import app, current_app, flash, redirect,render_template,Blueprint, url_for,session
from flask_login import login_required, login_user,current_user,logout_user

from werkzeug.utils import secure_filename

import seaborn as sns
import matplotlib
matplotlib.use('Agg')

import pandas as pd

import matplotlib.pyplot as plt


bp = Blueprint('main',__name__)

@bp.route("/")
def home():
    return render_template('index.html')
    
@bp.route("/registro",methods=['GET','POST'])
def registro():
    form_registro = FormularioRegistro()
    if form_registro.validate_on_submit():
        usuario_existente = Usuario.query.filter_by(email=form_registro.email.data).first()
        if usuario_existente:
            flash('Ese correo ya está registrado. Prueba con otro.', 'warning')
            return redirect(url_for('main.registro'))
        nuevo_usuario = Usuario(nombre=form_registro.nombre.data ,email=form_registro.email.data, rol= form_registro.rol.data)
        
        if form_registro.rol.data == 'admin':
            
            session["registro_admin"] = {
                'nombre': form_registro.nombre.data,
                'email': form_registro.email.data,
                'password': form_registro.password.data,
                'rol': 'Administrador'
            }
            
            return redirect (url_for('main.verificacion'))
        
        nuevo_usuario.set_password(form_registro.password.data)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect (url_for('main.dashboard'))
    
    
    return render_template("registro_form.html",form= form_registro)
    
@bp.route("/verificacion-admin",methods=['GET','POST'])
def verificacion():
    datos = session.get("registro_admin")
    if not datos:
        flash("Acceso no autorizado. Por favor, regístrate primero.")
        return redirect(url_for('main.registro'))
    form_verificacion =  FormularionVerificacion()
    if form_verificacion.validate_on_submit():
        nuevo_usuario = Usuario(
            nombre = datos['nombre'],
            email = datos['email'],
            rol = datos['rol'])
        
        if os.getenv("ADMIN_SECRET") == form_verificacion.codigo_verificacion.data:
            
            nuevo_usuario.set_password(datos['password'])
            db.session.add(nuevo_usuario)
            db.session.commit()
            session.pop('registro_admin')
            login_user(nuevo_usuario)
            return redirect (url_for('main.dashboard_admin'))
        else:
            flash('Contraseña incorrecta, Por favor intentelo de nuevo')
    return render_template('verificacion_admin.html', form=form_verificacion)

@bp.route("/login",methods=['GET','POST'])
def login():
    form_login = FormularioLogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario:
            if usuario.check_password(form_login.password.data):
                login_user(usuario) 
                if usuario.rol == "Administrador":
                    return redirect(url_for('main.dashboard_admin'))
                else:
                    return redirect('/dashboard')
            else:
                flash('Contraseña incorrecta')
        else:
            flash('Email incorrecto')
    
    return render_template("login_form.html",form= form_login)

@bp.route("/logout")
@login_required
def logout():
    logout_user() 
    return render_template('index.html')

@bp.route("/dashboard")
@login_required
def dashboard():
    proyectos_usuario = Proyecto.query.filter_by(usuario_id=current_user.id).order_by(Proyecto.fecha.desc()).all()
    
    proyectos_ordenados = sorted(proyectos_usuario, key=lambda p: p.estado != "Pendiente")
    return render_template("dashboard.html",user = current_user.nombre,lista_proyectos = proyectos_ordenados)

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
        flash('Por favor completa todos los campos corectamente')
        
        
    return render_template('crear_proyecto.html',form=form_registro)

@bp.route("/subir-archivo/<int:proyecto_id>", methods=['GET', 'POST'])
@login_required
def subir_archivo(proyecto_id):
    form_archivo = FormularioDataset()
    if form_archivo.validate_on_submit():
        archivo = form_archivo.archivo.data
        dir_segura = secure_filename(archivo.filename)
        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], dir_segura)
        archivo.save(ruta)
        
        nuevo_archivo = Dataset(
            nombre_archivo = form_archivo.nombre.data,
            ruta_archivo = dir_segura,
            proyecto_id = proyecto_id
        )
        
        db.session.add(nuevo_archivo)
        db.session.commit()
        
        proyecto = Proyecto.query.get_or_404(proyecto_id)
        proyecto.estado = "completado"
        db.session.commit()
        
        proyecto = Proyecto.query.get(proyecto_id)
        if proyecto.tipo == "sentimiento":
            return redirect(url_for('main.resultado_modelo_sentimiento', dataset_id=nuevo_archivo.id))
        elif proyecto.tipo == "prediccion":
            return redirect(url_for('main.resultado_modelo_prediccion', dataset_id=nuevo_archivo.id))
        elif proyecto.tipo == "anomalias":
            return redirect(url_for('main.resultado_modelo_anomalias', dataset_id=nuevo_archivo.id))

        # En caso de tipo desconocido
        flash("Tipo de proyecto no reconocido. Redirigiendo al dashboard.")
        return redirect(url_for('main.dashboard'))

    else:
        flash('Por favor introduce valores correctos')
    proyecto = Proyecto.query.get_or_404(proyecto_id)
    return render_template('subir_archivo.html',form=form_archivo,proyecto=proyecto)

@bp.route("/dashboard-admin")
@login_required
def dashboard_admin():
    if current_user.rol != 'Administrador':
        flash("Acceso restringido a administradores.")
        return redirect(url_for('main.dashboard'))
    tabla_usuarios = Usuario.query.filter(Usuario.rol != 'Administrador').order_by(Usuario.id.desc())
    
    return render_template("dashboard_admin.html",user=current_user.nombre, tabla_usuarios=tabla_usuarios)

@bp.route("/proyectos-usuarios/<int:usuario_id>")
@login_required
def proyectos_usuarios(usuario_id):
    if current_user.rol != 'Administrador':
        flash("Acceso restringido a administradores.")
        return redirect(url_for('main.dashboard'))
    usuario = Usuario.query.get_or_404(usuario_id)
    proyectos = Proyecto.query.filter_by(usuario_id=usuario_id).all()
    
    return render_template('proyectos_usuarios.html',usuario = usuario,proyectos=proyectos)

#ruta para eliminar las tareas
@bp.route("/eliminar-proyecto/<int:proyecto_id>")
@login_required
def eliminar_proyecto(proyecto_id):
    proyecto= Proyecto.query.get_or_404(proyecto_id)
    usuario_id = proyecto.usuario_id
    
    if proyecto.dataset:
        db.session.delete(proyecto.dataset)
    db.session.delete(proyecto)
    db.session.commit()
    return redirect(url_for('main.proyectos_usuarios', usuario_id=usuario_id))

@bp.route("/resultado-prediccion/<int:dataset_id>",methods=['GET','POST'])
@login_required
def resultado_modelo_prediccion(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], dataset.ruta_archivo)
    resultado = prediccion(ruta)
    return render_template("resultado_predicion.html",resultado = resultado) 

@bp.route("/resultado-sentimientos/<int:dataset_id>",methods=(['GET','POST']))
@login_required
def resultado_modelo_sentimiento(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], dataset.ruta_archivo)
    resultado = analisis_sentimientos(ruta)
    
    df_grafico = pd.DataFrame(list(resultado.items()), columns=["sentimiento", "cantidad"])
    plt.figure(figsize=(6, 4))
    grafico = sns.barplot(data=df_grafico, x= 'sentimiento',y='cantidad',hue='cantidad')
    
    ruta_grafico = f"app/static/plots/sentimientos_{dataset_id}.png"
    os.makedirs(os.path.dirname(ruta_grafico), exist_ok=True)
    plt.savefig(ruta_grafico)
    plt.close()
    nombre_archivo = f"plots/sentimientos_{dataset_id}.png"
    
    return render_template("resultado_sentimientos.html",resultado = resultado, grafico = nombre_archivo) 

@bp.route("/resultado-anomalias/<int:dataset_id>",methods=(['GET','POST']))
@login_required
def resultado_modelo_anomalias(dataset_id):
    
    dataset = Dataset.query.get_or_404(dataset_id)
    ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], dataset.ruta_archivo)
    completo, anomalias,df_grafico = detectar_anomalias(ruta)
    
    plt.figure(figsize=(12, 8))
    grafico = sns.scatterplot(data=df_grafico, x='fecha', y='valores', hue='anomalia')
    ax = plt.gca()
    # Rotar las etiquetas del eje x
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45,ha='right')
    ruta_grafico = f"app/static/plots/anomalias_{dataset_id}.png"
    os.makedirs(os.path.dirname(ruta_grafico), exist_ok=True)
    plt.savefig(ruta_grafico)
    plt.close()
    nombre_archivo = f"plots/anomalias_{dataset_id}.png"


    return render_template("resultado_anomalias.html",resultado = anomalias,original=completo,grafico=nombre_archivo)