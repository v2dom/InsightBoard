//DESCRIPTION: This script defines event listerns in the top section,
//              and then functions mapped to those listeners to handhe
//              the events.  You can hand this file to chatgpt and ask
//              it to add event listeners for elements on your html page
//              (give it an element id and the event you want to listen for).
//              When you do, you can also ask it to create a function to
//              handle the event that will be called by the listener.



// Wait until the DOM is fully loaded before attaching event listeners
document.addEventListener("DOMContentLoaded", function() {

    //add event listeners for any events from your index.html page
    //that you would like to capture and handle
    //
    //Note: a good appreach is to map the event to a function defined
    //      below in the script. This way you can keep your code organized.
});


//PLACE ALL OF YOUR FUNCTIONS BELOW
//  - functions called by the event listeners above
//  - any helper functions
// Function to handle login process

// TEMPLATE: handling login and storing the JWT token in localStorage
// Note: funcion retries 2 times if a server error is received
function handleLoginClick(username, password, attempt = 1) {
    // map this to your login route in routes.py - in this example it is /login
    fetch('/login', {
        method: 'POST',  // Send POST request to login endpoint
        headers: {
            'Content-Type': 'application/json',  // Send data as JSON
        },
        body: JSON.stringify({
            email: username,  // Username is assumed to be the email field
            password: password  // Include password in the request body
        }),
    })
    .then(response => {
        if (response.status === 500 && attempt <= 3) {
            // Retry the login on internal server error (up to 3 attempts)
            console.warn('Internal Server Error during login. Retrying attempt:', attempt);
            return new Promise((resolve) => setTimeout(resolve, 300))  // 300ms delay between retries
                .then(() => handleLoginClick(username, password, attempt + 1));  // Recursive retry call
        }
        return response.json();  // Parse response as JSON if not a 500 error
    })
    .then(data => {
        if (data.error) {
            // Handle login failure (e.g., display error message)
            alert('Login failed: ' + data.error);
        } else {

            //NOTE: EDIT THIS AREA TO HANDLE SUCCESSFUL LOGIN

            //HERE WE ARE STORING THE JWT TOKEN IN LOCAL STORAGE
            //WITH THE KEY jwtToken, SO WE CAN RETRIEVE LATER FROM
            //ANOTHER PAGE IN THE APP
            localStorage.setItem('jwtToken', data.token);

            // REDIRECT TO ANOTHER PAGE AFTER SUCCESSFUL LOGIN
            // Note: map this to a page serving route in routes.py
            window.location.href = '/your_route_here';
        }
    })
    .catch((error) => {
        // Log any errors that occur during the request
        console.error('Error:', error);
    });
}

// TEMPLATE: handling registration and displaying success message
// Sends a registration request to the server with email, name, and password (up to 3 retries on server error)
function handleRegistration(email, name, password, attempt = 1) {
    //assumes you have a route in routes.py mapped to /create_account
    fetch('/create_account', {
        method: 'POST',  // Send POST request to create_account endpoint
        headers: {
            'Content-Type': 'application/json',  // Send data as JSON
        },
        body: JSON.stringify({
            //Note: update these fields to match your route in routes.py
            email: email,  // Include email in the request body
            name: name,  // Include name in the request body
            password: password  // Include password in the request body
        }),
    })
    .then(response => {
        if (response.status === 500 && attempt <= 3) {
            // Retry the registration on internal server error (up to 3 attempts)
            console.warn('Internal Server Error. Retrying attempt:', attempt);
            return new Promise((resolve) => setTimeout(resolve, 300))  // 300ms delay between retries
                .then(() => handleRegistration(email, name, password, attempt + 1));  // Recursive retry call
        }
        return response.json();  // Parse response as JSON if not a 500 error
    })
    .then(data => {
        if (data.error) {
            // Handle registration failure (e.g., display error message)
            alert('Error creating account: ' + data.error);
        } else {
            // Display success message upon successful account creation
            alert('Account created successfully!');

            // EXAMPLE: IF USER WAAS IN A MODAL, HIDE THE MODAL AFTER SUCCESSFUL REGISTRATION
            //const registerModalElement = document.getElementById('registerModal');
            //const registerModal = bootstrap.Modal.getInstance(registerModalElement);  // Get existing modal instance
            //if (registerModal) {
            //    registerModal.hide();  // Hide the modal if instance exists
            //} else {
            //    const newModal = new bootstrap.Modal(registerModalElement);
            //    newModal.hide();  // Hide the modal if new instance is created
            //}
        }
    })
    .catch((error) => {
        // Log any errors that occur during the request
        console.error('Error:', error);
    });
}

// EXAMPLE: Function to show a bootstrap modal
//          Note: this function would be called from an event listener
//                (e.g., a button click event) defined above when the 
//                DOM is loaded
//function showRegisterModal() {
//    const registerModal = new bootstrap.Modal(document.getElementById('registerModal'));  // Initialize the modal
//    registerModal.show();  // Show the modal
//}