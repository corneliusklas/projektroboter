import re
import config
import requests
import json

system_prompt = config.system_prompt

# Funktion zum Entfernen unvollständiger Sätze
def remove_incomplete_sentences(text):
    if text == "":
        return text
    sentences = re.split(r'(?<=[.!?]) +', text)
    if sentences and not re.search(r'[.!?]$', sentences[-1]):
        if not re.match(r'^\w+#$', sentences[-1]):
            print("Removed incomplete sentence:", sentences[-1])
            sentences = sentences[:-1]
    return ' '.join(sentences)

# Gesprächsverlauf initialisieren
history = [
    {"role": "system", "content": system_prompt}
]

# Funktion zum Generieren einer Antwort über Ollama
def generate_response(question, role="user"):
    history.append({"role": role, "content": question})

    try:
        # Anfrage an den lokalen Ollama-Server senden
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2:1b",  # <--- Modellname hier ggf. anpassen
                "messages": history,
                "options": {
                    "temperature": 0.8,
                    "num_predict": 32
                },
                "stream": False
            }
        )

        response.raise_for_status()

        # --- Robust: Mehrere JSON-Objekte verarbeiten ---
        raw_text = response.text.strip()

        # Mehrere JSONs trennen (Ollama kann mehrere senden)
        json_objects = []
        for part in raw_text.splitlines():
            part = part.strip()
            if part:
                try:
                    json_objects.append(json.loads(part))
                except json.JSONDecodeError:
                    print("Warnung: konnte Teil nicht als JSON lesen:", part[:80])

        # Letztes gültiges JSON-Objekt enthält die finale Antwort
        if json_objects:
            data = json_objects[-1]
            answer = data.get("message", {}).get("content", "").strip()
        else:
            answer = "sad# Ich konnte keine gültige Antwort von Ollama lesen."

        # Unvollständige Sätze entfernen
        answer = remove_incomplete_sentences(answer)

    except Exception as e:
        print("Error:", e)
        answer = "sad# Ich konnte Ollama nicht verwenden."

    # Antwort zur Historie hinzufügen
    history.append({"role": "assistant", "content": answer})

    # Emotion und Text trennen
    if answer.count('#') != 1:
        history.append({"role": "system", "content": "Error: There must be exactly one # in the answer!"})
        emotion = "neutral"
        answer_text = answer
    else:
        emotion, answer_text = answer.split('#', 1)

    return emotion.strip(), answer_text.strip()


# Hauptschleife
if __name__ == "__main__":
    print("Assistant gestartet (Ollama).")
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break
        emotion, text = generate_response(user_input)
        print("Assistant:", text)
        print("Emotion:", emotion)
