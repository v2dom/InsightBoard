//DESCRIPTION: The ChatSocket object is accessible by any scripts that are
//linked and loaded on the same page. It handles the WebSocket connection
//and communication with the server using Socket.IO.  Since the socket
//will be receiving events from the server, it will need to be able to
//call functions in your page-specific scripts to update the UI accordingly.
//
//Note: add variables for these functions at the top in the variables list,
// and include setters for them in the ChatSocket object.  Examples below.

const ChatSocket = {
    socket: null,
    jwtToken: localStorage.getItem('jwtToken'),  // Retrieves JWT token from local storage
    messageCallback: null, // Callback function to handle new messages

    /**
     * Establishes a connection to the WebSocket server using Socket.IO
     * If a JWT token is missing, it logs an error and exits the function.
     * Handles events like connect, broadcast messages, disconnect, and errors.
     */
    connect: function () {
        if (!this.jwtToken) {
            console.error("No JWT token found. Cannot connect to WebSocket.");
            return;
        }

        // Establish SocketIO connection using WebSocket and polling transports
        // Note: includes the token in the query string for authentication
        this.socket = io.connect(`${window.location.protocol}//${window.location.host}`, {
            transports: ['websocket', 'polling'],    
            query: `token=${this.jwtToken}`
        });

        // Handle successful connection
        this.socket.on('connect', () => {
            console.log('SocketIO connection established.');
            console.log('Socket ID:', this.socket.id);  // Log unique socket connection ID
            console.log('Socket connected:', this.socket.connected);  // Confirm connection is open
            console.log('Socket URL:', this.socket.io.uri);  // Log the server URL
            console.log('Socket transport:', this.socket.io.engine.transport.name);  // Log current transport method (e.g., websocket)
        });

        /**
         * Listens for incoming messages via 'broadcast_message' event.
         */
        this.socket.on('broadcast_message', (data) => {
            console.log("Received message:", data);

                //IMPORTANT: check if a messageHandler function has been set
                //           and call it if so, passing the data object.
                if (this.messageCallback) {
                    this.messageCallback(data);  // Trigger the message callback if it exists
                }
        });

        // Handle Socket.IO disconnection
        this.socket.on('disconnect', (reason) => {
            console.log("SocketIO disconnected:", reason);
            // Retry connection logic can be added here
        });

        // Handle Socket.IO connection errors
        this.socket.on('connect_error', (error) => {
            console.error("SocketIO error:", error);
            // Retry connection logic can be added here
        });

        // Log a successful connection event
        this.socket.on('connect_success', (data) => {
            console.log('Connection successful:', data.message);
        });
    },

    /**
     * Disconnects the active Socket.IO connection if it exists.
     * Logs a message if there's no active connection to disconnect.
     */
    disconnect: function () {
        if (this.socket) {
            this.socket.disconnect();  // Close the socket connection
            console.log("Disconnected from SocketIO.");
        } else {
            console.log("No active SocketIO connection.");
        }
    },

    /**
     * Sends a message through the Socket.IO connection.  Includes the token for authentication.
     */
    sendMessage: function (message) {
        if (this.socket && this.socket.connected) {
            this.socket.emit('send_message', { message: message, token: this.jwtToken }, (response) => {
                if (response && response.error) {
                    console.error('Server error on emit:', response.error);  // Log server errors if any
                } else {
                    console.log('Message sent successfully:', message);  // Confirm message was sent
                }
            });
        } else {
            console.error("SocketIO connection is not open. Cannot send message.");  // Log if no connection is open
        }
    },

    /**
     * Sets a callback function to handle incoming messages.
     * This function is triggered whenever a new message is received.
     */
    setMessageCallback: function (callback) {
        this.messageCallback = callback;
    },

    // Add more setters for other callback functions here as needed
};