from flask import Flask, request, render_template
import os
import openai

app = Flask(__name__)

# Klucz API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Verify Token do weryfikacji webhooka
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "moj_bot")  # Możesz ustawić wartość domyślną, jeśli zmienna środowiskowa jest pusta

# URL aplikacji
CALLBACK_URL = os.getenv("CALLBACK_URL", "https://evening-ridge-17995-c165e0dc54de.herokuapp.com/webhook")

@app.route('/')
def index():
    # Przekazujemy VERIFY_TOKEN i CALLBACK_URL do template
    return render_template('index.html', verify_token=VERIFY_TOKEN, callback_url=CALLBACK_URL)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Weryfikacja webhooka
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("Webhook verified!")
            return challenge, 200
        else:
            return "Forbidden", 403

    elif request.method == 'POST':
        # Obsługa przychodzących wiadomości
        data = request.json
        print(f"Received data: {data}")
        
        if data.get('object') == 'page':
            for entry in data['entry']:
                for message_event in entry['messaging']:
                    if 'message' in message_event:
                        sender_id = message_event['sender']['id']
                        user_message = message_event['message']['text']

                        # Pobierz odpowiedź z OpenAI
                        response = openai.ChatCompletion.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Jesteś chatbotem Messenger."},
                                {"role": "user", "content": user_message}
                            ]
                        )
                        bot_reply = response['choices'][0]['message']['content']

                        # Wyślij odpowiedź do użytkownika
                        send_message(sender_id, bot_reply)

        return "EVENT_RECEIVED", 200

def send_message(recipient_id, text):
    """Wysyła wiadomość do użytkownika"""
    PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    print(f"Message sent: {response.json()}")

if __name__ == '__main__':
    app.run(debug=True)
