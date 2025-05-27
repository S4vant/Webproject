# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
import hashlib

#Кастомная модель пользователя

class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя
    """
    email = models.EmailField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.username

#2) Модель для хранения данных о QR кодах, которые были отсканированы. Хранит данные о QR коде и ссылку на кастомного пользователя, который его создал.

class QRCode(models.Model):
    FORMAT_CHOICES = [
        ('png', 'PNG'),
        ('svg', 'SVG'),
        ('jpg', 'JPG'),
        ('pdf', 'PDF'),
    ]
    
    def qr_code_upload_path(instance, filename):
        filename = filename.replace(' ', '_').replace('"', '')
        return f'qr_codes/{instance.user.id}/{filename}'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='qr_codes')
    title = models.CharField(max_length=255)
    content = models.TextField()
    qr_code = models.ImageField(upload_to=qr_code_upload_path)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='png')
    size = models.IntegerField(default=10)
    is_public = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_dynamic = models.BooleanField(default=False)
    background_image = models.ImageField(upload_to='qr_codes/backgrounds/', blank=True, null=True)
    hash_id = models.CharField(max_length=12, unique=True, blank=True, null=True)
    


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала сохраняем, чтобы появился self.id
        if not self.hash_id:
            self.hash_id = hashlib.sha1(f'{self.id}'.encode()).hexdigest()[:10]
            super().save(update_fields=['hash_id'])  # сохраняем хеш отдельно    
    
    def get_hashed_qr_id(self):
        """Получает хешированный ID QR-кода"""
        # Используем соль для дополнительной безопасности
        salt = settings.SECRET_KEY[:8]  # Используем ту же длину соли, что и в DynamicQRCode
        qr_id_str = f"{self.id}{salt}"
        return hashlib.sha256(qr_id_str.encode()).hexdigest()[:16]
    
    class Meta:
        ordering = ['-created_at']


class StaticQRCode(QRCode):
    

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
        url = f"{settings.SITE_URL}/redirect/{hashed_id}/{self.id}"
        print(f"Generated URL in model: {url}")
        print(f"SITE_URL: {settings.SITE_URL}")
        print(f"hashed_id: {hashed_id}")
        print(f"qr_id: {self.id}")
        return url
    
    def __str__(self):
        return f"{self.title} (Динамический)"
    
    class Meta:
        db_table = 'application_dynamicqrcode'