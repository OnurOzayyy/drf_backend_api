from rest_framework import serializers

from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='category_detail-api')
    class Meta:
        model = Category
        fields = '__all__'
