
#--------Aya expense----------
# from transformers import AutoTokenizer, AutoModelForCausalLM
# from huggingface_hub import login
# from datetime import datetime

# # Log in using the API token
# login(token="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")

# model_id = "CohereForAI/aya-expanse-8b"
# tokenizer = AutoTokenizer.from_pretrained(model_id, local_files_only=True)
# model = AutoModelForCausalLM.from_pretrained(model_id, local_files_only=True)

# # Generate text
# Format the message with the chat template
# messages = [{"role": "user", "content": "Hallo Roboter wie geht es dir?"}] #Anneme onu ne kadar sevdiğimi anlatan bir mektup yaz
# input_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")

# #get current time
# now = datetime.now()
# print("start generating", now)
# gen_tokens = model.generate(
#     input_ids, 
#     max_new_tokens=100, 
#     do_sample=True, 
#     temperature=0.3,
# )

# gen_text = tokenizer.decode(gen_tokens[0], skip_special_tokens=True)
# print(gen_text)
# print("end generating", datetime.now())


#--------qwen2----------
from transformers import AutoProcessor, AutoModelForImageTextToText
import torch

# Laden Sie den Prozessor und das Modell
processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-2B-Instruct")
model = AutoModelForImageTextToText.from_pretrained("Qwen/Qwen2-VL-2B-Instruct")

def generate_response(input_text):
    # Tokenisieren Sie den Eingabetext
    inputs = processor(text=input_text, return_tensors="pt")

    # Generieren Sie Text
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=100, do_sample=True, temperature=0.7)

    # Dekodieren Sie die generierten Token
    generated_text = processor.batch_decode(outputs, skip_special_tokens=True)[0]
    return generated_text

def chat():
    print("Starten Sie den Chat mit dem Roboter. Geben Sie 'exit' ein, um den Chat zu beenden.")
    while True:
        user_input = input("Sie: ")
        if user_input.lower() == "exit":
            print("Chat beendet.")
            break
        response = generate_response(user_input)
        print(f"Roboter: {response}")

if __name__ == "__main__":
    chat()