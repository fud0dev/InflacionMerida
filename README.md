# 📊 InflaciónMérida

> Seguimiento automático y gratuito de los precios de la cesta básica en Mérida, usando datos reales de la tienda online de Mercadona. Se actualiza cada mañana de forma autónoma y muestra la evolución histórica de precios en una web pública.

🔗 **Demo en vivo:** [fud0dev.github.io/InflacionMerida](https://fud0dev.github.io/InflacionMerida/)  
🏠 **Hub principal:** [meridaxyz.wordpress.com](https://meridaxyz.wordpress.com/)

---

## ¿Qué hace este proyecto?

**InflaciónMérida** es una herramienta de monitorización económica local que:

1. **Extrae precios** de ~40 productos básicos (leche, pan, aceite, huevos, carne, frutas, verduras, pasta, legumbres...) directamente de la API pública de la tienda online de Mercadona.
2. **Guarda un histórico** de esos precios día a día, sin sobrescribir los datos anteriores.
3. **Publica una web pública** donde cualquier ciudadano puede consultar la evolución de precios, buscar productos y ver cuánto cuesta la cesta básica semana tras semana.

Todo funciona de forma **completamente automática y gratuita**, sin servidores propios ni bases de datos.

---

## ¿Cómo funciona por dentro?

El proyecto tiene tres partes:

### 🕷️ 1. El Scraper (`scraper.py`)

Un script en Python que:
- Navega el árbol de categorías de la API de Mercadona (`tienda.mercadona.es/api/categories/`)
- Busca productos que coincidan con una lista de ~40 palabras clave de la cesta básica
- Guarda los resultados en dos archivos:
  - `data/prices_YYYY-MM-DD.json` → snapshot del día
  - `data/historico_completo.json` → histórico acumulado (leído por la web)
- Respeta un tiempo de espera entre peticiones para no saturar los servidores

### ⚙️ 2. La Automatización (`.github/workflows/scrape.yml`)

Un workflow de GitHub Actions que:
- Se ejecuta **cada día a las 08:00 UTC** (cron automático)
- Instala Python y las dependencias
- Lanza el scraper
- Hace `git commit + push` automático con los nuevos datos

No requiere ninguna intervención manual una vez configurado.

### 🌐 3. La Web (`index.html`)

Una Single Page Application (SPA) en HTML, CSS y JavaScript puro que:
- Lee el archivo `historico_completo.json` directamente desde GitHub Pages
- Muestra un **índice "Cesta Básica Mérida"** con el total diario y la variación respecto al día anterior
- Incluye un **buscador en tiempo real** de productos
- Genera **gráficas de evolución histórica** de precio por producto (Chart.js)
- Funciona sin backend, sin base de datos y sin coste de infraestructura

---

## Estructura del proyecto

```
InflacionMerida/
├── .github/
│   └── workflows/
│       └── scrape.yml          # Automatización diaria (GitHub Actions)
├── data/
│   ├── prices_2026-04-15.json  # Snapshot diario (uno por ejecución)
│   └── historico_completo.json # Histórico acumulado (leído por la web)
├── scraper.py                  # Script Python de extracción de precios
├── requirements.txt            # Dependencias Python (solo "requests")
├── index.html                  # Web pública (GitHub Pages)
└── README.md                   # Este archivo
```

---

## Cómo usar este proyecto

### Requisitos previos

- Python 3.10 o superior
- Cuenta en GitHub
- Git instalado en tu ordenador

### Instalación local

```bash
# Clona el repositorio
git clone https://github.com/fud0dev/InflacionMerida.git
cd InflacionMerida

# Instala las dependencias
pip install -r requirements.txt

# Ejecuta el scraper manualmente
python scraper.py

# Lanza un servidor local para ver la web
python -m http.server 8080
# Abre: http://localhost:8080
```

### Despliegue en GitHub Pages

1. Haz fork o crea tu propio repositorio con estos archivos
2. Ve a **Settings → Pages → Branch: main / (root)** → Guardar
3. Activa permisos de escritura: **Settings → Actions → General → Read and write permissions**
4. Lanza el workflow manualmente la primera vez: **Actions → Scrape Mercadona Prices → Run workflow**
5. A partir de ese momento, se actualiza solo cada día a las 08:00 UTC

---

## Tecnologías utilizadas

| Tecnología | Uso |
|-----------|-----|
| Python + `requests` | Scraper de la API de Mercadona |
| GitHub Actions | Automatización del cron diario |
| GitHub Pages | Hosting gratuito de la web |
| Chart.js | Gráficas de evolución de precios |
| HTML + CSS + JS vanilla | Frontend sin frameworks ni backend |

---

## Productos monitorizados

La cesta básica incluye productos de estas categorías:

| Categoría | Ejemplos |
|-----------|---------|
| Lácteos | Leche entera, semidesnatada, desnatada, yogur, mantequilla, queso |
| Huevos | Huevos camperos |
| Carne | Pechuga de pollo, contramuslos, lomo de cerdo |
| Pescado | Merluza, atún, sardinas, mejillones |
| Frutas | Manzana, pera, mandarina |
| Verduras | Tomate, patatas, cebolla, zanahoria, lechuga, judías verdes |
| Pan | Pan de molde, pan integral |
| Aceites | Aceite de oliva virgen extra, aceite de girasol |
| Cereales | Arroz, macarrones, espaguetis, lentejas, garbanzos, alubias |
| Conservas | Tomate frito, tomate triturado |
| Básicos | Azúcar, sal, harina de trigo |
| Agua | Agua mineral |

---

## Formato de los datos

### `data/prices_YYYY-MM-DD.json`
```json
{
  "fecha": "2026-04-15",
  "total_productos": 39,
  "productos": [
    {
      "id": "12345",
      "nombre": "Leche entera Hacendado",
      "precio": 5.76,
      "precio_por_unidad": "1.44",
      "unidad_medida": "l",
      "categoria": "Lacteos",
      "thumbnail": "https://..."
    }
  ]
}
```

### `data/historico_completo.json`
```json
{
  "fechas": ["2026-04-15", "2026-04-16"],
  "datos": {
    "2026-04-15": [ ... ],
    "2026-04-16": [ ... ]
  }
}
```

---

## ⚠️ Disclaimer — Aviso Legal y Educativo

> **Este proyecto ha sido creado con fines exclusivamente educativos y de investigación personal.**

- Los datos se obtienen de la API pública de la tienda online de Mercadona (`tienda.mercadona.es`). Esta API es accesible públicamente desde cualquier navegador y no requiere autenticación.
- El scraper implementa pausas entre peticiones (`time.sleep`) para no generar carga excesiva sobre los servidores.
- **Este proyecto no está afiliado, patrocinado ni respaldado por Mercadona S.A.** en ninguna forma.
- Los precios mostrados pueden variar según la zona geográfica, disponibilidad de stock o promociones activas.
- El autor no se responsabiliza del uso que terceros hagan de este código.
- Si eres representante de Mercadona y tienes alguna objeción, puedes contactar a través de [GitHub](https://github.com/fud0dev).

**Úsalo para aprender, no para sobrecargar servidores ajenos.**

---

## Autor

Creado por **[@fud0dev](https://github.com/fud0dev)** como parte del ecosistema [**Mérida XYZ**](https://meridaxyz.wordpress.com/) — un portal de datos abiertos para la ciudad de Mérida (Badajoz, España).

---

*Si este proyecto te ha resultado útil, dale una ⭐ en GitHub.*
