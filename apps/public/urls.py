from django.urls import path

from .views import contribute, home, know_church, plan_visit, prayer_request, privacy

urlpatterns = [
    path("", home, name="home"),
    path("planeje-sua-visita/", plan_visit, name="plan_visit"),
    path("pedido-de-oracao/", prayer_request, name="prayer_request"),
    path("quero-conhecer/", know_church, name="know_church"),
    path("contribuicoes/", contribute, name="contribute"),
    path("privacidade/", privacy, name="privacy"),
]
