from django.urls import path, re_path, include

from orders.views import (
    UserCheckoutAPI,
    UserAddressCreateAPIView,
    UserAddressListAPIView,
    OrderListAPIView,
    OrderRetrieveAPIView
)

urlpatterns = [
    re_path('^user/checkout/$', UserCheckoutAPI.as_view(), name='user_checkout_api'),
    re_path('^user/address/create/$', UserAddressCreateAPIView.as_view(), name='user_address_create'),
    re_path('^user/address/list/$', UserAddressListAPIView.as_view(), name='user_address_list'),
    re_path('^orders/$', OrderListAPIView.as_view(), name='orders_api'),
    re_path('^orders/(?P<pk>\d+)/$', OrderRetrieveAPIView.as_view(), name='orders_retreive_api'),
]