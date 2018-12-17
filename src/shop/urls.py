"""shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include, re_path

from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from carts.views import CartAPIView, CheckoutAPIView, CheckoutFinalizeAPIView


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api/product/', include('products.urls')),
    re_path(r'api/cart/$', CartAPIView.as_view(), name='cart_api'),
    re_path(r'api/checkout/$', CheckoutAPIView.as_view(), name='checkout_api'),
    re_path(r'api/checkout/finalize/$', CheckoutFinalizeAPIView.as_view(), name='checkout_api_finalize'),
    re_path(r'^api/', include('orders.urls')),
    re_path(r'^api/auth/token/$', obtain_jwt_token),
    re_path(r'^api/auth/token/refresh/$', refresh_jwt_token)
]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

