import json
import os


DB_FILE = "users.json"

def load_user_data():
    
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_user_data(data):
    
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_user_favorites(username):
    
    data = load_user_data()
    # Pastikan struktur favorit ada
    return data.get(username, {}).get('favorit', {})

def update_user_favorites(username, favorites_dict):
    
    data = load_user_data()
    # Pastikan pengguna ada dalam data
    if username in data:
        data[username]['favorit'] = favorites_dict
        save_user_data(data)
        return True
    return False

def check_user_credentials(username, password):
    
    data = load_user_data()
    if username in data and data[username].get('password') == password:
        return True
    return False