// ── Console Drawer ────────────────────────────────────────────────────
// Right-side slide-in drawer for per-server process log streaming.
// Each started server gets a tab; clicking a tab streams logs via WebSocket.
//
// Public API (on window):
//   window.ConsoleDrawer.openConsoleTab(serverName)

(function ConsoleDrawer() {

    // ── DOM refs ──────────────────────────────────────────────────────
    const toggle     = document.getElementById('console-drawer-toggle');
    const backdrop   = document.getElementById('console-drawer-backdrop');
    const drawer     = document.getElementById('console-drawer');
    const closeBtn   = document.getElementById('console-drawer-close');
    const tabBar     = document.getElementById('console-tab-bar');
    const outputArea = document.getElementById('console-output-area');

    if (!toggle || !drawer) {
        console.warn('ConsoleDrawer: required DOM elements not found.');
        return;
    }

    // ── State ─────────────────────────────────────────────────────────
    // Map<serverName, { tabEl, dotEl, panelEl, ws: WebSocket|null }>
    const _tabs = new Map();
    let _activeTab = null;

    // ── Open / Close ──────────────────────────────────────────────────
    function openDrawer() {
        drawer.classList.add('open');
        backdrop.classList.add('open');
    }

    function closeDrawer() {
        drawer.classList.remove('open');
        backdrop.classList.remove('open');
    }

    // ── Tab management ────────────────────────────────────────────────

    /**
     * Open (or focus) a console tab for the given serverName.
     * Called externally when a server is started.
     */
    function openConsoleTab(serverName) {
        if (_tabs.has(serverName)) {
            activateTab(serverName);
        } else {
            _createTab(serverName);
        }
        openDrawer();
    }

    function _createTab(serverName) {
        // —— Tab button ——
        const tab = document.createElement('button');
        tab.className = 'console-tab';

        const dot = document.createElement('span');
        dot.className = 'console-tab-dot';

        const label = document.createElement('span');
        label.textContent = serverName;

        const closeX = document.createElement('span');
        closeX.className = 'console-tab-close';
        closeX.title = 'Close tab';
        closeX.textContent = '×';
        closeX.addEventListener('click', (e) => {
            e.stopPropagation();
            _closeTab(serverName);
        });

        tab.appendChild(dot);
        tab.appendChild(label);
        tab.appendChild(closeX);
        tab.addEventListener('click', () => activateTab(serverName));
        tabBar.appendChild(tab);

        // Scroll new tab into view within the tab bar
        requestAnimationFrame(() => tab.scrollIntoView({ block: 'nearest', inline: 'end' }));

        // —— Log panel ——
        const panel = document.createElement('div');
        panel.className = 'console-log-panel';
        outputArea.appendChild(panel);

        // —— WebSocket ——
        const ws = _connectWebSocket(serverName, panel, dot, tab);

        _tabs.set(serverName, { tabEl: tab, dotEl: dot, panelEl: panel, ws });
        activateTab(serverName);
        _syncEmptyHint();
    }

    function activateTab(serverName) {
        _tabs.forEach((state, name) => {
            const isActive = name === serverName;
            state.tabEl.classList.toggle('active', isActive);
            state.panelEl.classList.toggle('active', isActive);
        });
        _activeTab = serverName;
    }

    function _closeTab(serverName) {
        const state = _tabs.get(serverName);
        if (!state) return;

        // Gracefully close WebSocket if still open
        if (state.ws && state.ws.readyState < WebSocket.CLOSING) {
            state.ws.close(1000, 'Tab closed by user');
        }
        state.tabEl.remove();
        state.panelEl.remove();
        _tabs.delete(serverName);

        // Activate next available tab
        if (_activeTab === serverName) {
            const firstKey = _tabs.keys().next().value;
            _activeTab = firstKey || null;
            if (firstKey) activateTab(firstKey);
        }
        _syncEmptyHint();
    }

    function _syncEmptyHint() {
        const existing = outputArea.querySelector('.console-empty-hint');
        if (_tabs.size === 0 && !existing) {
            const hint = document.createElement('div');
            hint.className = 'console-empty-hint';
            hint.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <polyline points="4 17 10 11 4 5"></polyline>
                    <line x1="12" y1="19" x2="20" y2="19"></line>
                </svg>
                <p>Start a server to see its logs here.</p>`;
            outputArea.appendChild(hint);
        } else if (_tabs.size > 0 && existing) {
            existing.remove();
        }
    }

    // ── WebSocket ─────────────────────────────────────────────────────

    function _connectWebSocket(serverName, panel, dot, tab) {
        const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
        const url   = `${proto}//${location.host}/sp/console/${encodeURIComponent(serverName)}/logs`;
        let ws;

        try {
            ws = new WebSocket(url);
        } catch (err) {
            _appendLine(panel, `[Failed to open WebSocket: ${err.message}]`, 'log-error');
            dot.style.background = '#ef4444';
            return null;
        }

        ws.onopen = () => {
            dot.style.background = '#10b981';
            tab.classList.remove('ws-error');
            _appendLine(panel, `[Connected to ${serverName}]`, 'log-info');
        };

        ws.onmessage = (e) => {
            if (e.data === '[PROCESS ENDED]') {
                dot.style.background = '#374151';
                _appendLine(panel, '[Process ended]', 'log-info');
            } else if (e.data.startsWith('[ERROR]')) {
                dot.style.background = '#ef4444';
                tab.classList.add('ws-error');
                _appendLine(panel, e.data, 'log-error');
            } else {
                _appendLine(panel, e.data, '');
            }
        };

        ws.onerror = () => {
            dot.style.background = '#ef4444';
            tab.classList.add('ws-error');
            _appendLine(panel, `[WebSocket error for '${serverName}']`, 'log-error');
        };

        ws.onclose = (e) => {
            // Only show disconnect message if it wasn't a clean user-initiated close
            if (e.code !== 1000) {
                dot.style.background = '#f59e0b';
                _appendLine(panel, `[Disconnected (code ${e.code})]`, 'log-info');
            }
        };

        return ws;
    }

    function _appendLine(panel, text, cssClass) {
        const line = document.createElement('div');
        line.className = cssClass ? `log-line ${cssClass}` : 'log-line';
        line.textContent = text;
        panel.appendChild(line);
        // Auto-scroll to bottom
        panel.scrollTop = panel.scrollHeight;
    }

    // ── Kill-Port ─────────────────────────────────────────────────────
    const killPortInput = document.getElementById('kill-port-input');
    const killPortBtn   = document.getElementById('kill-port-btn');

    // Allow only digits, up to 6 characters
    killPortInput.addEventListener('input', () => {
        killPortInput.value = killPortInput.value.replace(/\D/g, '').slice(0, 6);
    });
    killPortInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') _doKillPort();
    });
    killPortBtn.addEventListener('click', _doKillPort);

    const openTerminalBtn = document.getElementById('open-terminal-btn');
    openTerminalBtn.addEventListener('click', _doOpenTerminal);

    function _doOpenTerminal() {
        openTerminalBtn.disabled = true;
        fetch('/sp/console/openadavancedterminal', { method: 'POST' })
            .then(r => r.json())
            .then(data => {
                const isOk = data.status === 200;
                _showToast(data.message || (isOk ? 'Terminal opened.' : 'Failed to open terminal.'), isOk ? 'success' : 'error');
            })
            .catch(() => _showToast('Request failed. Is the server running?', 'error'))
            .finally(() => { openTerminalBtn.disabled = false; });
    }

    function _doKillPort() {
        const port = killPortInput.value.trim();
        if (!port || !/^\d{1,6}$/.test(port)) {
            _showToast('Please enter a valid port number (1–6 digits).', 'error');
            return;
        }
        killPortBtn.disabled = true;
        fetch(`/sp/console/killport/${encodeURIComponent(port)}`, { method: 'POST' })
            .then(r => r.json())
            .then(data => {
                const isOk = data.status === 200;
                _showToast(data.message || (isOk ? 'Port killed.' : 'Failed.'), isOk ? 'success' : 'error');
                if (isOk) killPortInput.value = '';
            })
            .catch(() => _showToast('Request failed. Is the server running?', 'error'))
            .finally(() => { killPortBtn.disabled = false; });
    }

    // ── Toast ─────────────────────────────────────────────────────────
    let _toastTimer = null;

    function _showToast(message, type) {
        let toast = document.getElementById('console-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'console-toast';
            toast.className = 'console-toast';
            document.body.appendChild(toast);
        }
        toast.textContent = message;
        toast.className = `console-toast toast-${type}`;
        // Force reflow so transition fires even on rapid calls
        void toast.offsetWidth;
        toast.classList.add('show');
        clearTimeout(_toastTimer);
        _toastTimer = setTimeout(() => toast.classList.remove('show'), 3200);
    }

    // ── Event wiring ──────────────────────────────────────────────────
    toggle.addEventListener('click', openDrawer);
    backdrop.addEventListener('click', closeDrawer);
    closeBtn.addEventListener('click', closeDrawer);

    // Render initial empty hint
    _syncEmptyHint();

    // ── Public API ────────────────────────────────────────────────────
    window.ConsoleDrawer = { openConsoleTab };

})();
