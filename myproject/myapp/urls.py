from django.urls import path
from . import views

urlpatterns = [
    path('',views.product_list, name='product_list'),
    path('product/<int:id>/',views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/',views.add_to_cart, name='add_to_cart'),
    path('delete-from-cart/<int:product_id>/',views.delete_from_cart, name='delete_from_cart'),
    path('update-cart/<int:product_id>/',views.update_cart, name='update_cart'),
    path('cart/',views.view_cart, name='view_cart'),
    path('register/',views.register, name='register'),
    path('my-orders/',views.my_orders, name='my_orders'),
    path('order-confirmation/<int:order_id>/',views.order_confirmation, name='order_confirmation'),
    path('checkout/',views.checkout, name='checkout'),
    
    
]
