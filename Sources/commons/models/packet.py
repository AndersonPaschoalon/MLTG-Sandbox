from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from commons.connectors.base import Base


class Packet(Base):
    __tablename__ = "Packets"

    packetID = Column(Integer, primary_key=True)
    traceID = Column(Integer, primary_key=True)
    flowID = Column(Integer)
    tsSec = Column(Integer)
    tsUsec = Column(Integer)
    pktSize = Column(Integer)
    timeToLive = Column(Integer)

    @property
    def timestamp_seconds(self) -> float:
        """Returns timestamp as float seconds (for calculations)"""
        return self.tsSec + (self.tsUsec / 1_000_000)
