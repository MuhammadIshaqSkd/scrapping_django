
from django.urls import path
from scrapping import views
urlpatterns = [
    path("", views.Login.as_view()),
    path("dashboard", views.Dashboard.as_view()),
    path("migrations", views.Migrations.as_view()),
]