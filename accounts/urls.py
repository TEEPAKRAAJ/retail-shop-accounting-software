from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('sales/', views.add_sale, name='add_sale'),
    path('bills/', views.add_bill, name='add_bill'),
    path('logout/', views.logout_view, name='logout'),
]
