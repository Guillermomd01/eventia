from datetime import datetime,timezone
from sqlalchemy import Column, ForeignKey, Integer, String 
from app.extensions import db,login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Usuario(UserMixin,db.Model):
    __tablename__ = 'Usuarios'
    __table_args__ = {'sqlite_autoincrement':True}
    
    id = Column(Integer,primary_key=True)
    nombre = Column(String,nullable=False)
    email = Column(String, nullable=False,unique=True)
    password_hash = Column(String(128),nullable=False )
    rol = Column(String(10), nullable=False)
    proyectos = db.relationship('Proyecto',backref = 'usuario',lazy='select')
    
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

class Proyecto (db.Model):
    __tablename__ = 'Proyectos'
    __table_args__ = {'sqlite_autoincrement':True}
    
    id = Column(Integer,primary_key=True)
    nombre = Column(String,nullable=False)
    tipo = Column(String,nullable=False)
    fecha= Column(db.DateTime,default = datetime.now(timezone.utc))
    estado = Column(String,nullable= False,default='Pendiente')
    usuario_id = Column(Integer,ForeignKey('Usuarios.id'))
    dataset = db.relationship('Dataset', backref='proyecto',uselist=False)
    
class Dataset(db.Model):
    __tablename__ = 'Dataset'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = Column(Integer,autoincrement=True,primary_key=True)
    nombre_archivo = Column(String,nullable=False)
    ruta_archivo = Column(String,nullable=False)
    fecha_subida = Column(db.DateTime,default=datetime.now(timezone.utc))
    proyecto_id = Column(Integer,ForeignKey('Proyectos.id'))