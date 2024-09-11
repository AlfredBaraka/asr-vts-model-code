document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const chatBox = document.getElementById("chat-box");
    const queryInput = document.getElementById("query");
    const optionsForm = document.getElementById("options-form");
    const useRagCheckbox = document.getElementById("use-rag");
    const ragTableSelect = document.getElementById("rag-table");

    chatForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const userMessage = queryInput.value;
        const useRag = useRagCheckbox.checked;
        const ragTable = ragTableSelect.value;

        appendMessage("user", userMessage);

        try {
            const response = await fetch(`/query_service?prompt=${encodeURIComponent(userMessage)}&use_rag=${useRag}&table=${encodeURIComponent(ragTable)}`);
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let result = '';

            // Create a new message element for the AI response
            const aiMessageElement = document.createElement("div");
            aiMessageElement.className = 'message ai';
            aiMessageElement.innerHTML = `<strong>Assistant:</strong> <span class="ai-response"></span>`;
            chatBox.appendChild(aiMessageElement);

            const aiResponseSpan = aiMessageElement.querySelector(".ai-response");

            // Clear previous response content
            aiResponseSpan.innerHTML = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                result += decoder.decode(value, { stream: true });
                aiResponseSpan.innerHTML = result; // Update the span with the accumulated result
                chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
            }
        } catch (error) {
            console.error("Error fetching service info:", error);
        }

        queryInput.value = '';
    });

    function appendMessage(sender, message) {
        const messageElement = document.createElement("div");
        messageElement.className = `message ${sender}`;
        messageElement.innerHTML = `<strong>${sender === 'user' ? 'You' : 'Assistant'}:</strong> ${message}`;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
    }
});
