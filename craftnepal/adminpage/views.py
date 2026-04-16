from django.shortcuts import render
from django.http import HttpResponse
from shop.models import *


# Create your views here.
def adminhome(request):
    return render(request, "admins/dashboard.html")


def productlist(request):
    product = Product.objects.all()
    return render(request, "admins/productlist.html", {"product": product})
