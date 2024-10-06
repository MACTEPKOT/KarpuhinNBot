from sqlalchemy import Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal  # Импортируйте SessionLocal из вашего файла базы данных

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, unique=True, nullable=False)  # Telegram ID
    username = Column(String)
    role = Column(String)  # 'teacher' или 'listener'
    token = Column(String)  # API токен Яндекс Диска
    teacher_id = Column(Integer, ForeignKey('users.id'))  # ID преподавателя, если это слушатель

    # Связь с моделью Folder
    folders = relationship("Folder", order_by="Folder.id", back_populates="user")

    # Метод для получения пользователя по его Telegram ID
    @classmethod
    async def get_user_by_tg_id(cls, tg_id):
        async with SessionLocal() as session:  # Используйте SessionLocal для получения сессии
            result = await session.execute(
                select(cls).where(cls.tg_id == tg_id)
            )
            return result.scalars().first()

    async def save(self):
        async with SessionLocal() as session:  # Используйте SessionLocal для получения сессии
            session.add(self)
            await session.commit()

    async def delete(self):
        async with SessionLocal() as session:  # Используйте SessionLocal для получения сессии
            await session.delete(self)
            await session.commit()

class Folder(Base):
    __tablename__ = 'folders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String, nullable=False)  # Путь к папке
    tg_user_id = Column(Integer, ForeignKey('users.tg_id'))  # ID пользователя Telegram

    user = relationship("User", back_populates="folders")  # Связь с моделью User

    async def save(self):
        async with SessionLocal() as session:  # Используйте SessionLocal для получения сессии
            session.add(self)
            await session.commit()

    async def delete(self):
        async with SessionLocal() as session:  # Используйте SessionLocal для получения сессии
            await session.delete(self)
            await session.commit()
