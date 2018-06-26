from django.urls import path, re_path, include

from products.views import (
    CategoryListAPIView,
    CategoryRetrieveAPIView )

urlpatterns = [
    re_path('^api/categories/$', CategoryListAPIView.as_view(), name='categories_api'),
    re_path('^api/categories/(?P<pk>\d+)/$', CategoryRetrieveAPIView.as_view(), name='category_detail-api'),
]
