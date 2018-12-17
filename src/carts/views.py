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
from carts.serializers import (
    CartItemSerializer, 
    CartVariationSerializer, 
    CheckoutSerializer)
from carts.mixins import TokenMixin, CartUpdateAPIMixin, CartTokenMixin
from rest_framework import status
from orders.models import Order, UserCheckout, UserAddress
from orders.serializers import OrderSerializer, FinalizedOrderSerializer


"""
{
"order_token":"eydvcmRlcl9pZCc6IDEyLCAndXNlcl9jaGVja291dF9pZCc6IDV9",
"payment_method_nonce": "abc1232"
}
"""

class CheckoutFinalizeAPIView(TokenMixin,  APIView):

    def get(self, request, format=None):
        response = {}
        order_token = request.GET.get("order_token")
        if order_token: 
            checkout_id = self.parse_token(order_token).get("user_checkout_id")
            if checkout_id: 
                checkout = UserCheckout.objects.get(id=checkout_id)
                client_token = checkout.get_client_token()
                response["client_token"] = client_token
            response = {
                "data": "data"
            }
            return Response(response)
        else: 
            response["message"] = "This method is not allowed"
            return Response(response, status=status.HTTP_405_METHOD_NOT_ALLOWED)



    def post(self, request, format=None):
        data = request.data
        response = {}
        serializer = FinalizedOrderSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            request_data = serializer.data
            order_id = request_data.get("order_id")
            order = Order.objects.get(id=order_id)
            if not order.is_complete:
                order_total = order.order_total
                nonce = request_data.get("payment_method_nonce")
                if nonce:
                    result = braintree.Transaction.sale({
                        "amount": order_total, 
                        "payment_method_nonce": nonce, 
                        "billing": {
                            "postal_code": f'{order.billing_address.zipcode}',
                        },
                        "options": {
                            "submit_for_settlement": True
                        }
                    })
                    success = result.is_success
                    if success: 
                        order.mark_completed(order_id=result.transaction.id)
                        order.cart.is_complete()
                        response["message"] = "Your order has been completed"
                        response["final_order_id"] = order.order_id
                        response["success"] = True
                    else: 
                        messages.success(request, f'{result.message}')
                        error_message = result.message
                        response["message"] = error_message
                        response["success"] = False
            else: 
                response["message"] = "Orderedn has been already completed"
                response["success"] = False
        return Response(response)


class CheckoutAPIView(CartTokenMixin, APIView):
    def post(self, request, format=None):
        data = request.data
        serializer = CheckoutSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.data
            user_checkout_id = data.get("user_checkout_id")
            cart_id = data.get("cart_id")
            billing_address = data.get("billing_address") 
            shipping_address = data.get("shipping_address") 
 
            user_checkout = UserCheckout.objects.get(id=user_checkout_id)
            cart_obj = Cart.objects.get(id=cart_id)
            s_a = UserAddress.objects.get(id=shipping_address)
            b_a = UserAddress.objects.get(id=billing_address)
            order, created = Order.objects.get_or_create(cart=cart_obj, user=user_checkout)
            if not order.is_complete: 
                order.shipping_address = s_a
                order.billing_address = b_a
                order.save()
                order_data = {
                    "order_id": order.id,
                    "user_checkout_id": user_checkout_id
                }
                order_token = self.create_token(order_data)

        response = {
            "order_token": order_token
        }
        print(self.parse_token(order_token))
        return Response(response)


    # def get(self, request, format=None):
    #     data, cart_obj, response_status = self.get_cart_from_token()
        
    #     user_checkout_token = self.request.GET.get("checkout_token")
    #     user_checkout_data = self.parse_token(user_checkout_token)
    #     user_checkout_id = user_checkout_data.get('user_checkout_id')
    #     billing_address = self.request.GET.get('billing')
    #     shipping_address = self.request.GET.get('shipping')
    #     billing_obj, shipping_obj = None, None
    #     try: 
    #         user_checkout = UserCheckout.objects.get(id=int(user_checkout_id))
    #         print('++',user_checkout)
    #     except: 
    #         user_checkout = None
    #     if not user_checkout: 
    #         data = {
    #             "message": "A user or guest user is required to continue"
    #         }
    #         response_status = status.HTTP_400_BAD_REQUEST
    #         return Response(data, status=response_status)
    #     if billing_address: 
    #         try:
    #             billing_obj = UserAddress.objects.get(user=user_checkout, id=int(billing_address))
    #         except:
    #             print('Something went wrong getting the billing obj')
    #             pass
    #     if shipping_address: 
    #         try:
    #             shipping_obj = UserAddress.objects.get(user=user_checkout, id=int(shipping_address))  
    #         except: 
    #             print('Something went wrong getting the shipping obj')
    #             pass

    #     if not billing_obj or not shipping_obj:
    #         data = {
    #             "message": "A valid billing and shipping is needed"
    #         }
    #         response_status = status.HTTP_400_BAD_REQUEST
    #         return Response(data, status=response_status)
        
    #     if cart_obj: 
    #         if cart_obj.items.count() == 0:
    #             data = {
    #                 "message": "Your cart is empty."
    #             }
    #             response_status = status.HTTP_400_BAD_REQUEST
    #         else: # create an order
    #             order, created = Order.objects.get_or_create(cart=cart_obj)
    #             if not order.user: 
    #                 order.user = user_checkout
    #             if order.is_complete: 
    #                 order.cart.is_complete()
    #                 data = {
    #                     "message": 'This order has been completed'
    #                 }
    #                 return Response(data)
    #             order.billing_address = billing_obj
    #             order.shipping_address = shipping_obj
    #             order.save()
    #             data = OrderSerializer(order).data
    #             # data['order'] = order.id
    #             #data["user"] = order.user
    #             #data["shipping_address"] = order.shipping_address
    #             #data["billing_address"] = order.billing_address
    #             # data["total"] = order.order_total
    #             # data["subtotal"] = cart_obj.total
    #             # data["shipping_order_price"] = order.shipping_total_price

    #     return Response(data, status=response_status)


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
