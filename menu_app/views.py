from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.contrib import messages

# Models + Forms
from .models import Item, Order, OrderItem
from .forms import RegisterForm, ItemForm


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------
def home(request):
    return render(request, 'home.html')


def menu_redirect(request):
    return redirect('home')


# ---------------------------------------------------------
# SESSION CART HELPERS
# ---------------------------------------------------------
def _get_cart(request):
    return request.session.get('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


# ---------------------------------------------------------
# MENU PAGE
# ---------------------------------------------------------
@login_required(login_url='login')
def menu_list(request):
    items = Item.objects.all()

    # Search
    q = request.GET.get("q")
    if q:
        items = items.filter(name__icontains=q)

    # Category filter
    selected_category = request.GET.get("category")
    if selected_category and selected_category != "":
        items = items.filter(category=selected_category)

    # Only available filter
    available_only = request.GET.get("available_only")
    if available_only == "on":
        items = items.filter(available=True)

    # Distinct categories
    categories = Item.objects.values_list("category", flat=True).distinct()

    # Cart Summary
    cart = _get_cart(request)
    total = Decimal("0.00")

    for item_id, qty in cart.items():
        try:
            item = Item.objects.get(id=item_id)
            total += item.price * qty
        except Item.DoesNotExist:
            pass

    return render(request, "menu.html", {
        "items": items,
        "categories": categories,
        "selected_category": selected_category,
        "cart_total": total,
        "cart_count": sum(cart.values()),
        "form": request.GET,
    })


# ---------------------------------------------------------
# QUICK VIEW / MODAL AJAX FETCH
# ---------------------------------------------------------
def quick_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return JsonResponse({
        "id": item.id,
        "name": item.name,
        "price": float(item.price),
        "rating": item.rating,
        "category": item.category,
        "description": item.description,
        "image": item.image.url if item.image else None,
    })


# ---------------------------------------------------------
# CART
# ---------------------------------------------------------
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id, available=True)
    cart = _get_cart(request)
    cart[str(item_id)] = cart.get(str(item_id), 0) + 1
    _save_cart(request, cart)
    return redirect('menu_list')


def update_cart(request, item_id, action):
    cart = _get_cart(request)
    key = str(item_id)

    if key in cart:
        if action == "inc":
            cart[key] += 1
        elif action == "dec":
            cart[key] -= 1
            if cart[key] <= 0:
                del cart[key]

    _save_cart(request, cart)
    return redirect('cart_view')


def remove_from_cart(request, item_id):
    cart = _get_cart(request)
    cart.pop(str(item_id), None)
    _save_cart(request, cart)
    return redirect('cart_view')


def cart_view(request):
    cart = _get_cart(request)
    cart_items = []
    total = Decimal("0.00")

    for item_id, qty in cart.items():
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            continue

        line_total = item.price * qty
        total += line_total

        cart_items.append({
            "item": item,
            "quantity": qty,
            "line_total": line_total,
        })

    return render(request, 'cart.html', {"cart_items": cart_items, "total": total})


# ---------------------------------------------------------
# ORDER
# ---------------------------------------------------------
@login_required
def place_order(request):
    cart = _get_cart(request)
    if not cart:
        return redirect('menu_list')

    order = Order.objects.create(user=request.user, total_price=0)
    total = Decimal("0.00")

    for item_id, qty in cart.items():
        item = get_object_or_404(Item, id=item_id)
        OrderItem.objects.create(order=order, item=item, quantity=qty)
        total += item.price * qty

    order.total_price = total
    order.save()

    _save_cart(request, {})
    return render(request, 'order_success.html', {'order': order})


# ---------------------------------------------------------
# TRACK ORDER (ADVANCED UI)
# ---------------------------------------------------------
@login_required
def track_order_advanced(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if not (request.user == order.user or request.user.is_staff):
        return HttpResponseForbidden("You cannot view this order.")
    return render(request, "track_order_advanced.html", {"order": order})


# ---------------------------------------------------------
# STATUS API (USER TRACKING AJAX POLLING)
# ---------------------------------------------------------
def order_status_api(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return JsonResponse({
        "status": order.status,
        "updated_at": order.created_at.isoformat(),
    })


# ---------------------------------------------------------
# ADMIN — UPDATE ORDER STATUS VIA AJAX
# ---------------------------------------------------------
@user_passes_test(lambda u: u.is_staff)
@require_POST
def update_order_status_api(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get("status")

    valid = ["Pending", "Preparing", "Ready", "Completed"]
    if new_status not in valid:
        return JsonResponse({"ok": False, "error": "Invalid status"}, status=400)

    order.status = new_status
    order.save()
    return JsonResponse({"ok": True, "status": new_status})


# ---------------------------------------------------------
# ADMIN QUICK STATUS UPDATE (URL BASED)
# ---------------------------------------------------------
@user_passes_test(lambda u: u.is_staff)
def update_order_status(request, order_id, new_status):
    valid = ["Pending", "Preparing", "Ready", "Completed"]
    order = get_object_or_404(Order, id=order_id)

    if new_status in valid:
        order.status = new_status
        order.save()

    return redirect("dashboard")


# ---------------------------------------------------------
# ADMIN — TOGGLE ITEM AVAILABLE / UNAVAILABLE
# ---------------------------------------------------------
@user_passes_test(lambda u: u.is_staff)
def toggle_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.available = not item.available
    item.save()
    return redirect('manage_items')








# ---------------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------------
@user_passes_test(lambda u: u.is_staff)
def dashboard(request):
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_items = Item.objects.count()
    total_users = Order.objects.values("user").distinct().count()

    recent_orders = Order.objects.order_by('-created_at')[:10]

    top_items = (
        OrderItem.objects.values('item__name')
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty')[:5]
    )

    sales_per_day = (
        Order.objects.extra({'date': "DATE(created_at)"})
        .values('date')
        .annotate(total=Sum('total_price'))
        .order_by('date')
    )

    return render(request, 'dashboard.html', {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_items': total_items,
        'total_users': total_users,
        'recent_orders': recent_orders,
        'top_items': top_items,
        'sales_per_day': sales_per_day,
    })


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'auth/register.html', {'form': form})


# ---------------------------------------------------------
# ADMIN ITEM MANAGEMENT
# ---------------------------------------------------------
@user_passes_test(lambda u: u.is_staff)
def manage_items(request):
    items = Item.objects.all().order_by('name')
    return render(request, 'items/manage_list.html', {'items': items})


@user_passes_test(lambda u: u.is_staff)
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_items')
    else:
        form = ItemForm()

    return render(request, 'items/item_form.html', {'form': form, 'is_edit': False})


@user_passes_test(lambda u: u.is_staff)
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('manage_items')
    else:
        form = ItemForm(instance=item)

    return render(request, 'items/item_form.html', {'form': form, 'is_edit': True, 'item': item})


