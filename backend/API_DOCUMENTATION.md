# File Management API Documentation

## Overview

This API provides file management capabilities with JWT-based authentication. All endpoints require a valid JWT token in the Authorization header. Users can only access and manage their own files.

## Base URL

- **Development**: `http://localhost:5001/api`
- **Production**: `https://your-domain.vercel.app/api`

## Authentication

All file management endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Upload File

Upload a new file associated with the authenticated user.

**Endpoint**: `POST /files`

**Headers**:
- `Authorization: Bearer <token>` (required)
- `Content-Type: multipart/form-data`

**Request Body** (multipart/form-data):
- `file`: The file to upload (required)

**Success Response** (201 Created):
```json
{
  "message": "File uploaded successfully",
  "file": {
    "id": 1,
    "filename": "document.pdf",
    "original_filename": "document.pdf",
    "file_size": 1024000,
    "mime_type": "application/pdf",
    "storage_path": "uploads/abc123_document.pdf",
    "upload_date": "2025-11-11T10:30:00.000Z",
    "is_deleted": false,
    "download_count": 0
  }
}
```

**Error Responses**:
- `400 Bad Request`: No file provided
- `401 Unauthorized`: Missing or invalid token
- `500 Internal Server Error`: Server error during upload

**Example**:
```bash
curl -X POST http://localhost:5001/api/files \
  -H "Authorization: Bearer your_token_here" \
  -F "file=@/path/to/document.pdf"
```

---

### 2. List Files

Get a paginated list of files owned by the authenticated user.

**Endpoint**: `GET /files`

**Headers**:
- `Authorization: Bearer <token>` (required)

**Query Parameters**:
- `page` (optional, default: 1): Page number
- `size` (optional, default: 10): Number of items per page

**Success Response** (200 OK):
```json
{
  "files": [
    {
      "id": 1,
      "filename": "document.pdf",
      "original_filename": "document.pdf",
      "file_size": 1024000,
      "mime_type": "application/pdf",
      "upload_date": "2025-11-11T10:30:00.000Z",
      "download_count": 5
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "pages": 1
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token

**Example**:
```bash
curl -X GET "http://localhost:5001/api/files?page=1&size=10" \
  -H "Authorization: Bearer your_token_here"
