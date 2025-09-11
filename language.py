import re
import config
from openai import OpenAI

system_prompt = config.system_prompt

# Funktion zum Entfernen unvollständiger Sätze
def remove_incomplete_sentences(text):
    # Wenn der Text leer ist, ist das in Ordnung
    if text == "":
        return text
    # Text in Sätze aufteilen
    sentences = re.split('(?<=[.!?]) +', text)

    # Überprüfen, ob der letzte Satz mit einem Satzzeichen endet
    if sentences and not re.search('[.!?]$', sentences[-1]):
        # Überprüfen, ob der letzte Satz nur aus einem Wort und einem `#` besteht
        if not re.match(r'^\w+#$', sentences[-1]):
            # Den letzten Satz entfernen
            print("Removed incomplete sentence: ", sentences[-1])
            sentences = sentences[:-1]

    # Sätze wieder zu einem Text zusammenfügen
    text = ' '.join(sentences)

    return text

# Initialisiere den Gesprächsverlauf
history = [
    {
        "role": "system",
        "content": system_prompt
    }
]

import loadapikey
loadapikey.api_key
# Initialisiere den Client
client = OpenAI(api_key=loadapikey.api_key)

def generate_response(question, role="user"):
    # Füge die Frage des Benutzers zur Historie hinzu
    history.append({
        "role": role,
        "content": question
    })
    # Initialisiere die Emotion
    emotion = "neutral"
    
    # Generiere Text aus dem Modell
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history,
            temperature=0.8,
            max_tokens=64,
        )
        # Antwort erhalten
        answer = response.choices[0].message.content

        # Unvollständige Sätze entfernen
        answer = remove_incomplete_sentences(answer)
    except:
        answer = "sad# I could not use OpenAI. Probably no internet connection."

    # Füge die Antwort des Assistenten zur Historie hinzu
    history.append({
        "role": "assistant",
        "content": answer
    })

    # Antwort in Text und Emotion aufteilen
    if answer.count('#') != 1:
        history.append({
            "role": "system",
            "content": "Error: There must be exactly one # in the answer!"
        })
        answer_text = answer
    else:
        answer_text = answer.split('#')[1]
        emotion = answer.split('#')[0]

    return emotion, answer_text

# Teste die Funktion, wenn main
if __name__ == "__main__":
    print("Assistant started.")
    # Chat erstellen
    while True:
        # Benutzereingabe erhalten
        user_input = input("User: ")
        # Antwort generieren
        emotion, text = generate_response(user_input)
        # Antwort ausgeben
        print("Assistant: ", text)
        print("Emotion: ", emotion)
        # Wenn der Benutzer "exit" eingibt, endet die Schleife
        if user_input == "exit":
            break

