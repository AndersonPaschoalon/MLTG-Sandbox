from typing import Optional, Type

from sqlalchemy import Connection, Engine, MetaData, Table, create_engine, text
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from commons.connectors.base import Base
from commons.pylang.repr_mixin import ReprMixin


class AlchemyConnector(ReprMixin):

    def __init__(self, connection_string, echo=True):
        self.connection_string = connection_string
        self.engine = create_engine(self.connection_string, echo=echo)
        self.session_fac = sessionmaker(bind=self.engine, expire_on_commit=False)
        print(f"Connected to: {self.connection_string}")

    def session(self) -> Session:
        """
        Return a session object that can be used with a `with` statement.
        """
        return self.session_fac()

    def connection(self) -> Connection:
        """
        Return a connection object that can be used with a `with` statement.
        """
        return self.engine.connect()

    def get_engine(self) -> Engine:
        return self.engine

    # def __repr__(self):
    #    session_status = "open" if self.session else "closed"
    #    return f"<AlchemyConnector(connection_string='{self.connection_string}', session={session_status}, type={self.config.database_type})>"
