// ── Config Download / Upload ───────────────────────────────────────────
// Handles the left-side download (↓) and upload (↑) buttons for
// transferring the server list JSON config.

(function ConfigTransfer() {

    // ── Download ──────────────────────────────────────────────────────
    const downloadBtn = document.getElementById('config-download-btn');

    if (downloadBtn) {
        downloadBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/sp/config/download');
                if (!response.ok) {
                    const data = await response.json().catch(() => ({}));
                    alert(data.message || 'Failed to download server config.');
                    return;
                }
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'serverlist.json';
                document.body.appendChild(a);
                a.click();
                a.remove();
                URL.revokeObjectURL(url);
            } catch (err) {
                console.error('Config download error:', err);
                alert('Network error: could not download server config.');
            }
        });
    }

    // ── Upload modal ──────────────────────────────────────────────────
    const uploadBtn    = document.getElementById('config-upload-btn');
    const overlay      = document.getElementById('upload-config-overlay');
    const closeBtn     = document.getElementById('upload-config-close');
    const dropZone     = document.getElementById('upload-drop-zone');
    const fileInput    = document.getElementById('upload-file-input');
    const selectedName = document.getElementById('upload-selected-name');
    const confirmBtn   = document.getElementById('upload-config-confirm-btn');
    const statusMsg    = document.getElementById('upload-config-status');

    let _selectedFile = null;

    function openModal() {
        resetModal();
        overlay.style.display = 'flex';
    }

    function closeModal() {
        overlay.style.display = 'none';
    }

    function resetModal() {
        _selectedFile = null;
        fileInput.value = '';
        selectedName.textContent = '';
        confirmBtn.disabled = true;
        statusMsg.textContent = '';
        statusMsg.className = 'upload-config-status';
    }

    function setFile(file) {
        if (!file) return;
        if (!file.name.endsWith('.json') && file.type !== 'application/json') {
            setStatus('Only JSON files are accepted.', 'error');
            return;
        }
        _selectedFile = file;
        selectedName.textContent = file.name;
        confirmBtn.disabled = false;
        setStatus('');
    }

    function setStatus(msg, type) {
        statusMsg.textContent = msg;
        statusMsg.className = 'upload-config-status' + (type ? ' ' + type : '');
    }

    // Open / close
    if (uploadBtn) uploadBtn.addEventListener('click', openModal);
    if (closeBtn)  closeBtn.addEventListener('click', closeModal);
    if (overlay) {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closeModal();
        });
    }

    // Drag-and-drop
    if (dropZone) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            const file = e.dataTransfer.files[0];
            setFile(file);
        });

        // Clicking the drop zone triggers the file input
        dropZone.addEventListener('click', (e) => {
            if (e.target.tagName !== 'LABEL' && e.target.tagName !== 'INPUT') {
                fileInput.click();
            }
        });
    }

    // File input via browse
    if (fileInput) {
        fileInput.addEventListener('change', () => {
            setFile(fileInput.files[0]);
        });
    }

    // Confirm upload
    if (confirmBtn) {
        confirmBtn.addEventListener('click', async () => {
            if (!_selectedFile) return;

            confirmBtn.disabled = true;
            setStatus('Uploading…');

            try {
                const formData = new FormData();
                formData.append('file', _selectedFile);

                const response = await fetch('/sp/config/upload', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json().catch(() => ({}));

                if (response.ok && data.status === 200) {
                    setStatus('Config uploaded successfully! Refreshing…', 'success');
                    setTimeout(() => {
                        closeModal();
                        // Reload the server table to reflect new config
                        if (typeof populateTable === 'function' && typeof _currentSessionId !== 'undefined') {
                            populateTable(_currentSessionId, _currentSessionName);
                        }
                    }, 1200);
                } else {
                    setStatus(data.message || 'Upload failed.', 'error');
                    confirmBtn.disabled = false;
                }
            } catch (err) {
                console.error('Config upload error:', err);
                setStatus('Network error: could not upload config.', 'error');
                confirmBtn.disabled = false;
            }
        });
    }

})();
