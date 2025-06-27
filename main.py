from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
from uuid import uuid4
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from pydantic import BaseModel
from typing import List
import sys
print("🚀 Running the CORRECT main.py", file=sys.stderr)
with open("debug_log.txt", "w") as f:
    f.write("This is the real main.py running!\n")


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
        from_attributes = True

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

@app.get("/outfits")
def get_outfits(db: Session = Depends(get_db)):
    outfits = db.query(models.Outfit).all()
    result = []

    for outfit in outfits:
        item_ids = [int(i) for i in outfit.items.split(",") if i]
        clothes = db.query(models.ClothingItem).filter(models.ClothingItem.id.in_(item_ids)).all()
        result.append({
            "id": outfit.id,
            "name": outfit.name,
            "items": [
                {
                    "id": c.id,
                    "name": c.name,
                    "color": c.color,
                    "garment_type": c.garment_type,
                    "image_url": c.image_url
                } for c in clothes
            ]
        })

    return result

@app.delete("/delete-all")
def delete_all_clothes(db: Session = Depends(get_db)):
    db.query(models.ClothingItem).delete()
    db.commit()
    return {"message": "All clothes deleted"}

    # Save image locally (in /app/data)
#    image_path = f"data/{image.filename}"
#    with open(image_path, "wb") as f:
#        f.write(image.file.read())

    # Store relative path in DB
#    new_item = models.ClothingItem(
#        name=name,
#        color=color,
#        garment_type=garment_type,
#        image_url=image_path  # local path
#    )
#    db.add(new_item)
#    db.commit()
#    db.refresh(new_item)
#    return new_item

@app.delete("/delete-placeholder-items")
def delete_placeholder_items(db: Session = Depends(get_db)):
    placeholders = db.query(models.ClothingItem).filter(
        models.ClothingItem.name.ilike("string"),
        models.ClothingItem.color.ilike("string"),
        models.ClothingItem.garment_type.ilike("string")
    ).all()

    if not placeholders:
        return {"message": "No placeholder items found."}

    for item in placeholders:
        db.delete(item)
    db.commit()

    return {"message": f"Deleted {len(placeholders)} placeholder item(s)."}

UPLOAD_DIR = "ustatic/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-clothing")
async def upload_clothing(
    file: UploadFile = File(...),
    name: str = Form(...),
    color: str = Form(...),
    garment_type: str = Form(...),
    db: Session = Depends(get_db)
):
        # 🚫 Basic validation
    if name.lower() == "string" or color.lower() == "string" or garment_type.lower() == "string":
        raise HTTPException(status_code=400, detail="Fields cannot be 'string'. Please provide meaningful values.")
    
    # Save image
    file_extension = file.filename.split(".")[-1]
    file_id = str(uuid4())
    saved_filename = f"{file_id}.{file_extension}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image_url = f"http://localhost:8000/uploads/{saved_filename}"

    # Save to database
    new_item = models.ClothingItem(
        name=name,
        color=color,
        garment_type=garment_type,
        image_url=image_url
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)  # This loads the DB-generated id

    return JSONResponse(content={
        "message": "Uploaded successfully!",
        "item": {
            "id": new_item.id,
            "name": new_item.name,
            "color": new_item.color,
            "garment_type": new_item.garment_type,
            "image_url": new_item.image_url
        }
    })

@app.get("/routes")
def get_routes():
    return [{"path": route.path, "methods": list(route.methods)} for route in app.routes]


app.mount("/uploads", StaticFiles(directory="ustatic/uploads"), name="uploads")