"""
Main Flask application
"""
import os
import logging
import sys
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv

from src.config import get_config
from src.models import db
from src.routes import auth_bp, files_bp

# Load environment variables
load_dotenv()

# Set Python unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

# Create Flask app
app = Flask(__name__)

# Load configuration
config = get_config()
app.config.from_object(config)

# Configure Flask logging based on environment variable
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
    log_level = 'INFO'

# Configure logging using Flask's built-in logger
if not app.debug:
    # In production, log to stdout for Vercel
    app.logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(getattr(logging, log_level))
    
    # Also configure root logger for libraries
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        stream=sys.stdout
    )
else:
    # In development, Flask's default logging is fine
    app.logger.setLevel(getattr(logging, log_level))

# Log startup information
app.logger.info(f"Starting Flask app with log level: {log_level}")
app.logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
app.logger.info(f"Storage mode: {os.getenv('STORAGE_MODE', 'local')}")
app.logger.info(f"MAX_CONTENT_LENGTH: {app.config.get('MAX_CONTENT_LENGTH')} bytes")
app.logger.info(f"MAX_FILE_SIZE env: {os.getenv('MAX_FILE_SIZE', 'not set')}")

# Ensure MAX_CONTENT_LENGTH is set for Flask to enforce file size limits
if app.config.get('MAX_CONTENT_LENGTH') is None:
    app.logger.warning("MAX_CONTENT_LENGTH not set, setting to default 100MB")
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Configure CORS with more comprehensive settings for production
cors_config = {
    'origins': app.config['CORS_ORIGINS'],
    'supports_credentials': True,
    'allow_headers': ['Content-Type', 'Authorization'],
    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'expose_headers': ['Content-Range', 'X-Content-Range']
}
CORS(app, **cors_config)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(files_bp)


# Handle preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response


@app.route("/")
def index():
    """Root endpoint"""
    return jsonify({
        "message": "Flask API is running",
        "version": "0.1.0",
        "environment": os.getenv("FLASK_ENV", "development")
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