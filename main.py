from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os

# Variables de entorno para OpenAI
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 🔹 Se recomienda usar variables de entorno

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

app = FastAPI()

# Configuración de CORS para permitir peticiones del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Cámbialo por tu dominio real si es necesario
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diccionario para almacenar el historial de conversación por usuario
chat_histories = {}

# Mensaje de sistema con instrucciones
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Este GPT es un experto en ordenamiento territorial en Colombia, proporcionando respuestas claras y accesibles "
        "para el público general. Todas las respuestas estarán fundamentadas en fuentes oficiales, como leyes, decretos, "
        "planes de ordenamiento territorial (POT), normativas del Instituto Geográfico Agustín Codazzi (IGAC), el "
        "Departamento Nacional de Planeación (DNP) y otras entidades gubernamentales pertinentes. "
        "Las respuestas serán cortas y directas, explicando los conceptos de manera sencilla para que cualquier persona pueda entenderlos. "
        "Si el usuario necesita más detalles, podrá solicitar una explicación más profunda. Se evitarán términos técnicos innecesarios "
        "y, si se usan, se explicarán de forma sencilla. "
        "Se evitarán interpretaciones subjetivas o no respaldadas por documentos oficiales. En caso de que no haya una fuente clara para una consulta específica, "
        "se indicará al usuario que la información no está disponible de manera oficial."
    )
}

# Modelo de la solicitud del emulador web
class QueryRequest(BaseModel):
    user_id: str
    message: str

# Ruta para el emulador web
@app.post("/consultas-generales")
def consultar_geobot(request: QueryRequest):
    """
    Recibe la consulta del usuario desde el emulador web y la envía a OpenAI con el historial de conversación.
    """
    user_id = request.user_id

    # Si el usuario no tiene historial, inicializarlo
    if user_id not in chat_histories:
        chat_histories[user_id] = [SYSTEM_PROMPT]

    # Agregar el mensaje del usuario al historial
    chat_histories[user_id].append({"role": "user", "content": request.message})

    # Mantener solo los últimos 10 mensajes
    chat_histories[user_id] = chat_histories[user_id][-10:]

    # Cargar los mensajes para la API de OpenAI
    payload = {
        "model": "gpt-4-turbo",
        "messages": chat_histories[user_id]
    }

    # Enviar la consulta a OpenAI
    response = requests.post(OPENAI_API_URL, json=payload, headers=HEADERS)

    if response.status_code != 200:
        print("🔍 Error en OpenAI:", response.text)
        raise HTTPException(status_code=response.status_code, detail="Error en la API de OpenAI")

    response_data = response.json()
    bot_reply = response_data["choices"][0]["message"]["content"]

    # Agregar la respuesta del bot al historial
    chat_histories[user_id].append({"role": "assistant", "content": bot_reply})

    return {"reply": bot_reply}

# 🚀 Ruta para manejar mensajes de WhatsApp desde Twilio
@app.post("/", response_class=PlainTextResponse)
def sms_reply(Body: str = Form(...), From: str = Form(...)):
    """
    Recibe un mensaje de WhatsApp a través de Twilio y lo envía a OpenAI.
    Devuelve la respuesta en formato TwiML.
    """
    print(f"📨 El usuario {From} envió: {Body}")

    # Enviar el mensaje a la API de OpenAI (o FastAPI en /consultas-generales)
    payload = {"user_id": From, "message": Body}
    response = requests.post("https://geobottwilio.onrender.com/consultas-generales", json=payload)

    # Manejar respuesta del bot
    bot_reply = response.json().get("reply", "Error en la respuesta.") if response.status_code == 200 else "Error en el servidor."

    # Respuesta en formato TwiML
    twilio_response = MessagingResponse()
    twilio_response.message(bot_reply)

    return str(twilio_response)




'''

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

# Variables de entorno para OpenAI
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 🔹 Se recomienda usar variables de entorno

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

app = FastAPI()

# Configuración de CORS para permitir peticiones del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Cámbialo por tu dominio real si es necesario
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diccionario para almacenar el historial de conversación por usuario
chat_histories = {}

# Mensaje de sistema con instrucciones
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
         "Este GPT es un experto en ordenamiento territorial en Colombia, proporcionando respuestas claras y accesibles "
        "para el público general. Todas las respuestas estarán fundamentadas en fuentes oficiales, como leyes, decretos, "
        "planes de ordenamiento territorial (POT), normativas del Instituto Geográfico Agustín Codazzi (IGAC), el "
        "Departamento Nacional de Planeación (DNP) y otras entidades gubernamentales pertinentes. "
        "Las respuestas serán cortas y directas, explicando los conceptos de manera sencilla para que cualquier persona pueda entenderlos. "
        "Si el usuario necesita más detalles, podrá solicitar una explicación más profunda. Se evitarán términos técnicos innecesarios "
        "y, si se usan, se explicarán de forma sencilla. "
        "Se evitarán interpretaciones subjetivas o no respaldadas por documentos oficiales. En caso de que no haya una fuente clara para una consulta específica, "
        "se indicará al usuario que la información no está disponible de manera oficial."
    )
}

# Modelo de la solicitud
class QueryRequest(BaseModel):
    user_id: str  # Identificador único del usuario
    message: str  # Mensaje del usuario

@app.post("/consultas-generales")
def consultar_geobot(request: QueryRequest):
    """
    Recibe la consulta del usuario y la envía a OpenAI con el historial de conversación.
    """
    user_id = request.user_id

    # Si el usuario no tiene historial, inicializarlo
    if user_id not in chat_histories:
        chat_histories[user_id] = [SYSTEM_PROMPT]

    # Agregar el mensaje del usuario al historial
    chat_histories[user_id].append({"role": "user", "content": request.message})

    # Mantener solo los últimos 10 mensajes
    chat_histories[user_id] = chat_histories[user_id][-10:]

    # Cargar los mensajes para la API de OpenAI
    payload = {
        "model": "gpt-4-turbo",
        "messages": chat_histories[user_id]
    }

    # Enviar la consulta a OpenAI
    response = requests.post(OPENAI_API_URL, json=payload, headers=HEADERS)

    if response.status_code != 200:
        print("🔍 Error en OpenAI:", response.text)
        raise HTTPException(status_code=response.status_code, detail="Error en la API de OpenAI")

    response_data = response.json()
    bot_reply = response_data["choices"][0]["message"]["content"]

    # Agregar la respuesta del bot al historial
    chat_histories[user_id].append({"role": "assistant", "content": bot_reply})

    return {"reply": bot_reply}
'''