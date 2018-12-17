import json 
import requests

base_url = "http://127.0.0.1:8000/api/"
login_url = base_url + 'auth/token/'
cart_url = base_url + "cart/"


cart_r = requests.get(cart_url)
cart_token = cart_r.json()


cart_url = "http://127.0.0.1:8000/api/cart"

def create_cart_token():
     # create cart
    cart_r = requests.get(cart_url)
    
    # get cart token
    cart_token = cart_r.json()["token"]
    return cart_token


def test_api(email=None, user_auth=None):
    cart_token = create_cart_token()
    #add item to cart
    new_cart_url = cart_url + "?token=" + cart_token + "&item=1&qty=2"
    new_cart_r = requests.get(new_cart_url)
    print("*"*20)
    #print(new_cart_r.text)
    print("*"*20)
    # get user checkout token
    user_checkout_url = "http://127.0.0.1:8000/api/user/checkout/"
    if email: 
        data = {
            "email": email
        }
        u_c_r = requests.post(user_checkout_url, data=data)
        user_checkout_token = u_c_r.json().get("user_checkout_token")
        print("*"*20)
        #print(u_c_r.text)
        print("*"*20)
        addresses = "http://127.0.0.1:8000/api/user/address/list/?checkout_token=" + user_checkout_token
        addresses_r = requests.get(addresses)
        addresses_r_data = addresses_r.json()
        print(addresses_r_data)
        print(len(addresses_r_data))
        if len(addresses_r_data) >=2 :
            b_id = addresses_r_data[0]["id"]
            s_id = addresses_r_data[1]["id"]
            print("*"*20)
            print('b id and shippping id')
            print(b_id)
            print(s_id)
            print("*"*20)
        else: 
            addresses_create = "http://127.0.0.1:8000/api/user/address/create/"
            user_id = 7
            data = {
                "user": user_id, 
                "type": "billing",
                "street": "123 armut street",
                "city": "Berkeley",
                "zipcode": 94522
            }
            addresses_create_r = requests.post(addresses_create, data=data)
            b_id = addresses_create_r.json().get("id")

            data = {
                "user": user_id, 
                "type": "shipping",
                "street": "123 armut street",
                "city": "Berkeley",
                "zipcode": 94522
            }
            addresses_create_r_s = requests.post(addresses_create, data=data)
            s_id = addresses_create_s_r.json().get("id")

        #Checkout
        checkout_url = "http://127.0.0.1:8000/api/checkout/"
        data = {
            "billing_address": b_id,
            "shipping_address": s_id,
            "cart_token": cart_token,
            "checkout_token": user_checkout_token
        }
        #print data
        order = requests.post(checkout_url, data=data)
        #print order.headers
        print(order.text)


test_api('onur@gmail.com')