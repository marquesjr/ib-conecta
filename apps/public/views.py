from django.shortcuts import render


def home(request):
    return render(request, "public/home.html")


def plan_visit(request):
    return render(request, "public/plan_visit.html")
