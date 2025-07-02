from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import StyledAuthenticationForm

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('sales/', views.add_sale, name='add_sale'),
    path('bills/', views.add_bill, name='add_bill'),
    path('credits/', views.add_credit, name='add_credit'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
