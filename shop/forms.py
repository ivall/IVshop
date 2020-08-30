from django import forms

from shop.models import Product


class ProductDescriptionForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['product_description']
        labels = {
            "product_description": "Opis produktu"
        }
