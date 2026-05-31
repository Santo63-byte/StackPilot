// App Settings Modal

(function () {
    const settingsBtn = document.getElementById('app-settings-btn');
    const settingsOverlay = document.getElementById('settings-modal-overlay');
    const settingsCloseBtn = document.getElementById('settings-modal-close');
    const settingsSaveBtn = document.getElementById('settings-save-btn');
    const settingsBrowseBtn = document.getElementById('settings-browse-btn');

    const refreshIntervalField = document.getElementById('settings-refresh-interval');
    const defaultTerminalField = document.getElementById('settings-default-terminal');
    const proxyRootPathField = document.getElementById('settings-proxy-root-path');
    const proxySection = document.getElementById('settings-proxy-section');

    // ── Tab switching ────────────────────────────────────────
    const tabs = document.querySelectorAll('.settings-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const target = tab.dataset.tab;
            document.querySelectorAll('.settings-tab-panel').forEach(panel => {
                panel.style.display = 'none';
            });
            document.getElementById('settings-tab-' + target).style.display = 'flex';
        });
    });

    function resetToSettingsTab() {
        tabs.forEach(t => t.classList.remove('active'));
        document.querySelector('.settings-tab[data-tab="settings"]').classList.add('active');
        document.querySelectorAll('.settings-tab-panel').forEach(panel => {
            panel.style.display = 'none';
        });
        document.getElementById('settings-tab-settings').style.display = 'flex';
    }

    // ── Populate Info tab from AppConfig render attributes ───
    function populateInfoTab() {
        const attrs = (typeof AppConfig !== 'undefined' && AppConfig.renderAttributes) ? AppConfig.renderAttributes : {};
        const version = attrs.version || '—';
        document.getElementById('settings-info-version').textContent = 'v' + version;
    }

    // Open modal and load current settings
    settingsBtn.addEventListener('click', async () => {
        resetToSettingsTab();
        populateInfoTab();
        await loadSettings();
        settingsOverlay.style.display = 'flex';
    });

    // Close modal
    settingsCloseBtn.addEventListener('click', closeModal);
    settingsOverlay.addEventListener('click', (e) => {
        if (e.target === settingsOverlay) closeModal();
    });

    function closeModal() {
        settingsOverlay.style.display = 'none';
    }

    async function loadSettings() {
        try {
            const response = await fetch('/sp/app/settings');
            if (!response.ok) {
                console.error('Failed to fetch app settings');
                return;
            }
            const data = await response.json();
            const appSettings = data.app_settings || {};
            const basic = appSettings.basic_settings || {};
            const advanced = appSettings.advanced_settings || {};

            // Populate basic settings
            if (basic.refresh_interval !== undefined) {
                refreshIntervalField.value = String(basic.refresh_interval);
            }
            if (basic.terminal !== undefined) {
                defaultTerminalField.value = basic.terminal;
            }

            // Populate proxy settings
            const proxy = advanced.proxy_settings || {};
            const proxyEnabled = proxy.root_path !== undefined && proxy.root_path !== null;
            if (proxySection) {
                // Show proxy section only if proxy addon is available (root_path key present)
                proxySection.style.display = 'root_path' in proxy ? 'flex' : 'none';
            }
            proxyRootPathField.value = proxy.root_path || '';
        } catch (err) {
            console.error('Error loading settings:', err);
        }
    }

    // Browse folder for proxy path
    settingsBrowseBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/sp/browse-folder');
            const data = await response.json();
            if (data.success && data.path) {
                proxyRootPathField.value = data.path;
            }
        } catch (err) {
            console.error('Error opening folder browser for proxy path:', err);
        }
    });

    // Save settings
    settingsSaveBtn.addEventListener('click', async () => {
        const newSettings = {
            basic_settings: {
                refresh_interval: parseInt(refreshIntervalField.value, 10),
                terminal: defaultTerminalField.value
            },
            advanced_settings: {
                proxy_settings: {
                    root_path: proxyRootPathField.value.trim() || null
                }
            }
        };

        try {
            settingsSaveBtn.disabled = true;
            settingsSaveBtn.textContent = 'Saving...';
            const response = await fetch('/sp/app/settings/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newSettings)
            });
            const data = await response.json();
            if (data.status === 200) {
                // Refresh render attributes so AppConfig.terminal reflects the new value
                if (typeof AppConfig !== 'undefined' && typeof AppConfig.refreshRenderAttributes === 'function') {
                    await AppConfig.refreshRenderAttributes();
                }
                closeModal();
            } else {
                console.error('Failed to save settings:', data.message);
                alert('Failed to save settings: ' + (data.message || 'Unknown error'));
            }
        } catch (err) {
            console.error('Error saving settings:', err);
            alert('Error saving settings. Please try again.');
        } finally {
            settingsSaveBtn.disabled = false;
            settingsSaveBtn.textContent = 'Save Settings';
        }
    });
})();
