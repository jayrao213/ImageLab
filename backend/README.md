# PhotoApp FastAPI Backend

This is the FastAPI backend for the PhotoApp application, migrated from the original `photoapp.py` module while preserving all logic and functionality.

## Features

- **User Management**: List all users
- **Image Upload/Download**: Upload images to S3, download by asset ID
- **AI Label Detection**: Automatic image labeling using AWS Rekognition
- **Label Search**: Search images by detected labels
- **Health Check**: Ping endpoint to verify S3 and database connectivity

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration management (loads .env)
├── database.py             # Database connection utilities
├── aws_services.py         # S3 and Rekognition clients
├── models.py               # Pydantic models for request/response
├── routes/
│   ├── __init__.py
│   ├── users.py           # User endpoints
│   ├── images.py          # Image upload/download/delete endpoints
│   ├── labels.py          # Label search endpoints
│   └── ping.py            # Health check endpoint
└── requirements.txt        # Python dependencies
```

## Configuration

The backend loads configuration from environment variables in a `.env` file. Copy `backend/.env.example` to `backend/.env` and set:

- `RDS_*`: MySQL database connection settings
- `S3_*`: S3 bucket and AWS credentials (read-only and read-write)

## Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

Start the development server:
```bash
uvicorn main:app --reload
```

Or run directly:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /ping` - Check S3 and database connectivity

### Users
- `GET /users/` - Get all users

### Images
- `GET /images/` - Get all images (optional `?userid=X` filter)
- `POST /images/` - Upload a new image (multipart form: userid, file)
- `GET /images/{assetid}` - Download an image by asset ID
- `DELETE /images/` - Delete all images

### Labels
- `GET /labels/image/{assetid}` - Get AI labels for a specific image
- `GET /labels/search?label=<term>` - Search images by label (supports partial matches)

## Migration from Original photoapp.py

All original functions have been migrated to FastAPI endpoints:

| Original Function | New Endpoint | File |
|------------------|--------------|------|
| `initialize()` | Handled by config.py | config.py |
| `get_ping()` | `GET /ping` | routes/ping.py |
| `get_users()` | `GET /users/` | routes/users.py |
| `get_images()` | `GET /images/` | routes/images.py |
| `post_image()` | `POST /images/` | routes/images.py |
| `get_image()` | `GET /images/{assetid}` | routes/images.py |
| `delete_images()` | `DELETE /images/` | routes/images.py |
| `get_image_labels()` | `GET /labels/image/{assetid}` | routes/labels.py |
| `get_images_with_label()` | `GET /labels/search` | routes/labels.py |

## Development Notes

- All original retry logic using tenacity is preserved
- Database connection handling matches the original implementation
- S3 and Rekognition client creation uses the same configuration
- Error handling and logging maintain the original behavior
- All SQL queries are unchanged from the original code
