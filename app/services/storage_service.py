"""Google Cloud Storage service for file operations"""

from google.cloud import storage
from datetime import timedelta
from typing import BinaryIO
from app.config import settings
import os

class StorageService:
    """Service for GCS operations"""

    def __init__(self):
        self.client = storage.Client(project=settings.PROJECT_ID)
        self.bucket_name = settings.GCS_BUCKET
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_file(
        self,
        file: BinaryIO,
        folder: str,
        filename: str,
        content_type: str
    ) -> dict:
        """Upload file to GCS"""
        blob_path = f"{folder}/{filename}"
        blob = self.bucket.blob(blob_path)

        blob.upload_from_file(file, content_type=content_type)

        return {
            'file_path': f"gs://{self.bucket_name}/{blob_path}",
            'blob_name': blob_path,
            'size': blob.size,
            'content_type': blob.content_type
        }

    def generate_signed_url(
        self,
        blob_name: str,
        expiration: int = 3600
    ) -> str:
        """Generate signed URL for download"""
        blob = self.bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=expiration),
            method="GET"
        )

        return url

    def delete_file(self, blob_name: str) -> None:
        """Delete file from GCS"""
        blob = self.bucket.blob(blob_name)
        blob.delete()

    def file_exists(self, blob_name: str) -> bool:
        """Check if file exists in GCS"""
        blob = self.bucket.blob(blob_name)
        return blob.exists()

# Global instance
storage_service = StorageService()
