from django.urls import path

from .views import home, plan_visit

urlpatterns = [
    path("", home, name="home"),
    path("planeje-sua-visita/", plan_visit, name="plan_visit"),
]
