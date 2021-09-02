'''
Created on Aug 30, 2021

@author: warno006089
'''
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Table, Column, Integer, String, Date, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db import ModelMixin, Base


user_to_group = Table('auth_user_to_group', Base.metadata,
    Column('auth_user_id', Integer, ForeignKey('auth_user.id')),
    Column('auth_user_group_id', Integer, ForeignKey('auth_user_group.id')))


class AuthUser(ModelMixin, Base):
    __tablename__ = 'auth_user'

    name = Column(String)
    email = Column(String)
    password = Column(String, unique=True)
    public_id = Column(String, unique=True)
    fullname = Column(String)
    groups = relationship('AuthUserGroup', secondary=user_to_group, backref='auth_users')

    def on_create(self, **kwargs):
        self.password = generate_password_hash(kwargs['password'])
        group = AuthUserGroup.get('id', kwargs['groups'])
        self.groups.append(group)

    # def generate_password(self, password):
    #     self.password = generate_password_hash(password)

    # def generate_token(self):
    #     return jwt.encode({
    #         'public_id': self.public_id,
    #         'exp': datetime.now() + timedelta(minutes=30)
    #     }, 'secret_key').decode('UTF-8')

    def authenticate(self, password):
        return check_password_hash(self.password, password)
    
    
class AuthUserGroup(ModelMixin, Base):
    __tablename__ = 'auth_user_group'

    name = Column(String)
    description = Column(String)
    parent = Column(String)
    