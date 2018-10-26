import ast 
import base64
from django.shortcuts import get_object_or_404
from products.models import Variation
from carts.models import Cart, CartItem

from rest_framework import status

class TokenMixin(object):
    token = None
    def create_token(self, data_dict):
        """
        Create a data object with the given cart id. 
        Encode and return the token.
        """
        if isinstance(data_dict, dict):
            byte_data = str(data_dict).encode('ascii')
            token = base64.b64encode(byte_data)
            self.token = token 
            return token 
        else: 
            raise ValueError('Please pass a Python Dictionary')

    def parse_token(self, token=None):
        if token is None: 
            return {}
        try: 
            token_decoded_dict = base64.b64decode(token).decode("utf-8") 
            token_dict = ast.literal_eval(token_decoded_dict)
            return token_dict
        except: 
            return {}

class CartUpdateAPIMixin(object):
    
    def update_cart(self, *args, **kwargs):
        """
        Get the item id and update accordingly
            - delete
            - add
            - update the quantity.
        """
        request = self.request
        cart = self.cart 
        if cart: 
            item_id = request.GET.get('item')
            delete_item = request.GET.get('delete', False)
            item_added = False
            if item_id: 
                item_instance = get_object_or_404(Variation, id=item_id)
                qty = int(request.GET.get('qty', 1))
                try: 
                    if qty < 1: 
                        delete_item = True
                except: 
                    raise Http404
                cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item_instance)
                if created: 
                    item_added = True
                if delete_item: 
                    cart_item.delete()
                else:
                    cart_item.quantity = qty
                    cart_item.save()


class CartTokenMixin(TokenMixin, object):
    token_param = 'cart_token'
    token = None
    def get_cart_from_token(self):
        request = self.request
        response_status = status.HTTP_200_OK
        cart_token = request.GET.get(self.token_param)
        
        message = "This requires a valid cart or cart token"
        
        cart_token_data = self.parse_token(cart_token)
        cart_id = cart_token_data.get('cart_id')
        try:
            cart = Cart.objects.get(id=int(cart_id))
        except:
            cart = None
        if cart is None: 
            data = {
                "success": False,
                "message": message
            }
            response_status = status.HTTP_400_BAD_REQUEST
        else:
            self.token = cart_token
            data = {
                "cart": cart.id,
                "success": True
            }
        return data, cart, response_status