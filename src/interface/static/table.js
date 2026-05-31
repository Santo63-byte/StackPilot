// Helper function to get initials from server name



function getInitials(name) {
	return name
		.split(/\s|-/)
		.map(word => word[0])
		.join('')
		.toUpperCase();
}

// ── Active session tracking ───────────────────────────────────────────
let _currentSessionId   = null;
let _currentSessionName = null;

function updateSessionLabel() {
	const label    = document.getElementById('current-session-label');
	const nameText = document.getElementById('current-session-name-text');
	if (!label || !nameText) return;
	if (_currentSessionName) {
		nameText.textContent = _currentSessionName;
		label.style.display  = 'flex';
	} else {
		label.style.display  = 'none';
	}
}

// ── Batch selection state ─────────────────────────────────────────────
const _selectedIds = new Set();

function syncBatchBar() {
	const bar   = document.getElementById('batch-start-bar');
	const label = document.getElementById('batch-selected-count');
	if (!bar || !label) return;
	const count = _selectedIds.size;
	if (count >= 2) {
		label.textContent = `${count} selected`;
		bar.style.display = 'flex';
	} else {
		bar.style.display = 'none';
	}
}

function setRowChecked(checkbox, serverId, checked) {
	checkbox.checked = checked;
	const row = checkbox.closest('tr');
	if (checked) {
		_selectedIds.add(serverId);
		row && row.classList.add('row-selected');
	} else {
		_selectedIds.delete(serverId);
		row && row.classList.remove('row-selected');
	}
	syncBatchBar();
}

async function handleBatchStart() {
	if (_selectedIds.size < 2) return;
	const ids = Array.from(_selectedIds);
	try {
		const response = await fetch('/sp/servers/batch/start', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ server_ids: ids })
		});
		if (!response.ok) throw new Error(`HTTP ${response.status}`);
		_selectedIds.clear();
		populateTable(_currentSessionId, _currentSessionName);
	} catch (err) {
		console.error('Batch start failed:', err);
		alert('Failed to batch start servers.');
	}
}

function handleBatchMove(event) {
	if (_selectedIds.size < 1) return;
	// Reuse the single-server move popover, but with all selected IDs
	_movePopoverServerId   = Array.from(_selectedIds); // store array for batch
	_movePopoverSelectedId = null;

	const popover    = getOrCreateMovePopover();
	const listEl     = popover.querySelector('#move-popover-list');
	const confirmBtn = popover.querySelector('.move-popover-confirm');

	// Reset
	confirmBtn.disabled    = true;
	confirmBtn.textContent = 'Move';
	listEl.innerHTML       = '<div class="move-popover-loading">Loading…</div>';

	// Position near the batch move button
	const btn  = event.currentTarget;
	const rect = btn.getBoundingClientRect();

	popover.style.display    = 'flex';
	popover.style.visibility = 'hidden';

	requestAnimationFrame(() => {
		const pw  = popover.offsetWidth  || 260;
		const ph  = popover.offsetHeight || 320;
		const vpW = window.innerWidth;
		const vpH = window.innerHeight;

		let left = rect.right + 10;
		let top  = rect.bottom + 8;

		if (left + pw > vpW - 8) left = rect.left - pw - 10;
		if (top  + ph > vpH - 8) top  = vpH - ph - 8;
		if (top < 8) top = 8;

		popover.style.left       = `${left}px`;
		popover.style.top        = `${top}px`;
		popover.style.visibility = '';
	});

	// Fetch sessions and render
	fetch('/sp/sessions')
		.then(r => r.json())
		.then(data => {
			const sessions = (data.sessions || []).filter(s => s.session_id !== _currentSessionId);
			if (!sessions.length) {
				listEl.innerHTML = '<div class="move-popover-empty">No other sessions available.</div>';
				return;
			}
			listEl.innerHTML = '';
			sessions.forEach(session => {
				const initials = (session.session_name || '?')
					.split(/\s+|-/)
					.filter(Boolean)
					.map(w => w[0])
					.join('')
					.toUpperCase()
					.slice(0, 2);
				const item = document.createElement('div');
				item.className         = 'move-session-item';
				item.dataset.sessionId = session.session_id;
				item.innerHTML = `
					<div class="move-session-avatar">${initials}</div>
					<span class="move-session-name">${escapeHtmlMove(session.session_name || 'Unnamed')}</span>
				`;
				item.addEventListener('click', () => selectMoveSession(session.session_id));
				listEl.appendChild(item);
			});
		})
		.catch(err => {
			console.error('Failed to load sessions for batch move:', err);
			listEl.innerHTML = '<div class="move-popover-empty">Failed to load sessions.</div>';
		});
}


