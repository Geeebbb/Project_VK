from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, Segment, Base
import random
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
Base.metadata.create_all(bind=engine)
app = FastAPI()

class UserCreate(BaseModel):
    id: int

class SegmentCreate(BaseModel):
    name: str

class UserSegmentRequest(BaseModel):
    user_id: int
    segment_name: str

class SegmentDistributionRequest(BaseModel):
    segment_name: str
    percent: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.middleware("http")

async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise

@app.post("/segments/", response_model=dict)
def create_segment(segment: SegmentCreate, db: Session = Depends(get_db)):
    try:
        existing_segment = db.query(Segment).filter(Segment.name == segment.name).first()
        if existing_segment:
            return {"message": f"Segment '{segment.name}' already exists"}

        db_segment = Segment(name=segment.name)
        db.add(db_segment)
        db.commit()
        db.refresh(db_segment)
        return {"message": f"Segment '{segment.name}' created successfully", "id": db_segment.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/users/", response_model=dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.id == user.id).first()
        if existing_user:
            return {"message": f"User {user.id} already exists"}

        db_user = User(id=user.id)
        db.add(db_user)
        db.commit()
        return {"message": f"User {user.id} created successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating user: {str(e)}"
        )


@app.post("/users/add_segment/")
def add_user_to_segment(request: UserSegmentRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == request.user_id).first()
    segment = db.query(Segment).filter(Segment.name == request.segment_name).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")

    if segment not in user.segments:
        user.segments.append(segment)
        db.commit()

    return {"message": f"User {request.user_id} added to segment {request.segment_name}"}

@app.get("/users/{user_id}/segments/", response_model=List[str])
def get_user_segments(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return [segment.name for segment in user.segments]


@app.post("/segments/distribute/")
def distribute_segment(request: SegmentDistributionRequest, db: Session = Depends(get_db)):
    if not (0 < request.percent <= 100):
        raise HTTPException(status_code=400, detail="Percent must be between 0 and 100")
    users = db.query(User).all()
    segment = db.query(Segment).filter(Segment.name == request.segment_name).first()

    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")

    num_users = min(len(users), max(1, int(len(users) * request.percent / 100)))
    selected_users = random.sample(users, num_users)

    for user in selected_users:
        if segment not in user.segments:
            user.segments.append(segment)

    db.commit()
    return {"message": f"Segment {request.segment_name} distributed to {num_users} users"}

@app.delete("/segments/{segment_name}")
def delete_segment(segment_name: str, db: Session = Depends(get_db)):
    segment = db.query(Segment).filter(Segment.name == segment_name).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    db.delete(segment)
    db.commit()
    return {"message": f"Segment {segment_name} deleted"}

@app.patch("/segments/{segment_name}")
def update_segment(segment_name: str, new_name: str, db: Session = Depends(get_db)):
    segment = db.query(Segment).filter(Segment.name == segment_name).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    segment.name = new_name
    db.commit()
    return {"message": f"Segment renamed to {new_name}"}

@app.post("/users/remove_segment/")
def remove_user_from_segment(request: UserSegmentRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == request.user_id).first()
    segment = db.query(Segment).filter(Segment.name == request.segment_name).first()
    if not user or not segment:
        raise HTTPException(status_code=404, detail="User or segment not found")
    if segment in user.segments:
        user.segments.remove(segment)
        db.commit()
    return {"message": f"User {request.user_id} removed from segment {request.segment_name}"}

@app.get("/db/users/", response_model=list[dict])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": user.id, "segments": [s.name for s in user.segments]} for user in users]

@app.get("/db/segments/", response_model=list[dict])
def get_all_segments(db: Session = Depends(get_db)):
    segments = db.query(Segment).all()
    return [{"id": seg.id, "name": seg.name, "users": [u.id for u in seg.users]} for seg in segments]