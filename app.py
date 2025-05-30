import functions as f
import logging
from fastapi import FastAPI, Depends, HTTPException, Security, Request
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title = "Motia API")

# Error Logging Middleware
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return {"detail": "Internal Server Error"}


API_KEY = "JD0XTu7Dte68MSOW7oNRSzSJsv9uKLSCGhVlDcuQ0Gw"  # Change this to a secure key
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.get("/fuelsites/fuelsites", dependencies=[Depends(verify_api_key)], tags=["Fuelsites"])
def fuelsites(limit: int = 1000, last_id: int = 0):
    MAX_LIMIT = 1000  # Set a maximum limit
    limit = min(limit, MAX_LIMIT)  # Ensure limit does not exceed MAX_LIMIT

    conn = f.connect_to_database()
    cursor = conn.cursor()

    # Fetch the next `limit` rows where ID > last seen ID
    query = f"""
        SELECT TOP {limit} * 
        FROM [data].[location].[fuel_sites] 
        WHERE fuel_site_id > {last_id} 
        ORDER BY fuel_site_id
    """
    cursor.execute(query)
    
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    conn.close()

    # Determine last_id for next page
    new_last_id = rows[-1][0] if rows else None

    return {
        "limit": limit,
        "max_limit": MAX_LIMIT,
        "last_id": new_last_id,  # Provide this in the next request for pagination
        "data": [dict(zip(columns, row)) for row in rows]
    }

@app.get("/fuelsites/fuelsite/{fuel_site_id}", dependencies=[Depends(verify_api_key)], tags=["Fuelsites"])
def get_fuel_site(fuel_site_id: int):
    conn = f.connect_to_database()
    cursor = conn.cursor()

    # Query for the specific fuel site by fuel_site_id
    cursor.execute("""
        SELECT * 
        FROM [data].[location].[fuel_sites] 
        WHERE fuel_site_id = ?
    """, (fuel_site_id,))
    
    row = cursor.fetchone()  # Fetch only one row

    conn.close()

    # Check if the fuel site exists
    if row is None:
        raise HTTPException(status_code=404, detail="Fuel site not found")
    
    # Convert the row to a dictionary using column names
    columns = [column[0] for column in cursor.description]
    fuel_site = dict(zip(columns, row))

    return fuel_site

@app.get("/fuelsites/pricing_attributes/{fuel_site_id}", dependencies=[Depends(verify_api_key)], tags=["Fuelsites"])
def get_pricing_attributes(fuel_site_id: int):
    conn = f.connect_to_database()
    cursor = conn.cursor()

    # Query for the specific fuel site by fuel_site_id
    cursor.execute("""
        SELECT * 
        FROM [data].[location].[fuelsite_pricing_attributes] 
        WHERE fuel_site_id = ?
    """, (fuel_site_id,))
    
    rows = cursor.fetchall()
    conn.close()

    # Check if the fuel site exists
    if rows is None:
        raise HTTPException(status_code=404, detail="Fuel site not found")
    
    # Convert the row to a dictionary using column names
    columns = [column[0] for column in cursor.description]
    fuel_site = [dict(zip(columns, row)) for row in rows]

    return fuel_site

@app.get("/fuelsites/pricing_attributes", dependencies=[Depends(verify_api_key)], tags=["Fuelsites"])
def get_all_pricing_attributes(limit: int = 1000, last_id: int = 0):
    MAX_LIMIT = 1000  # Set a maximum limit
    limit = min(limit, MAX_LIMIT)  # Ensure limit does not exceed MAX_LIMIT

    conn = f.connect_to_database()
    cursor = conn.cursor()

    # Fetch the next `limit` rows where ID > last seen ID
    query = f"""
        SELECT TOP {limit} *
        FROM [data].[location].[fuelsite_pricing_attributes] 
        WHERE id > {last_id} 
        ORDER BY id
    """
    cursor.execute(query)
    
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    conn.close()

    # Determine last_id for next page
    new_last_id = rows[-1][0] if rows else None

    return {
        "limit": limit,
        "max_limit": MAX_LIMIT,
        "last_id": new_last_id,  # Provide this in the next request for pagination
        "data": [dict(zip(columns, row)) for row in rows]
    }


@app.get("/fuelsites/cards_accepted/{fuel_site_id}", dependencies=[Depends(verify_api_key)], tags=["Fuelsites"])
def get_cards_accepted_by_site(fuel_site_id: int):
    conn = f.connect_to_database()
    cursor = conn.cursor()

    # Query for the specific fuel site by fuel_site_id
    cursor.execute("""
        SELECT * 
        FROM [data].[location].[fuelsite_cards_accepted]
        WHERE fuel_site_id = ?
    """, (fuel_site_id,))
    
    rows = cursor.fetchall()
    conn.close()

    # Check if the fuel site exists
    if rows is None:
        raise HTTPException(status_code=404, detail="Fuel site not found")
    
    # Convert the row to a dictionary using column names
    columns = [column[0] for column in cursor.description]
    cards = [dict(zip(columns, row)) for row in rows]

    return cards

@app.get("/fuelsites/cards_accepted", dependencies=[Depends(verify_api_key)], tags=["Fuelsites"])
def get_all_cards_accepted_by_sites(limit: int = 1000, last_id: int = 0):
    MAX_LIMIT = 1000  # Set a maximum limit
    limit = min(limit, MAX_LIMIT)  # Ensure limit does not exceed MAX_LIMIT

    conn = f.connect_to_database()
    cursor = conn.cursor()

    # Fetch the next `limit` rows where ID > last seen ID
    query = f"""
        SELECT TOP {limit} *
        FROM [data].[location].[fuelsite_cards_accepted]
        WHERE id > {last_id} 
        ORDER BY id
    """
    cursor.execute(query)
    
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    conn.close()

    # Determine last_id for next page
    new_last_id = rows[-1][0] if rows else None

    return {
        "limit": limit,
        "max_limit": MAX_LIMIT,
        "last_id": new_last_id,  # Provide this in the next request for pagination
        "data": [dict(zip(columns, row)) for row in rows]
    }

@app.get("/fuelsites/sites_by_card/{fuel_card_issuer_id}", dependencies=[Depends(verify_api_key)], tags=["Fuelsites"])
def get_cards_accepted_sites_by_card_issuer_id(fuel_card_issuer_id: int, limit: int = 50, last_id: int = 0):
    
    MAX_LIMIT = 100  # Set a maximum limit
    limit = min(limit, MAX_LIMIT)  # Ensure limit does not exceed MAX_LIMIT
    
    conn = f.connect_to_database()
    cursor = conn.cursor()

    # Corrected SQL Query
    query = f"""
        SELECT TOP {limit} * 
        FROM [data].[location].[fuelsite_cards_accepted]
        WHERE fuel_site_id > ? 
        AND fuel_card_issuer_id = ?
        ORDER BY fuel_site_id
    """
    cursor.execute(query, (last_id, fuel_card_issuer_id))
    
    rows = cursor.fetchall()

    # Check if any results were found
    if not rows:
        raise HTTPException(status_code=404, detail="Fuel sites not found")
    
    columns = [column[0] for column in cursor.description]

    # Determine last_id for next page
    new_last_id = rows[-1][1] if rows else None

    conn.close()

    return {
        "limit": limit,
        "max_limit": MAX_LIMIT,
        "last_id": new_last_id,  # Provide this in the next request for pagination
        "data": [dict(zip(columns, row)) for row in rows]
    }


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)},
    )