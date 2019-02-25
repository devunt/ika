from django.urls import path

from . import views

urlpatterns = [
    path('message', views.MessageView.as_view()),
]
