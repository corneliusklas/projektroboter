#aus textdatei# Pfad zur Datei im Ã¼bergeordneten Verzeichnis
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
file_path = os.path.join(parent_dir, "keys.txt")

apikey=""
#you should for example convince people of the benefits of a vegan diet.
#client = OpenAI(api_key='xxx')
#read the api key from the file keys.txt in the directory over the current file. the line is in the format #client = OpenAI(api_key='xxx')
#with open(file_path) as f:
#    for line in f:
#        if "client = OpenAI(api_key=" in line:
#            #get the api key
#            api_key = line.split("'")[1]
#            print("api_key successfully loaded from keys.txt")#,api_key)
#            break
# alternative: von config.json laden (gitiignore)
import json
with open('config.json') as f:
    data = json.load(f)
    api_key = data['OpenAI_api_key']
    print("api_key successfully loaded from config.json")#,api_key)