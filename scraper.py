#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InflacionMerida - Scraper de cesta basica via API REST de Mercadona.
Estrategia: navegar el arbol de categorias raiz y filtrar productos por
palabras clave. Guarda:
  - data/prices_YYYY-MM-DD.json  (snapshot diario)
  - data/historico_completo.json (historico acumulado, leido por el frontend)
"""

import sys
import io
import requests
import json
import os
import time
from datetime import datetime
from unicodedata import normalize

# Fuerza UTF-8 en consola Windows para evitar UnicodeEncodeError
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURACION
# ──────────────────────────────────────────────────────────────────────────────

API_BASE = "https://tienda.mercadona.es/api"
# Warehouse: vlc1=Valencia/peninsula. Mercadona usa el mismo catalogo para toda
# la peninsula, por lo que los precios son equivalentes a los de Merida.
WAREHOUSE = "vlc1"
LANG      = "es"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-ES,es;q=0.9",
    "Origin": "https://tienda.mercadona.es",
    "Referer": "https://tienda.mercadona.es/",
}

# Palabras clave normalizadas (sin tildes, minusculas) que identifican
# los productos de la cesta basica. Cuanto mas especifica sea la keyword,
# menos falsos positivos.
# Cada entrada: keyword (sin tildes, minusculas) -> categoria display
# IMPORTANTE: keywords largas primero para evitar falsos positivos en subcadenas
KEYWORDS = {
    # --- Lacteos ---
    "leche entera hacendado":        "Lacteos",
    "leche semidesnatada hacendado": "Lacteos",
    "leche desnatada hacendado":     "Lacteos",
    "yogur natural hacendado":       "Lacteos",
    "mantequilla hacendado":         "Lacteos",
    "queso tierno":                  "Lacteos",
    # --- Huevos ---
    "huevos camperos":               "Huevos",
    "huevos de gallinas camperas":   "Huevos",
    "huevos frescos":                "Huevos",
    # --- Carne ---
    "filetes pechuga de pollo":      "Carne y aves",
    "contramuslos de pollo":         "Carne y aves",
    "carne picada mixta":            "Carne y aves",
    "filetes lomo de cerdo":         "Carne y aves",
    # --- Pescado ---
    "filetes de merluza":            "Pescado",
    "merluza":                       "Pescado",
    "atun en aceite de girasol hacendado": "Pescado",
    "sardinas en aceite de oliva hacendado": "Pescado",
    "mejillones en escabeche hacendado": "Pescado",
    # --- Frutas ---
    "manzana royal gala":            "Frutas",
    "manzana golden":                "Frutas",
    "pera conferencia":              "Frutas",
    "mandarina clementina":          "Frutas",
    "mandarina": "Frutas",
    # --- Verduras ---
    "tomate rama": "Verduras",
    "tomates rama": "Verduras",
    "patatas hacendado":             "Verduras",
    "cebolla": "Verduras",
    "zanahoria": "Verduras",
    "lechuga iceberg": "Verduras",
    "judias verdes redondas hacendado": "Verduras",
    "pimiento rojo": "Verduras",
    # --- Pan ---
    "pan de molde blanco":           "Pan",
    "pan integral trigo":            "Pan",
    # --- Aceites ---
    "aceite de oliva virgen extra hacendado": "Aceites",
    "aceite de girasol refinado":    "Aceites",
    # --- Cereales y legumbres ---
    "arroz redondo hacendado":       "Cereales",
    "espaguetis hacendado":          "Cereales",
    "lentejas hacendado":            "Cereales",
    "garbanzos cocidos hacendado":   "Cereales",
    "alubias cocidas hacendado":     "Cereales",
    # --- Conservas ---
    "tomate frito hacendado":        "Conservas",
    "tomate triturado hacendado":    "Conservas",
    # --- Basicos ---
    "azucar blanquilla hacendado":   "Basicos",
    "sal fina hacendado":            "Basicos",
    "harina de trigo hacendado":     "Basicos",
    # --- Agua ---
    "agua mineral grande bronchales": "Agua",
    "agua mineral hacendado":        "Agua",
}

DATA_DIR       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
HISTORICO_PATH = os.path.join(DATA_DIR, "historico_completo.json")

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def nfkd(s: str) -> str:
    """Normaliza a ASCII-safe minusculas (sin tildes ni caracteres especiales)."""
    return normalize("NFKD", s.lower()).encode("ascii", "ignore").decode("ascii")


def get_json(url: str, params: dict = None) -> dict | None:
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"    [!] HTTP error {url}: {e}")
        return None


def extraer_precio(product: dict) -> float | None:
    try:
        pi = product.get("price_instructions", {})
        v  = pi.get("unit_price") or pi.get("bulk_price")
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def keyword_match(nombre_norm: str) -> tuple[str, str] | None:
    """Devuelve (keyword, categoria) si el nombre encaja con alguna keyword."""
    for kw, cat in KEYWORDS.items():
        if kw in nombre_norm:
            return kw, cat
    return None


# ──────────────────────────────────────────────────────────────────────────────
# LOGICA SCRAPER
# ──────────────────────────────────────────────────────────────────────────────

def obtener_arbol_categorias() -> list[dict]:
    """Descarga el arbol raiz de categorias de Mercadona."""
    data = get_json(f"{API_BASE}/categories/", {"lang": LANG, "wh": WAREHOUSE})
    if not data:
        return []
    # La API devuelve { results: [ { id, name, categories: [...] } ] }
    return data.get("results", [])


def obtener_productos_subcategoria(subcat_id: str) -> list[dict]:
    """Devuelve todos los productos de una subcategoria concreta."""
    data = get_json(f"{API_BASE}/categories/{subcat_id}/", {"lang": LANG, "wh": WAREHOUSE})
    if not data:
        return []
    productos = []
    # La subcategoria puede tener directamente 'products' o sub-subcategorias
    for cat in data.get("categories", [data]):
        productos.extend(cat.get("products", []))
    return productos


def scrape_precios() -> list[dict]:
    """
    Recorre todas las categorias raiz → subcategorias → productos y
    filtra los que coinciden con las keywords de la cesta basica.
    """
    print("  >> Descargando arbol de categorias...")
    raices = obtener_arbol_categorias()
    if not raices:
        print("  [!] No se pudo obtener el arbol. Abortando.")
        return []

    print(f"  >> {len(raices)} categorias raiz encontradas.")

    encontrados: dict[str, dict] = {}  # key = keyword, val = producto (1 por keyword)

    for raiz in raices:
        raiz_nombre = raiz.get("name", "?")
        subcategorias = raiz.get("categories", [])

        for subcat in subcategorias:
            subcat_id   = str(subcat.get("id", ""))
            subcat_name = subcat.get("name", "?")

            productos_raw = obtener_productos_subcategoria(subcat_id)
            time.sleep(0.5)  # Rate limiting

            for prod in productos_raw:
                nombre     = prod.get("display_name", "")
                nombre_n   = nfkd(nombre)
                match      = keyword_match(nombre_n)
                if not match:
                    continue

                kw, cat_display = match
                precio = extraer_precio(prod)
                if precio is None:
                    continue

                # Solo guardamos el primer producto que encaje con cada keyword
                if kw not in encontrados:
                    pi = prod.get("price_instructions", {})
                    encontrados[kw] = {
                        "id":               str(prod.get("id", "")),
                        "nombre":           nombre,
                        "precio":           precio,
                        "precio_por_unidad": pi.get("reference_price"),
                        "unidad_medida":    pi.get("reference_format"),
                        "categoria":        cat_display,
                        "categoria_api":    f"{raiz_nombre} > {subcat_name}",
                        "thumbnail":        prod.get("thumbnail"),
                        "keyword":          kw,
                    }
                    print(f"    [OK] {nombre[:45]:45s} = {precio:.2f} EUR  [{cat_display}]")

            # Si ya tenemos todos los productos, no hace falta seguir
            if len(encontrados) >= len(KEYWORDS):
                break

        if len(encontrados) >= len(KEYWORDS):
            break

    resultado = list(encontrados.values())
    resultado.sort(key=lambda x: x["categoria"])
    print(f"\n  >> {len(resultado)}/{len(KEYWORDS)} productos de la cesta encontrados.")
    return resultado


# ──────────────────────────────────────────────────────────────────────────────
# GUARDADO DE DATOS
# ──────────────────────────────────────────────────────────────────────────────

def guardar_diario(productos: list[dict], fecha: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    ruta = os.path.join(DATA_DIR, f"prices_{fecha}.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump({
            "fecha": fecha,
            "total_productos": len(productos),
            "productos": productos,
        }, f, ensure_ascii=False, indent=2)
    print(f"  >> JSON diario guardado: prices_{fecha}.json")
    return ruta


def actualizar_historico(productos: list[dict], fecha: str):
    """Agrega (o actualiza) la entrada de fecha en historico_completo.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(HISTORICO_PATH):
        with open(HISTORICO_PATH, "r", encoding="utf-8") as f:
            historico = json.load(f)
    else:
        historico = {"fechas": [], "datos": {}}

    historico["datos"][fecha] = productos
    if fecha not in historico["fechas"]:
        historico["fechas"].append(fecha)
        historico["fechas"].sort()

    with open(HISTORICO_PATH, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)
    print(f"  >> Historico: {len(historico['fechas'])} fechas registradas.")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    hoy = datetime.now().strftime("%Y-%m-%d")
    borde = "=" * 58

    print(f"\n{borde}")
    print(f"  InflacionMerida - Scraper  [{hoy}]")
    print(f"{borde}\n")

    print("[1/3] Extrayendo precios vía API Mercadona...")
    productos = scrape_precios()

    if not productos:
        print("\n[!] No se obtuvieron productos. Abortando.")
        sys.exit(1)

    print("\n[2/3] Guardando JSON diario...")
    guardar_diario(productos, hoy)

    print("\n[3/3] Actualizando historico completo...")
    actualizar_historico(productos, hoy)

    print(f"\n{borde}")
    print(f"  OK - {len(productos)} productos guardados correctamente.")
    print(f"{borde}\n")
