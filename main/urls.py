"""
URL configuration for url_shortener_project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from shortener import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shorturls/', views.create_short_url, name='create-short-url'),
    path('shorturls/<str:shortcode>', views.get_short_url_stats, name='get-short-url-stats'),  
    path('<str:shortcode>', views.redirect_to_long_url, name='redirect-to-long-url'),
]
