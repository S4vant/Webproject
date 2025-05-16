from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import QRCode, StaticQRCode, DynamicQRCode
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.conf import settings

class QRCodeTests(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Создаем тестовый статический QR-код
        self.static_qr = StaticQRCode.objects.create(
            user=self.user,
            title='Test Static QR',
            content='https://example.com',
            format='png',
            size=10,
            is_public=True
        )
        
        # Создаем тестовый динамический QR-код
        self.dynamic_qr = DynamicQRCode.objects.create(
            user=self.user,
            title='Test_Dynamic_QR',
            target_url='https://example.com',
            format='png',
            size=10,
            is_public=True

        )
        print('динам',dynamic_qr.qr_code)
        # Создаем клиент для тестирования
        self.client = Client()
        
        # Логиним пользователя
        self.client.login(username='testuser', password='testpass123')

    def test_static_qr_creation(self):
        """Тест создания статического QR-кода"""
        # Создаем тестовый файл для фона
        background_file = SimpleUploadedFile(
            "background.png",
            b"file_content",
            content_type="image/png"
        )
        
        response = self.client.post(reverse('create_static_qr'), {
            'title': 'New_Static_QR',
            'content': 'https://test.com',
            'format': 'png',
            'size': 10,
            'is_public': True,

        })
        print('динам',qr_code)
 
        self.assertTrue(StaticQRCode.objects.filter(title='New_Static_QR').exists())

    def test_dynamic_qr_creation(self):
        """Тест создания динамического QR-кода"""
        response = self.client.post(reverse('create_dynamic_qr'), {
            'title': 'New_Dynamic_QR',
            'target_url': 'https://test.com',
            'format': 'png',
            'size': 10,
            'is_public': True
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(DynamicQRCode.objects.filter(title='New_Dynamic_QR').exists())

    def test_qr_detail_view(self):
        """Тест просмотра деталей QR-кода"""
        # Тест для статического QR-кода
        response = self.client.get(reverse('qr_detail', args=[self.static_qr.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.static_qr.title)
        self.assertContains(response, self.static_qr.content)

        # Тест для динамического QR-кода
        response = self.client.get(reverse('qr_detail', args=[self.dynamic_qr.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.dynamic_qr.title)
        self.assertContains(response, self.dynamic_qr.target_url)

    def test_qr_redirect(self):
        """Тест переадресации с динамического QR-кода"""
        hashed_id = self.dynamic_qr.get_hashed_user_id()
        response = self.client.get(reverse('qr_redirect', args=[hashed_id, self.dynamic_qr.id]))
        self.assertEqual(response.status_code, 302)  # Проверяем редирект
        self.assertEqual(response.url, self.dynamic_qr.target_url)

    def test_qr_delete(self):
        """Тест удаления QR-кода"""
        response = self.client.post(reverse('qr_delete', args=[self.static_qr.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(StaticQRCode.objects.filter(id=self.static_qr.id).exists())

    def test_qr_edit(self):
        """Тест редактирования QR-кода"""
        # Тест редактирования статического QR-кода
        response = self.client.post(reverse('qr_edit', args=[self.static_qr.id]), {
            'title': 'Updated Static QR',
            'content': 'https://updated.com',
            'format': 'png',
            'size': 10,
            'is_public': True
        })
        self.assertEqual(response.status_code, 302)
        updated_qr = StaticQRCode.objects.get(id=self.static_qr.id)
        self.assertEqual(updated_qr.title, 'Updated Static QR')

        # Тест редактирования динамического QR-кода
        response = self.client.post(reverse('qr_edit', args=[self.dynamic_qr.id]), {
            'title': 'Updated Dynamic QR',
            'target_url': 'https://updated.com',
            'is_public': True
        })
        self.assertEqual(response.status_code, 302)
        updated_qr = DynamicQRCode.objects.get(id=self.dynamic_qr.id)
        self.assertEqual(updated_qr.title, 'Updated Dynamic QR')

    def test_unauthorized_access(self):
        """Тест доступа к QR-коду неавторизованным пользователем"""
        # Создаем приватный QR-код
        private_qr = StaticQRCode.objects.create(
            user=self.user,
            title='Private QR',
            content='https://private.com',
            format='png',
            size=10,
            is_public=False
        )
        
        # Создаем другого пользователя
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Логиним другого пользователя
        self.client.login(username='otheruser', password='testpass123')
        
        # Пытаемся получить доступ к приватному QR-коду
        response = self.client.get(reverse('qr_detail', args=[private_qr.id]))
        self.assertEqual(response.status_code, 404)

    def test_qr_views_counter(self):
        """Тест счетчика просмотров QR-кода"""
        initial_views = self.static_qr.views
        # Создаем другого пользователя
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.client.login(username='otheruser', password='testpass123')
        self.client.get(reverse('qr_detail', args=[self.static_qr.id]))
        self.static_qr.refresh_from_db()
        self.assertEqual(self.static_qr.views, initial_views + 1)

    def test_dynamic_qr_redirect_counter(self):
        """Тест счетчика переадресаций динамического QR-кода"""
        initial_redirects = self.dynamic_qr.redirect_count
        hashed_id = self.dynamic_qr.get_hashed_user_id()
        
        # Первая переадресация
        self.client.get(reverse('qr_redirect', args=[hashed_id, self.dynamic_qr.id]))
        self.dynamic_qr.refresh_from_db()
        self.assertEqual(self.dynamic_qr.redirect_count, initial_redirects + 1)
        
        # Вторая переадресация
        self.client.get(reverse('qr_redirect', args=[hashed_id, self.dynamic_qr.id]))
        self.dynamic_qr.refresh_from_db()
        self.assertEqual(self.dynamic_qr.redirect_count, initial_redirects + 2)

    def test_invalid_qr_redirect(self):
        """Тест переадресации с неверным хешем"""
        invalid_hash = 'invalid_hash'
        response = self.client.get(reverse('qr_redirect', args=[invalid_hash, self.dynamic_qr.id]))
        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        # Очищаем созданные файлы после тестов
        for qr in QRCode.objects.all():
            if qr.qr_code:
                file_path = os.path.join(settings.MEDIA_ROOT, qr.qr_code.name)
                if os.path.exists(file_path):
                    os.remove(file_path) 