from django.urls import path
from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.custdashboard, name='customer'),
    path('profile', views.cprofile, name='cprofile'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_detail/<str:order_number>/', views.order_detail, name='order_detail'),
]