from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("forms/contact/", views.contact, name="contact"),
    path("forms/newsletter/", views.newsletter, name="newsletter"),
]