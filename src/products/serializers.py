from rest_framework import serializers

from .models import Category, Product


class ProductSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='product_detail-api')
    image =serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = [
            "id",
            "url",
            "title",
            "price",
            "image"
        ]
    def get_image(self, obj):
        return obj.productimage_set.first().image.url

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
