from django.conf import settings
from django.urls import path, include
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeListView.as_view(), name='home'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('add_coupon/', views.add_coupon, name='add_coupon'),
    path('payment/<payment_option>/', views.PaymentView.as_view(), name='payment'),
    path('product/<slug>/', views.ProouctDetailView.as_view(), name='product'),
    path('add_to_cart/<slug>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<slug>/',
         views.remove_from_cart, name='remove_from_cart'),
    path('remove_single_from_cart/<slug>/',
         views.remove_single_from_cart, name='remove_single_from_cart'),

]