// Helper function to determine action button based on status
function getActionText(pidStatus) {
	return pidStatus === 1 ? 'Stop' : 'Start';
}

// Handle copy to clipboard
function handleCopyCommand(event, command) {
	event.preventDefault();
	navigator.clipboard.writeText(command).then(() => {
		// Visual feedback
		const copyLink = event.target.closest('.command-copy-link');
		if (copyLink) {
			const originalTitle = copyLink.title;
			copyLink.title = 'Copied!';
			setTimeout(() => {
				copyLink.title = originalTitle;
			}, 2000);
		}
	}).catch(err => {
		console.error('Failed to copy:', err);
		alert('Failed to copy command');
	});
}

// Handle open terminal at path
async function handleOpenTerminal(event, path) {
	event.preventDefault();
	try {
		const response = await fetch(`/sp/console/openadavancedterminal?path=${encodeURIComponent(path)}`, { method: 'POST' });
		if (!response.ok) throw new Error(`HTTP ${response.status}`);
	} catch (err) {
		console.error('Failed to open terminal:', err);
		alert('Failed to open terminal at path.');
	}
}

// Handle server action button clicks
async function handleServerAction(event, serverId, action, serverName) {
	event.preventDefault();
	const base = _currentSessionId
		? `/sp/servers/${encodeURIComponent(_currentSessionId)}/${serverId}`
		: `/sp/servers/${serverId}`;
	const endpoint = action === 'Start' ? `${base}/start` : `${base}/stop`;
	
	try {
		const response = await fetch(endpoint, { method: 'POST' });
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		// Open console drawer tab for this server when started
		if (action === 'Start' && serverName) {
			const useStackPilotTerminal =
				typeof AppConfig !== 'undefined' && AppConfig.terminal === 'StackPilot_Terminal';
			if (useStackPilotTerminal) {
				window.ConsoleDrawer?.openConsoleTab(serverName);
			}
		}
		// Refresh the table after action
		populateTable(_currentSessionId, _currentSessionName);
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
		const response = await fetch('/sp/servers/delete', {
			method: 'DELETE',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				session_id: _currentSessionId,
				server_lists: [serverId]
			})
		});
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		// Refresh the table after deletion
		populateTable(_currentSessionId, _currentSessionName);
	} catch (error) {
		console.error('Error deleting server:', error);
		alert('Failed to delete server');
	}
}

async function handleBatchDelete() {
	if (_selectedIds.size < 1) return;
	const count = _selectedIds.size;
	if (!confirm(`Are you sure you want to delete ${count} server(s)? This action cannot be undone.`)) {
		return;
	}
	const ids = Array.from(_selectedIds);
	try {
		const response = await fetch('/sp/servers/delete', {
			method: 'DELETE',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				session_id: _currentSessionId,
				server_lists: ids
			})
		});
		if (!response.ok) throw new Error(`HTTP ${response.status}`);
		_selectedIds.clear();
		populateTable(_currentSessionId, _currentSessionName);
	} catch (err) {
		console.error('Batch delete failed:', err);
		alert('Failed to batch delete servers.');
	}
}

