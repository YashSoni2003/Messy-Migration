from flask import Flask, jsonify, request
from config import Config
from .routes.users import register_user_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Security headers middleware
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        if hasattr(app.config, 'SECURITY_HEADERS'):
            for header, value in app.config.SECURITY_HEADERS.items():
                response.headers[header] = value
        return response
    
    # Request size limiting
    @app.before_request
    def limit_remote_addr():
        """Basic security checks on incoming requests."""
        # Check content length
        if request.content_length and request.content_length > app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024):
            return jsonify({'success': False, 'error': 'Request too large'}), 413
    
    register_user_routes(app)
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'Method not allowed'
        }), 405

    @app.errorhandler(413)
    def request_too_large(error):
        return jsonify({
            'success': False,
            'error': 'Request payload too large'
        }), 413

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    return app