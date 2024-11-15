// Example JavaScript to handle dynamic interactions and form submission

document.getElementById('upload-form').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent form from submitting

    const fileInput = document.getElementById('dars-file');
    const file = fileInput.files[0];

    if (file) {
        const formData = new FormData();
        formData.append('dars-file', file);

        // Simulating file upload process
        console.log("File uploaded:", file.name);
        // Here you would normally send the form data to the backend (Flask) using fetch or axios
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            displaySuggestions(data.suggested_majors);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});

// Function to dynamically display suggested majors
function displaySuggestions(majors) {
    const suggestionsContainer = document.querySelector('.suggestion-cards');
    suggestionsContainer.innerHTML = '';  // Clear existing suggestions

    majors.forEach(major => {
        const card = document.createElement('div');
        card.classList.add('suggestion-card');
        card.innerHTML = `
            <h4>${major.name}</h4>
            <p>${major.description}</p>
        `;
        suggestionsContainer.appendChild(card);
    });
}
