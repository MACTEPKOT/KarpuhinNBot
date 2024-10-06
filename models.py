from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True)
    name = Column(String)
    role = Column(String)  # 'teacher' or 'student'
    token = Column(String, nullable=True)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    folders = relationship("Folder", back_populates="user")

class Folder(Base):
    __tablename__ = 'folders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    path = Column(String)
    last_modified = Column(DateTime)

    user = relationship("User", back_populates="folders")
