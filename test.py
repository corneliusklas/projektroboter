import os
import json


#load language from config file
config_file_path = ("config.json")
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)
lang = config.get('lang', '')


# Pfad zur System-Prompt-Datei
system_prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
# Laden des System-Prompts aus der Textdatei
with open(system_prompt_path, 'r', encoding='utf-8') as file:
    system_prompt = file.read()
#replage $lang$ with the language
system_prompt = system_prompt.replace("$lang$", lang)


# Initialize the conversation history
history = [
    {
        "role": "system",
        "content": system_prompt
    }
]

def generate_response(question, role="user"):
    # Add the user's question to the history
    history.append({
        "role": role,
        "content": question
    })
    #initilize the emotion
    emotion = "neutral"
    
    answer = "sad# I could not use OpenAI. Probably no internet connection."
    # Add the assistant's message to the history
    history.append({
        "role": "assistant",
        "content": answer
    })

    #split the answer in text and emotion
    #check if there is exactly one #
    if answer.count('#') != 1:
        history.append({
        "role": "system",
        "content": "Error: There must be exactly one # in the answer!"
        })
        answer_text = answer
    else: 
        answer_text = answer.split('#')[1]
        #print(answer_text)
        #get the emotion
        emotion = answer.split('#')[0]

    return emotion, answer_text
    



# test the function if main
if __name__ == "__main__":
    # Test the function with a question. include the history with the system prompt
    #emotion, text =generate_response("Wie heißt du?")
    #print("Emotion: ",emotion)
    #print("Text: ",text)

    print("Assistant started.")
    #Make a Chat
    while True:
        #get the user input
        user_input = input("User: ")
        #generate the response
        emotion, text =generate_response(user_input)
        #print the response
        print("Assistant: ",text)
        print("Emotion: ",emotion)
        #if the user types "exit" the loop will end
        if user_input == "exit":
            break

