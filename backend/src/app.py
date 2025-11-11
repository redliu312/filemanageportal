"""
Main Flask application
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv

from src.config import get_config
from src.models import db
from src.routes import auth_bp

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Load configuration
config = get_config()
app.config.from_object(config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
CORS(app, origins=app.config['CORS_ORIGINS'])

# Register blueprints
app.register_blueprint(auth_bp)


@app.route("/")
def index():
    """Root endpoint"""
    return jsonify({
        "message": "Flask API is running",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    })


@app.route("/api/health")
def health():
    """Health check endpoint"""
    # Check database connection
    try:
        db.session.execute(db.text('SELECT 1'))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "service": "backend-api",
        "database": db_status
    })


@app.route("/api/db/init")
def init_db():
    """Initialize database tables (development only)"""
    if not app.config['DEBUG']:
        return jsonify({"error": "Not available in production"}), 403
    
    try:
        db.create_all()
        return jsonify({
            "message": "Database tables created successfully",
            "tables": list(db.metadata.tables.keys())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])