```

---

### 3. Get File Details

Get detailed information about a specific file.

**Endpoint**: `GET /files/<file_id>`

**Headers**:
- `Authorization: Bearer <token>` (required)

**URL Parameters**:
- `file_id`: The ID of the file

**Success Response** (200 OK):
```json
{
  "id": 1,
  "filename": "document.pdf",
  "original_filename": "document.pdf",
  "file_size": 1024000,
  "mime_type": "application/pdf",
  "storage_path": "uploads/abc123_document.pdf",
  "upload_date": "2025-11-11T10:30:00.000Z",
  "is_deleted": false,
  "download_count": 5
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: File belongs to another user
- `404 Not Found`: File not found

**Example**:
```bash
curl -X GET http://localhost:5001/api/files/1 \
  -H "Authorization: Bearer your_token_here"
```

---

### 4. Download File

Download a file and increment its download counter.

**Endpoint**: `GET /files/<file_id>/download`

**Headers**:
- `Authorization: Bearer <token>` (required)

**URL Parameters**:
- `file_id`: The ID of the file

**Success Response** (200 OK):
- Returns the file as an attachment with appropriate Content-Type and Content-Disposition headers

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: File belongs to another user
- `404 Not Found`: File not found or file deleted from storage

**Example**:
```bash
curl -X GET http://localhost:5001/api/files/1/download \
  -H "Authorization: Bearer your_token_here" \
  -o downloaded_file.pdf
```

---

### 5. Rename File

Update the filename of a file.

**Endpoint**: `PATCH /files/<file_id>`

**Headers**:
- `Authorization: Bearer <token>` (required)
- `Content-Type: application/json`

**URL Parameters**:
- `file_id`: The ID of the file

**Request Body**:
```json
{
  "filename": "new_filename.pdf"
}
```

**Success Response** (200 OK):
```json
{
  "message": "File renamed successfully",
  "file": {
    "id": 1,
    "filename": "new_filename.pdf",
    "original_filename": "document.pdf",
    "file_size": 1024000,
    "mime_type": "application/pdf",
    "upload_date": "2025-11-11T10:30:00.000Z",
    "download_count": 5
  }
}
```

**Error Responses**:
- `400 Bad Request`: Missing filename in request
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: File belongs to another user
- `404 Not Found`: File not found

**Example**:
```bash
curl -X PATCH http://localhost:5001/api/files/1 \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{"filename": "new_filename.pdf"}'
```

---

### 6. Delete File

Soft delete a file (marks as deleted but doesn't remove from storage).

**Endpoint**: `DELETE /files/<file_id>`

**Headers**:
- `Authorization: Bearer <token>` (required)

**URL Parameters**:
- `file_id`: The ID of the file

**Success Response** (200 OK):
```json
{
  "message": "File deleted successfully"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: File belongs to another user
- `404 Not Found`: File not found

**Example**:
```bash
curl -X DELETE http://localhost:5001/api/files/1 \
  -H "Authorization: Bearer your_token_here"
```

---

## Authentication Endpoints

For obtaining JWT tokens, see the authentication endpoints:

### Sign Up

**Endpoint**: `POST /auth/signup`

**Request Body**:
```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Success Response** (201 Created):
```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com"
  }
}
```

---

### Login

**Endpoint**: `POST /auth/login`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Success Response** (200 OK):
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com"
  }
}
```

---

### Logout

**Endpoint**: `POST /auth/logout`

**Headers**:
- `Authorization: Bearer <token>` (required)

**Success Response** (200 OK):
```json
{
  "message": "Logout successful"
}
```

---

### Get Profile

**Endpoint**: `GET /auth/profile`

**Headers**:
- `Authorization: Bearer <token>` (required)

**Success Response** (200 OK):
```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com"
}
```

---

## Error Handling

All endpoints follow a consistent error response format:

```json
{
  "error": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Authenticated but not authorized to access resource
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Security Features

1. **JWT Authentication**: All file operations require valid JWT tokens
2. **User Isolation**: Users can only access their own files
3. **Ownership Validation**: Every file operation validates user ownership
4. **Secure Filenames**: Uploaded files are stored with secure, unique names
5. **Soft Delete**: Deleted files are marked as deleted rather than physically removed

---

## File Storage

- Files are stored in the `uploads/` directory
- Each file is saved with a unique identifier prefix to prevent naming conflicts
- Original filenames are preserved in the database
- File metadata (size, MIME type, upload date) is tracked

---

## Rate Limiting

Currently, there are no rate limits implemented. Consider adding rate limiting in production to prevent abuse.

---

## Testing with cURL

### Complete Workflow Example

1. **Sign up**:
```bash
curl -X POST http://localhost:5001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

2. **Login and get token**:
```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

3. **Upload a file** (replace TOKEN with actual token):
```bash
curl -X POST http://localhost:5001/api/files \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@/path/to/file.pdf"
```

4. **List files**:
```bash
curl -X GET http://localhost:5001/api/files \
  -H "Authorization: Bearer TOKEN"
```

5. **Download file** (replace FILE_ID):
```bash
curl -X GET http://localhost:5001/api/files/FILE_ID/download \
  -H "Authorization: Bearer TOKEN" \
  -o downloaded_file.pdf
```

6. **Rename file**:
```bash
curl -X PATCH http://localhost:5001/api/files/FILE_ID \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename":"renamed_file.pdf"}'
```

7. **Delete file**:
```bash
curl -X DELETE http://localhost:5001/api/files/FILE_ID \
  -H "Authorization: Bearer TOKEN"
```

---

## Database Schema

### User Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password
- `created_at`: Account creation timestamp

### File Table
- `id`: Primary key
- `user_id`: Foreign key to User table
- `filename`: Display filename
- `original_filename`: Original uploaded filename
- `file_size`: File size in bytes
- `mime_type`: MIME type of the file
- `storage_path`: Path to file in storage
- `upload_date`: Upload timestamp
- `is_deleted`: Soft delete flag
- `download_count`: Number of times downloaded