// ── Move-to-session popover ───────────────────────────────────────────
let _movePopoverServerId   = null;
let _movePopoverSelectedId = null;

// ── Copy-to-session popover ───────────────────────────────────────────
let _copyPopoverServerId   = null;
let _copyPopoverSelectedId = null;

function escapeHtmlMove(str) {
	return String(str)
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;')
		.replace(/'/g, '&#39;');
}

function getOrCreateMovePopover() {
	let el = document.getElementById('move-popover');
	if (!el) {
		el = document.createElement('div');
		el.id = 'move-popover';
		el.className = 'move-popover';
		el.style.display = 'none';
		el.innerHTML = `
			<div class="move-popover-header">
				<span class="move-popover-title">Move to Session</span>
				<button class="move-popover-close" aria-label="Close">
					<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
						<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
					</svg>
				</button>
			</div>
			<div class="move-popover-list" id="move-popover-list">
				<div class="move-popover-loading">Loading…</div>
			</div>
			<div class="move-popover-footer">
				<button class="move-popover-btn move-popover-cancel">Cancel</button>
				<button class="move-popover-btn move-popover-confirm" disabled>Move</button>
			</div>
		`;
		document.body.appendChild(el);

		el.querySelector('.move-popover-close').addEventListener('click', closeMovePopover);
		el.querySelector('.move-popover-cancel').addEventListener('click', closeMovePopover);
		el.querySelector('.move-popover-confirm').addEventListener('click', confirmMove);

		// Click-outside to close
		document.addEventListener('click', (e) => {
			if (el.style.display !== 'none' && !el.contains(e.target) && !e.target.closest('.server-move-link')) {
				closeMovePopover();
			}
		}, true);
	}
	return el;
}

function closeMovePopover() {
	const el = document.getElementById('move-popover');
	if (el) el.style.display = 'none';
	_movePopoverServerId   = null;
	_movePopoverSelectedId = null;
}

function selectMoveSession(sessionId) {
	_movePopoverSelectedId = sessionId;
	const el = document.getElementById('move-popover');
	if (!el) return;
	el.querySelectorAll('.move-session-item').forEach(item => {
		item.classList.toggle('move-session-item--selected', item.dataset.sessionId === sessionId);
	});
	el.querySelector('.move-popover-confirm').disabled = false;
}

async function confirmMove() {
	if (!_movePopoverServerId || !_movePopoverSelectedId || !_currentSessionId) return;

	const confirmBtn = document.querySelector('#move-popover .move-popover-confirm');
	if (confirmBtn) { confirmBtn.disabled = true; confirmBtn.textContent = 'Moving…'; }

	// Support both single id (string) and batch (array)
	const serverLists = Array.isArray(_movePopoverServerId)
		? _movePopoverServerId
		: [_movePopoverServerId];

	try {
		const response = await fetch('/sp/servers/move', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				action: 'move',
				source_session_info: {
					session_id: _currentSessionId,
					server_lists: serverLists
				},
				target_session_info: {
					session_id: _movePopoverSelectedId,
					server_lists: []
				}
			})
		});
		if (!response.ok) throw new Error(`HTTP ${response.status}`);
		// Clear batch selection if it was a batch move
		if (Array.isArray(_movePopoverServerId)) {
			_selectedIds.clear();
			syncBatchBar();
		}
		closeMovePopover();
		populateTable(_currentSessionId, _currentSessionName);
	} catch (err) {
		console.error('Move server failed:', err);
		alert('Failed to move server.');
		if (confirmBtn) { confirmBtn.disabled = false; confirmBtn.textContent = 'Move'; }
	}
}

