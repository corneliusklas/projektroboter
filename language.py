from openai import OpenAI
import re
import os

# Pfad zur System-Prompt-Datei
system_prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
# Laden des System-Prompts aus der Textdatei
with open(system_prompt_path, 'r', encoding='utf-8') as file:
    system_prompt = file.read()

#function to remove incomplete sentences
def remove_incomplete_sentences(text):
    #if the text is empty its ok
    if text == "":
        return text
    # Split the text into sentences
    sentences = re.split('(?<=[.!?]) +', text)

    # Check if the last sentence ends with a punctuation mark
    if sentences and not re.search('[.!?:;]$', sentences[-1]):
        #print the last sentence that will be removed
        print("Removed incomplete sentence: ", sentences[-1])
        # Remove the last sentence
        sentences = sentences[:-1]

    # Join the sentences back into a text
    text = ' '.join(sentences)

    return text


# Initialize the conversation history
history = [
    {
        "role": "system",
        "content": system_prompt
    }
]

import loadapikey
loadapikey.api_key
#initialize the client
client = OpenAI(api_key=loadapikey.api_key)

def generate_response(question, role="user"):
    # Add the user's question to the history
    history.append({
        "role": role,
        "content": question
    })
    #initilize the emotion
    emotion = "neutral"
    # Initialize the OpenAI client
    
    # Generate text from the model
    #try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=history,
        temperature=0.8,
        max_tokens=64,
    )
    #get the answer
    answer = response.choices[0].message.content

    #remove incomplete sentences. Uncomplete sentences are caused by token limit. This is the last stentence without a dot, question mark or exclamation mark.
    answer = remove_incomplete_sentences(answer)
    #except:
    #    error = str(sys.exc_info()[1])
    #    #print the error
    #    print("error: ",error)
    #    #output the error as speeech
    #    return "sad",error


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

