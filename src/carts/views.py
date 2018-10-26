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

from carts.mixins import TokenMixin, CartUpdateAPIMixin, CartTokenMixin
from rest_framework import status

class CheckoutAPIView(CartTokenMixin, APIView):
    def get(self, request, format=None):
        data, cart_obj, response_status = self.get_cart_from_token()
        if cart_obj: 
            if cart_obj.items.count() == 0:
                data = {
                    "message": "Your cart is empty."
                }
                response_status = status.HTTP_400_BAD_REQUEST
            else: # create an order.
                pass
        return Response(data, status=response_status)


class CartAPIView(CartTokenMixin, CartUpdateAPIMixin, APIView):
    cart = None
    token_param = 'token'
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
        data, cart_obj, response_status =self.get_cart_from_token()
        
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
