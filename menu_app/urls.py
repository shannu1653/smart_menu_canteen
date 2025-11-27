from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .api_views import items_list, orders_list


urlpatterns = [

    # -------------------------
    # HOME
    # -------------------------
    path('', views.home, name='home'),


    # -------------------------
    # AUTHENTICATION
    # -------------------------
    path('login/', 
         auth_views.LoginView.as_view(template_name='auth/login.html'), 
         name='login'),

    path('logout/', 
         auth_views.LogoutView.as_view(next_page='home'), 
         name='logout'),

    path('register/', views.register_view, name='register'),


    # -------------------------
    # STANDARD MENU + CART
    # -------------------------
    path('menu/', views.menu_list, name='menu_list'),
    path('cart/', views.cart_view, name='cart_view'),

    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('place-order/', views.place_order, name='place_order'),


    # -------------------------
    # ADMIN CONTROLS
    # -------------------------
    path('toggle-item/<int:item_id>/', views.toggle_item, name='toggle_item'),
    path('dashboard/', views.dashboard, name='dashboard'),


    # -------------------------
    # ITEMS CRUD (Admin)
    # -------------------------
    path('items/manage/', views.manage_items, name='manage_items'),
    path('items/add/', views.item_create, name='item_create'),
    path('items/<int:pk>/edit/', views.item_edit, name='item_edit'),


    # -------------------------
    # APIs
    # -------------------------
    path('api/items/', items_list, name='api_items'),
    path('api/orders/', orders_list, name='api_orders'),
    

    path("order/<int:order_id>/status/<str:new_status>/", 
     views.update_order_status, 
     name="update_order_status"),
     
     # menu_app/urls.py (append)
     path("track/<int:order_id>/", views.track_order_advanced, name="track_order_advanced"),
     path("order-status/<int:order_id>/", views.order_status_api, name="order_status_api"),
     path("order/<int:order_id>/status/", views.update_order_status_api, name="update_order_status_api"),



    
]
