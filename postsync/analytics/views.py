from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, F, FloatField, Count
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64
from item.models import Item
from django.contrib.auth.models import User

def generate_chart(fig):
    """Helper to convert matplotlib figure to base64"""
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=120)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return image_base64

@login_required
@user_passes_test(lambda u: u.is_staff)
def analytics_dashboard(request):
    # ---- Basic stats ----
    total_users = User.objects.count()
    total_staff = User.objects.filter(is_staff=True).count()
    total_customers = total_users - total_staff

    # # Total stock and sold units using actual_quantity and quantity
    # total_items = Item.objects.aggregate(total=Sum('actual_quantity'))['total'] or 0
    # total_sold_units = Item.objects.aggregate(
    #     total=Sum(F('actual_quantity') - F('quantity'))
    # )['total'] or 0
    # total_unsold_units = total_items - total_sold_units

    # # Total revenue = price * sold_quantity
    # total_revenue = Item.objects.aggregate(
    #     total=Sum(F('price') * (F('actual_quantity') - F('quantity')))
    # )['total'] or 0
    # Total stock and sold units using actual_quantity and quantity
    total_items = max(Item.objects.aggregate(total=Sum('actual_quantity'))['total'] or 0, 0)

    total_sold_units = max(Item.objects.aggregate(
        total=Sum(F('actual_quantity') - F('quantity'))
    )['total'] or 0, 0)

    total_unsold_units = max(total_items - total_sold_units, 0)

    # Total revenue = price * sold_quantity
    total_revenue = max(Item.objects.aggregate(
        total=Sum(F('price') * (F('actual_quantity') - F('quantity')))
    )['total'] or 0, 0)

    # ---- Dates for charts ----
    today = datetime.today()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    date_labels = [d.strftime('%b %d') for d in dates]

    # ---- User Registrations Chart ----
    user_counts = [User.objects.filter(date_joined__date=d.date()).count() for d in dates]
    plt.switch_backend('AGG')
    fig1, ax1 = plt.subplots(figsize=(5, 3))
    ax1.plot(date_labels, user_counts, marker='o', color='#902bf5')  # Primary violet
    ax1.set_title('User Registrations (Last 7 Days)', color='#1a1463')
    ax1.set_xlabel('Date', color='#1a1463')
    ax1.set_ylabel('Users', color='#1a1463')
    ax1.tick_params(axis='x', rotation=30)
    chart_user_registrations = generate_chart(fig1)

    # ---- Sales by Category Chart ----
    category_sales = (
        Item.objects.annotate(
            sold_units=F('actual_quantity') - F('quantity')
        )
        .filter(sold_units__gt=0)
        .values('category__name')
        .annotate(total_sales=Sum('sold_units'))
        .order_by('-total_sales')
    )

    fig2, ax2 = plt.subplots(figsize=(5, 3))
    if category_sales:
        categories = [c['category__name'] for c in category_sales]
        sales = [c['total_sales'] for c in category_sales]
        colors = plt.cm.viridis(range(len(categories)))
        ax2.bar(categories, sales, color=colors)
        ax2.set_title('Sales by Category', color='#1a1463')
        ax2.set_xlabel('Category', color='#1a1463')
        ax2.set_ylabel('Units Sold', color='#1a1463')
        plt.xticks(rotation=30, ha='right')
    else:
        ax2.text(0.5, 0.5, 'No sales data yet', ha='center', va='center', fontsize=12)
    chart_category_sales = generate_chart(fig2)

    # ---- Revenue Trend (Last 7 Days) ----
    revenue_trend = []
    for d in dates:
        daily_revenue = Item.objects.filter(created_at__date=d.date()).aggregate(
            total=Sum(F('price') * (F('actual_quantity') - F('quantity')), output_field=FloatField())
        )['total'] or 0
        revenue_trend.append(daily_revenue)

    fig3, ax3 = plt.subplots(figsize=(5, 3))
    ax3.plot(date_labels, revenue_trend, marker='o', color='#31bacd')  # Accent color
    ax3.set_title('Revenue Trend (Last 7 Days)', color='#1a1463')
    ax3.set_xlabel('Date', color='#1a1463')
    ax3.set_ylabel('Revenue ($)', color='#1a1463')
    chart_revenue_trend = generate_chart(fig3)

    # ---- Sold vs Unsold Pie Chart ----
    fig4, ax4 = plt.subplots(figsize=(4, 4))
    ax4.pie(
        [total_sold_units, total_unsold_units],
        labels=['Sold', 'Unsold'],
        autopct='%1.1f%%',
        colors=['#2ecc71', '#e74c3c'],
        startangle=90
    )
    ax4.set_title('Sold vs Unsold Items', color='#1a1463')
    chart_sold_unsold = generate_chart(fig4)

    # ---- Context ----
    context = {
        'total_users': int(total_users),
        'total_staff': int(total_staff),
        'total_customers': int(total_customers),
        'total_items': int(total_items),
        'sold_items': int(total_sold_units),
        'unsold_items': int(total_unsold_units),
        'total_revenue': total_revenue,
        'chart_user_registrations': chart_user_registrations,
        'chart_category_sales': chart_category_sales,
        'chart_revenue_trend': chart_revenue_trend,
        'chart_sold_unsold': chart_sold_unsold,
    }

    return render(request, 'analytics/dashboard.html', context)
