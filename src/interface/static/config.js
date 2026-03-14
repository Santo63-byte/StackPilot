// Application Configuration
const AppConfig = {
  proxyEnvironments: [],
  renderAttributes: {},
  
  async init() {
    try {
      // Fetch proxy environments
      const proxyResponse = await fetch('/sp/proxy/environments/lookup');
      if (proxyResponse.ok) {
        const proxyData = await proxyResponse.json();
        this.proxyEnvironments = proxyData.environments || [];
        console.log('Proxy environments loaded:', this.proxyEnvironments);
      }
      // Fetch render attributes
      const renderResponse = await fetch('/sp/app/render-attributes');
      if (renderResponse.ok) {
        const renderData = await renderResponse.json();
        this.renderAttributes = renderData.render_attributes || {};
        console.log('Render attributes loaded:', this.renderAttributes);
      }
      return true;
    } catch (error) {
      console.error('Error initializing AppConfig:', error);
      return false;
    }
  }
};
