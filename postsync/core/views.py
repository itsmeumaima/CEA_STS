from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from postsync.settings import EMAIL_HOST_USER
from .forms import SignUpForm
from django.db.models import Count, Q
from item.models import Item, Category
from django.shortcuts import render, redirect
from django.core.mail import send_mail  # optional if you want to email
from django.contrib import messages


def index(request):
    # Latest 6 unsold items
    items = Item.objects.filter(is_sold=False).order_by('-created_at')[:6]

    # Categories with unsold item counts
    categories = Category.objects.annotate(
        unsold_count=Count('items', filter=Q(items__is_sold=False))
    )

    # Popular items (Python-side sorting)
    all_unsold_items = Item.objects.filter(is_sold=False)
    popular_items = sorted(all_unsold_items, key=lambda x: x.popularity_score, reverse=True)[:8]

    # For hero rotator: top 1 popular item per category
    popular_by_category = []
    for category in categories:
        top_item = category.items.filter(is_sold=False).order_by('-created_at')[:1]
        if top_item.exists():
            popular_by_category.append(top_item.first())

    return render(request, 'core/index.html', {
        'categories': categories,
        'items': items,
        'popular_items': popular_items,
        'popular_by_category': popular_by_category,
    })



def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # Print message to console for debugging
        print(f"New contact message from {name} ({email}): {subject}\n{message}")

        try:
            
            send_mail(
                subject,
                message,
                EMAIL_HOST_USER,  
                ['umaimaabdulrauf702@gmail.com'],  # recipient
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent!")
        except Exception as e:
            print("Email sending failed:", e)
            messages.error(request, "Email sending failed. Please try again later.")

        return redirect("core:contact")

    return render(request, "core/contact.html")


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')
    else:
        form = SignUpForm()

    return render(request, 'core/signup.html', {
        'form': form
    })

@login_required
def logout_view(request):
    logout(request)
    return redirect('core:index')