function getOrCreateCopyPopover() {
	let el = document.getElementById('copy-popover');
	if (!el) {
		el = document.createElement('div');
		el.id = 'copy-popover';
		el.className = 'move-popover';
		el.style.display = 'none';
		el.innerHTML = `
			<div class="move-popover-header">
				<span class="move-popover-title">Copy to Session</span>
				<button class="move-popover-close" aria-label="Close">
					<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
						<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
					</svg>
				</button>
			</div>
			<div class="move-popover-list" id="copy-popover-list">
				<div class="move-popover-loading">Loading…</div>
			</div>
			<div class="move-popover-footer">
				<button class="move-popover-btn move-popover-cancel">Cancel</button>
				<button class="move-popover-btn move-popover-confirm copy-popover-confirm" disabled>Copy</button>
			</div>
		`;
		document.body.appendChild(el);

		el.querySelector('.move-popover-close').addEventListener('click', closeCopyPopover);
		el.querySelector('.move-popover-cancel').addEventListener('click', closeCopyPopover);
		el.querySelector('.copy-popover-confirm').addEventListener('click', confirmCopy);

		document.addEventListener('click', (e) => {
			if (el.style.display !== 'none' && !el.contains(e.target) && !e.target.closest('.server-copy-link')) {
				closeCopyPopover();
			}
		}, true);
	}
	return el;
}

function closeCopyPopover() {
	const el = document.getElementById('copy-popover');
	if (el) el.style.display = 'none';
	_copyPopoverServerId   = null;
	_copyPopoverSelectedId = null;
}

function selectCopySession(sessionId) {
	_copyPopoverSelectedId = sessionId;
	const el = document.getElementById('copy-popover');
	if (!el) return;
	el.querySelectorAll('.move-session-item').forEach(item => {
		item.classList.toggle('move-session-item--selected', item.dataset.sessionId === sessionId);
	});
	el.querySelector('.copy-popover-confirm').disabled = false;
}

async function confirmCopy() {
	if (!_copyPopoverServerId || !_copyPopoverSelectedId || !_currentSessionId) return;

	const confirmBtn = document.querySelector('#copy-popover .copy-popover-confirm');
	if (confirmBtn) { confirmBtn.disabled = true; confirmBtn.textContent = 'Copying…'; }

	const serverLists = Array.isArray(_copyPopoverServerId)
		? _copyPopoverServerId
		: [_copyPopoverServerId];

	try {
		const response = await fetch('/sp/servers/copy', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				action: 'copy',
				source_session_info: {
					session_id: _currentSessionId,
					server_lists: serverLists
				},
				target_session_info: {
					session_id: _copyPopoverSelectedId,
					server_lists: []
				}
			})
		});
		if (!response.ok) throw new Error(`HTTP ${response.status}`);
		if (Array.isArray(_copyPopoverServerId)) {
			_selectedIds.clear();
			syncBatchBar();
		}
		closeCopyPopover();
		populateTable(_currentSessionId, _currentSessionName);
	} catch (err) {
		console.error('Copy server failed:', err);
		alert('Failed to copy server.');
		if (confirmBtn) { confirmBtn.disabled = false; confirmBtn.textContent = 'Copy'; }
	}
}

