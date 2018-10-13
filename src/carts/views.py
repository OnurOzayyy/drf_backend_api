from django.shortcuts import render

from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from carts.models import Cart

class CartAPIView(APIView):

    def get_cart(self):
        cart_id = self.request.GET.get("cart_id")
        try: 
            cart = Cart.objects.get(id=cart_id)
        except: 
            cart = Cart.objects.all().first()
        return cart 

    def get(self, request, format=None):
        """
        """
        cart = self.get_cart()

        data = {
            "cart": cart.id, 
            "total": cart.total,
            "subtotal": cart.subtotal, 
            "tax_total": cart.tax_total, 
            "items": cart.items.count()
        }
        return Response(data)
