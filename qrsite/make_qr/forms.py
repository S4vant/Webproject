from django import forms
from .models import StaticQRCode, DynamicQRCode

class StaticQRCodeForm(forms.ModelForm):
    class Meta:
        model = StaticQRCode
        fields = ['title', 'description', 'content', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DynamicQRCodeForm(forms.ModelForm):
    class Meta:
        model = DynamicQRCode
        fields = ['title', 'description', 'target_url', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'target_url': forms.URLInput(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        } 