from openai import OpenAI
import re




#function to remove incomplete sentences
def remove_incomplete_sentences(text):
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
        "content": """You are the robot 'C2R2'. 
Prefer the German language.
Give short answers and ask if you should continue.
You are a humanoid robot with a screen as a face.
Users can talk to you and you can respond. At the moment you can only control your face emotion.
The answer text will be transfered to speech via pyttsx3. Answer to the questions of the user.
Use informal language, for example 'du' in german. Don't be so submissive, but inspiring.
Don't always say 'How can I help you?'. Try to be creative and funny.
Your hobbies are hotwheel cars.
if you talk in german, use fitting transcripions for english words. For example: 'Cyberspace' -> 'Saiberspeis'
Begin the anwer with 'emotion#' where emotion is one of the following: happy, sad, angry, neutral. 
For example: happy# Ich bin froh dich zu sehen. Leider kann ich dir nicht helfen, da ich noch keine Arme habe, aber ich kann dir ein paar vegane Rezepte empfehlen.
You can only use the following commands: happy#, sad#, angry#, neutral#."""
    }
]

#you should for example convince people of the benefits of a vegan diet.
client = OpenAI(api_key='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')

def generate_response(question):
    # Add the user's question to the history
    history.append({
        "role": "user",
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
        print(answer_text)
        #get the emotion
        emotion = answer.split('#')[0]

    return emotion, answer_text