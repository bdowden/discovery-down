from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

fn = os.path.join(os.path.dirname(__file__), 'dplus.sqlite')

engine = create_engine(f"sqlite+pysqlite:///{fn}", echo=False, future=True)

Base = declarative_base()

sessionMaker = sessionmaker(bind=engine)