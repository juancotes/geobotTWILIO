from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import requests

# URL donde corre FastAPI (ajústala según sea necesario)
MAIN_API_URL = "http://localhost:8000/api/chat/consultas-generales"

app = Flask(__name__)

@app.route("/", methods=["POST"])
def sms_reply():
    """
    Recibe un mensaje de Twilio, lo envía a main.py para obtener una respuesta de OpenAI
    y devuelve la respuesta generada al usuario.
    """
    print("📩 Recibí un mensaje de Twilio:")
    print(request.form)  # Debug

    incoming_msg = request.form.get("Body", "Mensaje vacío").strip()
    user_id = request.form.get("From", "anon")  # Usa el número de teléfono como ID de usuario

    print(f"📨 El usuario {user_id} envió: {incoming_msg}")

    # Enviar la consulta a main.py
    payload = {"user_id": user_id, "message": incoming_msg}
    response = requests.post(MAIN_API_URL, json=payload)

    if response.status_code == 200:
        bot_reply = response.json().get("reply", "No se recibió respuesta.")
    else:
        bot_reply = "Error al procesar tu consulta."

    # Responder al usuario vía Twilio
    twilio_response = MessagingResponse()
    twilio_response.message(bot_reply)

    return str(twilio_response), 200  # Código HTTP 200 OK

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

'''
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/", methods=["POST"])
def sms_reply():
    print("📩 Recibí un mensaje de Twilio:")
    print(request.form)  # Muestra el contenido del POST recibido

    incoming_msg = request.form.get("Body", "Mensaje vacío").strip()
    print(f"📨 El usuario envió: {incoming_msg}")

    response = MessagingResponse()
    response.message(f"mensaje recibido: {incoming_msg}")

    return str(response), 200  # 🔹 Asegurar código HTTP 200 OK

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


'''


