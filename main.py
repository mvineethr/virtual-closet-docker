from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from pydantic import BaseModel
from typing import List

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic request model
class ClothingItemRequest(BaseModel):
    name: str
    color: str
    garment_type: str
    image_url: str

@app.get("/")
def read_root():
    return {"message": "Welcome to your Virtual Closet API!"}

@app.post("/add-clothing")
def add_clothing(item: ClothingItemRequest, db: Session = Depends(get_db)):
    clothing = models.ClothingItem(
        name=item.name,
        color=item.color,
        garment_type=item.garment_type,
        image_url=item.image_url
    )
    db.add(clothing)
    db.commit()
    db.refresh(clothing)
    return clothing

class ClothingItemOut(BaseModel):
    id: int
    name: str
    color: str
    garment_type: str
    image_url: str

    class Config:
        orm_mode = True

@app.get("/clothes", response_model=List[ClothingItemOut])
def get_clothes(db: Session = Depends(get_db)):
    clothes = db.query(models.ClothingItem).all()
    return clothes

class OutfitRequest(BaseModel):
    name: str
    item_ids: List[int]

@app.post("/save-outfit")
def save_outfit(outfit: OutfitRequest, db: Session = Depends(get_db)):
    item_str = ",".join(map(str, outfit.item_ids))
    new_outfit = models.Outfit(name=outfit.name, items=item_str)
    db.add(new_outfit)
    db.commit()
    return {"message": f"Outfit '{outfit.name}' saved successfully."}
