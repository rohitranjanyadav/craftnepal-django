import json
import uuid

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django_esewa import EsewaPayment

from .models import Order, Product


# Create your views here.
def index(request):
    product_objects = Product.objects.all()
    hero_images = list(
        Product.objects.exclude(image__isnull=True)
        .exclude(image__exact="")
        .values_list("image", flat=True)
        .distinct()[:20]
    )

    # Search Code
    item_name = request.GET.get("item_name")
    selected_category = request.GET.get("category")

    if item_name != "" and item_name is not None:
        product_objects = product_objects.filter(title__icontains=item_name)

    if selected_category:
        product_objects = product_objects.filter(category__category_name=selected_category)

    # Paginator Code
    paginator = Paginator(product_objects, 4)
    page = request.GET.get("page")
    product_objects = paginator.get_page(page)

    return render(
        request,
        "shop/index.html",
        {
            "product_objects": product_objects,
            "hero_images": hero_images,
        },
    )


def detail(request, id):
    product_object = Product.objects.get(id=id)
    return render(request, "shop/detail.html", {"product_object": product_object})


def checkout(request):
    if request.method == "POST":
        payment_method = request.POST.get("payment_method", "")
        if payment_method not in {"Cash On Delivery", "Esewa"}:
            messages.add_message(request, messages.ERROR, "Please select a valid payment method.")
            return redirect("/checkout/")

        if not request.user.is_authenticated:
            messages.add_message(request, messages.ERROR, "Please log in to place an order.")
            return redirect("/auth/login/")

        cart_raw = request.POST.get("cart_items", "{}")
        try:
            cart = json.loads(cart_raw) if cart_raw else {}
        except json.JSONDecodeError:
            cart = {}

        if not cart:
            messages.add_message(request, messages.ERROR, "Your cart is empty.")
            return redirect("/checkout/")

        contact_no = request.POST.get("contact_no", "")
        address = request.POST.get("address", "")
        email = request.POST.get("email", "")

        created_orders = []
        total_amount = 0
        transaction_uuid = str(uuid.uuid4())[:10] if payment_method == "Esewa" else ""
        for product_id, item in cart.items():
            if not isinstance(item, list) or len(item) < 5:
                continue

            quantity = int(item[0] or 0)
            line_total = float(item[4] or 0)
            if quantity <= 0:
                continue

            product = Product.objects.filter(id=product_id).first()
            if not product:
                continue

            order = Order.objects.create(
                product=product,
                total_price=int(line_total),
                quantity=quantity,
                payment_method=payment_method,
                user=request.user,
                contact_no=contact_no,
                address=address,
                email=email,
                payment_status="Pending",
                transaction_uuid=transaction_uuid,
            )
            total_amount += line_total
            created_orders.append(order)

        if not created_orders:
            messages.add_message(request, messages.ERROR, "Could not create the order. Please try again.")
            return redirect("/checkout/")

        if payment_method == "Esewa":
            total_amount = sum(order.total_price for order in created_orders)
            success_url = request.build_absolute_uri(f"/payment/success/{transaction_uuid}/")
            failure_url = request.build_absolute_uri(f"/payment/failure/{transaction_uuid}/")
            payment = EsewaPayment(
                product_code="EPAYTEST",
                success_url=success_url,
                failure_url=failure_url,
                amount=total_amount,
                tax_amount=0.0,
                total_amount=total_amount,
                product_delivery_charge=0.0,
                product_service_charge=0.0,
                transaction_uuid=transaction_uuid,
                secret_key="8gBm/:&EnhH.1/q",
            )
            payment.signature = payment.create_signature()
            return render(
                request,
                "shop/esewa_payment.html",
                {"form": payment.generate_form()},
            )

        return redirect("/myorder/")

    return render(request, "shop/checkout.html")


def payment_success(request, uid):
    orders = Order.objects.filter(transaction_uuid=uid, payment_method="Esewa")
    if not orders.exists():
        messages.error(request, "Transaction not found.")
        return redirect("/checkout/")

    total_amount = sum(order.total_price for order in orders)
    success_url = request.build_absolute_uri(f"/payment/success/{uid}/")
    failure_url = request.build_absolute_uri(f"/payment/failure/{uid}/")
    payment = EsewaPayment(
        product_code="EPAYTEST",
        success_url=success_url,
        failure_url=failure_url,
        amount=total_amount,
        tax_amount=0.0,
        total_amount=total_amount,
        product_delivery_charge=0.0,
        product_service_charge=0.0,
        transaction_uuid=uid,
        secret_key="8gBm/:&EnhH.1/q",
    )

    if payment.is_completed(dev=True):
        orders.update(payment_status="Completed")
        messages.success(request, f"Transaction Completed: {uid}")
        return render(request, "shop/payment_success.html", {"transaction_uuid": uid})

    return redirect(f"/payment/failure/{uid}/")


def payment_failure(request, uid):
    orders = Order.objects.filter(transaction_uuid=uid, payment_method="Esewa")
    if orders.exists():
        orders.update(payment_status="Failed")

    messages.error(request, f"Transaction Failed: {uid}")
    return render(request, "shop/payment_failure.html", {"transaction_uuid": uid})


def myorder(request):
    if not request.user.is_authenticated:
        return redirect("/auth/login/")

    orders = (
        Order.objects.filter(user=request.user)
        .select_related("product")
        .order_by("-id")
    )
    return render(request, "shop/myorder.html", {"orders": orders})


