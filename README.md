# Twilio Integration for OTP Verification
This project implements OTP verification using both manual storage (MySQL) and Twilio's Verify API.
Users can generate and verify OTPs using virtual numbers, with OTPs stored in MySQL and managed through FastAPI. 
Twilio's API is also integrated for seamless OTP delivery and verification. 
All sensitive credentials, including database and Twilio configurations, are securely managed using a .env file. 
