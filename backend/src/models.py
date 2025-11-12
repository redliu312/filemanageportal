"""
Database models for the file management service.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication and file ownership."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationship to files
    files = db.relationship('File', back_populates='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_files=False):
        """Convert user to dictionary representation."""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
        }
        if include_files:
            data['files'] = [file.to_dict() for file in self.files]
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'


class File(db.Model):
    """File model for storing file metadata and tracking uploads."""
    
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(100), nullable=True)
    file_hash = db.Column(db.String(64), nullable=True, index=True)  # SHA-256 hash for deduplication
    
    # Ownership
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    owner = db.relationship('User', back_populates='files')
    
    # Metadata
    description = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(500), nullable=True)  # Comma-separated tags
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed_at = db.Column(db.DateTime, nullable=True)
    
    # Status and access control
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Download tracking
    download_count = db.Column(db.Integer, default=0, nullable=False)
    
    def to_dict(self, include_owner=False):
        """Convert file to dictionary representation."""
        data = {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'file_hash': self.file_hash,
            'description': self.description,
            'tags': self.tags.split(',') if self.tags else [],
            'uploaded_at': self.uploaded_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_accessed_at': self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            'is_public': self.is_public,
            'is_deleted': self.is_deleted,
            'download_count': self.download_count,
        }
        if include_owner:
            data['owner'] = {
                'id': self.owner.id,
                'username': self.owner.username,
            }
        return data
    
    def mark_accessed(self):
        """Update the last accessed timestamp."""
        self.last_accessed_at = datetime.utcnow()
        db.session.commit()
    
    def increment_download_count(self):
        """Increment the download counter."""
        self.download_count += 1
        self.mark_accessed()
    
    def soft_delete(self):
        """Soft delete the file."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<File {self.filename} (User: {self.user_id})>'

#TODO: currently this is useless, but will be good if implement the file share feature.
# class FileShare(db.Model):
#     """Model for sharing files with other users or via public links."""
    
#     __tablename__ = 'file_shares'
    
#     id = db.Column(db.Integer, primary_key=True)
#     file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False, index=True)
#     file = db.relationship('File', backref='shares')
    
#     # Share token for public access
#     share_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    
#     # Optional: Share with specific user
#     shared_with_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
#     shared_with_user = db.relationship('User', foreign_keys=[shared_with_user_id])
    
#     # Permissions
#     can_download = db.Column(db.Boolean, default=True, nullable=False)
#     can_view = db.Column(db.Boolean, default=True, nullable=False)
    
#     # Expiration
#     expires_at = db.Column(db.DateTime, nullable=True)
    
#     # Timestamps
#     created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     accessed_count = db.Column(db.Integer, default=0, nullable=False)
#     last_accessed_at = db.Column(db.DateTime, nullable=True)
    
#     # Status
#     is_active = db.Column(db.Boolean, default=True, nullable=False)
    
#     def is_expired(self):
#         """Check if the share link has expired."""
#         if self.expires_at is None:
#             return False
#         return datetime.utcnow() > self.expires_at
    
#     def is_valid(self):
#         """Check if the share is valid (active and not expired)."""
#         return self.is_active and not self.is_expired()
    
#     def increment_access_count(self):
#         """Increment the access counter."""
#         self.accessed_count += 1
#         self.last_accessed_at = datetime.utcnow()
#         db.session.commit()
    
#     def to_dict(self):
#         """Convert share to dictionary representation."""
#         return {
#             'id': self.id,
#             'file_id': self.file_id,
#             'share_token': self.share_token,
#             'shared_with_user_id': self.shared_with_user_id,
#             'can_download': self.can_download,
#             'can_view': self.can_view,
#             'expires_at': self.expires_at.isoformat() if self.expires_at else None,
#             'created_at': self.created_at.isoformat(),
#             'accessed_count': self.accessed_count,
#             'last_accessed_at': self.last_accessed_at.isoformat() if self.last_accessed_at else None,
#             'is_active': self.is_active,
#             'is_expired': self.is_expired(),
#         }
    
#     def __repr__(self):
#         return f'<FileShare {self.share_token} for File {self.file_id}>'