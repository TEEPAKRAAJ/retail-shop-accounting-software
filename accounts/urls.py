from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('sales/add/', views.add_sale, name='add_sale'),
    path('logout/', views.logout_view, name='logout'),
]
