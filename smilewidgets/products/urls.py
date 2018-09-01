from django.urls import path

from . import views

app_name = 'products'
urlpatterns = [
    path('get-price', views.get_price, name='get_price'),
]