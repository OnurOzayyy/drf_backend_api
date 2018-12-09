from django.urls import path, re_path, include

from orders.views import (
    UserCheckoutAPI,
    UserAddressCreateAPIView,
    UserAddressListAPIView 
)

urlpatterns = [
    re_path('^user/checkout/$', UserCheckoutAPI.as_view(), name='user_checkout_api'),
    re_path('^user/address/create/$', UserAddressCreateAPIView.as_view(), name='user_address_create'),
    re_path('^user/address/list/$', UserAddressListAPIView.as_view(), name='user_address_list'),
]