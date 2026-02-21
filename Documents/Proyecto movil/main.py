import os
import time
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8354195368:AAHayQJH_YqbQjd-JdW79bi6gPdwjCRuwwM")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1898416546")


# 1. Configuración de productos
PRODUCTOS = {
    "Titanio Premium": "https://www.backmarket.es/es-es/p/gb/709c1c8e-000e-49ab-8656-4d617d68df69?l=9",
    "Negro Premium": "https://www.backmarket.es/es-es/p/gb/8a2bb3eb-7128-4c9a-83fc-0d52136a1425?l=9",
    "Titanio Excelente": "https://www.backmarket.es/es-es/p/gb/709c1c8e-000e-49ab-8656-4d617d68df69?l=10&offerType=7",
    "Titanio Bueno": "https://www.backmarket.es/es-es/p/gb/709c1c8e-000e-49ab-8656-4d617d68df69?l=11&offerType=7",
    "Negro Bueno": "https://www.backmarket.es/es-es/p/gb/8a2bb3eb-7128-4c9a-83fc-0d52136a1425?l=11&offerType=7"
}

def get_price(page, url, nombre):
    print(f"Consultando {nombre}...")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # Aceptar cookies solo la primera vez si aparece
        try:
            if page.is_visible('button[data-qa="accept-cta"]'):
                page.click('button[data-qa="accept-cta"]', timeout=2000)
        except:
            pass

        # Selector del precio
        selector = '[data-qa="productpage-product-price"]'
        page.wait_for_selector(selector, timeout=10000)
        
        price_text = page.inner_text(selector)
        
        # Limpieza de precio
        clean_text = "".join(filter(lambda x: x.isdigit() or x == ',', price_text))
        return float(clean_text.replace(",", "."))
    except Exception as e:
        print(f"Error en {nombre}: No se pudo obtener el precio.")
        return None

def check_all_prices():
    resultados = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for nombre, url in PRODUCTOS.items():
            precio = get_price(page, url, nombre)
            if precio:
                resultados[nombre] = precio
            
            # Pausa de seguridad para no ser bloqueado (2-4 segundos)
            time.sleep(3)

        browser.close()

    # Mostrar resultados finales
    print("\n--- RESUMEN DE PRECIOS ---")
    mensaje_telegram = "📊 *Precios Actualizados:* \n\n"
    
    for nombre, precio in resultados.items():
        linea = f"✅ {nombre}: {precio}€"
        print(linea)
        mensaje_telegram += linea + "\n"


    send_to_telegram(mensaje_telegram)

def send_to_telegram(mensaje):
    # Limpiamos el token por si acaso hay espacios invisibles
    token = TELEGRAM_TOKEN.strip()
    
    # La base de la URL (fíjate que NO pongo 'bot' aquí si lo vas a poner en el f-string)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID.strip(),
        "text": mensaje
    }

    try:
        response = requests.post(url, data=payload) # Usamos POST que es más seguro
        result = response.json()
        
        if result.get("ok"):
            print("✅ ¡Mensaje enviado!")
        else:
            print(f"❌ Error de Telegram: {result.get('description')}")
            
    except Exception as e:
        print(f"💥 Error de conexión: {e}")

if __name__ == "__main__":
    check_all_prices()