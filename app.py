# Description: This file is the entry point for the Flask application.

from gevent import monkey
monkey.patch_all()
import os
#from flask import Flask
from routes import routes_blueprint
from extensions import db, socketio, jwt, cors


# Try to import the Config class from config.py (only if it exists)
try:
    from config import Config
    config_available = True
except ImportError:
    print("config.py not found. Falling back to environment variables.")
    config_available = False

def create_app():
    app = Flask(__name__)

    # If config.py is available, use it. Otherwise, rely on environment variables.
    if config_available:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', Config.SQLALCHEMY_DATABASE_URI)
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', Config.SQLALCHEMY_TRACK_MODIFICATIONS)
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', Config.SECRET_KEY)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    # socketio.init_app(app, async_mode='gevent')  # Optional, only if using websockets

    # Import and register blueprints here (inside app context)
    from auth_routes import auth_bp
    from routes import routes_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)

    with app.app_context():
        db.create_all()

    return app

# Create the app instance
app = create_app()

# If running locally
if __name__ == '__main__':
    app.run(debug=True)
    
# If using websockets with gevent: use socketio.run(app) instead of Flask’s app.run()
# But for deployment with Passenger or gunicorn, don't run it here.
