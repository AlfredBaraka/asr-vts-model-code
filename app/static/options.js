document.addEventListener("DOMContentLoaded", () => {
    const ragTableSelect = document.getElementById("rag-table");
    const useRagCheckbox = document.getElementById("use-rag");

    // Hide the RAG table select initially
    ragTableSelect.style.display = 'none';

    // Function to populate RAG table options
    async function populateRagTables() {
        try {
            const response = await fetch("/list_tables");
            const tables = await response.json();
            
            // Clear existing options
            ragTableSelect.innerHTML = '<option value="">Select RAG Table</option>';

            // Add new options
            tables.forEach(table => {
                const option = document.createElement("option");
                option.value = table;
                option.textContent = table.charAt(0).toUpperCase() + table.slice(1);
                ragTableSelect.appendChild(option);
            });
        } catch (error) {
            console.error("Error fetching tables:", error);
        }
    }

    // Handle the checkbox change to show/hide the RAG table select
    useRagCheckbox.addEventListener("change", (event) => {
        if (event.target.checked) {
            ragTableSelect.style.display = 'inline'; // Show the dropdown
            populateRagTables(); // Populate options when RAG is enabled
        } else {
            ragTableSelect.style.display = 'none'; // Hide the dropdown
            ragTableSelect.innerHTML = '<option value="">Select RAG Table</option>'; // Reset options
        }
    });
});
