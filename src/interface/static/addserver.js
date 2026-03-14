// Initialize form handlers
function initAddServerForm() {
    const form = document.getElementById('addServerForm');
    
    // Handle form submission
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Form submission triggered');
            
            // Check if in edit mode
            const isEditMode = form.getAttribute('data-edit-mode') === 'true';
            const editServerId = form.getAttribute('data-server-id');
            
            // Collect form data
            const formData = {
                server_id: isEditMode ? editServerId : "0", 
                server_name: document.getElementById('server_name_field').value,
                root_path: document.getElementById('server_path_field').value,
                port_no: document.getElementById('server_port_field').value ? 
                         parseInt(document.getElementById('server_port_field').value) : null,
                runnable_command: document.getElementById('server_command_field').value
            };
            
            console.log('Sending form data:', formData);
            
            try {
                // Choose endpoint based on mode
                const endpoint = isEditMode ? '/sp/servers/edit' : '/sp/servers/add';
                const method = isEditMode ? 'PUT' : 'POST';
                
                const response = await fetch(endpoint, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (response.ok && result.status === 200) {
                    // Success - clear form and close modal
                    form.reset();
                    form.removeAttribute('data-edit-mode');
                    form.removeAttribute('data-server-id');
                    document.getElementById('modal-overlay').style.display = 'none';
                    
                    // Reload the server table
                    if (typeof populateTable === 'function') {
                        populateTable();
                    }
                    
                    alert(isEditMode ? 'Server updated successfully!' : 'Server added successfully!');
                } else {
                    alert('Error: ' + (result.message || (isEditMode ? 'Failed to update server' : 'Failed to add server')));
                }
            } catch (error) {
                console.error(isEditMode ? 'Error Updating Server:' : 'Error Adding Server:', error);
                alert('Error: ' + error.message);
            }
        });
    } else {
        console.warn('addServerForm element not found');
    }
}

// Call initialization immediately and also on DOM ready (for any timing issues)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAddServerForm);
} else {
    initAddServerForm();
}
