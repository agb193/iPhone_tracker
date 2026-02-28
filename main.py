import time
import requests
from playwright.sync_api import sync_playwright

# --- TUS DATOS ---
TOKEN = "8354195368:AAHayQJH_YqbQjd-JdW79bi6gPdwjCRuwwM"
CHAT_ID = "1898416546"

PRODUCTOS = {
    "Titanio Premium": "https://www.backmarket.es/es-es/p/gb/709c1c8e-000e-49ab-8656-4d617d68df69?l=9",
    "Negro Premium": "https://www.backmarket.es/es-es/p/gb/8a2bb3eb-7128-4c9a-83fc-0d52136a1425?l=9",
    "Titanio Excelente": "https://www.backmarket.es/es-es/p/gb/709c1c8e-000e-49ab-8656-4d617d68df69?l=10&offerType=7",
    "Titanio Bueno": "https://www.backmarket.es/es-es/p/gb/709c1c8e-000e-49ab-8656-4d617d68df69?l=11&offerType=7",
    "Negro Bueno": "https://www.backmarket.es/es-es/p/gb/8a2bb3eb-7128-4c9a-83fc-0d52136a1425?l=11&offerType=7"
}

def send_to_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN.strip()}/sendMessage"
    payload = {"chat_id": CHAT_ID.strip(), "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

def get_price(page, url, nombre):
    try:
        print(f"Consultando {nombre}...")
        # Cambiamos networkidle por commit o domcontentloaded para evitar esperas infinitas
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # Espera un poco para que carguen los scripts de precio
        time.sleep(3)

        # Intentar cerrar cookies
        try:
            page.click('button[data-qa="accept-cta"]', timeout=3000)
        except:
            pass

        # Selector del precio mejorado
        selector = '[data-qa="productpage-product-price"]'
        page.wait_for_selector(selector, timeout=10000)
        
        price_text = page.inner_text(selector)
        # Limpieza de texto más robusta
        clean_text = "".join(c for c in price_text if c.isdigit() or c == ',')
        precio = float(clean_text.replace(",", "."))
        
        print(f"✅ {nombre}: {precio}€")
        return precio

    except Exception as e:
        print(f"❌ Error en {nombre}: {str(e)}")
        # ESTO ES LO QUE NECESITA GITHUB ACTIONS:
        page.screenshot(path=f"error_{nombre.replace(' ', '_')}.png")
        return None

def check_all_prices():
    resultados = {}
    with sync_playwright() as p:
        # Usamos canales de chrome reales si es posible
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()

        # Stealth básico
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        for nombre, url in PRODUCTOS.items():
            precio = get_price(page, url, nombre)
            if precio:
                resultados[nombre] = precio
            else:
                print(f"Reintentando {nombre} en 5 segundos...")
                time.sleep(5)
                precio = get_price(page, url, nombre)
                if precio: resultados[nombre] = precio
            
            time.sleep(2)

        browser.close()
        
    if resultados:
        mensaje = "📊 *Precios detectados:* \n\n"
        contenido = False
        for k, v in resultados.items():
            if v <= 820:
                mensaje += f"• {k}: *{v}€*\n"
                contenido = True
        
        if contenido:
            send_to_telegram(mensaje)
        else:
            print("No hay ofertas por debajo de 820€.")

if __name__ == "__main__":
    check_all_prices()
