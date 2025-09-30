from http.server import BaseHTTPRequestHandler
import json

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
            # Check content type first
            content_type = self.headers.get('Content-Type', '')
            if 'application/json' not in content_type:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "bad_request",
                    "detail": "Only POST with content-type: application/json is supported"
                }).encode())
                return
            
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "bad_request",
                    "detail": "Invalid JSON format"
                }).encode())
                return
            
            # Check for required fields
            if 'zip' not in data or 'measure_name' not in data:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "bad_request",
                    "detail": "Missing required fields: zip and measure_name"
                }).encode())
                return
            
            zip_code = data['zip']
            measure_name = data['measure_name']
            
            # Validate zip code format (5-digit string)
            if not isinstance(zip_code, str) or len(zip_code) != 5 or not zip_code.isdigit():
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "bad_request",
                    "detail": "Invalid zip code format"
                }).encode())
                return
            
            # Validate measure name
            if measure_name not in VALID_MEASURES:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "not_found",
                    "detail": "Invalid measure name"
                }).encode())
                return
            
            # Special case: coffee=teapot -> HTTP 418
            if data.get('coffee') == 'teapot':
                self.send_response(418)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "teapot",
                    "detail": "I'm a teapot"
                }).encode())
                return
            
            # Sample data for testing
            sample_data = [
                {
                    "zip": "90210",
                    "county": "Beverly Hills",
                    "state": "CA",
                    "measure_name": "Violent crime rate",
                    "value": "150.2",
                    "rank": "15"
                },
                {
                    "zip": "90210",
                    "county": "Beverly Hills", 
                    "state": "CA",
                    "measure_name": "Unemployment",
                    "value": "3.2",
                    "rank": "5"
                },
                {
                    "zip": "90210",
                    "county": "Beverly Hills",
                    "state": "CA", 
                    "measure_name": "Children in poverty",
                    "value": "8.5",
                    "rank": "12"
                }
            ]
            
            # Filter by zip and measure_name
            results = []
            for item in sample_data:
                if item["zip"] == zip_code and item["measure_name"] == measure_name:
                    results.append(item)
            
            if not results:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "not_found",
                    "detail": "No data found for the given zip and measure"
                }).encode())
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
            self.wfile.write(json.dumps({
                "error": "internal_server_error",
                "detail": "Internal server error"
            }).encode())
    
    def do_GET(self):
        # Handle GET requests with the specific error format
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "error": "bad_request",
            "detail": "Only POST with content-type: application/json is supported"
        }).encode())
    
    def do_PUT(self):
        # Handle other HTTP methods with the same error
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "error": "bad_request",
            "detail": "Only POST with content-type: application/json is supported"
        }).encode())
    
    def do_DELETE(self):
        # Handle other HTTP methods with the same error
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "error": "bad_request",
            "detail": "Only POST with content-type: application/json is supported"
        }).encode())