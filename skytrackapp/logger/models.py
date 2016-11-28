# coding: UTF-8

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String
 
Base = declarative_base()
 
class Logins(Base):
    __tablename__ = 'logins'
    id = Column(Integer, primary_key=True)
    logins = Column(String(30), nullable=False)
 
class UserData(Base):
    __tablename__ = 'userdata'
    id = Column(Integer, primary_key=True)
    login_id = Column(Integer, ForeignKey('logins.id'))
    action = Column(String(512))
    eltime = Column(Integer)
    time = Column(String(10))

engine = create_engine('sqlite:////tmp/test.db')

Base.metadata.create_all(engine)