from django import forms
from store.models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image', 'category', 'brand', 'section']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }