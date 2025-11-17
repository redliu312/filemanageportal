"""
File management routes with JWT authentication
"""
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, redirect
from werkzeug.utils import secure_filename
from sqlalchemy import desc

from src.models import db, File
from src.auth import login_required
from src.storage import get_storage_service
from flask import current_app


files_bp = Blueprint('files', __name__, url_prefix='/api/files')


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@files_bp.route('', methods=['POST'])
@login_required
def upload_file(user):
    """
    Upload a file
    
    Request:
        - multipart/form-data with 'file' field
    
    Returns:
        201: File uploaded successfully
        400: No file provided or invalid file
        413: File too large
    """
    # Log request details
    current_app.logger.info(f"=== FILE UPLOAD REQUEST ===")
    current_app.logger.info(f"User ID: {user.id}")
    current_app.logger.info(f"Content-Type: {request.content_type}")
    current_app.logger.info(f"Content-Length: {request.content_length}")
    current_app.logger.info(f"MAX_CONTENT_LENGTH config: {current_app.config.get('MAX_CONTENT_LENGTH')}")
    current_app.logger.info(f"Request files: {list(request.files.keys())}")
    
    # Check if file is in request
    if 'file' not in request.files:
        current_app.logger.error("No file provided in request")
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        current_app.logger.error("Empty filename")
        return jsonify({'error': 'No file selected'}), 400
    
    # Get allowed extensions from config
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS')
    current_app.logger.info(f"Allowed extensions config: {allowed_extensions}")
    
    # If ALLOWED_EXTENSIONS is None or empty, allow all file types
    if allowed_extensions and not allowed_file(file.filename, allowed_extensions):
        current_app.logger.error(f"File type not allowed: {file.filename}")
        return jsonify({
            'error': 'File type not allowed',
            'allowed_types': list(allowed_extensions)
        }), 400
    
    try:
        current_app.logger.info(f"Starting file upload for user {user.id}")
        current_app.logger.debug(f"Original filename: {file.filename}")
        current_app.logger.debug(f"Content type: {file.content_type}")
        
        # Secure the filename
        original_filename = secure_filename(file.filename)
        
        # Generate unique filename to avoid conflicts
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{user.id}_{timestamp}_{original_filename}"
        current_app.logger.debug(f"Generated unique filename: {filename}")
        
        # Get storage service
        storage = get_storage_service()
        current_app.logger.info(f"Storage service initialized, mode: {storage.storage_mode}")
        
        # Upload file to storage (local or Supabase)
        current_app.logger.info("Calling storage.upload_file()")
        storage_path = storage.upload_file(file, user.id, filename)
        current_app.logger.info(f"Storage upload result: {storage_path}")
        
        if not storage_path:
            current_app.logger.error("Storage upload returned None/empty path")
            return jsonify({'error': 'Failed to upload file to storage'}), 500
        
        # Get file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        current_app.logger.info(f"File size: {file_size} bytes ({file_size / 1024 / 1024:.2f} MB)")
        
        # Create database record
        new_file = File(
            filename=filename,  # Store the unique filename
            original_filename=original_filename,  # Store the original filename
            file_path=storage_path,  # Store the storage path (local path or Supabase bucket path)
            file_size=file_size,
            mime_type=file.content_type or 'application/octet-stream',
            user_id=user.id
        )
        
        db.session.add(new_file)
        db.session.commit()
        
        current_app.logger.info(f"File record created in database with ID: {new_file.id}")
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file': {
                'id': new_file.id,
                'filename': new_file.original_filename,  # Return original filename to user
                'size': new_file.file_size,
                'mime_type': new_file.mime_type,
                'uploaded_at': new_file.uploaded_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"File upload failed: {str(e)}")
        current_app.logger.exception("Full traceback:")
        return jsonify({
            'error': 'Failed to upload file',
            'message': str(e),
            'type': type(e).__name__
        }), 500


