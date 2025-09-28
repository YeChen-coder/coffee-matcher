from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import json

from database import get_db, User, TimeSlot, Venue, MatchRequest, UserPreference

app = FastAPI(title="Coffee Matcher", description="Professional networking through coffee/dinner matching")

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 首页
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# 获取所有用户
@app.get("/api/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    result = []
    for user in users:
        # 获取用户的可用时间
        available_slots = db.query(TimeSlot).filter(
            TimeSlot.user_id == user.id,
            TimeSlot.status == "available",
            TimeSlot.start_time > datetime.now()
        ).all()
        
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "bio": user.bio,
            "available_slots": [
                {
                    "id": slot.id,
                    "start_time": slot.start_time.isoformat(),
                    "end_time": slot.end_time.isoformat()
                } for slot in available_slots
            ]
        })
    return result

# 获取特定用户的时间槽
@app.get("/api/users/{user_id}/timeslots")
def get_user_timeslots(user_id: int, db: Session = Depends(get_db)):
    slots = db.query(TimeSlot).filter(
        TimeSlot.user_id == user_id,
        TimeSlot.status == "available",
        TimeSlot.start_time > datetime.now()
    ).all()
    
    return [
        {
            "id": slot.id,
            "start_time": slot.start_time.isoformat(),
            "end_time": slot.end_time.isoformat()
        } for slot in slots
    ]

# 获取所有场所
@app.get("/api/venues")
def get_venues(venue_type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Venue)
    if venue_type:
        query = query.filter(Venue.type == venue_type)
    
    venues = query.all()
    return [
        {
            "id": venue.id,
            "name": venue.name,
            "type": venue.type,
            "price_range": venue.price_range,
            "location": venue.location,
            "description": venue.description
        } for venue in venues
    ]

# 发起匹配请求
@app.post("/api/matches")
def create_match_request(
    requester_id: int = Form(...),
    target_id: int = Form(...),
    time_slot_id: int = Form(...),
    venue_id: int = Form(...),
    message: str = Form(""),
    db: Session = Depends(get_db)
):
    # 获取时间槽信息
    time_slot = db.query(TimeSlot).filter(TimeSlot.id == time_slot_id).first()
    if not time_slot:
        raise HTTPException(status_code=404, detail="Time slot not found")
    
    # 检查用户是否存在
    requester = db.query(User).filter(User.id == requester_id).first()
    target = db.query(User).filter(User.id == target_id).first()
    
    if not requester or not target:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 创建匹配请求
    match_request = MatchRequest(
        requester_id=requester_id,
        target_id=target_id,
        proposed_time=time_slot.start_time,
        venue_id=venue_id,
        message=message
    )
    
    db.add(match_request)
    db.commit()
    db.refresh(match_request)
    
    return {"message": "Match request sent successfully", "request_id": match_request.id}

# 获取收到的匹配请求
@app.get("/api/matches/received/{user_id}")
def get_received_matches(user_id: int, db: Session = Depends(get_db)):
    matches = db.query(MatchRequest).filter(
        MatchRequest.target_id == user_id,
        MatchRequest.status == "pending"
    ).all()
    
    result = []
    for match in matches:
        requester = db.query(User).filter(User.id == match.requester_id).first()
        venue = db.query(Venue).filter(Venue.id == match.venue_id).first()
        
        result.append({
            "id": match.id,
            "requester_name": requester.name,
            "requester_email": requester.email,
            "proposed_time": match.proposed_time.isoformat(),
            "venue_name": venue.name,
            "venue_type": venue.type,
            "message": match.message,
            "created_at": match.created_at.isoformat()
        })
    
    return result

# 响应匹配请求
@app.put("/api/matches/{match_id}/respond")
def respond_to_match(
    match_id: int,
    action: str = Form(...),  # accept, reject, reschedule
    new_time_slot_id: Optional[int] = Form(None),
    new_venue_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    match = db.query(MatchRequest).filter(MatchRequest.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match request not found")
    
    if action == "accept":
        match.status = "accepted"
        # 将对应的时间槽标记为已预订
        time_slot = db.query(TimeSlot).filter(
            TimeSlot.user_id == match.target_id,
            TimeSlot.start_time == match.proposed_time
        ).first()
        if time_slot:
            time_slot.status = "booked"
            
    elif action == "reject":
        match.status = "rejected"
        
    elif action == "reschedule":
        if new_time_slot_id:
            new_time_slot = db.query(TimeSlot).filter(TimeSlot.id == new_time_slot_id).first()
            if new_time_slot:
                match.proposed_time = new_time_slot.start_time
        if new_venue_id:
            match.venue_id = new_venue_id
        match.status = "rescheduled"
    
    db.commit()
    return {"message": f"Match request {action}ed successfully"}

# 获取发送的匹配请求
@app.get("/api/matches/sent/{user_id}")
def get_sent_matches(user_id: int, db: Session = Depends(get_db)):
    matches = db.query(MatchRequest).filter(MatchRequest.requester_id == user_id).all()
    
    result = []
    for match in matches:
        target = db.query(User).filter(User.id == match.target_id).first()
        venue = db.query(Venue).filter(Venue.id == match.venue_id).first()
        
        result.append({
            "id": match.id,
            "target_name": target.name,
            "target_email": target.email,
            "proposed_time": match.proposed_time.isoformat(),
            "venue_name": venue.name,
            "status": match.status,
            "message": match.message,
            "created_at": match.created_at.isoformat()
        })
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)