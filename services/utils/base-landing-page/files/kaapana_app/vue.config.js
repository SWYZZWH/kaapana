/* Dev-only proxy to make the standalone landing page work against local services.
 * - Proxies `/ohif/*` to your OHIF server (VUE_APP_OHIF_BASE)
 * - Proxies `/api/kaapana-backend/*` to your Kaapana backend (VUE_APP_KAAPANA_BACKEND_ENDPOINT)
 */

const OHIF_BASE = process.env.VUE_APP_OHIF_BASE || 'http://localhost:3001';
const KAAPANA_BACKEND = process.env.VUE_APP_KAAPANA_BACKEND_ENDPOINT || 'http://localhost:8088/';
// Use a fixed origin for dev proxies to avoid double-prefixing when VUE_APP_* includes path segments
const PROXY_BACKEND_ORIGIN = process.env.PROXY_BACKEND_ORIGIN || 'http://localhost:8088';

module.exports = {
  transpileDependencies: ['vuetify'],
  devServer: {
    port: 5001,
    allowedHosts: "all",
    proxy: {
      '/ohif': {
        target: OHIF_BASE,
        changeOrigin: true,
        ws: true,
        secure: false,
        pathRewrite: { '^/ohif': '' },
      },
      '/api/kaapana-backend': {
        target: PROXY_BACKEND_ORIGIN,
        changeOrigin: true,
      },
      '/kaapana-backend': {
        target: PROXY_BACKEND_ORIGIN,
        changeOrigin: true,
        pathRewrite: { '^/kaapana-backend': '/api/kaapana-backend' },
      },
      '/aii': {
        target: PROXY_BACKEND_ORIGIN,
        changeOrigin: true,
        pathRewrite: { '^/aii': '/aii' }
      },
      '/notifications': {
        target: PROXY_BACKEND_ORIGIN,
        changeOrigin: true,
        ws: true,
      },
    },
  },
};
