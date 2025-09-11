import os
import json

#load language from config file
config_file_path = ("config.json")
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)
lang = config.get('lang', '')
speech_engine = config.get('speech_engine', 'openai')

# System-Prompt-Datei aus config.json laden
system_prompt_file = config.get('system_prompt_file', 'system_prompt.txt')

# Pfad zur System-Prompt-Datei
system_prompt_path = os.path.join(os.path.dirname(__file__), system_prompt_file)

#startnachricht and das LLM
first_message = config.get('first_message', 'System: Du wurdest gerade angeschaltet.')

# Laden des System-Prompts aus der Textdatei
with open(system_prompt_path, 'r', encoding='utf-8') as file:
    system_prompt = file.read()
#replage $lang$ with the language
system_prompt = system_prompt.replace("$lang$", lang)
system_prompt = system_prompt.replace("$speech_engine$", speech_engine)

#config_file_path = ("config.json")
#with open(config_file_path, 'r') as config_file:
#    config = json.load(config_file)

connection = config.get('connection', '')
if connection == "bluetooth":
    com_port = config.get('bluetooth_com_port', 'COM26')
    mac_adress = config.get('bluetooth_mac_address', '00:21:13:01:54:E7')
elif connection == "wlan":
    WS_URL = "ws://" +config.get('wlan_ip', '') + "/ws"
