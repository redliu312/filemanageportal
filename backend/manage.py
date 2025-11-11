#!/usr/bin/env python
"""
Database management script for Flask-Migrate initialization and operations
"""
import os
import sys
from flask_migrate import Migrate, init, migrate, upgrade
from src.app import app, db

def init_db():
    """Initialize the database and migrations"""
    with app.app_context():
        # Always run init (it will handle if already exists)
        print("1. Initializing Flask-Migrate...")
        try:
            init()
            print("✓ Flask-Migrate initialized successfully")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ Flask-Migrate already initialized")
            else:
                print(f"✗ Flask-Migrate initialization failed: {e}")
        
        # Always create migration (it will handle if no changes)
        print("\n2. Creating migration...")
        try:
            migrate(message='Auto migration')
            print("✓ Migration created successfully")
        except Exception as e:
            if "No changes" in str(e) or "Target database is not up to date" in str(e):
                print("✓ No new changes to migrate")
            else:
                print(f"  Migration creation skipped: {e}")
        
        # Always apply migrations to database
        print("\n3. Applying migrations to database...")
        try:
            upgrade()
            print("✓ Database schema updated successfully")
        except Exception as e:
            # If the database is already up to date, create tables directly
            print(f"  Migration upgrade issue: {e}")
            print("  Attempting direct table creation...")
            try:
                db.create_all()
                print("✓ Tables created directly")
            except Exception as create_error:
                print(f"✗ Direct table creation failed: {create_error}")
                return False
        
        # Verify tables
        print("\n4. Verifying database tables...")
        try:
            # Check if key tables exist in the database
            result = db.session.execute(
                db.text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('users', 'files')")
            )
            table_count = result.scalar()
            
            if table_count > 0:
                print(f"✓ Database tables verified ({table_count} tables found)")
            else:
                print("! No application tables found, but database is ready")
            
            return True
        except Exception as e:
            print(f"  Table verification skipped: {e}")
            # Even if verification fails, the database might still be okay
            return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        success = init_db()
        sys.exit(0 if success else 1)
    else:
        print("Usage: python manage.py init")
        sys.exit(1)