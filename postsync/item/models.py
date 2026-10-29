from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Item(models.Model):
    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    image = CloudinaryField('image', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    actual_quantity = models.PositiveIntegerField(default=0)  
    is_sold = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='items', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    # ----------------------
    # POPULARITY SCORE LOGIC
    # ----------------------
    def calculate_popularity_score(self):
        """
        Popularity is calculated using 3 factors:
        1. Quantity left   -> lower quantity = more popular
        2. Sold status     -> sold items get higher score
        3. Recency         -> newly created items get boost
        """

        # 1. Quantity score (0.4 weight)
        if self.quantity > 0:
            quantity_score = (1 - min(self.quantity, 100) / 100) * 100 * 0.4
        else:
            quantity_score = 100 * 0.4  # sold out = max score

        # 2. Sold status score (0.3 weight)
        sales_score = 100 * 0.3 if self.is_sold else 0

        # 3. Recency score (0.3 weight)
        days_since_creation = (timezone.now() - self.created_at).days
        recency_factor = max(0, (30 - days_since_creation) / 30)
        recency_score = recency_factor * 100 * 0.3

        return quantity_score + sales_score + recency_score

    @property
    def popularity_score(self):
        """Returns final popularity score (0–100) rounded to 2 decimals"""
        return round(self.calculate_popularity_score(), 2)

    def get_popularity_tier(self):
        """Categorize items by popularity: High / Medium / Low"""
        score = self.popularity_score
        if score >= 70:
            return "High"
        elif score >= 40:
            return "Medium"
        return "Low"
