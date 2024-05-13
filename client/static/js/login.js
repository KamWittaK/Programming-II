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
    const twofa    = document.getElementById("2FA").value

    // Compute SHA-256 hash of the password
    const passwordHash = await sha256(password);

    const data = {
        username: username,
        hash: passwordHash,
        twofa: twofa
    };

    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    };

    fetch('http://127.0.0.1:5000/auth', requestOptions)
        .then(response => response.json())
        .then(data => {
            if (data.token) {
                document.cookie = `token=${data.token};`;
                document.cookie = `username=${username};`;
                window.location.href = "/STrack";
            } else {
                console.error("Authentication failed.");
            }
        })
        .catch(error => {
            console.error("Error during login:", error);
        });
}