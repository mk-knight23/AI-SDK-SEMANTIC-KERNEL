"""
Semantic Kernel Flask Application.

Main application entry point for the Semantic Kernel AI orchestration backend.
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS

from app.api import api_bp


def create_app(config=None):
    """
    Create and configure the Flask application.

    Args:
        config: Optional configuration dictionary

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    if config:
        app.config.update(config)

    # Enable CORS for all routes
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix="/api")

    # Root endpoint
    @app.route("/", methods=["GET"])
    def root():
        """Root endpoint with service information."""
        return jsonify({
            "service": "semantic-kernel-backend",
            "version": "1.0.0",
            "description": "Semantic Kernel AI Orchestration Backend",
            "endpoints": {
                "health": "/api/health",
                "status": "/api/status",
                "chat": "/api/chat",
                "plugins": "/api/plugins",
                "conversations": "/api/conversations",
                "planner": "/api/planner/plan"
            }
        }), 200

    # Health check endpoint (legacy, also available at /api/health)
    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint for monitoring and load balancers."""
        return jsonify({
            "status": "healthy",
            "service": "semantic-kernel-backend",
            "version": "1.0.0"
        }), 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({
            "error": "Not found",
            "message": "The requested endpoint does not exist"
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({
            "error": "Internal server error",
            "message": str(error)
        }), 500

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors."""
        return jsonify({
            "error": "Method not allowed",
            "message": "The HTTP method is not allowed for this endpoint"
        }), 405

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "True").lower() == "true"

    print(f"Starting Semantic Kernel Backend on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Health check: http://localhost:{port}/health")
    print(f"API status: http://localhost:{port}/api/status")

    app.run(host="0.0.0.0", port=port, debug=debug)
