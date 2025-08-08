from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('sales/', views.add_sale, name='add_sale'),
    path('bills/', views.add_bill, name='add_bill'),
    path('credits/', views.add_credit, name='add_credit'),
    path('login/', views.login_view, name='login'),
    path('search/', views.search, name='search'),
    path('monthly_report/', views.monthly_report, name='monthly_report'),
    path('monthly_report_pdf/', views.monthly_report_pdf, name='monthly_report_pdf'),
    path('yearly_report/', views.yearly_report, name='yearly_report'),
    path('yearly_report_pdf/', views.yearly_report_pdf, name='yearly_report_pdf'),
    path('logout/', views.logout_view, name='logout'),
    path('delete_transaction/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('delete_credit_log/<int:log_id>/', views.delete_credit_log, name='delete_credit_log'),
    path('load_more_transactions/', views.load_more_transactions, name='load_more_transactions'),
]
