from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Metric(Base):
    __tablename__ = 'metrics'

    id = Column(Integer, primary_key=True, index=True)
    org = Column(String, index=True)
    date = Column(DateTime)
    data = Column(String)