@files_bp.route('', methods=['GET'])
@login_required
def list_files(user):
    """
    List user's files with pagination
    
    Query params:
        - page: Page number (default: 1)
        - size: Items per page (default: 10, max: 100)
    
    Returns:
        200: List of files
    """
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    
    # Limit page size
    size = min(size, 100)
    
    # Query files owned by current user (exclude deleted)
    query = File.query.filter_by(
        user_id=user.id,
        is_deleted=False
    ).order_by(desc(File.uploaded_at))
    
    # Paginate
    pagination = query.paginate(
        page=page,
        per_page=size,
        error_out=False
    )
    
    files = [{
        'id': f.id,
        'filename': f.original_filename,  # Return original filename to user
        'size': f.file_size,
        'mime_type': f.mime_type,
        'uploaded_at': f.uploaded_at.isoformat(),
        'download_count': f.download_count
    } for f in pagination.items]
    
    return jsonify({
        'files': files,
        'pagination': {
            'page': pagination.page,
            'size': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@files_bp.route('/<int:file_id>', methods=['GET'])
@login_required
def get_file(user, file_id):
    """
    Get file details
    
    Returns:
        200: File details
        403: Not authorized
        404: File not found
    """
    file = db.session.get(File, file_id)
    
    if not file or file.is_deleted:
        return jsonify({'error': 'File not found'}), 404
    
    # Check ownership
    if file.user_id != user.id:
        return jsonify({'error': 'Not authorized to access this file'}), 403
    
    return jsonify({
        'file': {
            'id': file.id,
            'filename': file.original_filename,  # Return original filename to user
            'size': file.file_size,
            'mime_type': file.mime_type,
            'uploaded_at': file.uploaded_at.isoformat(),
            'download_count': file.download_count
        }
    }), 200


@files_bp.route('/<int:file_id>/download', methods=['GET'])
@login_required
def download_file(user, file_id):
    """
    Download a file
    
    Returns:
        200: File content (for local storage)
        302: Redirect to signed URL (for Supabase storage)
        403: Not authorized
        404: File not found
    """
    file = db.session.get(File, file_id)
    
    if not file or file.is_deleted:
        return jsonify({'error': 'File not found'}), 404
    
    # Check ownership
    if file.user_id != user.id:
        return jsonify({'error': 'Not authorized to download this file'}), 403
    
    # Get storage service
    storage = get_storage_service()
    
    # Get download info based on storage mode
    signed_url, file_bytes = storage.get_download_info(file.file_path)
    
    # Increment download count
    file.download_count += 1
    db.session.commit()
    
    if storage.is_using_supabase():
        # For Supabase, redirect to the signed URL
        if signed_url:
            return redirect(signed_url)
        else:
            return jsonify({'error': 'Failed to generate download URL'}), 500
    else:
        # For local storage, send the file directly
        if file_bytes:
            from io import BytesIO
            return send_file(
                BytesIO(file_bytes),
                as_attachment=True,
                download_name=file.original_filename,
                mimetype=file.mime_type
            )
        else:
            return jsonify({'error': 'File not found on server'}), 404


@files_bp.route('/<int:file_id>', methods=['PATCH'])
@login_required
def rename_file(user, file_id):
    """
    Rename a file
    
    Request body:
        {
            "filename": "new_name.txt"
        }
    
    Returns:
        200: File renamed successfully
        400: Invalid request
        403: Not authorized
        404: File not found
    """
    file = db.session.get(File, file_id)
    
    if not file or file.is_deleted:
        return jsonify({'error': 'File not found'}), 404
    
    # Check ownership
    if file.user_id != user.id:
        return jsonify({'error': 'Not authorized to rename this file'}), 403
    
    data = request.get_json()
    
    if not data or 'filename' not in data:
        return jsonify({'error': 'New filename is required'}), 400
    
    new_filename = data['filename'].strip()
    
    if not new_filename:
        return jsonify({'error': 'Filename cannot be empty'}), 400
    
    try:
        # Update original filename (the one shown to user)
        file.original_filename = secure_filename(new_filename)
        db.session.commit()
        
        return jsonify({
            'message': 'File renamed successfully',
            'file': {
                'id': file.id,
                'filename': file.original_filename,
                'size': file.file_size,
                'mime_type': file.mime_type
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to rename file',
            'message': str(e)
        }), 500


@files_bp.route('/<int:file_id>', methods=['DELETE'])
@login_required
def delete_file(user, file_id):
    """
    Delete a file (soft delete)
    
    Returns:
        200: File deleted successfully
        403: Not authorized
        404: File not found
    """
    file = db.session.get(File, file_id)
    
    if not file or file.is_deleted:
        return jsonify({'error': 'File not found'}), 404
    
    # Check ownership
    if file.user_id != user.id:
        return jsonify({'error': 'Not authorized to delete this file'}), 403
    
    try:
        # Get storage service
        storage = get_storage_service()
        
        # Delete from storage (optional - you might want to keep files in storage)
        # storage.delete_file(file.file_path)
        
        # Soft delete in database
        file.is_deleted = True
        db.session.commit()
        
        return jsonify({
            'message': 'File deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete file',
            'message': str(e)
        }), 500