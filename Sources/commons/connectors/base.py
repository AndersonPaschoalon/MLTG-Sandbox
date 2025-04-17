from sqlalchemy.orm import DeclarativeBase

TINY_STR = 16
SMALL_STR = 64
MEDIUM_STR = 256
BIG_STR = 2048


class Base(DeclarativeBase):
    pass
