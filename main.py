"""
Local FastAPI server for testing the county data API
Run with: python main.py
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os
from typing import List, Dict, Any

# Valid measure names as specified in requirements
VALID_MEASURES = [
    "Violent crime rate",
    "Unemployment", 
    "Children in poverty",
    "Diabetic screening",
    "Mammography screening",
    "Preventable hospital stays",
    "Uninsured",
    "Sexually transmitted infections",
    "Physical inactivity",
    "Adult obesity",
    "Premature Death",
    "Daily fine particulate matter"
]

app = FastAPI(title="County Health Data API", version="1.0.0")

class CountyDataRequest(BaseModel):
    zip: str
    measure_name: str
    coffee: str = None

@app.get("/")
async def root():
    return {
        "message": "County Health Data API",
        "endpoint": "/county_data",
        "method": "POST",
        "required_fields": ["zip", "measure_name"],
        "valid_measures": VALID_MEASURES
    }

@app.post("/county_data", response_model=List[Dict[str, Any]])
async def get_county_data(request: CountyDataRequest):
    # Validate zip code format (5-digit string)
    if len(request.zip) != 5 or not request.zip.isdigit():
        raise HTTPException(status_code=400, detail="Invalid zip code format")
    
    # Validate measure name
    if request.measure_name not in VALID_MEASURES:
        raise HTTPException(status_code=404, detail="Invalid measure name")
    
    # Special case: coffee=teapot -> HTTP 418
    if request.coffee == 'teapot':
        raise HTTPException(status_code=418, detail="I'm a teapot")
    
    # Query the database
    results = query_county_data(request.zip, request.measure_name)
    
    if results is None or not results:
        raise HTTPException(status_code=404, detail="No data found for the given zip and measure")
    
    return results

def query_county_data(zip_code: str, measure_name: str) -> List[Dict[str, Any]]:
    """
    Query the county_health_rankings table for data matching zip and measure_name.
    Returns a list of dictionaries representing the rows.
    """
    try:
        # Database path
        db_path = 'data.db'
        
        if not os.path.exists(db_path):
            return None
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        # Get the column names from the table
        cursor.execute("PRAGMA table_info(county_health_rankings)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Build the WHERE clause dynamically based on available columns
        where_conditions = []
        params = []
        
        # Look for zip-related columns
        zip_columns = [col for col in columns if 'zip' in col.lower()]
        if zip_columns:
            # Use the first zip column found
            zip_col = zip_columns[0]
            where_conditions.append(f'"{zip_col}" = ?')
            params.append(zip_code)
        
        # Look for measure-related columns
        measure_columns = [col for col in columns if 'measure' in col.lower() or 'name' in col.lower()]
        if measure_columns:
            # Use the first measure column found
            measure_col = measure_columns[0]
            where_conditions.append(f'"{measure_col}" = ?')
            params.append(measure_name)
        
        if not where_conditions:
            conn.close()
            return None
        
        # Execute the query
        query = f'SELECT * FROM county_health_rankings WHERE {" AND ".join(where_conditions)}'
        cursor.execute(query, params)
        
        # Convert rows to list of dictionaries
        rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(row))
        
        conn.close()
        
        return results if results else None
        
    except Exception as e:
        print(f"Database query error: {e}")
        return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)