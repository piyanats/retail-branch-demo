# File Upload Implementation

## Overview

ระบบรองรับการอัพโหลดไฟล์เอกสารหลายประเภท โดยเก็บใน Google Cloud Storage (GCS) และบันทึก metadata ใน BigQuery ใช้ multipart form-data upload พร้อมรองรับ multiple files และ drag & drop

## File Types Support

| Team | Document Type | File Types | Max Size | Purpose |
|------|---------------|------------|----------|---------|
| Legal | ภ.พ.09 Documents | PDF, JPG, PNG | 10 MB | Legal documents |
| Legal | ภ.พ.20 Documents | PDF, JPG, PNG, XLS, XLSX | 10 MB | Tax documents, spreadsheets |
| SRD | Layout Plans | PDF, JPG, PNG, DWG | 10 MB | Floor plans, layouts |
| SCM | DC Documents | PDF, XLS, XLSX | 10 MB | Distribution center docs |
| New Branch | General Documents | PDF, JPG, PNG, XLS, XLSX | 10 MB | Any branch documents |

## GCS Bucket Structure

```
{GCS_BUCKET}/
├── legal/
│   ├── ppp09/
│   │   ├── BR001_ppp09_20240101.pdf
│   │   ├── BR001_ppp09_20240102_supplement.jpg
│   │   └── BR002_ppp09_20240103.pdf
│   └── ppp20/
│       ├── BR001_ppp20_202401.pdf
│       ├── BR001_ppp20_202402.xlsx
│       └── BR002_ppp20_202401.pdf
├── srd/
│   └── layout/
│       ├── BR001_layout_floor1.pdf
│       ├── BR001_layout_floor2.jpg
│       └── BR002_layout_main.dwg
├── scm/
│   └── dc/
│       ├── DC1_mapping_2024.xlsx
│       └── DC2_routes_2024.pdf
└── new_branch/
    └── documents/
        ├── BR005_proposal.pdf
        └── BR005_contract.pdf
```

**Naming Convention:**
```
{branch_id}_{document_type}_{timestamp_or_identifier}.{extension}
```

## Backend Implementation (Python/FastAPI)

### Storage Service (services/storage_service.py)

```python
from google.cloud import storage
from datetime import datetime, timedelta
import os
import uuid
import mimetypes

class StorageService:
    """Google Cloud Storage service for file operations"""

    def __init__(self):
        self.client = storage.Client()
        self.bucket_name = os.getenv('GCS_BUCKET')
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_file(
        self,
        file,
        folder: str,
        filename: str = None,
        content_type: str = None
    ) -> dict:
        """
        Upload file to GCS

        Args:
            file: File object (from FastAPI UploadFile)
            folder: Folder path in bucket (e.g., 'legal/ppp09')
            filename: Custom filename (optional, auto-generated if not provided)
            content_type: MIME type (optional, auto-detected if not provided)

        Returns:
            dict: File metadata including path, size, and public URL
        """
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ext = self._get_file_extension(file.filename)
            filename = f"{uuid.uuid4().hex}_{timestamp}.{ext}"

        # Full path in bucket
        blob_path = f"{folder}/{filename}"
        blob = self.bucket.blob(blob_path)

        # Set content type
        if not content_type:
            content_type = file.content_type or mimetypes.guess_type(file.filename)[0]

        # Upload file
        blob.upload_from_file(
            file.file,
            content_type=content_type,
            rewind=True
        )

        # Get file info
        return {
            'file_path': f"gs://{self.bucket_name}/{blob_path}",
            'file_name': filename,
            'file_size': blob.size,
            'mime_type': content_type,
            'public_url': blob.public_url if blob.public else None
        }

    def download_file(self, file_path: str):
        """
        Download file from GCS

        Args:
            file_path: Full GCS path (gs://bucket/path/to/file)

        Returns:
            bytes: File content
        """
        # Extract blob path from GCS path
        blob_path = file_path.replace(f"gs://{self.bucket_name}/", "")
        blob = self.bucket.blob(blob_path)

        if not blob.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        return blob.download_as_bytes()

    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from GCS

        Args:
            file_path: Full GCS path (gs://bucket/path/to/file)

        Returns:
            bool: True if deleted successfully
        """
        blob_path = file_path.replace(f"gs://{self.bucket_name}/", "")
        blob = self.bucket.blob(blob_path)

        if blob.exists():
            blob.delete()
            return True

        return False

    def generate_signed_url(self, file_path: str, expiration: int = 3600) -> str:
        """
        Generate signed URL for temporary access

        Args:
            file_path: Full GCS path
            expiration: URL expiration in seconds (default: 1 hour)

        Returns:
            str: Signed URL
        """
        blob_path = file_path.replace(f"gs://{self.bucket_name}/", "")
        blob = self.bucket.blob(blob_path)

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=expiration),
            method="GET"
        )

        return url

    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension"""
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    def validate_file(
        self,
        file,
        allowed_types: list,
        max_size: int
    ) -> tuple[bool, str]:
        """
        Validate file type and size

        Args:
            file: UploadFile object
            allowed_types: List of allowed MIME types or extensions
            max_size: Maximum file size in bytes

        Returns:
            tuple: (is_valid, error_message)
        """
        # Check file size
        if file.size > max_size:
            return False, f"File size exceeds maximum allowed size ({max_size / 1024 / 1024:.1f} MB)"

        # Check file type
        ext = self._get_file_extension(file.filename)
        mime_type = file.content_type

        is_allowed = (
            ext in allowed_types or
            mime_type in allowed_types or
            any(allowed.lower() == ext.lower() for allowed in allowed_types)
        )

        if not is_allowed:
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_types)}"

        return True, ""
```

