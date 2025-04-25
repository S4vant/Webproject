from django.shortcuts import redirect
from django.http import HttpResponseNotFound
from application.models import DynamicQRCode

def handle_qr_redirect(qr_id):
    """
    Обработка перенаправления по динамическому QR-коду
    """
    try:
        qr = DynamicQRCode.objects.get(id=qr_id)
        qr.redirect_count += 1
        qr.save()
        return redirect(qr.target_url)
    except DynamicQRCode.DoesNotExist:
        return HttpResponseNotFound("QR-код не найден")

def get_redirect_stats(qr_id):
    """
    Получение статистики по перенаправлениям
    """
    try:
        qr = DynamicQRCode.objects.get(id=qr_id)
        return {
            'total_redirects': qr.redirect_count,
            'last_redirect': qr.updated_at if hasattr(qr, 'updated_at') else None,
            'target_url': qr.target_url
        }
    except DynamicQRCode.DoesNotExist:
        return None 