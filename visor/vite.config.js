import { resolve } from 'path';

export default {
  // base vacío = rutas relativas → funciona tanto en servidor local como en Cloudflare Pages
  base: '',
  build: {
    outDir: resolve(__dirname, 'dist'),   // → visor/dist/
    target: 'esnext',
    chunkSizeWarningLimit: 10000,
    rollupOptions: {
      input: resolve(__dirname, 'voxelbim.html'),
    },
  }
};
