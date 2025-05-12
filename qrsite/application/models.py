# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
import hashlib



class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя
    """
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.username


class CreatedQrCodes(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    short_name = models.CharField(max_length=100)
    qr_code = models.ImageField(upload_to='qr_codes/')
    link = models.URLField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    scale = models.IntegerField(default=10)
    is_static = models.BooleanField(default=True)

    def __str__(self):
        return self.short_name


#3) Модель для хранения данных о QR кодах, которые были отсканированы. Хранит данные о QR коде и ссылку на кастомного пользователя, который его создал.

class QRCode(models.Model):
    FORMAT_CHOICES = [
        ('png', 'PNG'),
        ('svg', 'SVG'),
        ('jpg', 'JPG'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='qr_codes')
    title = models.CharField(max_length=255)
    content = models.TextField()
    qr_code = models.ImageField(upload_to='qr_codes/')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='png')
    size = models.IntegerField(default=10)
    is_public = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_dynamic = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class StaticQRCode(QRCode):
    background_image = models.ImageField(upload_to='qr_codes/backgrounds/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} (Статический)"

class DynamicQRCode(QRCode):
    target_url = models.URLField()
    redirect_count = models.IntegerField(default=0)
    
    def get_hashed_user_id(self):
        """Получает хешированный ID пользователя"""
        # Используем соль для дополнительной безопасности
        salt = settings.SECRET_KEY[:8]
        user_id_str = f"{self.user.id}{salt}"
        return hashlib.sha256(user_id_str.encode()).hexdigest()[:16]
    
    def get_redirect_url(self):
        """Получает полный URL для переадресации"""
        hashed_id = self.get_hashed_user_id()
        return f"{settings.SITE_URL}/redirect/{hashed_id}/{self.id}"
    
    def __str__(self):
        return f"{self.title} (Динамический)"
    
    class Meta:
        db_table = 'application_dynamicqrcode'