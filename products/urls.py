from django.urls import path, re_path, include

from products.views import CategoryAPIListView

urlpatterns = [
    re_path('^api/categories/$', CategoryAPIListView.as_view(), name='categories_api'),
]
