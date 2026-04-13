from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('api/paypal/order/create/', views.create_order, name='create_order'),
    path('api/paypal/order/<str:order_id>/capture/', views.capture_order, name='capture_order'),
]