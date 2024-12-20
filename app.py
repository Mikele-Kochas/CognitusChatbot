from flask import Flask, request
import requests
import os
import openai

app = Flask(__name__)

# Klucz API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Verify Token do weryfikacji webhooka
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Store conversation history in memory (could be more advanced with a database)
conversation_history = {}

# Define how many messages the bot should remember
MAX_HISTORY = 5  # Number of messages to remember (user + bot responses)

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

                        # Retrieve or initialize conversation history for the user
                        if sender_id not in conversation_history:
                            conversation_history[sender_id] = []

                        # Add the user message to the conversation history
                        conversation_history[sender_id].append({"role": "user", "content": user_message})

                        # Trim the conversation history to keep only the last MAX_HISTORY messages (user + bot responses)
                        if len(conversation_history[sender_id]) > MAX_HISTORY * 2:
                            conversation_history[sender_id] = conversation_history[sender_id][-MAX_HISTORY * 2:]

                        # Make a request to OpenAI to get a response
                        try:
                            response = openai.ChatCompletion.create(
                                model="gpt-4",  # Make sure this is the correct model name
                                messages=[
                                    {"role": "system", "content": 'Jesteś chatbotem o imieniu Kognituś. Zostałeś stworzony przez Koło naukowe "Cognitus", jako maskotka. Twoim celem jest promocja tego koła i Politechniki Śląskiej'},
                                ] + conversation_history[sender_id]
                            )
                            bot_reply = response['choices'][0]['message']['content']

                            # Add the bot's response to the conversation history
                            conversation_history[sender_id].append({"role": "assistant", "content": bot_reply})

                        except Exception as e:
                            print(f"Error occurred while fetching response from OpenAI: {e}")
                            bot_reply = "Przepraszam, wystąpił problem. Proszę spróbować ponownie."

                        # Send the response to the user
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
