document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('pdfFile');
    const statusDiv = document.getElementById('status');

    // Backend URL (change for production)
    const BACKEND_URL = 'http://localhost:5000/upload';

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Reset status
        statusDiv.textContent = '';
        statusDiv.style.color = 'black';

        // Validate file
        if (!fileInput.files.length) {
            statusDiv.textContent = 'Please select a PDF file';
            statusDiv.style.color = 'red';
            return;
        }

        const file = fileInput.files[0];
        
        // Validate file type
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            statusDiv.textContent = 'Please upload a PDF file';
            statusDiv.style.color = 'red';
            return;
        }

        // Validate file size (16MB max)
        if (file.size > 16 * 1024 * 1024) {
            statusDiv.textContent = 'File size must be less than 16MB';
            statusDiv.style.color = 'red';
            return;
        }

        // Prepare form data
        const formData = new FormData();
        formData.append('file', file);

        try {
            // Show loading status
            statusDiv.textContent = 'Processing PDF...';
            statusDiv.style.color = 'blue';

            // Send file to backend
            const response = await fetch(BACKEND_URL, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Upload failed');
            }

            // Create download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = file.name.replace('.pdf', '_extracted.jsonl');
            document.body.appendChild(a);
            a.click();
            a.remove();

            // Success message
            statusDiv.textContent = 'PDF extracted successfully!';
            statusDiv.style.color = 'green';

        } catch (error) {
            console.error('Error:', error);
            statusDiv.textContent = `Error: ${error.message}`;
            statusDiv.style.color = 'red';
        }
    });
});