document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('resumeForm').addEventListener('submit', async function (event) {
        // event.preventDefault(); // Prevent default form submission

        // Show loading spinner
        document.getElementById('loadingSpinner').style.display = 'block';

        // Get form values
        const fileInput = document.getElementById('file-upload');
        const name = document.getElementById('candidateName').value.trim();
        const email = document.getElementById('candidateEmail').value.trim();
        const phone = document.getElementById('candidatePhone').value.trim();
        const jobPosition = document.getElementById('jobPosition').value.trim();
        const jobDescription = document.getElementById('jobDescription').value.trim();
        const resultsDiv = document.getElementById('rankingOutput');

        // Clear previous messages
        resultsDiv.innerHTML = '';

        // Validate required fields
        if (!name || !email || !phone || !jobPosition || !jobDescription) {
            resultsDiv.innerHTML = `<p style="color:red;">All fields are required.</p>`;
            document.getElementById('loadingSpinner').style.display = 'none';
            return;
        }

        // Validate email format
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(email)) {
            resultsDiv.innerHTML = `<p style="color:red;">Invalid email format.</p>`;
            document.getElementById('loadingSpinner').style.display = 'none';
            return;
        }

        // Validate phone format (basic check)
        const phonePattern = /^[0-9\-+\s()]+$/;
        if (!phonePattern.test(phone)) {
            resultsDiv.innerHTML = `<p style="color:red;">Invalid phone number format.</p>`;
            document.getElementById('loadingSpinner').style.display = 'none';
            return;
        }

        // Validate file upload
        if (fileInput.files.length === 0) {
            resultsDiv.innerHTML = `<p style="color:red;">Please upload a resume.</p>`;
            document.getElementById('loadingSpinner').style.display = 'none';
            return;
        }

        // Validate file type
        const file = fileInput.files[0];
        const validFileTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (!validFileTypes.includes(file.type)) {
            resultsDiv.innerHTML = `<p style="color:red;">Invalid file type. Only PDF, DOC, and DOCX are allowed.</p>`;
            document.getElementById('loadingSpinner').style.display = 'none';
            return;
        }

        // Create FormData object
        const formData = new FormData();
        formData.append('resume', file);
        formData.append('name', name);
        formData.append('email', email);
        formData.append('phone', phone);
        formData.append('jobPosition', jobPosition);
        formData.append('jobDescription', jobDescription);

        try {
            // Send data to the backend
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            // Parse response
            const data = await response.json();

            // Hide loading spinner
            document.getElementById('loadingSpinner').style.display = 'none';

            if (!response.ok) {
                throw new Error(data.error || 'Upload failed.');
            }

            // Display success message
            resultsDiv.innerHTML = `<p style="color:green;"><strong>${sanitizeHTML(data.message)}</strong></p>`;
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('loadingSpinner').style.display = 'none';
            resultsDiv.innerHTML = `<p style="color:red;">An error occurred: ${sanitizeHTML(error.message)}</p>`;
        }
    });
});

// Utility function to sanitize HTML (Prevent XSS Attacks)
function sanitizeHTML(str) {
    const temp = document.createElement('div');
    temp.textContent = str;
    return temp.innerHTML;
}

document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM fully loaded!");

    const form = document.getElementById('resumeForm');
    if (!form) {
        console.log("❌ Form with id 'resumeForm' not found!");
        return;
    }

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        console.log("✅ Form submission event triggered!");
    });
});
