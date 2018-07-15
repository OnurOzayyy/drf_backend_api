from django.shortcuts import render

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response


from .models import UserCheckout

class UserCheckoutMixin(object):
    def get_checkout_data(self, user=None, email=None):
        data = {}
        if user.is_authenticated:
            user_checkout = UserCheckout.objects.get_or_create(user=user)[0] #(instance, created)
            data['token'] = user_checkout.get_client_token()
            data['braintree_id'] = user_checkout.get_braintree_id
        return data
    
class UserCheckoutAPI(UserCheckoutMixin, APIView):
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        data = self.get_checkout_data(user=request.user)
        return Response(data)

