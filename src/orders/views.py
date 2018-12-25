from django.shortcuts import render

from django.contrib.auth import get_user_model

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from .models import UserCheckout, UserAddress, Order
from .serializers import UserAddressSerializer, OrderSerializer, OrderDetailSerializer

from carts.mixins import TokenMixin
User = get_user_model()

from .permissions import IsOwnerandAuth

class OrderRetrieveAPIView(RetrieveAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsOwnerandAuth]
    model = Order 
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer

    def get_queryset(self, *args, **kwargs):
        return Order.objects.filter(user__user=self.request.user)

class OrderListAPIView(ListAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsOwnerandAuth]
    model = Order
    serializer_class = OrderDetailSerializer
    queryset = Order.objects.all()

    def get_queryset(self, *args, **kwargs):
        return Order.objects.filter(user__user=self.request.user)

class UserAddressCreateAPIView(CreateAPIView):
    model = UserAddress 
    serializer_class = UserAddressSerializer

class UserAddressListAPIView(TokenMixin, ListAPIView):
    model = UserAddress 
    queryset = UserAddress.objects.all()
    serializer_class = UserAddressSerializer

    def get_queryset(self, *args, **kwargs):
        user_checkout_token = self.request.GET.get("checkout_token")
        user_checkout_data = self.parse_token(user_checkout_token)
        user_checkout_id = user_checkout_data.get('user_checkout_id')
        if self.request.user.is_authenticated:
            return UserAddress.objects.filter(user__user=self.request.user)
        elif user_checkout_id:
            return UserAddress.objects.filter(user__id=int(user_checkout_id))
        else: 
            return []

class UserCheckoutMixin(TokenMixin, object):
    
    def user_failure(self, message=None):
        """
        Return a dictionary with a given message or default message.
        """
        data = {
            "message": "There was an error. Please try again", 
            "success": False
        }
        if message: 
            data['message'] = message
        return data
    
    def get_checkout_data(self, user=None, email=None):
        """
        Return the checkout data. 
        """
        if email and not user: 
            user_exists = User.objects.filter(email=email).count()
            print('user_exists', user_exists)
            if user_exists != 0:
                return self.user_failure(message="This user already exists, please login.")        
        
        data = {}
        user_checkout = None
        
        if user and not email: 
            if user.is_authenticated:
                user_checkout = UserCheckout.objects.get_or_create(user=user, email=user.email)[0] #(instance, created)
        elif email: 
            try: 
                user_checkout = UserCheckout.objects.get_or_create(email=email)[0]
                if user: 
                    user_checkout.user = user
                    user_checkout.save()
                    print('user:', user)
            except: 
                pass
        else: 
            pass
            
        if user_checkout:
            data["success"] = True
            data['braintree_id'] = user_checkout.get_braintree_id
            data['user_checkout_id'] = user_checkout.id
            data['user_checkout_token'] = self.create_token(data)

            del data["braintree_id"]
            del data["user_checkout_id"]
            data['braintree_client_token'] = user_checkout.get_client_token()
            
        return data
    
class UserCheckoutAPI(UserCheckoutMixin, APIView):
    
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        """
        Get request for the user checkout. 
        """
        data = self.get_checkout_data(user=request.user)
        return Response(data)

    def post(self, request, format=None):
        """
        Post request for the user checkout. 
        """
        data = {}
        email = request.data.get('email')
      
        if request.user.is_authenticated:
            if email == request.user.email:
                data = self.get_checkout_data(user=request.user, email=email)
            else:
                data = self.get_checkout_data(user=request.user)
        elif email and not request.user.is_authenticated:
            data = self.get_checkout_data(email=email)
        else:
            data = self.user_failure(message="Make sure you are authenticated or using a valid email")
        return Response(data)