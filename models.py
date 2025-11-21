from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

user_segment = Table(
    'user_segment', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE")),
    Column('segment_id', Integer, ForeignKey('segments.id', ondelete="CASCADE"))
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    segments = relationship(
        "Segment",
        secondary=user_segment,
        back_populates="users",
        cascade="all, delete",
        passive_deletes=True
    )

class Segment(Base):
    __tablename__ = 'segments'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    users = relationship(
        "User",
        secondary=user_segment,
        back_populates="segments",
        cascade="all, delete",
        passive_deletes=True
    )
