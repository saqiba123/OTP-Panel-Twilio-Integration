import random
import time
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from init_db import SessionLocal, VirtualNumber,OTP
from twilio.rest import Client
import keys
import os
from dotenv import load_dotenv

load_dotenv()

# Twilio Configurations
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
account_token = os.getenv("TWILIO_AUTH_TOKEN")
verify_sid = os.getenv("TWILIO_VERIFY_SERVICE_SID")
# Initialize Twilio Client
client = Client(account_sid, account_token)

app = FastAPI()
START_NUMBER = 923000000000  #  Pakistan Virtual Number Series 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Next Available Virtual Number (Auto-Generate)
@app.get("/get_number")
def get_virtual_number(db: Session = Depends(get_db)):
    last_number = db.query(VirtualNumber).order_by(VirtualNumber.number.desc()).first()
    if last_number:
        next_number = int(last_number.number) + 1
    else:
        next_number = START_NUMBER 
    new_number = VirtualNumber(number=str(next_number), is_used=True)
    db.add(new_number)
    db.commit()

    return {"number": next_number}

# API to Generate OTP (Store in MySQL)
@app.post("/generate_otp/{phone_number}")
def generate_otp(phone_number: str, db: Session = Depends(get_db)):
    otp = random.randint(100000, 999999)
    current_time = int(time.time()) 
    otp_entry = db.query(OTP).filter_by(phone_number=phone_number).first()    # Check if OTP entry already exists
    if otp_entry:
        otp_entry.otp = otp
        otp_entry.timestamp = current_time  
        otp_entry.status = "pending"
    else:
        otp_entry = OTP(phone_number=phone_number, otp=otp, timestamp=current_time, status="pending")
        db.add(otp_entry)
    
    db.commit()
    return {"message": "OTP sent successfully", "otp": otp}

# API to Verify OTP 
@app.post("/verify_otp/{phone_number}/{otp}")
def verify_otp(phone_number: str, otp: int, db: Session = Depends(get_db)):
    otp_entry = db.query(OTP).filter_by(phone_number=phone_number).first()
    if not otp_entry:
        raise HTTPException(status_code=400, detail="OTP not found or expired")
    current_time = int(time.time())
    if otp_entry.status == "verified":
        return {"message": "OTP already verified"}

    if current_time - otp_entry.timestamp > 300: # 5min
        otp_entry.status = "expired"
        db.commit()
        raise HTTPException(status_code=400, detail="OTP expired")
    
    if otp_entry.otp == otp:
        otp_entry.status = "verified"
        db.commit()
        return {"message": "OTP verified successfully"}
    
    raise HTTPException(status_code=400, detail="Invalid OTP")


@app.post("/twilio_generate_otp/{phone_number}")
def twilio_generate_otp(phone_number: str):
    try:
        otp_verification = client.verify.v2.services(verify_sid).verifications.create(
            to=phone_number, channel="sms"
        )
        return {"message": "OTP sent successfully via Twilio", "status": otp_verification.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Twilio Error: {str(e)}")

# Twilio-based OTP Verification
@app.post("/twilio_verify_otp/{phone_number}/{otp}")
def twilio_verify_otp(phone_number: str, otp: str):
    try:
        otp_verify_code = client.verify.v2.services(verify_sid).verification_checks.create(
            to=phone_number, code=otp
        )
        if otp_verify_code.status == "approved":
            return {"message": "OTP verified successfully via Twilio"}
        else:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Twilio Error: {str(e)}")
