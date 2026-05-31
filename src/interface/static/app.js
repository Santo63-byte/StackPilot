async function includeComponent(tag, url) {
		const elements = document.getElementsByTagName(tag);
		if (elements.length > 0) {
			const resp = await fetch(url);
			const html = await resp.text();
			Array.from(elements).forEach(el => { el.outerHTML = html; });
		}
	}
	document.addEventListener('DOMContentLoaded', async () => {
		// Initialize app configuration first
		const configInitialized = await AppConfig.init();
		if (!configInitialized) {
			console.warn('Failed to initialize AppConfig');
		}
		
		// Setup proxy environment dropdown
		const proxyDropdown = document.getElementById('proxy-env-dropdown');
		const proxySettings = AppConfig.renderAttributes?.addons?.proxy_settings;
		if (proxySettings?.enabled) {
			proxyDropdown.style.display = 'block';
			// Populate dropdown with proxy environments
			AppConfig.proxyEnvironments.forEach(env => {
				const option = document.createElement('option');
				option.value = env;
				option.textContent = env;
				proxyDropdown.appendChild(option);
			});
			// Set the active environment as selected
			if (proxySettings.active_environment) {
				proxyDropdown.value = proxySettings.active_environment;
			}
			
			proxyDropdown.addEventListener('change', async (e) => {
				const selectedEnv = e.target.value;
				if (selectedEnv) {
					try {
						const response = await fetch(`/sp/proxy/environments/set?env=${encodeURIComponent(selectedEnv)}`, {
							method: 'POST'
						});
						const data = await response.json();
						if (response.ok) {
							console.log(`Proxy environment set to '${selectedEnv}' successfully`);
						} else {
							console.error(`Failed to set proxy environment: ${data.message}`);
						}
					} catch (error) {
						console.error('Error setting proxy environment:', error);
					}
				}
			});

			// Proxy start button
			const proxyBtnWrapper = document.getElementById('proxy-start-btn-wrapper');
			const proxyBtn = document.getElementById('proxy-start-btn');
			const proxyDot = proxyBtn.querySelector('.proxy-dot');
			const proxyErrorIcon = document.getElementById('proxy-error-icon');

			proxyBtnWrapper.style.display = 'flex';

			function setProxyDotState(state, errorMsg) {
				proxyDot.className = 'proxy-dot';
				if (state === 'loading') {
					proxyDot.classList.add('proxy-dot--yellow');
					proxyBtn.disabled = true;
					proxyErrorIcon.style.display = 'none';
				} else if (state === 'success') {
					proxyDot.classList.add('proxy-dot--green');
					proxyBtn.disabled = false;
					proxyErrorIcon.style.display = 'none';
				} else {
					proxyDot.classList.add('proxy-dot--red');
					proxyBtn.disabled = false;
					if (errorMsg) {
						proxyErrorIcon.textContent = '⚠️';
						proxyErrorIcon.setAttribute('data-msg', errorMsg);
						proxyErrorIcon.style.display = 'inline-block';
					} else {
						proxyErrorIcon.style.display = 'none';
					}
				}
			}

			proxyBtn.addEventListener('click', async () => {
				setProxyDotState('loading');
				try {
					const response = await fetch('/sp/proxy/server/start', { method: 'POST' });
					const data = await response.json();
					if (data.status === 200) {
						setProxyDotState('success');
					} else {
						setProxyDotState('error', data.message || 'Failed to start proxy');
					}
				} catch (error) {
					setProxyDotState('error', 'Network error: could not reach proxy start endpoint');
				}
			});

			// Set initial dot state based on is_proxy_running from render attributes
			if (proxySettings.is_proxy_running === true) {
				setProxyDotState('success');
			} else {
				setProxyDotState('error');
			}
		}
		
		await includeComponent('box-button', '/templates/boxbutton.html');
		await includeComponent('server-table', '/templates/tableview.html');
		await includeComponent('add-server-modal', '/templates/addserver.html');
		
		// After table HTML is loaded, attach JS
		const script = document.createElement('script');
		script.src = '/static/table.js';
		document.body.appendChild(script);

		// Load folder browser script
		const folderBrowserScript = document.createElement('script');
		folderBrowserScript.src = '/static/folder-browser.js';
		document.body.appendChild(folderBrowserScript);

		// Load add server form script
		const addServerScript = document.createElement('script');
		addServerScript.src = '/static/addserver.js';
		addServerScript.onload = function() {
			// Initialize form after script loads
			if (typeof initAddServerForm === 'function') {
				initAddServerForm();
			}
		};
		document.body.appendChild(addServerScript);

		// Load session drawer script
		const sessionDrawerScript = document.createElement('script');
		sessionDrawerScript.src = '/static/session-drawer.js';
		document.body.appendChild(sessionDrawerScript);

		// Load console drawer script
		const consoleDrawerScript = document.createElement('script');
		consoleDrawerScript.src = '/static/console-drawer.js';
		document.body.appendChild(consoleDrawerScript);

		// Load settings modal script
		const settingsScript = document.createElement('script');
		settingsScript.src = '/static/settings.js';
		document.body.appendChild(settingsScript);

		// Box button click handler to open modal
		const boxButton = document.querySelector('.box-button');
		const modalOverlay = document.getElementById('modal-overlay');
		if (boxButton && modalOverlay) {
			boxButton.addEventListener('click', () => {
				modalOverlay.style.display = 'flex';
			});
			// Close modal when clicking outside
			modalOverlay.addEventListener('click', (e) => {
				if (e.target === modalOverlay) {
					modalOverlay.style.display = 'none';
				}
			});
		}
	});
