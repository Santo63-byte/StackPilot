// Folder browser functionality
function setupFolderBrowser() {
    const browseBtn = document.getElementById('browse-btn');
    
    if (browseBtn) {
        browseBtn.addEventListener('click', openFolderBrowser);
        console.log('Browse button listener attached');
    } else {
        console.log('Browse button not found, retrying...');
        setTimeout(setupFolderBrowser, 100);
    }
}

// Setup when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupFolderBrowser);
} else {
    setupFolderBrowser();
}

function openFolderBrowser(e) {
    e.preventDefault();
    console.log('Browse button clicked');
    
    // Call backend api :: Todo will be replaced with actual folder browser integration at clientside in the future
    fetch('/sp/browse-folder')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.path) {
                const pathField = document.getElementById('server_path_field');
                pathField.value = data.path;
                console.log('Path set to:', data.path);
            } else {
                console.log('No folder selected');
            }
        })
        .catch(error => {
            console.error('Error opening folder browser:', error);
        });
}
