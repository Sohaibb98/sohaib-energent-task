"""
Database configuration and models for MySQL integration
"""

import os
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Enum, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.mysql import LONGTEXT

# Database configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root1234")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "computer_use_demo")

# Create database URL
DATABASE_URL = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
def init_db():
    Base.metadata.create_all(bind=engine)

# Session model
class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    status = Column(Enum('idle', 'running', 'completed', 'error'), default='idle')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to messages
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_status', 'status'),
        Index('idx_created_at', 'created_at'),
    )

# Message model
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum('user', 'assistant', 'tool', 'system'), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(Enum('text', 'tool_result', 'screenshot', 'error'), default='text')
    tool_name = Column(String(255), nullable=True)
    screenshot = Column(LONGTEXT, nullable=True)  # base64 encoded image
    error = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to session
    session = relationship("Session", back_populates="messages")
    
    __table_args__ = (
        Index('idx_session_id', 'session_id'),
        Index('idx_timestamp', 'timestamp'),
        Index('idx_role', 'role'),
    ) 