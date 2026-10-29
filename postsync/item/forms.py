from django import forms
from .models import Item

INPUT_CLASSES = 'w-full py-4 px-6 rounded-xl border'

# class NewItemForm(forms.ModelForm):
#     class Meta:
#         model = Item
#         fields = ['category', 'name', 'description', 'price', 'quantity', 'image']  # 🔹 Added quantity

#         widgets = {
#             'category': forms.Select(attrs={
#                 'class': INPUT_CLASSES
#             }),
#             'name': forms.TextInput(attrs={
#                 'class': INPUT_CLASSES
#             }),
#             'description': forms.Textarea(attrs={
#                 'class': INPUT_CLASSES
#             }),
#             'price': forms.NumberInput(attrs={ 
#                 'class': INPUT_CLASSES
#             }),
#             'quantity': forms.NumberInput(attrs={  
#                 'class': INPUT_CLASSES,
#                 'min': 0,  
#                 'placeholder': 'Enter available stock quantity'
#             }),
#             'image': forms.FileInput(attrs={
#                 'class': INPUT_CLASSES
#             }),
#         }
class NewItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['category', 'name', 'description', 'price', 'quantity', 'actual_quantity', 'image']

        widgets = {
            'category': forms.Select(attrs={'class': INPUT_CLASSES}),
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASSES}),
            'price': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'quantity': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'min': 0,
            }),
            'actual_quantity': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'min': 0,
                'placeholder': 'Enter real stock quantity'
            }),
            'image': forms.FileInput(attrs={'class': INPUT_CLASSES}),
        }


# class EditItemForm(forms.ModelForm):
#     class Meta:
#         model = Item
#         fields = ['category', 'name', 'description', 'price', 'quantity', 'image']  # 🔹 Added quantity

#         widgets = {
#             'category': forms.Select(attrs={
#                 'class': INPUT_CLASSES
#             }),
#             'name': forms.TextInput(attrs={
#                 'class': INPUT_CLASSES
#             }),
#             'description': forms.Textarea(attrs={
#                 'class': INPUT_CLASSES
#             }),
#             'price': forms.NumberInput(attrs={
#                 'class': INPUT_CLASSES
#             }),
            
#             'quantity': forms.NumberInput(attrs={  
#                 'class': INPUT_CLASSES,
#                 'min': 0,
#                 'placeholder': 'Enter available stock quantity'
#             }),
            
#             'image': forms.FileInput(attrs={
#                 'class': INPUT_CLASSES
#             }),
#         }
class EditItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['category', 'name', 'description', 'price', 'quantity', 'actual_quantity', 'image']

        widgets = {
            'category': forms.Select(attrs={'class': INPUT_CLASSES}),
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASSES}),
            'price': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'quantity': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'min': 0,
            }),
            'actual_quantity': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'min': 0,
                'placeholder': 'Enter real stock quantity'
            }),
            'image': forms.FileInput(attrs={'class': INPUT_CLASSES}),
        }
