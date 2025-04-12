from sqlalchemy import Column, Integer, String
from src.database import Base


class User(Base):
    __tablename__ = "`user`"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    discord_id = Column(Integer, unique=True, index=True)
    github_id = Column(Integer, unique=True, index=True)
    github_name = Column(String)
    github_access_token = Column(String)
    category = Column(String)
    career = Column(String)
