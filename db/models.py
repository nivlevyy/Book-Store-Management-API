
from sqlalchemy import Column, Integer, String
from sqlalchemy import and_ 
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Books(Base):
    __tablename__ = 'books'
    rawid = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    year = Column(Integer)
    price = Column(Integer)
    genres = Column(String)  # ערכים מופרדים בפסיק
