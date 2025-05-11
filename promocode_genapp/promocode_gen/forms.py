from django import forms
from .models import PromoSubmission

class PromoForm(forms.ModelForm):
    class Meta:
        model = PromoSubmission
        fields = ['name', 'email', 'contact', 'address']