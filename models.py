from sqlalchemy import Column, Integer, String
from database import Base

class ClothingItem(Base):
    __tablename__ = "clothing"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    color = Column(String, index=True)
    garment_type = Column(String, index=True)
    image_url = Column(String, index=True)

class Outfit(Base):
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    items = Column(String)  # store clothing item IDs as comma-separated string
