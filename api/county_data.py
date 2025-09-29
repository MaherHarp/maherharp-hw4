from http.server import BaseHTTPRequestHandler
import json
import sqlite3
import os

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

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Check if this is the correct endpoint
            if self.path != '/county_data':
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Not found"}).encode())
                return
            
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Check content type
            content_type = self.headers.get('Content-Type', '')
            if 'application/json' not in content_type:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Content-Type must be application/json"}).encode())
                return
            
            # Parse JSON data
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                return
            
            # Check for required fields
            if 'zip' not in data or 'measure_name' not in data:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing required fields: zip and measure_name"}).encode())
                return
            
            zip_code = data['zip']
            measure_name = data['measure_name']
            
            # Validate zip code format (5-digit string)
            if not isinstance(zip_code, str) or len(zip_code) != 5 or not zip_code.isdigit():
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid zip code format"}).encode())
                return
            
            # Validate measure name
            if measure_name not in VALID_MEASURES:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid measure name"}).encode())
                return
            
            # Special case: coffee=teapot -> HTTP 418
            if data.get('coffee') == 'teapot':
                self.send_response(418)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "I'm a teapot"}).encode())
                return
            
            # Query the database
            results = self.query_county_data(zip_code, measure_name)
            
            if results is None:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No data found for the given zip and measure"}).encode())
                return
            
            # Return successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Internal server error"}).encode())
    
    def query_county_data(self, zip_code, measure_name):
        """
        Query the county_health_rankings table for data matching zip and measure_name.
        Returns a list of dictionaries representing the rows.
        """
        try:
            # Database path - in Vercel, this would be in the project directory
            db_path = '/var/task/data.db'
            
            # If running locally, use relative path
            if not os.path.exists(db_path):
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
    
    def do_GET(self):
        # Handle GET requests with a simple response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "message": "County Health Data API",
            "endpoint": "/county_data",
            "method": "POST",
            "required_fields": ["zip", "measure_name"],
            "valid_measures": VALID_MEASURES
        }).encode())