// DESCRIPTION: This is the controller/presenter for your application.
// It is responsible for handling user interactions, interacting with the
// DataModel to fetch and update data, and interacting with the ChatSocket
// to send and receive messages.
//
// Add event listeners to any html elements that require user interaction
// in the top section inside of the load event.  Then, add the functions
// to handle those events in the bottom section of the script.


window.addEventListener('load', () => {
    
    //NOTE: IF YOU APP USES WEBSOCKETS THEN UNCOMMENT THIS LINE
    //      TO ESTABLISH A CONNECTION TO THE WEBSOCKET SERVER

    //ChatSocket.connect();  // Establish the WebSocket connection

    // NOTE: SET CALLBACKS FOR SOCKET EVENTS HERE (MAPPED TO FUNCTIONS BELOW)

    //ChatSocket.setMessageCallback(sendChat);

});

//NOTE: PLACE ALL OF YOUR FUNCTIONS BELOW

// Example function that sends a websocket message via the ChatSocket object
function sendChat(text) {
    //checks to make sure string is not empty
    if (text.trim() === "") {
        console.error("Cannot send an empty message.");  // Log error if message is empty
        return;
    }

    ChatSocket.sendMessage(text);  // Send the message using ChatSocket
}

