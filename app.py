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
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def sms_reply():
    print("📩 Recibí un mensaje de Twilio:")
    print(request.form)  # Muestra el contenido del POST recibido

    incoming_msg = request.form.get("Body", "Mensaje vacío")
    print(f"📨 El usuario envió: {incoming_msg}")

    response = MessagingResponse()
    response.message(f"mensaje recibido: {incoming_msg}")

    return str(response)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


'''

