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
from carts.serializers import CartItemSerializer, CartVariationSerializer, CheckoutSerializer

from carts.mixins import TokenMixin, CartUpdateAPIMixin, CartTokenMixin
from rest_framework import status
from orders.models import Order, UserCheckout
from orders.serializers import OrderSerializer


class CheckoutAPIView(CartTokenMixin, APIView):
    def post(self, request, format=None):
        data = request.data
        serializer = CheckoutSerializer(data=data)
        if serializer.is_valid(raise_exception=True): 
            print(serializer.data)
        
        response = {
            "data": "none"
        }
        return Response(response)


    def get(self, request, format=None):
        data, cart_obj, response_status = self.get_cart_from_token()
        
        user_checkout_token = self.request.GET.get("checkout_token")
        user_checkout_data = self.parse_token(user_checkout_token)
        user_checkout_id = user_checkout_data.get('user_checkout_id')
        billing_address = self.request.GET.get('billing')
        shipping_address = self.request.GET.get('shipping')
        billing_obj, shipping_obj = None, None
        try: 
            user_checkout = UserCheckout.objects.get(id=int(user_checkout_id))
            print('++',user_checkout)
        except: 
            user_checkout = None
        if not user_checkout: 
            data = {
                "message": "A user or guest user is required to continue"
            }
            response_status = status.HTTP_400_BAD_REQUEST
            return Response(data, status=response_status)
        if billing_address: 
            try:
                billing_obj = UserAddress.objects.get(user=user_checkout, id=int(billing_address))
            except:
                print('Something went wrong getting the billing obj')
                pass
        if shipping_address: 
            try:
                shipping_obj = UserAddress.objects.get(user=user_checkout, id=int(shipping_address))  
            except: 
                print('Something went wrong getting the shipping obj')
                pass

        if not billing_obj or not shipping_obj:
            data = {
                "message": "A valid billing and shipping is needed"
            }
            response_status = status.HTTP_400_BAD_REQUEST
            return Response(data, status=response_status)
        
        if cart_obj: 
            if cart_obj.items.count() == 0:
                data = {
                    "message": "Your cart is empty."
                }
                response_status = status.HTTP_400_BAD_REQUEST
            else: # create an order
                order, created = Order.objects.get_or_create(cart=cart_obj)
                if not order.user: 
                    order.user = user_checkout
                if order.is_complete: 
                    order.cart.is_complete()
                    data = {
                        "message": 'This order has been completed'
                    }
                    return Response(data)
                order.billing_address = billing_obj
                order.shipping_address = shipping_obj
                order.save()
                data = OrderSerializer(order).data
                # data['order'] = order.id
                #data["user"] = order.user
                #data["shipping_address"] = order.shipping_address
                #data["billing_address"] = order.billing_address
                # data["total"] = order.order_total
                # data["subtotal"] = cart_obj.total
                # data["shipping_order_price"] = order.shipping_total_price

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
        
        if cart_obj == None or not cart_obj.active: 
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
