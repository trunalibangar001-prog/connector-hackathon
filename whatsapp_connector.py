from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "connector_challenge_2026")


# WhatsApp webhook verification
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


# Receive WhatsApp messages
@app.route("/webhook", methods=["POST"])
def receive_webhook():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    print("\nWhatsApp webhook received:")
    print(json.dumps(data, indent=2))

    # Save received payload
    with open("whatsapp_output.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return jsonify({"status": "received"}), 200


@app.route("/", methods=["GET"])
def home():
    return "WhatsApp connector is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)