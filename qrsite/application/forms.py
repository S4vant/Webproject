# application/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from .models import CustomUser, StaticQRCode, DynamicQRCode, QRCode

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    
    class Meta:
        model = User
        fields = ('username',  'password1', 'password2')
    
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
        ('pdf', 'PDF'),
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
        ('pdf', 'PDF'),
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
        model = DynamicQRCode
        fields = ('title','target_url',  'size', 'format', 'is_public')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'target_url': forms.TextInput(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EditDynamicQRForm(forms.ModelForm):
    class Meta:
        model = DynamicQRCode
        fields = ['title', 'target_url', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'target_url': forms.URLInput(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Текущий пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='Подтверждение нового пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = get_user_model()
        fields = ('old_password', 'new_password1', 'new_password2')

class EditStaticQRForm(forms.ModelForm):
    """Форма для редактирования статического QR-кода"""
    class Meta:
        model = StaticQRCode
        
        fields = ['title', 'content',  'is_public', 'background_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            # 'format': forms.Select(attrs={'class': 'form-control'}),
            # 'size': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'background_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