async function handleCopyServer(event, serverId) {
	event.preventDefault();
	event.stopPropagation();

	_copyPopoverServerId   = serverId;
	_copyPopoverSelectedId = null;

	const popover    = getOrCreateCopyPopover();
	const listEl     = popover.querySelector('#copy-popover-list');
	const confirmBtn = popover.querySelector('.copy-popover-confirm');

	confirmBtn.disabled    = true;
	confirmBtn.textContent = 'Copy';
	listEl.innerHTML       = '<div class="move-popover-loading">Loading…</div>';

	const btn  = event.currentTarget;
	const rect = btn.getBoundingClientRect();

	popover.style.display    = 'flex';
	popover.style.visibility = 'hidden';

	requestAnimationFrame(() => {
		const pw  = popover.offsetWidth  || 260;
		const ph  = popover.offsetHeight || 320;
		const vpW = window.innerWidth;
		const vpH = window.innerHeight;

		let left = rect.right + 10;
		let top  = rect.top;

		if (left + pw > vpW - 8) left = rect.left - pw - 10;
		if (top  + ph > vpH - 8) top  = vpH - ph - 8;
		if (top < 8) top = 8;

		popover.style.left       = `${left}px`;
		popover.style.top        = `${top}px`;
		popover.style.visibility = '';
	});

	try {
		const data     = await fetch('/sp/sessions').then(r => r.json());
		const sessions = (data.sessions || []).filter(s => s.session_id !== _currentSessionId);

		if (!sessions.length) {
			listEl.innerHTML = '<div class="move-popover-empty">No other sessions available.</div>';
			return;
		}

		listEl.innerHTML = '';
		sessions.forEach(session => {
			const initials = (session.session_name || '?')
				.split(/\s+|-/)
				.filter(Boolean)
				.map(w => w[0])
				.join('')
				.toUpperCase()
				.slice(0, 2);

			const item = document.createElement('div');
			item.className        = 'move-session-item';
			item.dataset.sessionId = session.session_id;
			item.innerHTML = `
				<div class="move-session-avatar">${initials}</div>
				<span class="move-session-name">${escapeHtmlMove(session.session_name || 'Unnamed')}</span>
			`;
			item.addEventListener('click', () => selectCopySession(session.session_id));
			listEl.appendChild(item);
		});
	} catch (err) {
		console.error('Failed to load sessions for copy:', err);
		listEl.innerHTML = '<div class="move-popover-empty">Failed to load sessions.</div>';
	}
}

function handleBatchCopy(event) {
	if (_selectedIds.size < 1) return;
	_copyPopoverServerId   = Array.from(_selectedIds);
	_copyPopoverSelectedId = null;

	const popover    = getOrCreateCopyPopover();
	const listEl     = popover.querySelector('#copy-popover-list');
	const confirmBtn = popover.querySelector('.copy-popover-confirm');

	confirmBtn.disabled    = true;
	confirmBtn.textContent = 'Copy';
	listEl.innerHTML       = '<div class="move-popover-loading">Loading…</div>';

	const btn  = event.currentTarget;
	const rect = btn.getBoundingClientRect();

	popover.style.display    = 'flex';
	popover.style.visibility = 'hidden';

	requestAnimationFrame(() => {
		const pw  = popover.offsetWidth  || 260;
		const ph  = popover.offsetHeight || 320;
		const vpW = window.innerWidth;
		const vpH = window.innerHeight;

		let left = rect.right + 10;
		let top  = rect.bottom + 8;

		if (left + pw > vpW - 8) left = rect.left - pw - 10;
		if (top  + ph > vpH - 8) top  = vpH - ph - 8;
		if (top < 8) top = 8;

		popover.style.left       = `${left}px`;
		popover.style.top        = `${top}px`;
		popover.style.visibility = '';
	});

	fetch('/sp/sessions')
		.then(r => r.json())
		.then(data => {
			const sessions = (data.sessions || []).filter(s => s.session_id !== _currentSessionId);
			if (!sessions.length) {
				listEl.innerHTML = '<div class="move-popover-empty">No other sessions available.</div>';
				return;
			}
			listEl.innerHTML = '';
			sessions.forEach(session => {
				const initials = (session.session_name || '?')
					.split(/\s+|-/)
					.filter(Boolean)
					.map(w => w[0])
					.join('')
					.toUpperCase()
					.slice(0, 2);
				const item = document.createElement('div');
				item.className         = 'move-session-item';
				item.dataset.sessionId = session.session_id;
				item.innerHTML = `
					<div class="move-session-avatar">${initials}</div>
					<span class="move-session-name">${escapeHtmlMove(session.session_name || 'Unnamed')}</span>
				`;
				item.addEventListener('click', () => selectCopySession(session.session_id));
				listEl.appendChild(item);
			});
		})
		.catch(err => {
			console.error('Failed to load sessions for batch copy:', err);
			listEl.innerHTML = '<div class="move-popover-empty">Failed to load sessions.</div>';
		});
}

