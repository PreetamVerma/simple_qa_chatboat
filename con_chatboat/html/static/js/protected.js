document.addEventListener("DOMContentLoaded", () => {
    // Retrieve token, email, and login time from localStorage
    const email = localStorage.getItem("email");
    const loginTime = localStorage.getItem("loginTime");

    if (!email || !loginTime) {
        alert("Unauthorized access! Redirecting to login...");
        window.location.href = "/index.html"; // Redirect to login page
        return;
    }

    // Display user email and login time
    document.getElementById("user-email").textContent = `Logged in as: ${email}`;
    document.getElementById("login-time").textContent = `Login time: ${loginTime}`;

    // Add functionality for chatboat here
    const token = localStorage.getItem("token");
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");

    document.getElementById("submit-query").addEventListener("click", async () => {
        const question = userInput.value.trim();
        if (!question) return;

        try {
            const response = await fetch("http://127.0.0.1:8000/query", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ question }),
            });

            if (!response.ok) {
                throw new Error("Failed to fetch the query response.");
            }

            const data = await response.json();
            chatBox.value += `You: ${question}\nAI: ${data.response}\n\n`;
            chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
            userInput.value = ""; // Clear input
        } catch (error) {
            console.error("Error:", error);
            alert("Error fetching query response.");
        }
    });
});
