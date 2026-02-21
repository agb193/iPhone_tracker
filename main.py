import time
import requests
from playwright.sync_api import sync_playwright
# Importamos la librería de sigilo
from playwright_stealth import stealth_sync

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

def check_all_prices():
    resultados = {}
    with sync_playwright() as p:
        # Usamos un navegador real
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800},
            locale="es-ES"
        )
        page = context.new_page()
        
        # APLICAMOS EL SIGILO A LA PÁGINA
        stealth_sync(page)

        for nombre, url in PRODUCTOS.items():
            try:
                print(f"Consultando {nombre}...")
                page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Pausa para que Cloudflare nos analice y nos deje pasar
                time.sleep(5)

                selector = '[data-qa="productpage-product-price"]'
                page.wait_for_selector(selector, timeout=20000)
                
                price_text = page.inner_text(selector)
                clean_text = "".join(filter(lambda x: x.isdigit() or x == ',', price_text))
                resultados[nombre] = float(clean_text.replace(",", "."))
                print(f"✅ {nombre}: {resultados[nombre]}€")
            
            except Exception as e:
                print(f"❌ Error en {nombre}")
                page.screenshot(path=f"bloqueo_{nombre}.png")
            
            time.sleep(4)

        browser.close()

    if resultados:
        mensaje = "📊 *Precios Actualizados:* \n\n" + "\n".join([f"• {k}: *{v}€*" for k, v in resultados.items()])
        send_to_telegram(mensaje)

if __name__ == "__main__":
    check_all_prices()
