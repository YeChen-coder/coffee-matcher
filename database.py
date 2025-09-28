from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

SQLALCHEMY_DATABASE_URL = "sqlite:///./coffee_matcher.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    bio = Column(Text)
    ai_analysis_json = Column(Text)  # 预留给AI分析
    
    time_slots = relationship("TimeSlot", back_populates="user")
    sent_requests = relationship("MatchRequest", foreign_keys="MatchRequest.requester_id", back_populates="requester")
    received_requests = relationship("MatchRequest", foreign_keys="MatchRequest.target_id", back_populates="target")

class TimeSlot(Base):
    __tablename__ = "time_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String, default="available")  # available, booked
    
    user = relationship("User", back_populates="time_slots")

class Venue(Base):
    __tablename__ = "venues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(String)  # coffee, restaurant
    price_range = Column(String)  # $, $$, $$$
    location = Column(String)
    description = Column(Text)

class MatchRequest(Base):
    __tablename__ = "match_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"))
    target_id = Column(Integer, ForeignKey("users.id"))
    proposed_time = Column(DateTime)
    venue_id = Column(Integer, ForeignKey("venues.id"))
    status = Column(String, default="pending")  # pending, accepted, rejected, rescheduled
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    requester = relationship("User", foreign_keys=[requester_id], back_populates="sent_requests")
    target = relationship("User", foreign_keys=[target_id], back_populates="received_requests")
    venue = relationship("Venue")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    preference_type = Column(String)  # interest, game, team, etc.
    preference_value = Column(String)
    confidence = Column(Integer, default=1)  # AI分析的置信度

# 创建数据库表
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()