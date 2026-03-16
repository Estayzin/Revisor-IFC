# Reporte IFC por Especialidad

Herramienta web para verificar y contar entidades IFC por especialidad (MOP Chile / PlanBIM).

---

## ⚠ Paso obligatorio antes del primer deploy

El visor 3D necesita dos archivos que **debes descargar manualmente** y subir al repositorio.

### 1. Descarga estos archivos (clic derecho → Guardar como)

| Guardar como... | URL |
|---|---|
| `js/web-ifc-api.js` | https://unpkg.com/web-ifc@0.0.51/web-ifc-api.js |
| `wasm/web-ifc.wasm` | https://unpkg.com/web-ifc@0.0.51/web-ifc.wasm |

> ⚠ **Usa unpkg.com**, no jsDelivr — jsDelivr sirve una versión ESM incompatible.

### 2. Estructura del repositorio después de descargar

```
tu-repo/
├── index.html
├── js/
│   └── web-ifc-api.js     ← ~2 MB
└── wasm/
    └── web-ifc.wasm       ← ~5 MB
```

### 3. Commit y push de AMBOS archivos

```bash
git add js/web-ifc-api.js wasm/web-ifc.wasm
git commit -m "add web-ifc files for 3D viewer"
git push
```

---

## Deploy en GitHub Pages

1. Settings → Pages → Source: **main / root**
2. URL: `https://<usuario>.github.io/<repo>/`
3. Esperar 1-2 minutos después de cada push

---

## Uso

1. Arrastra o selecciona un archivo `.ifc`
2. Elige especialidad en el dropdown
3. Marca las entidades a revisar
4. **Generar reporte** → toggle **◈ 3D** o **⬧ Ambos** para el visor

---

## Pruebas locales (requiere servidor HTTP)

```bash
python -m http.server 8080
# Abrir: http://localhost:8080
```

---

Creado por Carlos Estay Ruggieri
