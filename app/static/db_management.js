document.addEventListener("DOMContentLoaded", () => {
    const createTableForm = document.getElementById("create-table-form");
    const uploadPdfForm = document.getElementById("upload-pdf-form");
    const vectorTableSelect = document.getElementById("vector-table");

    if (!createTableForm || !uploadPdfForm || !vectorTableSelect) {
        console.error("Forms or dropdown not found.");
        return;
    }

    // Fetch tables and populate dropdown
    async function populateTables() {
        try {
            const response = await fetch("/list_tables");
            const tables = await response.json();
            if (Array.isArray(tables) && tables.length > 0) {
                tables.forEach(table => {
                    const option = document.createElement("option");
                    option.value = table;
                    option.textContent = table;
                    vectorTableSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error("Error fetching tables:", error);
        }
    }

    // Handle create table form submission
    createTableForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const tableName = document.getElementById("table-name").value;

        try {
            const response = await fetch("/create_table", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ table_name: tableName })
            });
            const result = await response.json();
            alert(result.message);
        } catch (error) {
            console.error("Error creating table:", error);
            alert("Failed to create table.");
        }
    });

    // Handle upload PDF form submission
    uploadPdfForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(uploadPdfForm);
    
        try {
            const response = await fetch("/upload_pdf", {
                method: "POST",
                body: formData
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            alert(result.message);
        } catch (error) {
            console.error("Error uploading PDF:", error);
            alert("Failed to upload PDF.");
        }
    });
    

    // Populate tables on page load
    populateTables();
});
