from .models import Category


def categories(request):
    return {
        "category_objects": Category.objects.prefetch_related("product_set")
        .all()
        .order_by("category_name")
    }
