from django.contrib.auth.decorators import login_required
from django.shortcuts import render,get_object_or_404, redirect
from django.db.models import Q
from .forms import NewItemForm, EditItemForm
from .models import Item, Category

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User

# Create your views here.
from django.shortcuts import render
from django.core.paginator import Paginator

def items(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category')
    sort = request.GET.get('sort')
    page = request.GET.get('page', 1)  # get current page

    items = Item.objects.all()

    # Search
    if query:
        items = items.filter(name__icontains=query)
        
    # BUG FOR TESTING: search term is ignored
    # if query:
        #     items = items.filter(name__icontains="THIS_ITEM_SHOULD_NOT_EXIST_12345")

    # Category filter
    if category_id and category_id.isdigit():
        items = items.filter(category_id=int(category_id))

    # Sorting logic
    if sort == 'price_low':
        items = items.order_by('price')
    elif sort == 'price_high':
        items = items.order_by('-price')
    elif sort == 'name':
        items = items.order_by('name')
    else:
        items = items.order_by('-created_at')

    # Pagination
    paginator = Paginator(items, 6)  # show 6 items per page
    page_obj = paginator.get_page(page)

    categories = Category.objects.all()

    return render(request, 'item/items.html', {
        'items': page_obj,  # paginated items
        'query': query,
        'categories': categories,
        'category_id': category_id,
        'sort': sort,
        'page_obj': page_obj,
    })



def detail(request, pk):
    item=get_object_or_404(Item, pk=pk)
    related_items=Item.objects.filter(category=item.category,is_sold=False).exclude(pk=pk)[0:3]
    return render(request, 'item/detail.html',{
        'item':item,
        'related_items':related_items
    })

@login_required
def new(request):
    if request.method == 'POST':
        form = NewItemForm(request.POST, request.FILES)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect('item:detail', pk=item.id)
    else:
        form = NewItemForm()

    return render(request, 'item/form.html', {
        'form': form,
        'title': 'Create Item',
    })

@login_required
def delete(request,pk):
    item=Item.objects.get(pk=pk, created_by=request.user)

    item.delete()
    return redirect('dashboard:index')

@login_required
def edit(request, pk):
    item = get_object_or_404(Item, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = EditItemForm(request.POST, request.FILES, instance=item)

        if form.is_valid():
            form.save()

            return redirect('item:detail', pk=item.id)
    else:
        form = EditItemForm(instance=item)

    return render(request, 'item/form.html', {
        'form': form,
        'title': 'Edit item',
    })

def item_to_dict(item):
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "category": item.category_id,
        "quantity": item.quantity,
        "actual_quantity": item.actual_quantity,
        "is_sold": item.is_sold,
        "created_by": item.created_by_id,
    }


@csrf_exempt
@require_http_methods(["POST"])
def api_create_item(request):
    try:
        data = json.loads(request.body)
        category = Category.objects.get(pk=data["category"])
        user = User.objects.get(pk=data["created_by"])

        item = Item.objects.create(
            name=data["name"],
            description=data.get("description", ""),
            price=float(data["price"]),
            category=category,
            created_by=user,
            quantity=int(data.get("quantity", 0)),
            actual_quantity=int(data.get("actual_quantity", 0)),
            is_sold=data.get("is_sold", False),
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return JsonResponse({"error": "Invalid input"}, status=400)
    except (Category.DoesNotExist, User.DoesNotExist):
        return JsonResponse(
            {"error": "Invalid category or user"}, status=400
        )

    return JsonResponse(item_to_dict(item), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def api_item_detail(request, pk):
    try:
        item = Item.objects.get(pk=pk)
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(item_to_dict(item))

    if request.method == "PUT":
        try:
            data = json.loads(request.body)

            if "name" in data:
                item.name = data["name"]
            if "description" in data:
                item.description = data["description"]
            if "price" in data:
                item.price = float(data["price"])
            if "category" in data:
                item.category = Category.objects.get(pk=data["category"])
            if "quantity" in data:
                item.quantity = int(data["quantity"])
            if "actual_quantity" in data:
                item.actual_quantity = int(data["actual_quantity"])
            if "is_sold" in data:
                item.is_sold = data["is_sold"]

            item.save()

        except (json.JSONDecodeError, TypeError, ValueError):
            return JsonResponse({"error": "Invalid input"}, status=400)
        except Category.DoesNotExist:
            return JsonResponse(
                {"error": "Invalid category"}, status=400
            )

        return JsonResponse(item_to_dict(item))

    item.delete()
    return JsonResponse({"message": "Item deleted successfully"})
