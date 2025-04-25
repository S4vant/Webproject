# application/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import CustomUser, StaticQRCode, DynamicQRCode, QRCode

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')

class StaticQRCodeForm(forms.ModelForm):
    background_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Загрузите изображение для фона QR-кода (не поддерживается для SVG)'
    )
    
    class Meta:
        model = StaticQRCode
        fields = ['title', 'content', 'size', 'format', 'is_public', 'background_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'size': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 40}),
            'format': forms.Select(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['format'].choices = [
            ('png', 'PNG'),
            ('svg', 'SVG'),
            ('jpg', 'JPG'),
        ]
        self.fields['qr_type'].initial = 'static'
        self.fields['qr_type'].widget = forms.HiddenInput()

class DynamicQRCodeForm(forms.ModelForm):
    background_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Загрузите изображение для фона QR-кода (не поддерживается для SVG)'
    )
    
    class Meta:
        model = DynamicQRCode
        fields = ['title', 'target_url', 'size', 'format', 'is_public', 'background_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'target_url': forms.URLInput(attrs={'class': 'form-control'}),
            'size': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 40}),
            'format': forms.Select(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['format'].choices = [
            ('png', 'PNG'),
            ('svg', 'SVG'),
            ('jpg', 'JPG'),
        ]
        self.fields['qr_type'].initial = 'dynamic'
        self.fields['qr_type'].widget = forms.HiddenInput()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class StaticQRForm(forms.ModelForm):
    FORMAT_CHOICES = [
        ('png', 'PNG'),
        ('svg', 'SVG'),
        ('jpg', 'JPG'),
    ]
    
    size = forms.IntegerField(
        min_value=1,
        max_value=40,
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите размер от 1 до 40'
        }),
        label='Размер QR-кода',
        help_text='Чем больше число, тем больше размер QR-кода (рекомендуется от 5 до 15)'
    )
    
    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Формат'
    )
    
    class Meta:
        model = QRCode
        fields = ('title', 'content', 'size', 'format', 'is_public')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DynamicQRForm(forms.ModelForm):
    FORMAT_CHOICES = [
        ('png', 'PNG'),
        ('svg', 'SVG'),
        ('jpg', 'JPG'),
    ]
    
    size = forms.IntegerField(
        min_value=1,
        max_value=40,
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите размер от 1 до 40'
        }),
        label='Размер QR-кода',
        help_text='Чем больше число, тем больше размер QR-кода (рекомендуется от 5 до 15)'
    )
    
    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Формат'
    )
    
    class Meta:
        model = QRCode
        fields = ('title', 'content', 'size', 'format', 'is_public')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.URLInput(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }