'''
Created on Aug 28, 2021

@author: warno006089
'''
from sqlalchemy import create_engine, Column, Integer, select, Sequence
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm.interfaces import ONETOMANY, MANYTOONE, MANYTOMANY
from sqlalchemy.exc import SQLAlchemyError
try:
    from sqlalchemy import inspect
    from sqlalchemy.orm.state import InstanceState
except ImportError as e:
    def __nomodule(*args, **kwargs): raise e
    inspect = __nomodule
    InstanceState = __nomodule
from .config import config
from .filters import build_filters

db_engine = create_engine(config['config']['db_uri'], echo=True, future=True)
db_session = sessionmaker(db_engine)

class JsonSerializableBase(object):

    _json_include = []
    _json_exclude = []

    def __json__(self, excluded_keys=set()):
        ins = inspect(self)
        
        columns = set(ins.mapper.column_attrs.keys())
        relationships = set(ins.mapper.relationships.keys())
        unloaded = ins.unloaded
        expired = ins.expired_attributes
        include = set(self._json_include)
        exclude = set(self._json_exclude) | excluded_keys
        keys = columns | relationships
        if not ins.transient:
            keys -= unloaded
        if ins.expired:
            keys |= expired
        keys |= include
        """ if ins.deleted or ins.detached:
            keys -= relationships
            keys -= unloaded """
        keys -= exclude
        return { key: getattr(self, key)  for key in keys }
    
    def _constructor(self, **kwargs):
        columns = self._get_member()[0]
        for key, val in kwargs.items():
            if key in columns:
                setattr(self, key, val)
    
    @classmethod
    def create(cls, env, **kwargs):
        obj = cls(**kwargs)
        with db_session() as session:
            obj.init_env(env, session)
            obj.on_create(**kwargs)
            session.add(obj)
            obj.after_create(**kwargs)
            try:
                session.commit()
            except SQLAlchemyError as e:
                raise e
            return obj.id
        
    @classmethod
    def write(cls, env, *args, **kwargs):
        query = cls._query_get_single(cls, 'id', args['id'])
        with db_session() as session:
            obj = session.execute(query)
            obj.init_env(env, session)
            obj.change(**kwargs)
            try:
                session.commit()
            except SQLAlchemyError as e:
                raise e
            return obj
            
    @classmethod
    def read(cls, filters, page=1, page_size=1, order='id', order_dir='asc'):
        pass
        
    @classmethod
    def browse(cls, filters, order='id', order_dir='asc'):
        order_col = getattr(cls, order)
        query = cls._query_read(cls, filters).order_by(order_col)
        with db_session() as session:
            rows = session.execute(query).scalars().all()
        return rows
    
    @classmethod
    def get(cls, field, param, options=None):
        query = cls._query_get_single(cls, field, param, options)
        with db_session() as session:
            obj = session.execute(query).scalars().one()
        return obj
        
    def _query_read(self, filters):
        query = select(self)
        for filter_spec in filters:
            filter_objs = build_filters(filter_spec)
            sqlalchemy_filters = [
                filter_item.format_for_sqlalchemy(self) for filter_item in filter_objs
            ]
            query = query.filter(*sqlalchemy_filters)
        return query
        
    def _query_get_single(self, field, param, options=None):
        column = getattr(self, field)
        return select(self).filter(column == param)
    
    def on_create(self, **kwargs):
        self._write_relationship(**kwargs)
        
    def after_create(self, **kwargs):
        pass
        
    def change(self, **kwargs):
        pass
    
    def _write_relationship(self, **kwargs):
        relationships = self._get_member()[1]          
        for key, val in kwargs.items():
            if key in relationships:
                relate = relationships[key]
                if relate.direction == ONETOMANY:
                    for item in val:
                        if 'id' in item.keys():
                            relate.mapper.entity.write(self.env, 'id', '1', **item)
                        else:
                            d = relate.mapper.entity.create(self.env, **item)
                            p = getattr(self, key)
                            p.append(d)
                # elif relate.direction == MANYTOMANY:
                #     pass
                
    def _set_id(self):
        seq = Sequence(self.__tablename__ + '_id_seq')
        self.id = self.session.execute(seq)
        
    def _get_member(self):
        ins = inspect(self)
        columns = set(ins.mapper.column_attrs.keys())
        relationships = set(ins.mapper.relationships.keys())
        return (columns, relationships)
    
    def init_env(self, env, session):
        self.env = env
        self.session = session
        

class ModelMixin:
    id = Column(Integer, primary_key=True)
    
# Base Model
Base = declarative_base(cls=JsonSerializableBase, constructor=JsonSerializableBase._constructor)


    
        
    
    
    
    