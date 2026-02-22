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
    requests.post(url, data=payload)

def get_price(page, url, nombre):
    try:
        print(f"Consultando {nombre}...")
        # Vamos a la URL y esperamos a que la red se relaje
        page.goto(url, wait_until="networkidle", timeout=60000)
        
        # Intentar cerrar cookies rápidamente
        try:
            page.wait_for_selector('button[data-qa="accept-cta"]', timeout=4000)
            page.click('button[data-qa="accept-cta"]')
        except:
            pass

        # El selector del precio
        selector = '[data-qa="productpage-product-price"]'
        page.wait_for_selector(selector, timeout=15000)
        
        price_text = page.inner_text(selector)
        clean_text = "".join(filter(lambda x: x.isdigit() or x == ',', price_text))
        precio = float(clean_text.replace(",", "."))
        print(f"✅ {nombre}: {precio}€")
        return precio
    except:
        print(f"❌ Error en {nombre}")
        return None

def check_all_prices():
    resultados = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="es-ES",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()

        # --- TRUCO DE SIGILO MANUAL ---
        # Esto elimina la marca de "bot" que busca Cloudflare
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Paso 1: "Calentar" la web entrando a la home
        try:
            page.goto("https://www.backmarket.es", wait_until="domcontentloaded", timeout=20000)
            time.sleep(2)
        except:
            pass

        # Paso 2: Consultar productos
        for nombre, url in PRODUCTOS.items():
            precio = get_price(page, url, nombre)
            if precio:
                resultados[nombre] = precio
            else:
                # Si falla (especialmente el primero), esperamos y reintentamos UNA vez
                print(f"Reintentando {nombre} en 5 segundos...")
                time.sleep(5)
                precio = get_price(page, url, nombre)
                if precio: resultados[nombre] = precio
            
            time.sleep(4) # Pausa entre productos

        browser.close()
        
    contenido = False
    if resultados:
        mensaje = "📊 *Precios Menores de 820:* \n\n"
        for k, v in resultados.items():
            if v<=820:
                mensaje += f"• {k}: *{v}€*\n"
                contenido = True
         
        
        if contenido:
            send_to_telegram(mensaje) 
        else:
            print("Precios altos lambebicho.")

if __name__ == "__main__":
    check_all_prices()
