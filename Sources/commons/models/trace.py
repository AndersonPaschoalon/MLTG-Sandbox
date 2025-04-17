from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from commons.connectors.base import Base


class Trace(Base):
    __tablename__ = "Trace"

    id = Column(Integer, primary_key=True, autoincrement=True)
    traceName = Column(String, nullable=False)
    traceSource = Column(String)
    traceType = Column(String)
    comment = Column(String)
    nPackets = Column(Integer)
    nFlows = Column(Integer)
    duration = Column(Float)
