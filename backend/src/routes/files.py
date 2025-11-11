"""
File management routes with JWT authentication
"""
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from sqlalchemy import desc

from src.models import db, File
from src.auth import login_required


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
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get allowed extensions from config
    allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip'}
    
    if not allowed_file(file.filename, allowed_extensions):
        return jsonify({
            'error': 'File type not allowed',
            'allowed_types': list(allowed_extensions)
        }), 400
    
    try:
        # Secure the filename
        original_filename = secure_filename(file.filename)
        
        # Generate unique filename to avoid conflicts
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{user.id}_{timestamp}_{original_filename}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create database record
        new_file = File(
            filename=original_filename,
            file_path=filename,  # Store the unique filename
            file_size=file_size,
            mime_type=file.content_type or 'application/octet-stream',
            user_id=user.id
        )
        
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file': {
                'id': new_file.id,
                'filename': new_file.filename,
                'size': new_file.file_size,
                'mime_type': new_file.mime_type,
                'uploaded_at': new_file.uploaded_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to upload file',
            'message': str(e)
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
        'filename': f.filename,
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
            'filename': file.filename,
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
        200: File content
        403: Not authorized
        404: File not found
    """
    file = db.session.get(File, file_id)
    
    if not file or file.is_deleted:
        return jsonify({'error': 'File not found'}), 404
    
    # Check ownership
    if file.user_id != user.id:
        return jsonify({'error': 'Not authorized to download this file'}), 403
    
    # Get file path
    file_path = os.path.join(os.getcwd(), 'uploads', file.file_path)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found on server'}), 404
    
    # Increment download count
    file.download_count += 1
    db.session.commit()
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=file.filename,
        mimetype=file.mime_type
    )


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
        # Update filename
        file.filename = secure_filename(new_filename)
        db.session.commit()
        
        return jsonify({
            'message': 'File renamed successfully',
            'file': {
                'id': file.id,
                'filename': file.filename,
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
        # Soft delete
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