async function handleMoveServer(event, serverId) {
	event.preventDefault();
	event.stopPropagation();

	_movePopoverServerId   = serverId;
	_movePopoverSelectedId = null;

	const popover    = getOrCreateMovePopover();
	const listEl     = popover.querySelector('#move-popover-list');
	const confirmBtn = popover.querySelector('.move-popover-confirm');

	// Reset
	confirmBtn.disabled    = true;
	confirmBtn.textContent = 'Move';
	listEl.innerHTML       = '<div class="move-popover-loading">Loading…</div>';

	// Position near clicked button, then show
	const btn  = event.currentTarget;
	const rect = btn.getBoundingClientRect();

	popover.style.display    = 'flex';
	popover.style.visibility = 'hidden';

	requestAnimationFrame(() => {
		const pw  = popover.offsetWidth  || 260;
		const ph  = popover.offsetHeight || 320;
		const vpW = window.innerWidth;
		const vpH = window.innerHeight;

		let left = rect.right + 10;
		let top  = rect.top;

		if (left + pw > vpW - 8) left = rect.left - pw - 10;
		if (top  + ph > vpH - 8) top  = vpH - ph - 8;
		if (top < 8) top = 8;

		popover.style.left       = `${left}px`;
		popover.style.top        = `${top}px`;
		popover.style.visibility = '';
	});

	// Fetch sessions and render
	try {
		const data     = await fetch('/sp/sessions').then(r => r.json());
		const sessions = (data.sessions || []).filter(s => s.session_id !== _currentSessionId);

		if (!sessions.length) {
			listEl.innerHTML = '<div class="move-popover-empty">No other sessions available.</div>';
			return;
		}

		listEl.innerHTML = '';
		sessions.forEach(session => {
			const initials = (session.session_name || '?')
				.split(/\s+|-/)
				.filter(Boolean)
				.map(w => w[0])
				.join('')
				.toUpperCase()
				.slice(0, 2);

			const item = document.createElement('div');
			item.className        = 'move-session-item';
			item.dataset.sessionId = session.session_id;
			item.innerHTML = `
				<div class="move-session-avatar">${initials}</div>
				<span class="move-session-name">${escapeHtmlMove(session.session_name || 'Unnamed')}</span>
			`;
			item.addEventListener('click', () => selectMoveSession(session.session_id));
			listEl.appendChild(item);
		});
	} catch (err) {
		console.error('Failed to load sessions for move:', err);
		listEl.innerHTML = '<div class="move-popover-empty">Failed to load sessions.</div>';
	}
}

