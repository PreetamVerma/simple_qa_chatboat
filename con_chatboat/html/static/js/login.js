document.getElementById("login-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const messageDiv = document.getElementById("message");

    try {
        const response = await fetch("http://127.0.0.1:8000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email }),
        });

        if (response.ok) {
            const data = await response.json();
            const token = data.access_token;

            // Display success message and store token
            messageDiv.style.color = "green";
            messageDiv.textContent = "Login successful!";
            localStorage.setItem("token", token);
            localStorage.setItem("email", email);
            localStorage.setItem("loginTime", new Date().toLocaleString());

            // Redirect or load a new page
            setTimeout(() => {
                alert("You are now logged in!");
                window.location.href = "protected_page.html"; // Replace with your protected page
            }, 1000);
        } else {
            const errorData = await response.json();
            messageDiv.textContent = errorData.detail || "Login failed!";
        }
    } catch (error) {
        console.error("Error:", error);
        messageDiv.textContent = "An error occurred. Please try again.";
    }
});
