from django.shortcuts import render

from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse


from .serializers import CategorySerializer, ProductSerializer, ProductDetailSerializer
from .models import Category, Product
from .filters import ProductFilter

class APIHomeView(APIView):
    def get(self, request, format=None):
        """
        Home page view. Display: 
            - Product count, url
            - Category count, url
        """

        data = {
            "auth": {
                "login_url": reverse("auth_login_api", request=request),
                "refresh_url": reverse("refresh_token_api", request=request),
                "user_checkout": reverse("user_checkout_api", request=request)
            },
            "address": {
                "url": reverse("user_address_list", request=request),
                "create": reverse("user_address_create", request=request)
            },
            "checkout": {
                "cart": reverse("cart_api", request=request),
                "checkout": reverse("checkout_api", request=request),
                "finalize": reverse("checkout_api_finalize", request=request)
            },
            "products": {
                "count": Product.objects.all().count(),
                "url": reverse("products_api", request=request)
            },
            "categories": {
                "count": Category.objects.all().count(), 
                "url": reverse("categories_api",request=request)
            },
            "orders": {
                "url": reverse("orders_api",request=request),
            }
        }
        return Response(data)

class ProductListAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
                       filters.SearchFilter,
                       filters.OrderingFilter,
                       DjangoFilterBackend 
                       ]
    search_fields = ["title", "description"]
    filter_class = ProductFilter

class ProductRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer


class CategoryListAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryRetrieveAPIView(generics.RetrieveAPIView):
    #authentication_classes = [SessionAuthentication]
    #permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