// Fetch servers from API and populate table
async function populateTable(session_id = null, session_name = null) {
	_currentSessionId   = session_id;
	_currentSessionName = session_name;
	updateSessionLabel();
	const tbody = document.getElementById('serverTableBody');
	tbody.innerHTML = '';
	
	try {
		const url = session_id ? `/sp/list/${encodeURIComponent(session_id)}/servers` : '/sp/list/servers';
		const response = await fetch(url);
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		const servers = await response.json();
	
		// Wire select-all checkbox (re-attach each render)
		const selectAllCb = document.getElementById('select-all-checkbox');
		if (selectAllCb) {
			selectAllCb.checked = false;
			selectAllCb.indeterminate = false;
			selectAllCb.addEventListener('change', () => {
				const checkable = document.querySelectorAll('.row-checkbox:not(:disabled)');
				checkable.forEach(cb => {
					setRowChecked(cb, cb.dataset.serverId, selectAllCb.checked);
				});
			});
		}

		// Wire batch start button
		const batchBtn = document.getElementById('batch-start-btn');
		if (batchBtn) {
			// Remove old listeners by cloning
			const fresh = batchBtn.cloneNode(true);
			batchBtn.parentNode.replaceChild(fresh, batchBtn);
			fresh.addEventListener('click', handleBatchStart);
		}

		const batchMoveBtn = document.getElementById('batch-move-btn');
		if (batchMoveBtn) {
			const freshMove = batchMoveBtn.cloneNode(true);
			batchMoveBtn.parentNode.replaceChild(freshMove, batchMoveBtn);
			freshMove.addEventListener('click', handleBatchMove);
		}

		const batchCopyBtn = document.getElementById('batch-copy-btn');
		if (batchCopyBtn) {
			const freshCopy = batchCopyBtn.cloneNode(true);
			batchCopyBtn.parentNode.replaceChild(freshCopy, batchCopyBtn);
			freshCopy.addEventListener('click', handleBatchCopy);
		}

		const batchDeleteBtn = document.getElementById('batch-delete-btn');
		if (batchDeleteBtn) {
			const freshDelete = batchDeleteBtn.cloneNode(true);
			batchDeleteBtn.parentNode.replaceChild(freshDelete, batchDeleteBtn);
			freshDelete.addEventListener('click', handleBatchDelete);
		}

		servers.forEach(server => {
			const row = document.createElement('tr');
			const actionText = getActionText(server.pid_status);
			const isCurrentApp = server.server_id === '1';
			const warnings = server.warnings || [];
			const pathWarningEntry = warnings.find(w => 'file_path_present' in w);
			const filePathPresent = pathWarningEntry ? pathWarningEntry.file_path_present : true;

			row.innerHTML = `
				<td class="checkbox-col">
					<input type="checkbox"
						class="row-checkbox"
						data-server-id="${server.server_id}"
						${isCurrentApp ? 'disabled title="Cannot batch-start current app"' : ''}>
				</td>
				<td title="${server.server_name}">
					<div class="server-info">
						<div class="server-avatar">${getInitials(server.server_name)}</div>
						<span class="server-name">
							${server.server_name}
							${server.server_id === "1" ? '<span class="current-app-badge">● Current</span>' : ''}
						</span>
					</div>
				</td>
				<td title="${server.root_path}">
					<div class="command-cell">
						<span>${server.root_path}</span>
						${!filePathPresent ? `
						<button class="path-warning-btn" title="Path not detected in your system">
							<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
								<path d="M12 2L1 21h22L12 2zm0 3.99L20.47 19H3.53L12 5.99zM11 10v4h2v-4h-2zm0 6v2h2v-2h-2z"/>
							</svg>
						</button>` : ''}
						<a href="#" class="command-copy-link path-copy-link" title="Copy path" data-path="${server.root_path.replace(/"/g, '&quot;')}">
							<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
								<rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
							</svg>
						</a>
						<a href="#" class="path-terminal-link" title="Open terminal at path" data-path="${server.root_path.replace(/"/g, '&quot;')}">
							<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<polyline points="4 17 10 11 4 5"></polyline>
								<line x1="12" y1="19" x2="20" y2="19"></line>
							</svg>
						</a>
					</div>
				</td>
				<td title="${server.runnable_command}">
					<div class="command-cell">
						<span>${server.runnable_command}</span>
						<a href="#" class="command-copy-link" title="Copy command" data-command="${server.runnable_command.replace(/"/g, '&quot;')}">
							<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
								<rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
							</svg>
						</a>
					</div>
				</td>
				<td title="${server.git_branch}">${server.git_branch}</td>
				<td>
					<div class="server-actions">
					${!isCurrentApp ? `
						<a href="#" class="server-action-link" data-server-id="${server.server_id}" data-server-name="${server.server_name}" data-action="${actionText}">${actionText}</a>
						<a href="#" class="server-move-link" data-server-id="${server.server_id}" title="Move to another session">Move To</a>
					<a href="#" class="server-copy-link" data-server-id="${server.server_id}" title="Copy to another session">Copy To</a>
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
		
		// Attach click handlers to copy command links
		document.querySelectorAll('.command-copy-link:not(.path-copy-link)').forEach(link => {
			link.addEventListener('click', (event) => {
				const command = link.getAttribute('data-command');
				handleCopyCommand(event, command);
			});
		});

		// Attach click handlers to path copy links
		document.querySelectorAll('.path-copy-link').forEach(link => {
			link.addEventListener('click', (event) => {
				const path = link.getAttribute('data-path');
				handleCopyCommand(event, path);
			});
		});

		// Attach click handlers to path terminal links
		document.querySelectorAll('.path-terminal-link').forEach(link => {
			link.addEventListener('click', (event) => {
				const path = link.getAttribute('data-path');
				handleOpenTerminal(event, path);
			});
		});

		// Attach click handlers to path warning buttons
		document.querySelectorAll('.path-warning-btn').forEach(btn => {
			btn.addEventListener('click', (event) => {
				event.preventDefault();
				alert('Path is not detected in your system');
			});
		});
		
		// Attach click handlers to move links
		document.querySelectorAll('.server-move-link').forEach(link => {
			link.addEventListener('click', (event) => {
				const serverId = link.getAttribute('data-server-id');
				handleMoveServer(event, serverId);
			});
		});

		// Attach click handlers to copy links
		document.querySelectorAll('.server-copy-link').forEach(link => {
			link.addEventListener('click', (event) => {
				const serverId = link.getAttribute('data-server-id');
				handleCopyServer(event, serverId);
			});
		});

		// Attach click handlers to action links
		document.querySelectorAll('.server-action-link').forEach(link => {
			link.addEventListener('click', (event) => {
				const serverId   = link.getAttribute('data-server-id');
				const action     = link.getAttribute('data-action');
				const serverName = link.getAttribute('data-server-name');
				handleServerAction(event, serverId, action, serverName);
			});
		});

		// Attach row checkbox handlers
		document.querySelectorAll('.row-checkbox:not(:disabled)').forEach(cb => {
			// Restore checked state if already selected
			if (_selectedIds.has(cb.dataset.serverId)) {
				cb.checked = true;
				cb.closest('tr').classList.add('row-selected');
			}
			cb.addEventListener('change', () => {
				setRowChecked(cb, cb.dataset.serverId, cb.checked);
				// Sync select-all header checkbox state
				const all   = document.querySelectorAll('.row-checkbox:not(:disabled)');
				const checked = document.querySelectorAll('.row-checkbox:not(:disabled):checked');
				const sa = document.getElementById('select-all-checkbox');
				if (sa) {
					sa.checked       = checked.length === all.length && all.length > 0;
					sa.indeterminate = checked.length > 0 && checked.length < all.length;
				}
			});
		});
		syncBatchBar();
	} catch (error) {
		console.error('Error fetching servers:', error);
		const tbody = document.getElementById('serverTableBody');
		tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Error loading servers</td></tr>';
	}
}

// Initialize table when DOM is loaded
// Call directly since table HTML is injected dynamically
if (document.getElementById('serverTableBody')) {
	populateTable();
	wireRefreshButton();
} else {
	// If not found, try again after a short delay (in case of async load)
	setTimeout(() => { populateTable(); wireRefreshButton(); }, 100);
}

function wireRefreshButton() {
	const btn = document.getElementById('refresh-table-btn');
	if (!btn) return;
	btn.addEventListener('click', () => {
		btn.classList.add('spinning');
		btn.addEventListener('animationend', () => btn.classList.remove('spinning'), { once: true });
		populateTable(_currentSessionId, _currentSessionName);
	});

	const sessionLabel = document.getElementById('current-session-label');
	if (sessionLabel) {
		sessionLabel.addEventListener('click', () => {
			const toggle = document.getElementById('session-drawer-toggle');
			if (toggle) toggle.click();
		});
	}
}
