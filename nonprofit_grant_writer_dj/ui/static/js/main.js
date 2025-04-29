document.addEventListener('DOMContentLoaded', function() {
    // Get form elements
    const form = document.getElementById('nonprofit-form');
    const generateBtn = document.getElementById('generate-btn');
    const progressContainer = document.getElementById('progress-container');
    const statusMessage = document.getElementById('status-message');
    
    // Add form submission handler
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        const nonprofitName = document.getElementById('nonprofit-name').value;
        const nonprofitMission = document.getElementById('nonprofit-mission').value;
        const nonprofitWebsite = document.getElementById('nonprofit-website').value;
        const grantUrl = document.getElementById('grant-url').value;
        
        // Show progress indicator
        progressContainer.classList.remove('d-none');
        statusMessage.classList.remove('d-none');
        generateBtn.disabled = true;
        
        // Send data to server
        fetch('http://127.0.0.1:5000/api/generate-grant', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nonprofit_name: nonprofitName,
                nonprofit_mission: nonprofitMission,
                nonprofit_website: nonprofitWebsite,
                grant_url: grantUrl
            })
        })
        .then(response => response.json())
        .then(data => {
            // Check response status
            if (data.status === 'processing') {
                // Redirect to review page
                window.location.href = 'http://127.0.0.1:8000/review/';
            } else {
                // Show error if any
                statusMessage.textContent = data.message || 'An error occurred. Please try again.';
                progressContainer.classList.add('d-none');
                generateBtn.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            statusMessage.textContent = 'An error occurred. Please try again.';
            progressContainer.classList.add('d-none');
            generateBtn.disabled = false;
        });
    });
}); 