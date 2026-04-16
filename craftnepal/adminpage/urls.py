from django.urls import path
from .views import *

urlpatterns = [
    path("", adminhome, name="admins"),
    path("productlist/", productlist, name="productlist"),
    path("addproduct/", addproduct, name="addproduct"),
    path('categorylist/', categorylist, name='categorylist'),
    path('addcategory/', addcategory, name='addcategory'),
]
