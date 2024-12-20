from flask import Flask, request, jsonify
import openai
import os
import requests

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Pobranie klucza API OpenAI z zmiennych środowiskowych
openai.api_key = os.getenv("OPENAI_API_KEY")

# Funkcja do komunikacji z GPT-4
def get_gpt_response(user_message):
    try:
        response = openai.Completion.create(
            model="gpt-4o-mini",  # Używamy modelu GPT-4
            prompt=user_message,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Endpoint do przyjmowania wiadomości z Messengera
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Weryfikacja webhooka (Facebook)
        if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.challenge'):
            return request.args['hub.challenge'], 200
        return 'Invalid request', 403

    if request.method == 'POST':
        # Obsługa wiadomości
        data = request.get_json()
        for entry in data['entry']:
            for message in entry['messaging']:
                sender_id = message['sender']['id']
                if 'message' in message:
                    user_message = message['message'].get('text', '')
                    if user_message:
                        gpt_response = get_gpt_response(user_message)
                        send_message(sender_id, gpt_response)
        return 'OK', 200

# Funkcja do wysyłania wiadomości do użytkownika przez Facebook Messenger
def send_message(recipient_id, message_text):
    access_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')  # Token dostępu do strony Facebooka z zmiennych środowiskowych
    url = f'https://graph.facebook.com/v15.0/me/messages?access_token={access_token}'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text}
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Error sending message: {str(e)}")

# Uruchomienie aplikacji
if __name__ == '__main__':
    app.run(debug=True, port=5000)
