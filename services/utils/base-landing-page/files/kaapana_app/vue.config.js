/* Dev-only proxy to make the standalone landing page work against local services.
 * - Proxies `/ohif/*` to your OHIF dev server (VUE_APP_OHIF_BASE)
 * - Proxies `/api/kaapana-backend/*` to your Kaapana backend (VUE_APP_KAAPANA_BACKEND_ENDPOINT)
 */

const OHIF_BASE = process.env.VUE_APP_OHIF_BASE || 'http://localhost:3001';
const KAAPANA_BACKEND = process.env.VUE_APP_KAAPANA_BACKEND_ENDPOINT || 'http://localhost:8088/';

module.exports = {
  devServer: {
    port: 5001,
    proxy: {
      '/ohif': {
        target: OHIF_BASE,
        changeOrigin: true,
        ws: true,
        pathRewrite: { '^/ohif': '' },
      },
      '/api/kaapana-backend': {
        target: KAAPANA_BACKEND,
        changeOrigin: true,
        // Keep the prefix so target sees /api/kaapana-backend/... as our mock expects
        // pathRewrite: { '^/api/kaapana-backend': '' },
      },
    },
  },
};

module.exports = {
    transpileDependencies: ['vuetify'],
    devServer: {
        allowedHosts: "all"
    }
}
