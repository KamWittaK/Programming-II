async function sha256(message) {
    const encoder = new TextEncoder();
    const data = encoder.encode(message);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hashBuffer))
        .map(byte => byte.toString(16).padStart(2, '0'))
        .join('');
}

async function submitForm(event) {
    try {
        event.preventDefault(); // Prevent the default form submission

        const form = document.getElementById('loginForm');
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        // Validate input
        if (!username || !password) {
            throw new Error('Username and password are required.');
        }

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

        const response = await fetch('http://127.0.0.1:4444/signupapi', requestOptions);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const blob = await response.blob();

        // Create a new Image element
        const image = new Image();
        image.src = URL.createObjectURL(blob);

        // Append the image to the QR code container
        const qrCodeContainer = document.getElementById('qrCodeContainer');
        if (!qrCodeContainer) {
            throw new Error('qrCodeContainer not found');
        }
        qrCodeContainer.appendChild(image);
    } catch (error) {
        console.error("Error submitting form:", error);
    }
}

// Attach submitForm function to the form submit event
document.getElementById('loginForm').addEventListener('submit', submitForm);
