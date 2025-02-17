import functions as f
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

API_KEY = "JD0XTu7Dte68MSOW7oNRSzSJsv9uKLSCGhVlDcuQ0Gw"  # Change this to a secure key
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}

@app.get("/fuelsites", dependencies=[Depends(verify_api_key)])
def fuelsites():
    conn = f.connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT TOP (10) * FROM [data].[location].[fuel_sites]")
    rows = cursor.fetchall()
    conn.close()

    return [{"fuel_site_id": row[0], "cat_no": row[1], "fuel_site_status": row[2], "site_name": row[3]} for row in rows]  # Modify based on your schema