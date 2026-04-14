# 📊 InflaciónMérida

> Seguimiento automático de precios de la cesta básica en Mérida usando datos reales de Mercadona. Actualización diaria mediante GitHub Actions y visualización en GitHub Pages.

🔗 **Demo en vivo:** `https://TU-USUARIO.github.io/InflacionMerida/`

---

## ✨ Características

- 🕷️ **Scraper Python** que extrae ~50 productos básicos de la API de Mercadona
- 📅 **Actualización diaria automática** a las 08:00 UTC vía GitHub Actions
- 💾 **Histórico acumulativo** sin sobreescribir datos anteriores
- 📈 **Gráficas Chart.js** de evolución histórica por producto
- 🔍 **Buscador en tiempo real** de productos
- 🧺 **Índice "Cesta Básica Mérida"** con total semanal y variaciones
- 📱 **100% responsive** sin dependencias de backend

---

## 📁 Estructura del proyecto

```
InflacionMerida/
├── .github/
│   └── workflows/
│       └── scrape.yml          # GitHub Actions: cron diario
├── data/
│   ├── prices_2025-04-15.json  # JSON diario (uno por ejecución)
│   └── historico_completo.json # Histórico acumulado (leído por el frontend)
├── scraper.py                  # Scraper Python
├── requirements.txt            # Dependencias Python
├── index.html                  # SPA Frontend (GitHub Pages)
└── README.md
```

---

## 🚀 Despliegue en GitHub

### 1. Crear el repositorio

```bash
git init
git add .
git commit -m "🎉 Initial commit: InflacionMerida"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/InflacionMerida.git
git push -u origin main
```

### 2. Activar GitHub Pages

1. Ve a **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / `/ (root)`
4. Guarda y espera 1-2 minutos

### 3. Activar el workflow

El workflow `.github/workflows/scrape.yml` se activa automáticamente:
- **Cada día a las 08:00 UTC** (cron)
- **Manualmente** desde la pestaña *Actions → Run workflow*

> ⚠️ **Primera ejecución:** Ve a *Actions* → selecciona el workflow → haz click en **"Run workflow"** para generar el primer JSON de datos.

---

## 🏃 Ejecución local

```bash
# Instala dependencias
pip install -r requirements.txt

# Ejecuta el scraper
python scraper.py

# Lanza un servidor local para probar el frontend
python -m http.server 8080
# Abre: http://localhost:8080
```

---

## 📦 Datos generados

### `data/prices_YYYY-MM-DD.json`
```json
{
  "fecha": "2025-04-15",
  "total_productos": 48,
  "productos": [
    {
      "id": "12345",
      "nombre": "Leche entera Hacendado",
      "precio": 0.99,
      "precio_por_unidad": "0.99",
      "unidad_medida": "l",
      "categoria": "Leche y bebidas vegetales",
      "thumbnail": "https://..."
    }
  ]
}
```

### `data/historico_completo.json`
```json
{
  "fechas": ["2025-04-15", "2025-04-16"],
  "datos": {
    "2025-04-15": [ /* array de productos */ ],
    "2025-04-16": [ /* array de productos */ ]
  }
}
```

---

## ⚙️ Configuración del workflow

El archivo `.github/workflows/scrape.yml` no requiere configuración extra. Usa el token `GITHUB_TOKEN` automático de GitHub Actions para hacer el commit. Solo asegúrate de que el repositorio tiene permisos de escritura habilitados:

**Settings → Actions → General → Workflow permissions → Read and write permissions** ✅

---

## 🛒 Productos monitorizados

| Categoría | Productos |
|-----------|-----------|
| Lácteos | Leche entera/semi/desnatada, yogur, mantequilla, queso |
| Huevos | Huevos camperos/granja |
| Carne | Pechuga de pollo, muslos, carne picada, lomo |
| Pescado | Merluza, atún en aceite, sardinas, mejillones |
| Frutas | Manzanas, naranjas, plátanos, peras, mandarinas |
| Verduras | Tomates, patatas, cebollas, zanahorias, lechuga |
| Pan | Pan de molde, pan integral |
| Aceites | Aceite de oliva virgen extra, aceite de girasol |
| Pasta y arroz | Arroz, macarrones, espaguetis, fideos |
| Legumbres | Lentejas, garbanzos, alubias |
| Conservas | Tomate frito, tomate triturado |
| Básicos | Azúcar, sal, harina, agua mineral |

---

## 📜 Disclaimer

Este proyecto es **independiente** y no está afiliado a Mercadona S.A. Los datos se obtienen de la API pública de su tienda online. El scraper respeta los tiempos de respuesta del servidor.

---

*Creado como parte del proyecto [Mérida Digital Hub](https://github.com/TU-USUARIO)*
