# PhotoApp Backend - Quick Start Guide

## Setup Instructions

### 1. Install Python Dependencies

Navigate to the backend directory and install required packages:

```bash
cd backend
pip install -r requirements.txt
```

Or install packages individually:
```bash
pip install fastapi uvicorn pydantic pydantic-settings pymysql boto3 python-multipart tenacity
```

### 2. Verify Configuration

Create `backend/.env` by copying `backend/.env.example`, then fill in your credentials:
- `RDS_*` - Database connection settings
- `S3_*` - S3 bucket configuration and AWS credentials

### 3. Run the Server

Start the FastAPI development server:

```bash
# Option 1: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Run the main script
python main.py
```

### 4. Test the API

Once the server is running:

1. **Visit the interactive documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

2. **Run the test script:**
   ```bash
   python test_api.py
   ```

3. **Test manually with curl:**
   ```bash
   # Health check
   curl http://localhost:8000/ping
   
   # Get all users
   curl http://localhost:8000/users/
   
   # Get all images
   curl http://localhost:8000/images/
   ```

## Available Endpoints

### Health & Info
- `GET /` - API information
- `GET /ping` - Health check (S3 + Database)

### Users
- `GET /users/` - List all users

### Images
- `GET /images/` - List all images (optional: `?userid=123`)
- `POST /images/` - Upload image (form-data: userid, file)
- `GET /images/{assetid}` - Download image
- `DELETE /images/` - Delete all images

### Labels
- `GET /labels/image/{assetid}` - Get labels for image
- `GET /labels/search?label=term` - Search images by label

## Uploading an Image (Example)

Using curl:
```bash
curl -X POST "http://localhost:8000/images/" \
  -F "userid=1001" \
  -F "file=@/path/to/image.jpg"
```

Using Python requests:
```python
import requests

url = "http://localhost:8000/images/"
files = {'file': open('image.jpg', 'rb')}
data = {'userid': 1001}
response = requests.post(url, files=files, data=data)
print(response.json())
```

## Troubleshooting

### Import Errors
If you see import errors in VS Code, install the dependencies:
```bash
pip install -r requirements.txt
```

### Database Connection Issues
- Verify `.env` has correct RDS credentials
- Ensure your IP is whitelisted in RDS security group
- Check VPN/network access to AWS

### S3 Access Issues  
- Verify AWS credentials in `.env`
- Ensure IAM user has S3 and Rekognition permissions
- Check bucket name and region are correct

### Port Already in Use
If port 8000 is busy, use a different port:
```bash
uvicorn main:app --reload --port 8080
```

## Next Steps

- Configure CORS settings in `main.py` for your frontend domain
- Set up environment variables for sensitive credentials
- Add authentication/authorization middleware
- Implement rate limiting for production
- Set up logging to external service (CloudWatch, etc.)
