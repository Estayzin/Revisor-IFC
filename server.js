const http = require('http');
const fs   = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname);   // relativo al server.js, funciona en cualquier PC
const PORT = 3000;

const MIME = {
  html: 'text/html; charset=utf-8',
  js:   'application/javascript',
  css:  'text/css',
  png:  'image/png',
  jpg:  'image/jpeg',
  jpeg: 'image/jpeg',
  svg:  'image/svg+xml',
  json: 'application/json',
  ico:  'image/x-icon',
  wasm: 'application/wasm',
  mjs:  'application/javascript',
  txt:  'text/plain',
};

http.createServer((req, res) => {
  const url  = req.url.split('?')[0];
  const file = url === '/' ? '/index.html' : url;
  const full = path.join(ROOT, file);

  // Seguridad: no salir del ROOT
  if (!full.startsWith(path.resolve(ROOT))) {
    res.writeHead(403); res.end('Forbidden'); return;
  }

  fs.readFile(full, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('404 Not Found: ' + file);
      return;
    }
    const ext = full.split('.').pop().toLowerCase();

    // Headers COOP/COEP necesarios para SharedArrayBuffer (web-ifc / WASM)
    const isAutodesk = file.startsWith('/app/autodesk') || file.startsWith('/app/viewer');
    res.writeHead(200, {
      'Content-Type': MIME[ext] || 'application/octet-stream',
      'Access-Control-Allow-Origin': '*',
      'Cross-Origin-Opener-Policy': 'same-origin',
      'Cross-Origin-Embedder-Policy': isAutodesk ? 'require-corp' : 'credentialless',
      'Cross-Origin-Resource-Policy': 'cross-origin',
    });
    res.end(data);
  });
}).listen(PORT, () => {
  console.log('VoxelBIM Server listo en http://localhost:' + PORT);
});
