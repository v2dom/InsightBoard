# Description: This file is the entry point for the Flask application.
# IMPORATNT: There are two areas below you need to uncomment if you want
#            to use websockets.

import os
from flask import Flask
from extensions import db, socketio, jwt, cors
from gevent import monkey
monkey.patch_all()

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
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)  # Default to False
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')  # Provide a default or ensure it's set in production

    # Initialize extensions within the app context.
    db.init_app(app)

    # UNCOMMENT THIS IF YOU WANT TO USE WEBSOCKETS!
    #socketio.init_app(app, async_mode='gevent')

    jwt.init_app(app)
    cors.init_app(app)

    # Register blueprints for routing.
    from routes import routes_blueprint
    app.register_blueprint(routes_blueprint)

    # Create tables if they don't exist.
    with app.app_context():
        db.create_all()

    # UNCOMMENT THIS IF YOU WANT TO USE WEBSOCKETS!
    # Register WebSocket event handlers.
    #from websockets import register_websocket_handlers
    #register_websocket_handlers(socketio)

    return app


# Create the app instance.
app = create_app()

# Passenger WSGI expects `app` to be the WSGI callable.
# No need to call `socketio.run()` here since Passenger takes care of starting the app.