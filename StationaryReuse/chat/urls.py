from django.contrib import admin
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.message_inbox, name = "message_inbox"),
    path('<int:receiver_id>/', views.text_person, name="text_person"),
]