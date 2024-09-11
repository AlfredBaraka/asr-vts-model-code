document.addEventListener("DOMContentLoaded", () => {
    const searchForm = document.getElementById("search-form");
    const resultsDiv = document.getElementById("results");
    const tableSelect = document.getElementById("table");

    if (!searchForm || !resultsDiv || !tableSelect) {
        console.error("Form, results div, or table select not found.");
        return;
    }

    // Function to fetch and populate table options
    async function populateTableOptions() {
        try {
            const response = await fetch("/list_tables");
            const tables = await response.json();
            
            if (Array.isArray(tables)) {
                tableSelect.innerHTML = ""; // Clear existing options
                tables.forEach(table => {
                    const option = document.createElement("option");
                    option.value = table;
                    option.textContent = table;
                    tableSelect.appendChild(option);
                });
            } else {
                console.error("Invalid table data received.");
            }
        } catch (error) {
            console.error("Error fetching tables:", error);
        }
    }

    // Fetch table options on page load
    populateTableOptions();

    searchForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const query = document.getElementById("query").value;
        const table = tableSelect.value;

        try {
            const response = await fetch("/semantic_search", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ query, table })
            });
            const result = await response.json();
        
            // Clear previous results
            resultsDiv.innerHTML = "";
        
            if (Array.isArray(result.answer)) {
                // If result.answer is an array, display each item separately
                result.answer.forEach((answer, index) => {
                    const p = document.createElement("p");
                    p.textContent = `${index + 1}. ${answer}`;  // Add numbering to each result
                    resultsDiv.appendChild(p);
        
                    // Optionally, add a separator after each result
                    const separator = document.createElement("hr");
                    resultsDiv.appendChild(separator);
                });
            } else {
                // If it's not an array, handle it as a single result or display a message
                const p = document.createElement("p");
                p.textContent = result.answer || "No results found.";
                resultsDiv.appendChild(p);
            }
        } catch (error) {
            console.error("Error during search:", error);
            resultsDiv.textContent = "Failed to perform search.";
        }
        
    });
});
