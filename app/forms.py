from flask_wtf import FlaskForm
from wtforms import FileField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email


class FormularioRegistro(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()]) 
    email = StringField('email',validators=[DataRequired(),Email()])
    password = PasswordField('Contraseña',validators=[DataRequired()])
    rol = SelectField(choices=[('admin','Administrador'),('cliente','Cliente')])
    enviar = SubmitField('Registrarme')

class FormularioLogin(FlaskForm):
    email = StringField('email',validators=[DataRequired(),Email()])
    password = PasswordField('Contraseña',validators=[DataRequired()])    
    enviar = SubmitField('Iniciar Sesión')
    
class FormularioProyecto(FlaskForm):
    nombre = StringField('nombre', validators=[DataRequired()])
    tipo =  SelectField(choices=[
        ('sentimiento','sentimiento'),
        ('prediccion','prediccion'),
        ('anomalias','anomalias')])
    enviar = SubmitField('Guardar Proyecto')
    
class FormularioDataset(FlaskForm):
    nombre = StringField('nombre del archivo',validators=[DataRequired()])
    archivo = FileField('Insertar archivo',validators=[DataRequired()])
    enviar = SubmitField('Subir archivo')