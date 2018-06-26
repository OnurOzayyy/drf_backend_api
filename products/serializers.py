from rest_framework import serializers

from .models import Category, Product


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='category_detail-api')
    product_set = ProductSerializer(many=True)
    class Meta:
        model = Category
        fields = [
            "id",
            "url",
            "title",
            "description",
            "slug",
            "active",
            "product_set"]
