async function sha256(message) {
    const encoder = new TextEncoder();
    const data = encoder.encode(message);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hashBuffer))
        .map(byte => byte.toString(16).padStart(2, '0'))
        .join('');
}

async function submitForm(event) {
    event.preventDefault(); // Prevent the default form submission

    const form = document.getElementById('loginForm');
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Compute SHA-256 hash of the password
    const passwordHash = await sha256(password);

    const data = {
        Username: username,
        Password: passwordHash
    };

    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    };

    console.log(data)

    fetch('http://127.0.0.1:4444/signupapi', requestOptions) // Corrected endpoint to auth
        .then(response => response.json())
        .then(data => {
            console.log(data); // Log the response from the server
            // Further actions based on the response
        })
        .catch(error => {
            console.error("Error during login:", error);
        });
}