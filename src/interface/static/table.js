// Helper function to get pid_status as human readable text
function getStatusText(pidStatus) {
	return pidStatus === 1 ? 'Running' : 'Stopped';
}

// Helper function to get initials from server name
function getInitials(name) {
	return name
		.split(/\s|-/)
		.map(word => word[0])
		.join('')
		.toUpperCase();
}

// Helper function to get status badge class
function getStatusClass(pidStatus) {
	if (pidStatus === 1) return 'status-active';
	if (pidStatus === 0) return 'status-offline';
	return 'status-idle';
}

// Helper function to determine action button based on status
function getActionText(pidStatus) {
	return pidStatus === 1 ? 'Stop' : 'Start';
}

// Handle server action button clicks
async function handleServerAction(event, serverId, action) {
	event.preventDefault();
	const endpoint = action === 'Start' ? `/sp/servers/${serverId}/start` : `/sp/servers/${serverId}/stop`;
	
	try {
		const response = await fetch(endpoint, { method: 'POST' });
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		// Refresh the table after action
		populateTable();
	} catch (error) {
		console.error(`Error ${action.toLowerCase()}ing server:`, error);
		alert(`Failed to ${action.toLowerCase()} server`);
	}
}

// Handle server edit action
async function handleEditServer(event, serverId, servers) {
	event.preventDefault();
	
	// Find the server data
	const server = servers.find(s => s.server_id === serverId);
	if (!server) {
		console.error('Server not found:', serverId);
		alert('Server not found');
		return;
	}
	
	// Populate form fields with server data
	document.getElementById('server_name_field').value = server.server_name || '';
	document.getElementById('server_path_field').value = server.root_path || '';
	document.getElementById('server_port_field').value = server.port_no || '';
	document.getElementById('server_command_field').value = server.runnable_command || '';
	
	// Store the server_id for later use in form submission
	document.getElementById('addServerForm').setAttribute('data-edit-mode', 'true');
	document.getElementById('addServerForm').setAttribute('data-server-id', serverId);
	
	// Open the modal
	document.getElementById('modal-overlay').style.display = 'flex';
}

// Handle server delete action
async function handleDeleteServer(event, serverId) {
	event.preventDefault();
	
	// Confirm before deleting
	if (!confirm('Are you sure you want to delete this server? This action cannot be undone.')) {
		return;
	}
	
	try {
		const response = await fetch(`/sp/servers/${serverId}`, { method: 'DELETE' });
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		// Refresh the table after deletion
		populateTable();
		alert('Server deleted successfully');
	} catch (error) {
		console.error('Error deleting server:', error);
		alert('Failed to delete server');
	}
}

// Fetch servers from API and populate table
async function populateTable() {
	const tbody = document.getElementById('serverTableBody');
	tbody.innerHTML = '';
	
	try {
		const response = await fetch('/sp/list/servers');
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		const servers = await response.json();
	
		servers.forEach(server => {
			const row = document.createElement('tr');
			const statusText = getStatusText(server.pid_status);
			const actionText = getActionText(server.pid_status);
			
			row.innerHTML = `
				<td>
					<div class="server-info">
						<div class="server-avatar">${getInitials(server.server_name)}</div>
						<span class="server-name">
							${server.server_name}
							${server.server_id === "1" ? '<span class="current-app-badge">● Current</span>' : ''}
						</span>
					</div>
				</td>
				<td>${server.port_no}</td>
				<td>${server.root_path}</td>
				<td>${server.runnable_command}</td>
				<td>${server.git_branch}</td>
				<td>
					<span class="status-badge ${getStatusClass(server.pid_status)}">
						${statusText}
					</span>
				</td>
				<td>
					<div class="server-actions">
					${server.server_id !== "1" ? `
						<a href="#" class="server-action-link" data-server-id="${server.server_id}" data-action="${actionText}">${actionText}</a>
							<a href="#" class="server-edit-link" data-server-id="${server.server_id}" title="Edit server">
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
									<path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
								</svg>
							</a>
							<a href="#" class="server-delete-link" data-server-id="${server.server_id}" title="Delete server">
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<polyline points="3 6 5 6 21 6"></polyline>
									<path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
									<line x1="10" y1="11" x2="10" y2="17"></line>
									<line x1="14" y1="11" x2="14" y2="17"></line>
								</svg>
							</a>
						` : ''}
					</div>
				</td>
			`;
			tbody.appendChild(row);
		});
		
		// Attach click handlers to edit links
		document.querySelectorAll('.server-edit-link').forEach(link => {
			link.addEventListener('click', (event) => {
				const serverId = link.getAttribute('data-server-id');
				handleEditServer(event, serverId, servers);
			});
		});
		
		// Attach click handlers to delete links
		document.querySelectorAll('.server-delete-link').forEach(link => {
			link.addEventListener('click', (event) => {
				const serverId = link.getAttribute('data-server-id');
				handleDeleteServer(event, serverId);
			});
		});
		
		// Attach click handlers to action links
		document.querySelectorAll('.server-action-link').forEach(link => {
			link.addEventListener('click', (event) => {
				const serverId = link.getAttribute('data-server-id');
				const action = link.getAttribute('data-action');
				handleServerAction(event, serverId, action);
			});
		});
	} catch (error) {
		console.error('Error fetching servers:', error);
		const tbody = document.getElementById('serverTableBody');
		tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Error loading servers</td></tr>';
	}
}

// Initialize table when DOM is loaded
// Call directly since table HTML is injected dynamically
if (document.getElementById('serverTableBody')) {
	populateTable();
} else {
	// If not found, try again after a short delay (in case of async load)
	setTimeout(populateTable, 100);
}
