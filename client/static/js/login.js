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
        username: username,
        hash: passwordHash
    };

    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    };

    fetch('/auth', requestOptions)
        .then(response => response.json())
        .then(data => {
            if (data.token) {
                document.cookie = `token=${data.token};`;
                window.location.href = "/dash";
            } else {
                console.error("Authentication failed.");
            }
        })
        .catch(error => {
            console.error("Error during login:", error);
        });
}