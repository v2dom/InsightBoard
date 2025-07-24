# Description: This file contains the routes for the Flask application.
# Scroll down and add routes to serve your html pages
# Update the create account and login routes to work with your data model
# Add your API routes to interact with your database
#
# Note: ou can hand chatgpt your file and your model.py file and ask it to generate
# the routes you want and add them to your routes.py code

import datetime
from flask import Blueprint, current_app, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import decode_token
from extensions import db  # Import db from the newly created extensions.py file
import jwt

# IMPORTANT: import any objects from your model.py file that you need to work with here
#            uncomment the line below and update it to match your model
#from model import oneOfMyObjects, anotherOfMyObjects

# PLACE UTILITY FUNCTIONS HERE
# For example, you can define a function to validate the JWT token
# and then use this in any route that requires token authorization
# Helper function to decode the JWT token and validate the user

def validate_token(request):
    auth_header = request.headers.get('Authorization', None)  # Extract the authorization header
    if not auth_header:
        return None, jsonify({"error": "Token is missing!"}), 401  # Return error if token is missing

    try:
        token = auth_header.split(" ")[1]  # Split the header and get the token (format: "Bearer <token>")
        decoded_token = decode_token(token)  # Decode the JWT token

        # Example of pulling the sub key out of the token and using it
        # to query user records to find a user with a matching email
        # Note: you can store any unique identifier in the sub key
        # and you will decide what that is when you generate the token at logon
        
        #user = User.query.filter_by(email=decoded_token['sub']).first()  # Find the user by email
        #if not user:
        #    return None, jsonify({"error": "User not found!"}), 404  # Return error if user not found
        #return user, None  # Return the user if the token is valid

    except Exception as e:
        return None, jsonify({"error": f"Token error: {str(e)}"}), 401  # Return error if token validation fails


# PLACE ROUTES HERE
# Define a blueprint for routing (modularizes the app's routes)
routes_blueprint = Blueprint('routes', __name__)

# Default route to serve the index.html file (home page)
@routes_blueprint.route('/')
def index():
    return render_template('index.html')  # Render the index.html template when accessing '/'

# Add routes for any other htmml pages you want to serve
#EXAMPLE: Route to serve a page called chatwindow.html from your templates folder
#@routes_blueprint.route('/chatwindow', methods=['GET'])
#def chatwindow():
#    return render_template('chatwindow.html')  # Render the chat window template

# TEMPLATE: Route to handle account creation
@routes_blueprint.route('/create_account', methods=['POST'])
def create_account():
    data = request.json  # Extract the incoming JSON data from the request
    
    # edet these to match the fields in your user table
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    # Check if any required fields are missing
    if not email or not name or not password:
        return jsonify({"error": "Missing email, name, or password"}), 400  # Return error if any fields are missing

    # Perform any additional validation here
    # EXAMPLE: heck if a user with the provided email already exists
    #existing_user = User.query.filter_by(email=email).first()
    #if existing_user:
    #    return jsonify({"error": "User with that email already exists"}), 400  # Return error if the email is already registered

    # Hash the user's password for security
    # EXAMPLE: hashing a value stored in a variable called password
    #hashed_password = generate_password_hash(password, method='sha256')

    # Create the new account
    # EXAMPLE: creating a new user object with the hashed password
    # note that the object you will use depends on your model in model.py
    #new_user = User(email=email, name=name, password=hashed_password)
    #db.session.add(new_user)  # Add the new user to the database session
    #db.session.commit()  # Commit the transaction to save the new user

    return jsonify({"message": "Account created successfully!"}), 201  # Return success message

# TEMPLATE: route to handle user login
@routes_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json  # Extract the incoming JSON data from the request
    # edit these to match the fields in your user table
    email = data.get('email')
    password = data.get('password')

    # Check if any required fields are missing
    # edit this to match the variables above
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400  # Return error if email or password is missing


    # Check if the user exists and if the password matches
    # EXAMPLE: working with a user object from model.py to
    # check if the user exists and if the password matches
    # Note: update this to work with your objects in your model

    #user = User.query.filter_by(email=email).first()
    #if not user or not check_password_hash(user.password, password):
    #    return jsonify({"error": "Invalid credentials"}), 400  # Return error if credentials are invalid

    # Generate a JWT token that expires in 1 hour
    # EXAMPLE: generating a token with the user's email as the subject
    # Note: referencing the user variable above.

    token = jwt.encode({
        'sub': '<place a unique identifier from your user object here>',  # Subject is the user's email
        #Example:
        #'sub': user.email,  # Subject is the user's email
       'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expiration time
    }, current_app.config['SECRET_KEY'], algorithm='HS256')  # Sign the token with the app's secret key

    return jsonify({"message": "Login successful!", "token": token}), 200  # Return success message and token

# ADD YOUR API ROUTES HERE
# EXAMPLE: Route to retrieve all RoboChatters from the database

#@routes_blueprint.route('/robochatters', methods=['GET'])
#def get_all_robochatters():
#    print("Getting all RoboChatters...")  # Log for debugging
#
#    ###
#    ### Note: example of using your validate_token function to check the token
#    ###
#    user, error_response = validate_token(request)  # Validate the user's token
#    if error_response:
#        return error_response  # Return error if the token validation fails
#
#    # Fetch all RoboChatters from the database
#    robochatters = RoboChatter.query.all()
#    # Create a list of dictionaries with RoboChatter details
#    result = [{"id": r.id, "name": r.name, "description": r.description, "enabled": r.enabled} for r in robochatters]
#    return jsonify(result), 200  # Return the list of RoboChatters
