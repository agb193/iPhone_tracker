import requests
import os

# 1. Asegúrate de que aquí NO haya espacios ni la palabra "bot" delante
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8354195368:AAHayQJH_YqbQjd-JdW79bi6gPdwjCRuwwM")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1898416546")

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

send_to_telegram("Prueba definitiva 🚀")