from sqlalchemy import Column, Integer, String, BigInteger, JSON, Text
from src.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True, nullable=False)   
    username = Column(String, nullable=True)
    
    text_resume = Column(Text, nullable=True)  
    tech_stack = Column(JSON, nullable=True)  