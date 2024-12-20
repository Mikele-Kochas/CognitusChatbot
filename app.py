import os
import openai
from flask import Flask, request, render_template, jsonify

# Konfiguracja aplikacji Flask
app = Flask(__name__)

# Ustawienie klucza API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")  # Klucz API zapisany jako zmienna środowiskowa

@app.route('/')
def index():
    return render_template('index.html')  # Renderujemy formularz HTML

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']  # Pobieramy wiadomość użytkownika z formularza

    if not user_message:
        return render_template('index.html', error="No message provided")

    try:
        # Wysyłanie wiadomości do GPT-4
        response = openai.Completion.create(
            model="gpt-4",  # Wybór modelu GPT-4
            prompt=user_message,
            max_tokens=150,
            temperature=0.7
        )

        # Odpowiedź z OpenAI
        bot_message = response.choices[0].text.strip()
        
        # Renderowanie strony z odpowiedzią chatbota
        return render_template('index.html', user_message=user_message, bot_message=bot_message)

    except Exception as e:
        return render_template('index.html', error=str(e))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
