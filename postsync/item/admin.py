from django.contrib import admin
from .models import Category, Item


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Show all relevant fields
    search_fields = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'name', 
        'category', 
        'description', 
        'price', 
        'quantity',
        'actual_quantity', 
        'is_sold', 
        'created_by', 
        'created_at',
        'popularity_score', 
        'get_popularity_tier'
    )
    list_filter = ('category', 'is_sold', 'created_at')  # Filter sidebar
    search_fields = ('name', 'category__name', 'created_by__username')
    readonly_fields = ('popularity_score', 'get_popularity_tier')  # Computed fields

