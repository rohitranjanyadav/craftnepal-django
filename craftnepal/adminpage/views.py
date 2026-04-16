from django.shortcuts import render,redirect
from shop.models import *
from shop.forms import *
from django.contrib import messages


# Create your views here.
def adminhome(request):
    return render(request, "admins/dashboard.html")


def productlist(request):
    product = Product.objects.all()
    return render(request, "admins/productlist.html", {"product": product})


def addproduct(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Product Added Successfully")
            return redirect("/admins/addproduct")
        else:
            messages.add_message(request, messages.ERROR, "Error Adding Product")
            return render(request, "admins/addproduct.html", {"form": form})
    
    forms = {
        "form": ProductForm
    }
    
    return render(request,'admins/addproduct.html',forms)

def categorylist(request):
    category = Category.objects.all()
    return render(request, "admins/categorylist.html", {"category": category})


def addcategory(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Category Added Successfully")
            return redirect("/admins/addcategory")
        else:
            messages.add_message(request, messages.ERROR, "Error Adding Category")
            return render(request, "admins/addcategory.html", {"form": form})
    
    forms = {
        "form": CategoryForm
    }
    
    return render(request,'admins/addcategory.html',forms)