from django.shortcuts import render

from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from carts.models import Cart, CartItem
import base64
import ast
from django.shortcuts import get_object_or_404
from products.models import Variation
from django.http import HttpResponseRedirect, Http404, JsonResponse
from carts.serializers import CartItemSerializer, CartVariationSerializer

from carts.mixins import TokenMixin, CartUpdateAPIMixin


class CartAPIView(TokenMixin, CartUpdateAPIMixin, APIView):
    token = None
    cart = None

    # def create_token(self, cart_id):
    #     """
    #     Create a data object with the given cart id. 
    #     Encode and return the token.
    #     """
    #     data = {
    #         "cart_id": cart_id
    #     }
    #     byte_data = str(data).encode('ascii')
    #     token = base64.b64encode(byte_data)
    #     self.token = token 
    #     return token 
        
    def get_cart(self):
        """
        Get the token from the url. 
        if token is valid: 
            - decode
            - get cart id
            - get the cart object
        if not: 
            create a cart object
            associcate is with the user if exists
            save the cart and create a token for the cart
        return the cart object.
        """
        token_data = self.request.GET.get('token')
        cart_obj = None
        if token_data:
            token_dict = self.parse_token(token=token_data)
            cart_id = token_dict.get('cart_id')
            try: 
                cart_obj = Cart.objects.get(id=cart_id)
            except: 
                pass
            self.token = token_data
        
        if cart_obj == None: 
            cart = Cart()
            cart.tax_percentage = 0.075
            if self.request.user.is_authenticated: 
                cart.user = self.request.user
            cart.save()
            data = {
                "cart_id": cart.id
            }
            self.create_token(data)
            cart_obj = cart 
        return cart_obj

    def get(self, request, format=None):
        """
        get the cart object.
        return the data. 
        """
        cart = self.get_cart()
        self.cart = cart 
        self.update_cart()
        items = CartItemSerializer(cart.cartitem_set.all(), many=True)
        data = {
            "cart": cart.id, 
            "total": cart.total,
            "subtotal": cart.subtotal, 
            "tax_total": cart.tax_total, 
            "token": self.token,
            "items": items.data, 
            "count": cart.items.count()
        }
        return Response(data)
