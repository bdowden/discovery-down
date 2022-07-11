from sqlalchemy import *
from sqlalchemy.orm import relationship
from .common import Base

class Episode(Base):
    __tablename__ = 'episode'
    id = Column(Integer, primary_key=True)
    title = Column('Title', String)
    url = Column('Url', String)
    num = Column('Num', Integer)
    isDownloaded = Column('IsDownloaded', Boolean, default = False)
    seasonId = Column(Integer, ForeignKey("season.id"))
    season = relationship("Season", back_populates="episodes")
    airDate = Column('AirDate', DateTime)
    publishDate = Column('PublishDate', DateTime)
    resolution = Column('Resolution', Integer, default = 0)
    