from sqlalchemy import *
from sqlalchemy.orm import relationship
from .common import Base

class Show(Base):
    __tablename__ = 'show'
    id = Column(Integer, primary_key=True)
    slug = Column('Slug', String)
    title = Column('Title', String)
    seasons = relationship("Season", back_populates="show")