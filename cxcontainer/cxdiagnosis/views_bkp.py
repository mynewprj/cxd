from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseNotFound
def hello(request):
    return HttpResponse("<h2>Hello, Welcome to Django!</h2>")
def client_user(request):
    return render(request, "clientuser/client.html")
