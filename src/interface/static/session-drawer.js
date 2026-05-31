// ── Session Drawer ────────────────────────────────────────────────────
// Handles the left-side slide-in drawer for session management.
// APIs used:
//   GET    /sp/sessions               → list all sessions
//   POST   /sp/sessions               → create a session  { session_name }
//   PUT    /sp/sessions/:id           → rename a session  { session_name }
//   DELETE /sp/sessions/:id           → delete a session

(function SessionDrawer() {

    // ── DOM refs ──────────────────────────────────────────────────────
    const toggle   = document.getElementById('session-drawer-toggle');
    const backdrop = document.getElementById('session-drawer-backdrop');
    const drawer   = document.getElementById('session-drawer');
    const closeBtn = document.getElementById('session-drawer-close');
    const addBtn   = document.getElementById('session-add-btn');
    const addForm  = document.getElementById('session-add-form');
    const addInput = document.getElementById('session-add-input');
    const addConfirm = document.getElementById('session-add-confirm');
    const addCancel  = document.getElementById('session-add-cancel');
    const listEl   = document.getElementById('session-drawer-list');

    // ── Helpers ───────────────────────────────────────────────────────
    function getInitials(name) {
        return (name || '?')
            .split(/\s+|-/)
            .filter(Boolean)
            .map(w => w[0])
            .join('')
            .toUpperCase()
            .slice(0, 2);
    }

    function svgEdit() {
        return `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>`;
    }

    function svgDelete() {
        return `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
            <path d="M10 11v6M14 11v6"/>
            <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
        </svg>`;
    }

    function svgSave() {
        return `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"/>
        </svg>`;
    }

    function svgCancel() {
        return `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>`;
    }

    // ── Active session state ─────────────────────────────────────────
    let _activeSessionId = null;

    function setActiveSession(id, name) {
        _activeSessionId = id;
        document.querySelectorAll('#session-drawer-list .session-item').forEach(el => {
            el.classList.toggle('session-item--active', el.dataset.sessionId === id);
        });
        if (typeof populateTable === 'function') {
            populateTable(id, name || null);
        }
    }

    // ── Open / Close ──────────────────────────────────────────────────
    function openDrawer() {
        drawer.classList.add('open');
        backdrop.classList.add('open');
        loadSessions();
    }

    function closeDrawer() {
        drawer.classList.remove('open');
        backdrop.classList.remove('open');
        hideAddForm();
    }

    // ── Add-form visibility ───────────────────────────────────────────
    function showAddForm() {
        addForm.classList.add('visible');
        addInput.value = '';
        addInput.focus();
    }

    function hideAddForm() {
        addForm.classList.remove('visible');
        addInput.value = '';
    }

    // ── API calls ─────────────────────────────────────────────────────
    async function apiFetch(url, options = {}) {
        const res = await fetch(url, options);
        if (!res.ok) {
            const text = await res.text();
            throw new Error(`HTTP ${res.status}: ${text}`);
        }
        return res.json();
    }

    async function loadSessions() {
        listEl.innerHTML = `<div class="session-loading"><div class="session-spinner"></div></div>`;
        try {
            const data = await apiFetch('/sp/sessions');
            renderSessions(data.sessions || []);
        } catch (err) {
            console.error('Failed to load sessions:', err);
            listEl.innerHTML = `<div class="session-drawer-empty">Failed to load sessions.</div>`;
        }
    }

    async function createSession(name) {
        await apiFetch('/sp/sessions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_name: name })
        });
        await loadSessions();
    }

    async function renameSession(id, name) {
        await apiFetch(`/sp/sessions/${encodeURIComponent(id)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_name: name })
        });
        await loadSessions();
    }

    async function deleteSession(id) {
        await apiFetch(`/sp/sessions/${encodeURIComponent(id)}`, { method: 'DELETE' });
        await loadSessions();
    }

    // ── Render list ───────────────────────────────────────────────────
    function renderSessions(sessions) {
        if (!sessions.length) {
            listEl.innerHTML = `<div class="session-drawer-empty">No sessions yet.<br>Click <strong>+</strong> to create one.</div>`;
            return;
        }

        listEl.innerHTML = '';
        sessions.forEach(session => {
            const item = buildSessionItem(session);
            listEl.appendChild(item);
        });

        // Auto-select first session on initial load
        if (!_activeSessionId && sessions.length) {
            setActiveSession(sessions[0].session_id, sessions[0].session_name);
        } else if (_activeSessionId) {
            // Re-apply active highlight after re-render
            const activeEl = listEl.querySelector(`[data-session-id="${_activeSessionId}"]`);
            if (activeEl) activeEl.classList.add('session-item--active');
        }
    }

    function buildSessionItem(session) {
        const id   = session.session_id;
        const name = session.session_name || 'Unnamed';

        const item = document.createElement('div');
        item.className = 'session-item';
        item.dataset.sessionId = id;

        item.innerHTML = `
            <div class="session-item-avatar">${getInitials(name)}</div>
            <span class="session-item-name" title="${escapeHtml(name)}">${escapeHtml(name)}</span>
            <div class="session-item-actions">
                <button class="session-item-btn edit-btn" title="Rename">${svgEdit()}</button>
                <button class="session-item-btn delete-btn" title="Delete">${svgDelete()}</button>
            </div>
        `;

        // Session select — click anywhere on item except action buttons
        item.addEventListener('click', (e) => {
            if (!e.target.closest('.session-item-actions')) {
                setActiveSession(id, name);
            }
        });

        // Edit button → switch to inline edit mode
        item.querySelector('.edit-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            enterEditMode(item, id, name);
        });

        // Delete button
        item.querySelector('.delete-btn').addEventListener('click', async (e) => {
            e.stopPropagation();
            if (!confirm(`Delete session "${name}"?`)) return;
            try {
                if (_activeSessionId === id) _activeSessionId = null;
                await deleteSession(id);
            } catch (err) {
                console.error('Delete session failed:', err);
                alert('Failed to delete session.');
            }
        });

        return item;
    }

    function enterEditMode(item, id, currentName) {
        // Replace name span + action buttons with inline edit UI
        const nameSpan   = item.querySelector('.session-item-name');
        const actionsDiv = item.querySelector('.session-item-actions');

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'session-item-edit-input';
        input.value = currentName;

        const saveBtn = document.createElement('button');
        saveBtn.className = 'session-item-btn save-btn';
        saveBtn.title = 'Save';
        saveBtn.innerHTML = svgSave();

        const cancelBtn = document.createElement('button');
        cancelBtn.className = 'session-item-btn cancel-btn';
        cancelBtn.title = 'Cancel';
        cancelBtn.innerHTML = svgCancel();

        nameSpan.replaceWith(input);
        actionsDiv.innerHTML = '';
        actionsDiv.appendChild(saveBtn);
        actionsDiv.appendChild(cancelBtn);

        input.focus();
        input.select();

        async function save() {
            const newName = input.value.trim();
            if (!newName) { input.focus(); return; }
            if (newName === currentName) { await loadSessions(); return; }
            try {
                await renameSession(id, newName);
            } catch (err) {
                console.error('Rename session failed:', err);
                alert('Failed to rename session.');
            }
        }

        saveBtn.addEventListener('click', save);
        cancelBtn.addEventListener('click', () => loadSessions());
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter')  save();
            if (e.key === 'Escape') loadSessions();
        });
    }

    // ── HTML escape helper (prevent XSS from session names) ───────────
    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    // ── Event wiring ──────────────────────────────────────────────────
    // ── Init: load sessions on page load ─────────────────────────────
    loadSessions();

    toggle.addEventListener('click', openDrawer);
    backdrop.addEventListener('click', closeDrawer);
    closeBtn.addEventListener('click', closeDrawer);

    addBtn.addEventListener('click', () => {
        if (addForm.classList.contains('visible')) {
            hideAddForm();
        } else {
            showAddForm();
        }
    });

    addConfirm.addEventListener('click', async () => {
        const name = addInput.value.trim();
        if (!name) { addInput.focus(); return; }
        try {
            await createSession(name);
            hideAddForm();
        } catch (err) {
            console.error('Create session failed:', err);
            alert('Failed to create session.');
        }
    });

    addCancel.addEventListener('click', hideAddForm);

    addInput.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
            const name = addInput.value.trim();
            if (!name) return;
            try {
                await createSession(name);
                hideAddForm();
            } catch (err) {
                console.error('Create session failed:', err);
                alert('Failed to create session.');
            }
        }
        if (e.key === 'Escape') hideAddForm();
    });

})();
