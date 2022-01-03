'''
Created on Aug 30, 2021

@author: warno006089
'''

import enum
import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Date, Float
from app.db import Base, ModelMixin


class KasEnum(enum.Enum):
    operational = 'Kas Operasional'
    pembangunan = 'Kas Pembangunan'


class KasLedger(ModelMixin,Base):
    __tablename__ = 'kas_ledger'
    
    name = Column(String)
    code = Column(String)
    

class KasJournal(ModelMixin, Base):
    __tablename__ = 'kas_journal'
    
    name = Column(String)
    kas_type = Column(Enum(KasEnum))
    kas_legder_id = Column(Integer, ForeignKey('kas_ledger.id'))
    journal_date = Column(Date, default=datetime.date.today())
    debit = Column(Float(precision=17))
    credit = Column(Float(precision=17))
    balance = Column(Float(precision=17))
    