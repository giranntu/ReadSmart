from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class StudentProgress(Base):
    __tablename__ = 'student_progress'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    reading_level = Column(String)
    areas_for_improvement = Column(JSON)
    strengths = Column(JSON)
    points = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Reading(Base):
    __tablename__ = 'readings'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    text = Column(Text)
    grade_level = Column(Integer)
    reading_level = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Use SQLite for simplicity, but in a production environment, 
# you'd want to use a more robust database like PostgreSQL
engine = create_engine('sqlite:///./personalized_reading_support.db', connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create the database tables
Base.metadata.create_all(bind=engine)