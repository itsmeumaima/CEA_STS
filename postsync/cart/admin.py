from django.contrib import admin
from .models import Cart, CartItem, Payment, PaymentItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price')
    search_fields = ('user__username',)
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'item', 'quantity', 'subtotal')
    search_fields = ('cart__user__username', 'item__name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'currency', 'status', 'stripe_payment_intent', 'stripe_session_id', 'created_at')
    search_fields = ('user__username', 'status', 'stripe_payment_intent', 'stripe_session_id')


@admin.register(PaymentItem)
class PaymentItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'item', 'item_name', 'quantity', 'price', 'subtotal')
    search_fields = ('payment__user__username', 'item__name', 'item_name')
