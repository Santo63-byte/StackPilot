// Application Configuration
const AppConfig = {
  proxyEnvironments: [],
  renderAttributes: {},

  get terminal() {
    return this.renderAttributes.terminal || null;
  },

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
      await this.refreshRenderAttributes();
      return true;
    } catch (error) {
      console.error('Error initializing AppConfig:', error);
      return false;
    }
  },

  async refreshRenderAttributes() {
    try {
      const renderResponse = await fetch('/sp/app/render-attributes');
      if (renderResponse.ok) {
        const renderData = await renderResponse.json();
        this.renderAttributes = renderData.render_attributes || {};
        console.log('Render attributes loaded:', this.renderAttributes);
      }
    } catch (error) {
      console.error('Error refreshing render attributes:', error);
    }
  }
};