### Upload API Endpoint (routes/legal_routes.py)

```python
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import uuid

router = APIRouter()
storage_service = StorageService()
bigquery_service = BigQueryService()

@router.post("/api/legal/ppp09/{ppp09_id}/upload-documents")
async def upload_ppp09_documents(
    ppp09_id: str,
    files: List[UploadFile] = File(...),
    document_type: str = Form(...),
    branch_id: str = Form(...)
):
    """
    Upload ภ.พ.09 documents

    Supports multiple files upload
    """
    # Validate ppp09 exists
    ppp09 = bigquery_service.get_ppp09(ppp09_id)
    if not ppp09:
        raise HTTPException(status_code=404, detail="ภ.พ.09 not found")

    # File validation settings
    ALLOWED_TYPES = ['pdf', 'jpg', 'jpeg', 'png', 'application/pdf', 'image/jpeg', 'image/png']
    MAX_SIZE = 10 * 1024 * 1024  # 10 MB

    uploaded_files = []
    errors = []

    for file in files:
        try:
            # Validate file
            is_valid, error_msg = storage_service.validate_file(
                file,
                ALLOWED_TYPES,
                MAX_SIZE
            )

            if not is_valid:
                errors.append({
                    'file_name': file.filename,
                    'error': error_msg
                })
                continue

            # Generate filename
            ext = storage_service._get_file_extension(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d')
            filename = f"{branch_id}_ppp09_{ppp09_id}_{timestamp}_{uuid.uuid4().hex[:8]}.{ext}"

            # Upload to GCS
            file_info = storage_service.upload_file(
                file=file,
                folder=f"legal/ppp09",
                filename=filename
            )

            # Save metadata to BigQuery
            document = {
                'document_id': str(uuid.uuid4()),
                'document_type': document_type,
                'reference_id': ppp09_id,
                'branch_id': branch_id,
                'file_name': file.filename,
                'file_path': file_info['file_path'],
                'file_size': file_info['file_size'],
                'mime_type': file_info['mime_type'],
                'uploaded_at': datetime.now(timezone.utc),
                'uploaded_by': current_user.email
            }

            bigquery_service.insert_legal_document(document)

            uploaded_files.append({
                'document_id': document['document_id'],
                'file_name': file.filename,
                'file_size': file_info['file_size'],
                'uploaded_at': document['uploaded_at'].isoformat()
            })

        except Exception as e:
            errors.append({
                'file_name': file.filename,
                'error': str(e)
            })

    # Audit log
    audit_service.log_action(
        user_id=current_user.user_id,
        action_type='ppp09_document_upload',
        resource_type='ppp09',
        resource_id=ppp09_id,
        action_detail={
            'files_count': len(files),
            'uploaded_count': len(uploaded_files),
            'error_count': len(errors)
        }
    )

    return {
        'success': True,
        'message': f"Uploaded {len(uploaded_files)} of {len(files)} files",
        'data': uploaded_files,
        'errors': errors if errors else None
    }
```

### Download API Endpoint

```python
@router.get("/api/legal/ppp09/{ppp09_id}/download-document/{document_id}")
async def download_ppp09_document(
    ppp09_id: str,
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Download ภ.พ.09 document"""

    # Get document metadata
    document = bigquery_service.get_legal_document(document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document['reference_id'] != ppp09_id:
        raise HTTPException(status_code=400, detail="Document does not belong to this ภ.พ.09")

    # Check permissions
    if not user_has_permission(current_user, 'legal'):
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Download file from GCS
    file_content = storage_service.download_file(document['file_path'])

    # Audit log
    audit_service.log_action(
        user_id=current_user.user_id,
        action_type='ppp09_document_download',
        resource_type='ppp09',
        resource_id=ppp09_id,
        action_detail={
            'document_id': document_id,
            'file_name': document['file_name']
        }
    )

    # Return file response
    from fastapi.responses import Response

    return Response(
        content=file_content,
        media_type=document['mime_type'],
        headers={
            'Content-Disposition': f'attachment; filename="{document["file_name"]}"'
        }
    )
```

## Frontend Implementation

### File Upload Component Usage

