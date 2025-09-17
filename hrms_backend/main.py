from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


from database_models import create_database, Employee, LocationLog  

# DB session
SessionLocal = create_database()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas
class LocationCreate(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    source: str

class LocationOut(BaseModel):
    id: int
    latitude: float
    longitude: float
    accuracy: Optional[float]
    source: str
    timestamp: datetime

    class Config:
        from_attributes = True

# FastAPI
app = FastAPI(title="Mini HRMS - Location Module")

# Save Location
@app.post("/location/employee/{employee_id}", response_model=LocationOut)
def save_location(employee_id: int, location: LocationCreate, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    db_location = LocationLog(
        employee_id=employee_id,
        latitude=location.latitude,
        longitude=location.longitude,
        accuracy=location.accuracy,
        source=location.source
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

# Get Location History
@app.get("/location/history/{employee_id}", response_model=List[LocationOut])
def get_location_history(employee_id: int, start: Optional[datetime] = Query(None), end: Optional[datetime] = Query(None), db: Session = Depends(get_db)):
    query = db.query(LocationLog).filter(LocationLog.employee_id == employee_id)
    if start:
        query = query.filter(LocationLog.timestamp >= start)
    if end:
        query = query.filter(LocationLog.timestamp <= end)
    return query.order_by(LocationLog.timestamp.desc()).all()

# Get All Locations
@app.get("/location/all", response_model=List[LocationOut])
def get_all_locations(db: Session = Depends(get_db)):
    return db.query(LocationLog).all()

# Get Latest Location
@app.get("/location/latest/{employee_id}", response_model=LocationOut)
def get_latest_location(employee_id: int, db: Session = Depends(get_db)):
    location = (
        db.query(LocationLog)
        .filter(LocationLog.employee_id == employee_id)
        .order_by(LocationLog.timestamp.desc())
        .first()
    )
    if not location:
        raise HTTPException(status_code=404, detail="No location found for this employee")
    return location
