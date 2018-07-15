from django.urls import path, re_path, include

from orders.views import (
    UserCheckoutAPI
    
)

urlpatterns = [
    re_path('^user/checkout/$', UserCheckoutAPI.as_view(), name='user_checkout_api'),
   
]