from django.urls import path
from . import views

urlpatterns = [
    
    path('login/', views.xero_login, name='xero_login'),
    path('callback/', views.xero_callback, name='xero_callback'),
    path('data/', views.xero_data, name='xero_data'),
]