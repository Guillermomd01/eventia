from sqlalchemy import Column, Integer, String 
from app import db
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
    
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)