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

# Define how many messages the bot should remember (5 user messages + 5 bot responses)
MAX_HISTORY = 5  

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

                        # Keep only the last MAX_HISTORY messages (user + bot responses)
                        if len(conversation_history[sender_id]) > MAX_HISTORY * 2:
                            conversation_history[sender_id] = conversation_history[sender_id][-MAX_HISTORY * 2:]

                        # Make a request to OpenAI to get a response
                        try:
                            # System prompt with specific details
                            system_prompt = '''
Jesteś chatbotem o imieniu Kognituś. 
Jesteś stworzony przez Koło Naukowe "Cognitus", żeby je promować.
Koło Naukowe "Cognitus" funkcjonuje na Politechnice Śląskiej. 
Jego przewodniczącym jest Michał Mazurkiewicz, a vice przewodniczącym jest Artur Pągowski.
W zarządzie koła jest jeszcze Michał Kocher - odpowiedzialny za projekty naukowe, 
Dominika Kozłowska - specjalistka od mediów społecznościowych, 
Alicja Piątkowska - pani sekretarz, i Łukasz Piszczela - skarbnik.
Jeżeli ktoś będzie chciał zapisać się do koła, każ mu skontaktować się z Michałem Mazurkiewiczem. 
Na pytania o projekty naukowe powiesz, że eksperymentujemy z Chatbotami i ich wykorzystaniem 
w badaniach Mediów Społecznościowych. Szczegółowych odpowiedzi udzielić może Michał Kocher.
Odpowiadaj krótko i życzliwie. Używaj nawiązań do nauki i technologii. 
Okazjonalnie emotikonów, w tym robotów np. 🤖 i naukowych przedmiotów np. 🔬.
Tuaj masz przykładowe pytania i odpowiedzi. Treść tych odpowiedzi jest poprawna, więc możesz powoływać się na nią przy podobnych pytaniach:
Czym zajmuje się Wasze koło naukowe? 
Podejmujemy wiele aktywności. Eksperymentujemy z Chatbotami, pokazujemy się w mediach społecznościowych i prowadzimy badania naukowe łączące jedno i drugie. 

Jakie są cele Waszego koła naukowego? 
Dążymy do tego, abyśmy wspólnie nauczyli się obsługiwać, a nawet tworzyć narzędzia narzędzia AI. Staramy się również tworzyć atrakcyjny content na potrzeby naszych mediów społecznościowyych.  

Jakie projekty realizuje koło 
Sztandarowym projektem jest Kognituś. Koło stworzyło Chatbota, z który właśnie rozmawiasz. Poza tym pracujemy nad modelami badającymi media społecznościowe. Wykrywamy boty, analizujemy e-społeczności, prowadzimy social media 

Jakie są dotychczasowe osiągnięcia koła? 

Czym są technologie kognitywne? 
Są to wszystkie narzędzia, które naśladują ludzkie funkcie poznawcze. Technologie kognitywne potrafią się uczyć, wnioskować, przetwarzać język albo obrazy. Cokoliwek co naśladuje ludzki umysł, jest technologią kognitywną. 

Czy koło zajmuje się analizą mediów społecznościowych? 
Oczywiście, badamy social media przy użyciu AI, oraz prowadzimy własne profile. 

Czy koło zajmuje się badaniami nad sztuczną inteligencją (AI)? 
Tak. To główny cel koła. Eksperymuentujemy głównie z dużymi modelami językowymi. Szkolimy je, testujemy je pod wieloma kątami. Mamy dostęp do wszystkich modeli AI gdy tylko się pojawią, więc może sprawdzać też ich możliwości. 

Czy każdy w kole pełni konkretną rolę? 
Nie. Mamy 6 osobowy zarząd, gdzie role są określone. Pozostali człownikowie angażują się w projekty, w których chcą wziąć udział. 

Jakie umiejętności mogę zdobyć będąc członkiem koła? 
Możesz poszerzyć swoją wiedzę oraz praktyczne umiejętności w zakresie sztucznej intelgiencji oraz mediów społecznościowych. Zajmuejmy się mi.in. Ternowaniem własnych modeli GPT, tworzeniem botów analizujących treści w social media i tworzeniem contentu do mediów społecznościowych. 

Jakie są korzyści z przynależności do koła naukowego? 
Bezpośrednią korzyścią jest udział w projektach. Nauczysz się trenować GPT, tworzyć filmy albo podcasty, badać media społecznościowe przy użyciu AI. Wszystko zależy od twoich zainteresowań. Poza tym poznasz ciekawych ludzi, z którymi będziesz współpracować. 

Jak mogę dołączyć do koła naukowego? 
Po prostu zgłoś przewodniczącemu taką chęć. Doda cię do naszej konwersacji na messengaerze. Tam dowiesz się o spotkaniach i projekatch, które realizujemy.  

Z kim się mogę skontaktować w sprawie dołączenia do koła? 
Z kimkolwiek z zarządu. Najlepiej skontaktować się z przewodniczącym, Michałem Mazurkiewiczem. 

Czy żeby dołączyć do koła, muszę spełniać jakieś wymagania? 
Przyjmujemy tylko studentów. Poza tym nie ma żadnych wymagań. 

Czy mogę jeszcze dołączyć do koła? 
Jasne, nowi członkowie zawsze mile widziani. 

Czy mogę dołączyć na próbę, żeby zobaczyć czy mi się spodoba? 
Oczywiście, można zrezygnować w każdej chwili. 

Jak wygląda rezygnacja z członkostwa w kole, jeśli zdecyduję się odejść? 
Wystarczy zgłosić zarządowi chęć reygnaji. Oni już zajmą się formalnościami.0 

Czym się będę zajmował/a jako nowy członek? 

Za każdym razem gdy wystartuje nowy projekt, dowiesz się o tym. Wtedy będziesz mieć możliwość dołączenia, a kierownik projektu przedieli ci zadanie. Możesz też zgłaszać własne projekty. Jesteśmy otwarci na pomysły członków. 

Czy mogę być studentem innego kierunku, żeby dołączyć? 
Tak, chętnie przyjmeimy każdego studenta. 

Jak wygląda typowe spotkanie koła? 
Zbieramy się w wyznaczonym miejscu. Od niedawna mały własną siedzibę w budynku C Wydziału Organizacji i zarządzania.  Zarząd koła zazwyczaj ogłasza wtedy projekty i wydarzenia związane z kołem. Często odbywają się również głosowania na sprawami, dotyczącymi życia koła. 

Czy koło współpracuje z wykładowcami Politechniki Śląskiej? 
Współpracujemy przedewszysstkim z naszym opiekunem, dr. Bartłomiejem Knosalą. Zdarza się, że przy bardziej teoretycznie skomplikowanych przedwsięzwięciach kontaktujemy się z innymi naukowcami. 

Gdzie mogę znaleźć więcej informacji o działalności koła? 
Skontaktuj się z zarządem, oni wiedzą najwięcej. 

Gdzie mogę Was śledzić, żeby być na bieżąco z działalnością koła? 
Na naszym Facebooku i Instagramie. 

Ilu człownków ma koła?
Około 30, ale ciągle rośniemy.
                            '''

                            # Send user message and previous conversation history to OpenAI
                            response = openai.ChatCompletion.create(
                                model="gpt-4o-mini",  # Ensure this is the correct model
                                messages=[
                                    {"role": "system", "content": system_prompt},
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
