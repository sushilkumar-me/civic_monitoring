from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Float, Boolean
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20))
    ward = Column(Integer)
    otp_code = Column(String(6), nullable=True)
    otp_expiry = Column(TIMESTAMP, nullable=True)
    is_verified = Column(Boolean, default=False)

class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True)
    issue_type = Column(String(50))
    ward = Column(Integer)
    priority = Column(String(20))
    status = Column(String(20), default="OPEN")
    before_image = Column(Text)
    after_image = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    ai_confidence = Column(Float, nullable=True)
    ai_reasoning = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