```javascript
// pages/legal/ppp09.js

// Initialize file upload component
const fileUpload = new FileUpload('uploadContainer', {
  multiple: true,
  accept: '.pdf,.jpg,.jpeg,.png',
  maxSize: 10 * 1024 * 1024,
  endpoint: `/api/legal/ppp09/${ppp09Id}/upload-documents`,
  onSuccess: (data) => {
    Toast.success(`Uploaded ${data.data.length} files successfully`);
    loadDocuments(); // Reload document list
  },
  onError: (error) => {
    Toast.error(error.message || 'Upload failed');
  },
  onProgress: (progress) => {
    console.log(`Upload progress: ${progress}%`);
  }
});

// Upload button handler
document.getElementById('uploadBtn').addEventListener('click', async () => {
  await fileUpload.upload();
});
```

### Download File

```javascript
async function downloadDocument(documentId, fileName) {
  try {
    await API.download(
      `/api/legal/ppp09/${ppp09Id}/download-document/${documentId}`,
      fileName
    );
    Toast.success('Download started');
  } catch (error) {
    Toast.error('Download failed');
  }
}
```

## File Validation Rules

### Server-Side Validation (Required)

```python
# Validation rules
VALIDATION_RULES = {
    'legal_ppp09': {
        'allowed_types': ['pdf', 'jpg', 'jpeg', 'png'],
        'max_size': 10 * 1024 * 1024,  # 10 MB
        'mime_types': ['application/pdf', 'image/jpeg', 'image/png']
    },
    'legal_ppp20': {
        'allowed_types': ['pdf', 'jpg', 'jpeg', 'png', 'xls', 'xlsx'],
        'max_size': 10 * 1024 * 1024,
        'mime_types': [
            'application/pdf',
            'image/jpeg',
            'image/png',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]
    },
    'srd_layout': {
        'allowed_types': ['pdf', 'jpg', 'jpeg', 'png', 'dwg'],
        'max_size': 10 * 1024 * 1024,
        'mime_types': ['application/pdf', 'image/jpeg', 'image/png', 'application/acad']
    }
}
```

### Client-Side Validation (Optional, for UX)

```javascript
function validateFile(file) {
  const maxSize = 10 * 1024 * 1024; // 10 MB
  const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png'];

  if (file.size > maxSize) {
    return { valid: false, error: 'File too large (max 10 MB)' };
  }

  if (!allowedTypes.includes(file.type)) {
    return { valid: false, error: 'Invalid file type' };
  }

  return { valid: true };
}
```

## Security Considerations

### 1. File Type Validation
- **Check MIME type** from request headers
- **Check file extension**
- **Verify file content** (magic numbers) for critical uploads
- **Block executable files** (.exe, .sh, .bat, etc.)

### 2. File Size Limits
- **Client-side check**: Improve UX, prevent unnecessary uploads
- **Server-side enforcement**: Required, never trust client
- **Configure web server limits**: Nginx/Apache max upload size

### 3. Filename Sanitization
- **Generate unique filenames**: Use UUID + timestamp
- **Remove special characters** from original filename
- **Prevent path traversal**: Check for `../` patterns

### 4. Storage Security
- **Private buckets**: Not publicly accessible by default
- **Signed URLs**: Temporary access for authorized users
- **Access control**: IAM policies for GCS bucket
- **Encryption at rest**: Enable GCS encryption

### 5. Virus Scanning (Optional)
- Integrate with **Cloud Security Scanner** or **ClamAV**
- Scan files before saving to permanent storage
- Quarantine suspicious files

## Error Handling

### Common Upload Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `FILE_TOO_LARGE` | File exceeds max size | Reduce file size or compress |
| `INVALID_FILE_TYPE` | File type not allowed | Convert to allowed format |
| `UPLOAD_FAILED` | Network or storage error | Retry upload |
| `PERMISSION_DENIED` | User lacks permissions | Contact admin |
| `STORAGE_QUOTA_EXCEEDED` | GCS quota exceeded | Clean up old files or increase quota |

### Error Response Format

```json
{
  "success": false,
  "error": "Upload failed",
  "code": "FILE_TOO_LARGE",
  "details": {
    "file_name": "document.pdf",
    "file_size": 12582912,
    "max_size": 10485760
  }
}
```

## Performance Optimization

### 1. Chunked Upload (For Large Files)
```python
# Use resumable uploads for files > 5MB
from google.cloud.storage import transfer_manager

blob.upload_from_filename(
    filename,
    chunk_size=1024 * 1024,  # 1MB chunks
    num_retries=3
)
```

### 2. Concurrent Uploads
```javascript
// Upload multiple files in parallel (max 3 at a time)
async function uploadFiles(files) {
  const MAX_CONCURRENT = 3;
  const results = [];

  for (let i = 0; i < files.length; i += MAX_CONCURRENT) {
    const batch = files.slice(i, i + MAX_CONCURRENT);
    const batchResults = await Promise.all(
      batch.map(file => uploadSingleFile(file))
    );
    results.push(...batchResults);
  }

  return results;
}
```

### 3. Client-Side Compression
```javascript
// Compress images before upload (optional)
async function compressImage(file) {
  // Use canvas API or library like pica.js
  // Reduce image size while maintaining quality
}
```

## Related Documentation

- [../development/api-standards.md](../development/api-standards.md) - API conventions
- [javascript.md](javascript.md) - FileUpload component
- [../DATABASE.md](../DATABASE.md) - legal_documents table schema
