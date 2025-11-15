"""
dashboard/urls.py - URL Configuration LENGKAP dengan Payment Integration
Replace file dashboard/urls.py Anda dengan file ini
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'dashboard'

urlpatterns = [
    # ==================== PUBLIC PAGES ====================
    path('', views.index, name='index'),
    path('products/', views.products, name='products'),
    path('products/<slug:slug>/', views.product_detail, name='product-detail'),
    path('about/', views.about, name='about'),
    path('kontak/', views.kontak, name='kontak'),
    
    # ==================== AUTHENTICATION ====================
    path('masuk/', views.masuk, name='masuk'),
    path('registrasi/', views.registrasi, name='registrasi'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password Reset (using Django's built-in views)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='dashboard/password_reset.html',
             email_template_name='dashboard/password_reset_email.html',
             subject_template_name='dashboard/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='dashboard/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='dashboard/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='dashboard/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    # ==================== CART ====================
    path('cart/', views.view_cart, name='view-cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update-cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove-from-cart'),
    path('cart/clear/', views.clear_cart, name='clear-cart'),
    path('cart/apply-coupon/', views.apply_coupon, name='apply-coupon'),
    
    # ==================== CHECKOUT & PAYMENT (MIDTRANS) ====================
    path('checkout/', views.checkout, name='checkout'),
    path('payment/create/', views.create_payment, name='payment-create'),
    path('payment/notification/', views.payment_notification, name='payment-notification'),
    path('payment/finish/', views.payment_finish, name='payment-finish'),
    
    # ==================== ORDERS ====================
    path('orders/', views.order_list, name='order-list'),
    path('orders/<int:pk>/', views.order_detail, name='order-detail'),
    
    # ==================== USER PROFILE ====================
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile-edit'),
    
    # ==================== REVIEWS ====================
    path('products/<int:product_id>/review/', views.add_review, name='add-review'),
]