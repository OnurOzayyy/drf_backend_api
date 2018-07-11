from django.urls import path, re_path, include

from products.views import (
    CategoryListAPIView,
    CategoryRetrieveAPIView,
    ProductListAPIView,
    ProductRetrieveAPIView,
    APIHomeView
    )

urlpatterns = [
    re_path('^home/$', APIHomeView.as_view(), name='home_view_api'),
    re_path('^categories/$', CategoryListAPIView.as_view(), name='categories_api'),
    re_path('^categories/(?P<pk>\d+)/$', CategoryRetrieveAPIView.as_view(), name='category_detail-api'),
    re_path('^products/$', ProductListAPIView.as_view(), name='products_api'),
    re_path('^products/(?P<pk>\d+)/$', ProductRetrieveAPIView.as_view(), name='product_detail-api'),
]
