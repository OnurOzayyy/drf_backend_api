from django.urls import path, re_path, include

from products.views import (
    CategoryListAPIView,
    CategoryRetrieveAPIView,
    ProductListAPIView,
    ProductRetrieveAPIView
    )

urlpatterns = [
    re_path('^api/categories/$', CategoryListAPIView.as_view(), name='categories_api'),
    re_path('^api/categories/(?P<pk>\d+)/$', CategoryRetrieveAPIView.as_view(), name='category_detail-api'),
    re_path('^api/products/$', ProductListAPIView.as_view(), name='products_api'),
    re_path('^api/products/(?P<pk>\d+)/$', ProductRetrieveAPIView.as_view(), name='product_detail-api'),
]
