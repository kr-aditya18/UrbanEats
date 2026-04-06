from django.urls import path
from . import views
from accounts import views as AccountViews
urlpatterns = [
    path('',AccountViews.custdashboard, name = 'customer'),
    
    path('profile',views.cprofile,name = 'cprofile')
]
