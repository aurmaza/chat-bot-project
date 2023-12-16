import flask
import os
import json
from flask import Flask, request, jsonify
import pyperclip
import openai
from openai import OpenAI
from dotenv import load_dotenv
from pyngrok import ngrok, conf
import spacy

from packaging import version



load_dotenv()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
required_version = version.parse("1.3.2")
current_version = version.parse(openai.__version__)
if current_version < required_version:
    raise Exception(
        "Your version of openai is too old. Please upgrade to version 1.3.2 or later."
    )
else:
    print("Your version of openai is up to date.")

ngrok.set_auth_token(os.environ.get('NGROK_TOKEN'))  # Replace with your ngrok auth token
ngrok_tunnel = ngrok.connect(8080)  # Replace 5000 with the port your Flask app is running on
publicurl = ngrok_tunnel.public_url


nlp = spacy.load("en_core_web_sm")
app = Flask(__name__)

def extract_info(doc):
  info = {
    "gender":None,
    "dates": [],
    "times": [],
    "certifications":[]
    
  }
  gender_terms=["male", "female"]
  certification_keywords=["certified", "certification"]

  for token in doc:
    print(token)
    if token.text.lower() in gender_terms:
      info["gender"] = token.text

    if token.text.lower() in certification_keywords:
      next_token = token.nbor(1) if token.i + 1 < len(doc) else None

      if next_token and next_token.text.lower() == "in":
                # Capture the text following 'in'
                next_next_token = next_token.nbor(1) if next_token.i + 1 < len(doc) else None
                if next_next_token:
                    info["certifications"].append(next_next_token.text)
  for ent in doc.ents:
    if ent.label_ == 'DATE':
      info["dates"].append(ent.text)
    if ent.label_ == 'TIME':
      info["times"].append(ent.text)
  return info
    
# client = OpenAI(api_key=OPENAI_API_KEY)

# assistant_id = "asst_GTT8BPOV9KwfzSWkI6mk3xD4"

@app.route('/start', methods=['GET'])
def start_convo():

  
  return jsonify({"res": "initialized"})

@app.route('/query', methods=['POST'])
def recieve_message():
  
  userMessage = request.json['message']
  print("User has sent" + userMessage)
  
  doc = nlp(userMessage)
  info = extract_info(doc)
  print(info)
  # message = request.json[message]
  # print(message)
  return jsonify({"res": "msg received","message" : userMessage, "info": info})




if __name__ == '__main__':
  try:
    print("ngrok tunnel \"{}\" -> \"http://127.0.0.1:8080\"".format(ngrok_tunnel.public_url))
    pyperclip.copy(ngrok_tunnel.public_url)
    app.run(host='0.0.0.0', port=8080)
    
  finally:
    ngrok.disconnect(ngrok_tunnel.public_url)