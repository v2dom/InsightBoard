# Description: this file contains all of your websocket event handlers
# You need handlers for connecting, sending a message, and disconnecting
# Update the handlers below to work with your model and and your application
# Note: you can hand chatgpt a handler, tell it what you want the handler
# to do, and ask it to update the code for you.

from flask_socketio import emit, disconnect
from flask import request
from flask_jwt_extended import decode_token

# IMPORTANT: import any objects from your model.py file that you need to work with here
#            uncomment the line below and update it to match your model
#from model import oneOfMyObjects, anotherOfMyObjects

from extensions import db, socketio  # Import socketio and db from extensions.py

# Function to register WebSocket event handlers for real-time communication
def register_websocket_handlers(socketio):

    # Note: you need handlers for connect, disconnect, and send_message
    # edit the below to suit your needs for each event

    # Handle the event when a client connects to the WebSocket
    @socketio.on('connect')
    def handle_connect():
        print("Client attempting to connect...")  # Log connection attempt

        # grabbing the token to authorize the user
        token = request.args.get('token')  # Retrieve the JWT token from query parameters
        print(f"Token received: {token}")  # Log the received token

        if not token:
            print("No token provided, disconnecting client.")
            # If no token is provided, emit a connection error and disconnect the client
            emit('connect_error', {'error': 'No token provided. Disconnecting...'})
            disconnect()
            return

        try:
            # Decode the JWT token to verify user identity
            decoded_token = decode_token(token)

            # Query the correct object from your data model to validate the token
            # EXAMPLE: grabbing the user with a matching email address
            #user = User.query.filter_by(email=decoded_token['sub']).first()  # Fetch the user by email

            # EXAMPLE: if the user is found, perform any actions needed
            # for when a user connects, such as broadcasting a message
            # to all clients that the user has entered the chat

            #if user:
            #    print(f"Token successfully decoded: {decoded_token}")  # Log successful token decoding
            #    # Emit a success message to the connected client
            #    emit('connect_success', {'message': f'Client connected with token: {decoded_token}'})
            #    # Broadcast a message that the user has entered the chat to all clients
            #    emit('broadcast_message', {'message': f"{user.name} has entered the chat...", 'user': f"{user.name}", 'event': "new_chatter", 'user_count': f"{count_connected_clients()}"}, broadcast=True)
            #else:
            #    emit('broadcast_message', {'error': 'User not found'}, broadcast=False)

        except Exception as e:
            # Handle errors during token decoding and disconnect the client
            print(f"Error decoding token: {str(e)}")  # Log the specific error encountered
            emit('connect_error', {'error': f'Invalid token: {str(e)}. Disconnecting...'})
            disconnect()
            print("Client disconnected due to invalid token.")

    # Handle the event when a client sends a message
    @socketio.on('send_message')
    def handle_message(data):
        message = data.get('message')  # Retrieve the message text
        token = data.get('token')  # Retrieve the JWT token

        if not token:
            # If no token is provided, emit an error message
            emit('broadcast_message', {'error': 'No token provided'}, broadcast=False)
            return

        try:
            # Decode the JWT token to verify user identity
            decoded_token = decode_token(token)

            # Query the correct object from your data model to validate the token
            # EXAMPLE: grabbing the user with a matching email address

            #user = User.query.filter_by(email=decoded_token['sub']).first()  # Fetch the user by email

            # EXAMPLE: if the user is found, perform any actions needed
            # for when a user connects, such as broadcasting a message
            # to all clients that the user has entered the chat

            #if user:
            #    # when sending messages to clients, you can include
            #    # any additional property/value pairs you want to send
            #    # along with the message itself.
            #    # Note: must set broadcast=True to send to all clients
            #    # otherwise set broadcast=False to only send to the client that sent the message
            #
            #    # EXAMPLE: broadcasting a message to all clients including the message, the user's name, and a count of the number of connected clients
            #    emit('broadcast_message', {'message': f"{user.name}: {message}", 'user': f"{user.name}", 'user_count': f"{count_connected_clients()}"}, broadcast=True)
            #else:
            #   emit('broadcast_message', {'error': 'User not found'}, broadcast=False)

        except Exception as e:
            # Handle errors during token decoding and emit an error message
            emit('broadcast_message', {'error': f'Invalid token: {str(e)}'}, broadcast=False)

    # Handle the event when a client disconnects from the WebSocket
    @socketio.on('disconnect')
    def handle_disconnect():
        token = request.args.get('token')  # Retrieve the token from the socket object

        if not token:
            # If no token is provided, assume an unknown user and broadcast the disconnect event
            emit('broadcast_message', {'message': f"unknown user has left the chat...", 'event': "remove_chatter", 'user_count': f"{count_connected_clients()}"}, broadcast=True)
            return

        try:
            # Decode the token
            decoded_token = decode_token(token)

            # Query the correct object from your data model to validate the token
            # EXAMPLE: grabbing the user with a matching email address
            
            #user = User.query.filter_by(email=decoded_token['sub']).first()  # Fetch the user by email

            # EXAMPLE: if the user is found, perform any actions needed
            # for when a user disconnects, such as broadcasting a message

            #if user:
            #    # Broadcast that the user has left the chat
            #    emit('broadcast_message', {'message': f"{user.name} has left the chat...", 'user': f"{user.name}", 'event': "remove_chatter", 'user_count': f"{count_connected_clients()}"}, broadcast=True)
            #else:
            #    # Broadcast the disconnect event for an unknown user
            #    emit('broadcast_message', {'message': f"unknown user has left the chat...", 'event': "remove_chatter", 'user_count': f"{count_connected_clients()}"}, broadcast=True)

        except Exception as e:
            # Log any errors that occur during disconnect handling
            print(f"Error during disconnect: {str(e)}")


# PLACE ANY UTILITY FUNCTIONS HERE, E.G.:
# Utility function to count the number of connected clients
from flask import current_app

def count_connected_clients():
    # Access the current app's SocketIO instance
    socketio = current_app.extensions['socketio']  # Retrieve the socketio instance

    # The `eio.sockets` dictionary contains all currently connected clients
    connected_clients = socketio.server.eio.sockets
    
    # Count the number of connected clients
    clients = len(connected_clients)
    
    print(f"Total connected clients: {clients}")  # Log the total number of clients
    return clients