from django.shortcuts import render

from rest_framework import generics
from .serializers import CategorySerializer

from .models import Category

class CategoryAPIListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
