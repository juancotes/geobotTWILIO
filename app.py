from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def sms_reply():
    if request.method == "GET":
        return "El servidor está funcionando correctamente", 200

    incoming_msg = request.form.get("Body", "")
    response = MessagingResponse()
    response.message(f"mensaje recibido: {incoming_msg}")

    return str(response)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


'''
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/sms", methods=["POST"])
def sms_reply():
    """ Responde a los mensajes recibidos con 'mensaje recibido' """
    incoming_msg = request.form.get("Body")
    
    response = MessagingResponse()
    response.message(f"mensaje recibido: {incoming_msg}")
    
    return str(response)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
'''