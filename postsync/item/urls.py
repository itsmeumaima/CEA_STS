
from django.urls import path
from . import views

app_name = "item"

urlpatterns = [
    # API routes
    path("api/", views.api_create_item, name="api_create"),
    path("api/<int:pk>/", views.api_item_detail, name="api_detail"),

    # Existing website routes
    path("", views.items, name="items"),
    path("new/", views.new, name="new"),
    path("<int:pk>/", views.detail, name="detail"),
    path("<int:pk>/delete/", views.delete, name="delete"),
    path("<int:pk>/edit/", views.edit, name="edit"),
]
