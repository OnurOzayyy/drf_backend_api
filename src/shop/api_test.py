import json 

base_url = "http://127.0.0.1:8000/api/"
login_url = base_url + 'auth/token/'
cart_url = base_url + "cart/"


cart_r = requests.get(cart_url)
cart_token = cart_r.json()