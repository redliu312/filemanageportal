#!/usr/bin/env python
"""
Database management script for Flask-Migrate
"""
from flask_migrate import Migrate, init, migrate, upgrade, downgrade
from src.app import app
from src.models import db

# Initialize Flask-Migrate
migrate_obj = Migrate(app, db)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python manage.py [init|migrate|upgrade|downgrade]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    with app.app_context():
        if command == 'init':
            init()
            print("Migration repository initialized")
        elif command == 'migrate':
            message = sys.argv[2] if len(sys.argv) > 2 else "Auto migration"
            migrate(message=message)
            print(f"Migration created: {message}")
        elif command == 'upgrade':
            upgrade()
            print("Database upgraded")
        elif command == 'downgrade':
            downgrade()
            print("Database downgraded")
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)