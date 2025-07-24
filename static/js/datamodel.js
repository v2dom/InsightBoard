// DESCRIPTION: the DataModel object is accessible by any other
//scripts linked and loaded on the same page.  It handles all of the
//communications with your api, and the goal is to store state information
//and data in this object as well when possible, in order to minimize
//API calls and to create a single point of access for data in the 
//front-end of your app.

const DataModel = {
    items: [],  // Placeholder for data fetched from the API
    baseUrl: `${window.location.protocol}//${window.location.host}/`,  // Base URL dynamically generated for API requests

    /**
     * Helper function for making authenticated API requests with retries.
     * This function sends a request to the given URL using the provided options.
     * It automatically adds the Authorization header with the JWT token from local storage.
     * If the request fails, it retries up to 3 times before throwing an error.
     *
     * IMPORTANT: Use this to make API calls in all of your functions below.
     *            See example of use below.
     * @param {string} url - The API endpoint to send the request to.
     * @param {object} options - Optional fetch options (e.g., method, headers).
     * @returns {Promise<object>} - The JSON response from the API.
     */
    async fetchWithAuth(url, options = {}) {
        const headers = {
            'Authorization': `Bearer ${localStorage.getItem('jwtToken')}`,  // Add JWT token for authentication
            'Content-Type': 'application/json',  // Ensure the request sends and receives JSON
        };
        options.headers = headers;

        // Retry logic: attempt the request up to 3 times
        for (let attempt = 1; attempt <= 3; attempt++) {
            try {
                const response = await fetch(url, options);  // Send the request using fetch
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);  // Throw an error if response is not OK
                }
                return await response.json();  // Parse and return the response JSON if successful
            } catch (error) {
                if (attempt === 3) {
                    // If this is the third and final attempt, rethrow the error
                    throw error;
                }
                // Optional: add a short delay (e.g., 200ms) before retrying
                await new Promise(resolve => setTimeout(resolve, 200));
            }
        }
    },

    //EXAMPLE - function to grab data from a route, store it in the object,
    //and return it to the caller.

    //async getAllItems() {
    //    const url = this.baseUrl + '<your route here>';  // Construct the full API URL
    //    try {
    //        const myItems = await this.fetchWithAuth(url, { method: 'GET' });  // Send GET request to fetch data
    //        this.items= myItems;  // Store the fetched data in the object (optional) (note the variable items is defined above)
    //        return myItems;  // Return the list of RoboChatters
    //    } catch (error) {
    //        console.error('Error fetching RoboChatters:', error);  // Log any errors that occur
    //        throw error;  // Rethrow the error so it can be handled elsewhere
    //    }
    //},


};

