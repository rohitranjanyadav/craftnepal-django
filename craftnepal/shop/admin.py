from django.contrib import admin
from .models import Product, Order, Category

# Register your models here.
admin.site.site_header = "Craft Nepal"
admin.site.site_title = "Craft Nepal"
admin.site.index_title = "Manage Craft Nepal"


class ProductAdmin(admin.ModelAdmin):

    def change_category_to_default(self, request, queryset):
        queryset.update(category="default")

    change_category_to_default.short_description = "Set category to default"
    list_display = (
        "title",
        "price",
        "discount_price",
        "category",
        "description",
    )
    search_fields = (
        "title",
        "category",
    )
    actions = ("change_category_to_default",)
    list_editable = ("category","price","discount_price")


admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(Category)
