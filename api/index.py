import sys
import os

# Add the parent directory to the path so we can import the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try to import the lightweight app first
    from vercel_app_lightweight import app
except Exception as e:
    try:
        # Fallback to the original app
        from vercel_app import app
    except Exception as e2:
        # Create a simple Flask app as fallback if all imports fail
        from flask import Flask, jsonify
        
        app = Flask(__name__)
        
        @app.route('/')
        def index():
            return jsonify({
                'error': 'Failed to load application',
                'message': f"Lightweight app error: {str(e)}, Original app error: {str(e2)}"
            })
        
        @app.route('/api/health-check')
        def health_check():
            return jsonify({
                'status': 'error',
                'message': 'Applications failed to load',
                'errors': {
                    'lightweight': str(e),
                    'original': str(e2)
                }
            })

# This file is needed for Vercel to properly import the Flask app
# Make sure that 'app' is an instance of a Flask app, not just a module 

# Using vercel_app instead of app for Vercel deployment
# This simplified version is optimized for serverless functions 