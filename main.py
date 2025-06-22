from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to your Virtual Closet API!"}

@app.post("/add-clothing")
def add_clothing(name: str, color: str, garment_type: str, image_url: str, db: Session = Depends(get_db)):
    item = models.ClothingItem(
        name=name,
        color=color,
        garment_type=garment_type,
        image_url=image_url
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
