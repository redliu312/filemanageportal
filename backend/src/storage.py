import os
from typing import Optional, Tuple
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import logging
from flask import current_app

logger = logging.getLogger(__name__)

# Try to import Supabase, but don't fail if it's not available
try:
    from supabase import Client
    from .supabase_fix import create_fixed_supabase_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.info("Supabase not available, using local storage only")

class StorageService:
    """Service for handling file storage operations with both local and Supabase Storage"""
    
    def __init__(self):
        self.storage_mode = os.getenv('STORAGE_MODE', 'local').lower()  # 'local' or 'supabase'
        
        # Use Flask's logger if available, otherwise use module logger
        self.logger = current_app.logger if current_app else logger
        
        self.logger.info(f"Initializing StorageService with mode: {self.storage_mode}")
        
        if self.storage_mode == 'supabase':
            if not SUPABASE_AVAILABLE:
                self.logger.warning("Supabase storage requested but supabase-py not installed. Falling back to local storage.")
                self.storage_mode = 'local'
            else:
                self.supabase_url = os.getenv('SUPABASE_URL')
                self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
                self.bucket_name = os.getenv('SUPABASE_STORAGE_BUCKET', 'files')
                
                self.logger.debug(f"Supabase URL: {self.supabase_url}")
                self.logger.debug(f"Supabase key present: {bool(self.supabase_key)}")
                self.logger.debug(f"Bucket name: {self.bucket_name}")
                
                if not self.supabase_url or not self.supabase_key:
                    self.logger.warning("Supabase credentials not found. Falling back to local storage.")
                    self.logger.debug(f"SUPABASE_URL present: {bool(self.supabase_url)}")
                    self.logger.debug(f"SUPABASE_SERVICE_KEY present: {bool(self.supabase_key)}")
                    self.storage_mode = 'local'
                else:
                    try:
                        # Ensure the keys are strings
                        url = str(self.supabase_url) if self.supabase_url else ""
                        key = str(self.supabase_key) if self.supabase_key else ""
                        
                        self.logger.debug(f"Creating Supabase client with URL type: {type(url)}, key type: {type(key)}")
                        
                        # Use the fixed client creation to prevent header encoding issues
                        self.client: Client = create_fixed_supabase_client(url, key)
                        self.logger.info("Supabase client created successfully with header fixes applied")
                        
                        # Patch the client to ensure headers are strings
                        if hasattr(self.client, 'storage') and hasattr(self.client.storage, '_client'):
                            storage_client = self.client.storage._client
                            if hasattr(storage_client, '_headers'):
                                # Convert any boolean headers to strings
                                original_headers = storage_client._headers.copy()
                                for key, value in original_headers.items():
                                    if isinstance(value, bool):
                                        self.logger.info(f"FOUND BOOLEAN HEADER during init - {key}: {value}, converting to string")
                                        storage_client._headers[key] = str(value).lower()
                                    elif value is None:
                                        self.logger.info(f"Found None header during init - {key}, converting to empty string")
                                        storage_client._headers[key] = ""
                                    elif not isinstance(value, str):
                                        self.logger.info(f"Found non-string header during init - {key}: {value} (type: {type(value)}), converting to string")
                                        storage_client._headers[key] = str(value)
                        
                        self._ensure_bucket_exists()
                    except Exception as e:
                        self.logger.error(f"Failed to create Supabase client: {str(e)}")
                        self.logger.exception("Full traceback:")
                        self.storage_mode = 'local'
        
        if self.storage_mode == 'local':
            self.upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
            try:
                os.makedirs(self.upload_folder, exist_ok=True)
                self.logger.info(f"Using local storage in folder: {self.upload_folder}")
            except Exception as e:
                self.logger.error(f"Failed to create upload folder: {str(e)}")
                raise
        else:
            self.logger.info("Using Supabase storage")
    
    def _ensure_bucket_exists(self):
        """Ensure the storage bucket exists, create if it doesn't"""
        if self.storage_mode != 'supabase':
            return
            
        try:
            buckets = self.client.storage.list_buckets()
            # Handle different response formats from Supabase
            if isinstance(buckets, list):
                bucket_names = [b.get('name') or b.get('id') for b in buckets if isinstance(b, dict)]
            else:
                # If it's not a list, try to extract bucket info differently
                bucket_names = []
                self.logger.warning(f"Unexpected bucket list format: {type(buckets)}")
            
            if self.bucket_name not in bucket_names:
                # Create bucket with minimal options
                try:
                    self.client.storage.create_bucket(self.bucket_name)
                    self.logger.info(f"Created storage bucket: {self.bucket_name}")
                except Exception as create_error:
                    # Bucket might already exist
                    self.logger.info(f"Bucket creation skipped: {create_error}")
            else:
                self.logger.info(f"Storage bucket already exists: {self.bucket_name}")
        except Exception as e:
            # Log the error but don't fail - bucket operations might not be critical
            self.logger.warning(f"Error checking/creating bucket: {str(e)}")
    
    def upload_file(self, file: FileStorage, user_id: int, filename: str) -> Optional[str]:
        """
        Upload a file to storage (local or Supabase)
        
        Args:
            file: The file to upload
            user_id: The ID of the user uploading the file
            filename: The unique filename to use for storage
            
        Returns:
            The storage path (relative path for local, bucket path for Supabase) if successful, None otherwise
        """
        # Create a user-specific path
        storage_path = f"user_{user_id}/{filename}"
        
        if self.storage_mode == 'local':
            return self._upload_local(file, storage_path)
        else:
            return self._upload_supabase(file, storage_path)
    
    def _upload_local(self, file: FileStorage, storage_path: str) -> Optional[str]:
        """Upload file to local storage"""
        try:
            # Create full file path
            file_path = os.path.join(self.upload_folder, storage_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save file
            file.save(file_path)
            
            self.logger.info(f"File uploaded locally: {storage_path}")
            return storage_path
            
        except Exception as e:
            self.logger.error(f"Error uploading file locally: {str(e)}")
            return None
    
    def _upload_supabase(self, file: FileStorage, storage_path: str) -> Optional[str]:
        """Upload file to Supabase Storage"""
        try:
            self.logger.info(f"Starting Supabase upload for path: {storage_path}")
            self.logger.debug(f"File details - Name: {file.filename}, Content-Type: {file.content_type}")
            
            # Read file content
            file_content = file.read()
            file.seek(0)  # Reset file pointer
            
            self.logger.debug(f"File size: {len(file_content)} bytes")
            
            # Debug and fix storage client headers
            if hasattr(self.client.storage, '_client') and hasattr(self.client.storage._client, '_headers'):
                storage_client = self.client.storage._client
                self.logger.debug("Storage client headers before upload:")
                headers = storage_client._headers.copy()
                for key, value in headers.items():
                    self.logger.debug(f"  {key}: {repr(value)} (type: {type(value).__name__})")
                    # Fix any non-string headers
                    if isinstance(value, bool):
                        self.logger.info(f"FOUND BOOLEAN HEADER before upload - {key}: {value}, converting to string")
                        storage_client._headers[key] = str(value).lower()
                    elif value is None:
                        self.logger.info(f"Converting None header before upload - {key} to empty string")
                        storage_client._headers[key] = ""
                    elif not isinstance(value, str):
                        self.logger.info(f"Converting non-string header before upload - {key}: {value} to string")
                        storage_client._headers[key] = str(value)
            
            # Upload to Supabase Storage
            self.logger.debug(f"Uploading to bucket: {self.bucket_name}")
            
            # Wrap the upload call to catch the exact point of failure
            try:
                response = self.client.storage.from_(self.bucket_name).upload(
                    path=storage_path,
                    file=file_content,
                    file_options={
                        "content-type": file.content_type or 'application/octet-stream',
                        "upsert": False  # Don't overwrite existing files
                    }
                )
            except AttributeError as ae:
                self.logger.error(f"AttributeError during upload: {str(ae)}")
                # Try to find what's causing the boolean issue
                if hasattr(self.client, '_headers'):
                    self.logger.error("Client headers at error time:")
                    for k, v in self.client._headers.items():
                        self.logger.error(f"  {k}: {repr(v)} (type: {type(v).__name__})")
                raise
            
            # Log the response details
            self.logger.info(f"Supabase upload response: {response}")
            self.logger.debug(f"Response type: {type(response)}")
            
            # Check if response indicates success
            if response is False:
                self.logger.error("Supabase returned False - upload failed")
                self.logger.error("This usually means the file already exists or there's a permission issue")
                return None
            
            self.logger.info(f"File successfully uploaded to Supabase: {storage_path}")
            return storage_path
            
        except Exception as e:
            self.logger.error(f"Error uploading file to Supabase: {str(e)}")
            self.logger.exception("Full traceback:")
            return None
    
    def get_download_info(self, storage_path: str) -> Tuple[Optional[str], Optional[bytes]]:
        """
        Get download information based on storage mode.
        
        For local storage: Returns (None, file_bytes)
        For Supabase: Returns (signed_url, None)
        
        Args:
            storage_path: The storage path of the file
            
        Returns:
            Tuple of (url, bytes) - only one will be non-None based on storage mode
        """
        if self.storage_mode == 'local':
            file_bytes = self._download_local(storage_path)
            return (None, file_bytes)
        else:
            # Generate a signed URL valid for 1 hour
            signed_url = self._get_supabase_signed_url(storage_path, expires_in=3600)
            return (signed_url, None)
    
    def _get_supabase_signed_url(self, storage_path: str, expires_in: int) -> Optional[str]:
        """Get a temporary signed URL from Supabase"""
        try:
            response = self.client.storage.from_(self.bucket_name).create_signed_url(
                path=storage_path,
                expires_in=expires_in
            )
            return response['signedURL']
        except Exception as e:
            logger.error(f"Error creating signed URL: {str(e)}")
            return None
    
    def _download_local(self, storage_path: str) -> Optional[bytes]:
        """Download file from local storage"""
        try:
            file_path = os.path.join(self.upload_folder, storage_path)
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error downloading file locally: {str(e)}")
            return None
    
    def delete_file(self, storage_path: str) -> bool:
        """
        Delete a file from storage
        
        Args:
            storage_path: The storage path of the file
            
        Returns:
            True if successful, False otherwise
        """
        if self.storage_mode == 'local':
            return self._delete_local(storage_path)
        else:
            return self._delete_supabase(storage_path)
    
    def _delete_local(self, storage_path: str) -> bool:
        """Delete file from local storage"""
        try:
            file_path = os.path.join(self.upload_folder, storage_path)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted locally: {storage_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file locally: {str(e)}")
            return False
    
    def _delete_supabase(self, storage_path: str) -> bool:
        """Delete file from Supabase Storage"""
        try:
            response = self.client.storage.from_(self.bucket_name).remove([storage_path])
            logger.info(f"File deleted from Supabase: {storage_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file from Supabase: {str(e)}")
            return False
    
    def is_using_supabase(self) -> bool:
        """Check if using Supabase storage"""
        return self.storage_mode == 'supabase'
    
    def ensure_bucket_exists(self) -> bool:
        """Public method to ensure bucket exists"""
        if self.storage_mode != 'supabase':
            return True  # Local storage doesn't need buckets
        
        try:
            self._ensure_bucket_exists()
            return True
        except Exception as e:
            logger.error(f"Failed to ensure bucket exists: {str(e)}")
            return False

# Create a singleton instance
storage_service = None

def get_storage_service():
    """Get or create the storage service instance"""
    global storage_service
    if storage_service is None:
        storage_service = StorageService()
    return storage_service