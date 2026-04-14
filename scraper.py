#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InflacionMerida - Scraper Extendido (Mérida XYZ Extra)
Estrategia: navegación de API Mercadona con más de 100 productos categorizados.
Grupos de Índice: Alimentación, Bebidas, Mascotas, Hogar, Higiene.
"""

import sys
import io
import requests
import json
import os
import time
from datetime import datetime
from unicodedata import normalize

# Fuerza UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

API_BASE = "https://tienda.mercadona.es/api"
WAREHOUSE = "vlc1"
LANG      = "es"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Origin": "https://tienda.mercadona.es",
}

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURACION DE PRODUCTOS (100+ KEYWORDS)
# cada entrada: keyword -> (Categoría Display, Grupo Indice)
# ──────────────────────────────────────────────────────────────────────────────

PRODUCT_MAP = {
    # --- ALIMENTACION (Básicos) ---
    "leche entera hacendado":        ("Lácteos", "ALIMENTACION"),
    "leche semidesnatada hacendado": ("Lácteos", "ALIMENTACION"),
    "leche desnatada hacendado":     ("Lácteos", "ALIMENTACION"),
    "yogur natural hacendado":       ("Lácteos", "ALIMENTACION"),
    "mantequilla hacendado":         ("Lácteos", "ALIMENTACION"),
    "queso tierno":                  ("Lácteos", "ALIMENTACION"),
    "queso rallado mozzarella":      ("Lácteos", "ALIMENTACION"),
    "queso lonchas":                 ("Lácteos", "ALIMENTACION"),
    "huevos camperos":               ("Huevos", "ALIMENTACION"),
    "huevos frescos l":              ("Huevos", "ALIMENTACION"),
    # Carnes
    "filetes pechuga de pollo":      ("Carnicería", "ALIMENTACION"),
    "contramuslos de pollo":         ("Carnicería", "ALIMENTACION"),
    "pechuga de pavo":               ("Carnicería", "ALIMENTACION"),
    "carne picada vacuno":           ("Carnicería", "ALIMENTACION"),
    "filetes ternera":               ("Carnicería", "ALIMENTACION"),
    "lomo de cerdo":                 ("Carnicería", "ALIMENTACION"),
    "chorizo":                       ("Carnicería", "ALIMENTACION"),
    "jamon cocido extra":            ("Carnicería", "ALIMENTACION"),
    "jamon serrano":                 ("Carnicería", "ALIMENTACION"),
    # Pescados
    "filetes de merluza":            ("Pescado", "ALIMENTACION"),
    "merluza":                       ("Pescado", "ALIMENTACION"),
    "salmon":                        ("Pescado", "ALIMENTACION"),
    "atun en aceite de girasol":     ("Conservas", "ALIMENTACION"),
    "sardinas en aceite":            ("Conservas", "ALIMENTACION"),
    "mejillones en escabeche":       ("Conservas", "ALIMENTACION"),
    # Frutas y Verduras
    "manzana royal gala":            ("Fruta", "ALIMENTACION"),
    "manzana golden":                ("Fruta", "ALIMENTACION"),
    "pera conferencia":              ("Fruta", "ALIMENTACION"),
    "mandarina":                     ("Fruta", "ALIMENTACION"),
    "platano":                       ("Fruta", "ALIMENTACION"),
    "limon":                         ("Fruta", "ALIMENTACION"),
    "kiwi":                          ("Fruta", "ALIMENTACION"),
    "aguacate":                      ("Fruta", "ALIMENTACION"),
    "tomates rama":                  ("Verdura", "ALIMENTACION"),
    "patatas":                       ("Verdura", "ALIMENTACION"),
    "cebolla":                       ("Verdura", "ALIMENTACION"),
    "zanahoria":                     ("Verdura", "ALIMENTACION"),
    "lechuga iceberg":               ("Verdura", "ALIMENTACION"),
    "calabacin":                     ("Verdura", "ALIMENTACION"),
    "berenjena":                     ("Verdura", "ALIMENTACION"),
    "brocoli":                       ("Verdura", "ALIMENTACION"),
    "pimiento rojo":                 ("Verdura", "ALIMENTACION"),
    "pepino":                        ("Verdura", "ALIMENTACION"),
    "ajos":                          ("Verdura", "ALIMENTACION"),
    # Desayuno / Despensa
    "pan de molde blanco":           ("Panadería", "ALIMENTACION"),
    "pan integral":                  ("Panadería", "ALIMENTACION"),
    "barra de pan":                  ("Panadería", "ALIMENTACION"),
    "aceite oliva virgen extra":     ("Aceites", "ALIMENTACION"),
    "aceite girasol":                ("Aceites", "ALIMENTACION"),
    "arroz redondo":                 ("Cereales", "ALIMENTACION"),
    "espaguetis":                    ("Cereales", "ALIMENTACION"),
    "macarrones":                    ("Cereales", "ALIMENTACION"),
    "lentejas":                      ("Legumbres", "ALIMENTACION"),
    "garbanzos":                     ("Legumbres", "ALIMENTACION"),
    "alubias":                       ("Legumbres", "ALIMENTACION"),
    "azucar blanquilla":             ("Básicos", "ALIMENTACION"),
    "sal fina":                      ("Básicos", "ALIMENTACION"),
    "harina de trigo":               ("Básicos", "ALIMENTACION"),
    "cafe molido":                   ("Despensa", "ALIMENTACION"),
    "cacao soluble":                 ("Despensa", "ALIMENTACION"),
    "galletas maria":                ("Despensa", "ALIMENTACION"),
    "chocolate 70%":                 ("Despensa", "ALIMENTACION"),
    "mermelada":                     ("Despensa", "ALIMENTACION"),
    "miel":                          ("Despensa", "ALIMENTACION"),
    "cereales corn flakes":          ("Despensa", "ALIMENTACION"),
    "nueces peladas":                ("Despensa", "ALIMENTACION"),
    "tomate frito":                  ("Conservas", "ALIMENTACION"),
    "tomate triturado":              ("Conservas", "ALIMENTACION"),
    "caldo de pollo":                ("Conservas", "ALIMENTACION"),
    # Congelados
    "pizza margarita":               ("Congelados", "ALIMENTACION"),
    "varitas de pescado":            ("Congelados", "ALIMENTACION"),
    "guisantes congelados":          ("Congelados", "ALIMENTACION"),

    # --- BEBIDAS / ALCOHOL ---
    "cerveza steinburg clasica":     ("Cerveza", "BEBIDAS"),
    "cerveza cruzcampo":             ("Cerveza", "BEBIDAS"),
    "vino tinto rioja":              ("Vino", "BEBIDAS"),
    "vino tinto ribera":             ("Vino", "BEBIDAS"),
    "vino blanco rueda":             ("Vino", "BEBIDAS"),
    "refresco cola":                 ("Refrescos", "BEBIDAS"),
    "refresco naranja":              ("Refrescos", "BEBIDAS"),
    "refresco limon":                ("Refrescos", "BEBIDAS"),
    "agua mineral grande":           ("Agua", "BEBIDAS"),
    "zumo naranja exprimido":        ("Zumos", "BEBIDAS"),

    # --- MASCOTAS ---
    "comida perro adulto compy":     ("Perro", "MASCOTAS"),
    "pienso perro":                  ("Perro", "MASCOTAS"),
    "comida gato adulto compy":      ("Gato", "MASCOTAS"),
    "pienso gato":                   ("Gato", "MASCOTAS"),
    "arena para gatos":              ("Gato", "MASCOTAS"),
    "alimento humedo perro":         ("Mascotas", "MASCOTAS"),
    "alimento humedo gato":          ("Mascotas", "MASCOTAS"),

    # --- HOGAR / LIMPIEZA ---
    "detergente ropa liquido":       ("Limpieza", "HOGAR"),
    "suavizante ropa":               ("Limpieza", "HOGAR"),
    "lavavajillas mano":             ("Limpieza", "HOGAR"),
    "pastillas lavavajillas":        ("Limpieza", "HOGAR"),
    "limpiador multiusos":           ("Limpieza", "HOGAR"),
    "lejia":                         ("Limpieza", "HOGAR"),
    "limpiasuelos":                  ("Limpieza", "HOGAR"),
    "papel higienico":               ("Papel", "HOGAR"),
    "papel de cocina":               ("Papel", "HOGAR"),
    "bolsas de basura":              ("Hogar", "HOGAR"),

    # --- HIGIENE ---
    "champu":                        ("Cuidado", "HIGIENE"),
    "gel de baño":                   ("Cuidado", "HIGIENE"),
    "pasta de dientes":              ("Cuidado", "HIGIENE"),
    "desodorante":                   ("Cuidado", "HIGIENE"),
    "jabon de manos":                ("Cuidado", "HIGIENE"),
    "compresas":                     ("Cuidado", "HIGIENE"),
    "tampones":                      ("Cuidado", "HIGIENE"),
}

DATA_DIR       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
HISTORICO_PATH = os.path.join(DATA_DIR, "historico_completo.json")

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def nfkd(s: str) -> str:
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

def match_product(nombre_norm: str) -> tuple[str, str, str] | None:
    """Devuelve (keyword, categoria_desc, grupo_indice) si encaja."""
    for kw, (cat, grupo) in PRODUCT_MAP.items():
        if kw in nombre_norm:
            return kw, cat, grupo
    return None

# ──────────────────────────────────────────────────────────────────────────────
# MAIN SCRAPER
# ──────────────────────────────────────────────────────────────────────────────

def scrape_full() -> list[dict]:
    print("  >> Descargando árbol de categorías de Mercadona...")
    raices = get_json(f"{API_BASE}/categories/", {"lang": LANG, "wh": WAREHOUSE})
    if not raices or "results" not in raices:
        return []

    results = raices.get("results", [])
    encontrados: dict[str, dict] = {}  # key = keyword

    for raiz in results:
        raiz_name = raiz.get("name", "?")
        print(f"  -- Procesando raiz: {raiz_name}")
        
        for subcat in raiz.get("categories", []):
            subcat_id = str(subcat.get("id", ""))
            
            # Rate limit preventivo
            time.sleep(0.4)
            data = get_json(f"{API_BASE}/categories/{subcat_id}/", {"lang": LANG, "wh": WAREHOUSE})
            if not data: continue
            
            # Recopilar todos los productos de esta subcat (y sus hijos)
            productos_sub = []
            for c in data.get("categories", [data]):
                productos_sub.extend(c.get("products", []))
            
            for prod in productos_sub:
                nombre   = prod.get("display_name", "")
                nombre_n = nfkd(nombre)
                match    = match_product(nombre_n)
                
                if match:
                    kw, display_cat, grupo = match
                    precio = extraer_precio(prod)
                    if precio is None: continue
                    
                    # Guardamos el primero que encontremos para esa keyword
                    if kw not in encontrados:
                        pi = prod.get("price_instructions", {})
                        encontrados[kw] = {
                            "id":               str(prod.get("id", "")),
                            "nombre":           nombre,
                            "precio":           precio,
                            "precio_por_unidad": pi.get("reference_price"),
                            "unidad_medida":    pi.get("reference_format"),
                            "categoria":        display_cat,
                            "grupo":            grupo,
                            "thumbnail":        prod.get("thumbnail"),
                            "keyword":          kw,
                        }
                        print(f"    [OK] {nombre[:40]:40s} = {precio:5.2f}€ [{grupo}]")
        
        # Si ya hemos encontrado todo, paramos (ahorramos peticiones)
        if len(encontrados) >= len(PRODUCT_MAP):
            break

    final = list(encontrados.values())
    print(f"\n  >> Fin del scrape. Encontrados {len(final)}/{len(PRODUCT_MAP)} productos.")
    return final

def save_data(productos: list[dict], fecha: str):
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Snapshot diario
    with open(os.path.join(DATA_DIR, f"prices_{fecha}.json"), "w", encoding="utf-8") as f:
        json.dump({"fecha": fecha, "productos": productos}, f, ensure_ascii=False, indent=2)
    
    # Historico completo
    if os.path.exists(HISTORICO_PATH):
        with open(HISTORICO_PATH, "r", encoding="utf-8") as f:
            hist = json.load(f)
    else:
        hist = {"fechas": [], "datos": {}}
    
    hist["datos"][fecha] = productos
    if fecha not in hist["fechas"]:
        hist["fechas"].append(fecha)
        hist["fechas"].sort()
    
    with open(HISTORICO_PATH, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    hoy = datetime.now().strftime("%Y-%m-%d")
    print(f"\nINFLACION MERIDA - SCRAPER COMPLETO [{hoy}]")
    print("=" * 60)
    
    productos = scrape_full()
    if productos:
        save_data(productos, hoy)
        print(f"\nÉXITO: {len(productos)} productos indexados.")
    else:
        print("\nERROR: No se pudieron obtener datos.")
        sys.exit(1)
