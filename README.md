# Homework 4: API Prototyping with Generative AI

This repository contains the implementation of Homework 4, which includes a CSV-to-SQLite converter and an API prototype for county health data queries.

## Repository Structure

```
├── csv_to_sqlite.py          # CSV to SQLite converter script
├── main.py                   # Local FastAPI server for testing
├── api/
│   └── county_data.py        # Vercel serverless function
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel deployment configuration
├── .gitignore               # Git ignore file
├── link.txt                 # Contains deployed API endpoint URL
└── README.md                # This file
```

## Part 1: CSV to SQLite Converter

The `csv_to_sqlite.py` script converts CSV files to SQLite database tables.

### Usage

```bash
python3 csv_to_sqlite.py data.db input.csv
```

### Features

- Creates or updates SQLite database `data.db`
- Table name is derived from CSV filename (without .csv extension)
- Header row becomes SQL column names
- Sanitizes column names (replaces spaces with underscores, removes special characters)
- Handles data type conversion automatically
- Clears existing data before inserting new data

### Example

```bash
python3 csv_to_sqlite.py data.db county_health_rankings.csv
```

This creates a table named `county_health_rankings` in `data.db`.

## Part 2: API Prototype

The API provides a `/county_data` endpoint for querying county health data.

### Endpoint

- **URL**: `/county_data`
- **Method**: POST
- **Content-Type**: `application/json`

### Request Format

```json
{
  "zip": "12345",
  "measure_name": "Violent crime rate"
}
```

### Valid Measure Names

- Violent crime rate
- Unemployment
- Children in poverty
- Diabetic screening
- Mammography screening
- Preventable hospital stays
- Uninsured
- Sexually transmitted infections
- Physical inactivity
- Adult obesity
- Premature Death
- Daily fine particulate matter

### Response Format

Returns a JSON array of rows matching the zip code and measure name:

```json
[
  {
    "column1": "value1",
    "column2": "value2",
    ...
  }
]
```

### Error Responses

- **400 Bad Request**: Missing required fields or invalid zip code format
- **404 Not Found**: Invalid measure name or no data found
- **418 I'm a teapot**: Special case when `coffee: "teapot"` is provided

## Local Development

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create the database with sample data:
```bash
rm data.db  # Remove existing database if any
python3 csv_to_sqlite.py data.db zip_county.csv
python3 csv_to_sqlite.py data.db county_health_rankings.csv
```

3. Run the local server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Testing

Test the API with curl:

```bash
curl -X POST "http://localhost:8000/county_data" \
  -H "Content-Type: application/json" \
  -d '{"zip": "12345", "measure_name": "Violent crime rate"}'
```

## Deployment

This project is configured for deployment on Vercel. The `api/county_data.py` file contains the serverless function implementation.

### Vercel Deployment

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. Update `link.txt` with the deployed URL.

## Security Features

- SQL injection prevention through parameterized queries
- Input validation for zip codes and measure names
- Proper error handling and sanitization
- Content-Type validation

## Testing Requirements

The implementation satisfies the testing requirements:

1. **Database Creation**:
   ```bash
   rm data.db && python3 csv_to_sqlite.py data.db zip_county.csv && python3 csv_to_sqlite.py data.db county_health_rankings.csv
   ```

2. **Database Verification**:
   ```bash
   sqlite3 data.db
   .schema
   .quit
   ```

3. **API Testing**:
   ```bash
   curl -X POST "https://your-deployed-url/county_data" \
     -H "Content-Type: application/json" \
     -d '{"zip": "12345", "measure_name": "Violent crime rate"}'
   ```
