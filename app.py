from flask import Flask, request, jsonify, render_template
import openai
import os

app = Flask(__name__)

# Pobierz klucz API OpenAI z zmiennych środowiskowych
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ustawienia dla domyślnych promptów i pamięci rozmowy
default_prompts = [
    {"role": "system", "content": (
        "Jesteś chatbotem. Odpowiadasz na pytania użytkownika i prowadzisz rozmowę. "
        "Piszesz w sposób naturalny i zrozumiały. Używasz prostego języka."
    )}
]
conversation = []  # Pamięć rozmowy

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get('input', '')
    print(f"Received input: {user_input}")

    # Dodaj domyślne prompty, jeśli to pierwsze zapytanie
    if not conversation:
        conversation.extend(default_prompts)

    # Dodaj wiadomość użytkownika do rozmowy
    conversation.append({"role": "user", "content": user_input})

    # Pobierz odpowiedź z OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=conversation
        )
        assistant_reply = response['choices'][0]['message']['content']
        print(f"Assistant reply: {assistant_reply}")

        # Dodaj odpowiedź do rozmowy
        conversation.append({"role": "assistant", "content": assistant_reply})

        return jsonify({"response": assistant_reply})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": "Przepraszam, wystąpił błąd."})

if __name__ == '__main__':
    # Pobierz PORT z zmiennych środowiskowych lub ustaw domyślny 5000
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
