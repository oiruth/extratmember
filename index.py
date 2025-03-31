from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import random
import string
from datetime import datetime, timedelta
import os
import requests

app = Flask(__name__)
CORS(app)

KEYS_FILE = 'keys.json'

BOT_TOKEN = '7950073092:AAGIF-CiHHFG79wiCpsw-xnQRXiPllrKCTs'
CHAT_ID = '5650303115'

def generate_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def load_keys():
    try:
        with open(KEYS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=4)

def send_code_to_telegram():
    code = str(random.randint(100000, 999999))
    message = f'Seu código de autenticação é: {code}'
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}'
    response = requests.get(url)
    return code if response.status_code == 200 else None

@app.route('/')
def serve_html():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/generate_key', methods=['POST'])
def generate_key_api():
    data = request.json
    validity_days = int(data['validity_days'])
    expiration_date = datetime.now() + timedelta(days=validity_days)
    expiration_str = expiration_date.strftime('%d/%m/%Y')
    
    new_key = generate_key()
    keys = load_keys()
    keys.append({
        'key': new_key,
        'created_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'expires_at': expiration_str
    })
    save_keys(keys)
    
    return jsonify({"message": "Key generated successfully", "key": new_key, "expires_at": expiration_str})

@app.route('/delete_key', methods=['POST'])
def delete_key_api():
    data = request.json
    key_to_delete = data['key']
    keys = load_keys()
    keys = [key for key in keys if key['key'] != key_to_delete]
    save_keys(keys)
    return jsonify({"message": "Key deleted successfully"})

@app.route('/check_expired_keys', methods=['GET'])
def check_expired_keys():
    keys = load_keys()
    current_time = datetime.now()
    expired_keys = [key for key in keys if datetime.strptime(key['expires_at'], '%d/%m/%Y') < current_time]
    keys = [key for key in keys if datetime.strptime(key['expires_at'], '%d/%m/%Y') >= current_time]
    save_keys(keys)
    return jsonify({"expired_keys": expired_keys})

@app.route('/send_code', methods=['POST'])
def send_code():
    code = send_code_to_telegram()
    return jsonify({'message': 'Código enviado com sucesso', 'code': code}) if code else jsonify({'message': 'Erro ao enviar código'}), 500

@app.route('/get_keys', methods=['GET'])
def get_keys():
    return jsonify(load_keys())

def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    app.run(debug=True)
