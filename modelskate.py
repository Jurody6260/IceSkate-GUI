from sqlalchemy import func, and_, delete, create_engine, text, MetaData, Integer, String, Column, ForeignKey, Date, Time, DateTime, Boolean, extract
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, subqueryload, joinedload, relationship
from datetime import date, time, datetime
import logging

from sqlalchemy.sql.expression import null
logging.basicConfig()
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)

meta = MetaData()
Base = declarative_base()
engine = create_engine("sqlite:///skates.db")

Session = sessionmaker(bind=engine)
session = Session()


def search_query(session, Class):
    return session.query(Class).order_by(Class.id.desc()).limit(10).all()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    RFID = Column(String(8), nullable=False)
    name = Column(String, nullable=True)
    action_isActive = (Boolean, ForeignKey('action.isActive'))
    timing = Column(Integer, nullable=False)
    action = relationship("Action", back_populates="user")


class Action(Base):
    __tablename__ = "action"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    action_time = Column(DateTime, default=datetime.now())
    isActive = Column(Boolean, nullable=False, default=False)
    is_entry = Column(Boolean, nullable=False)
    left_on_time = Column(Boolean, nullable=False, default=True)
    user = relationship("User", back_populates="action")


# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
session.close()
