import qrcode
from PIL import Image, ImageDraw, ImageOps
import os
from django.conf import settings
from datetime import datetime
import qrcode.image.svg
from io import BytesIO
from django.http import HttpResponse

def create_qr_code(data, size=10, format='png', background_image=None, fill_color='black', back_color='white'):
    """
    Создает QR-код с возможностью добавления фонового изображения
    
    Args:
        data (str): Данные для кодирования в QR-код
        size (int): Размер QR-кода (1-40)
        format (str): Формат выходного файла (png, svg, jpg)
        background_image (str): Путь к фоновому изображению
        fill_color (str): Цвет QR-кода
        back_color (str): Цвет фона
    
    Returns:
        BytesIO: Поток с изображением QR-кода
    """
    # Создаем QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Генерируем QR-код в зависимости от формата
    if format == 'svg':
        factory = qrcode.image.svg.SvgPathImage
        img = qr.make_image(image_factory=factory, fill_color=fill_color, back_color=back_color)
    else:
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
    
    # Если указано фоновое изображение
    if background_image and format != 'svg':  # SVG не поддерживает фоновые изображения
        try:
            # Открываем фоновое изображение
            bg_img = Image.open(background_image)
            
            # Изменяем размер фонового изображения под размер QR-кода
            bg_img = bg_img.resize((img.size[0], img.size[1]))
            
            # Создаем маску для QR-кода
            mask = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rectangle((0, 0, img.size[0], img.size[1]), fill=255)
            
            # Накладываем QR-код на фоновое изображение
            bg_img.paste(img, (0, 0), mask)
            img = bg_img
            
        except Exception as e:
            print(f"Ошибка при добавлении фонового изображения: {e}")
    
    # Преобразуем формат 'JPG' в 'JPEG'
    if format.lower() == 'jpg':
        format = 'JPEG'
    
    # Сохраняем результат в BytesIO
    output = BytesIO()
    if format == 'svg':
        img.save(output)
    else:
        img.save(output, format=format.upper())  # Убедитесь, что формат передается в верхнем регистре
    output.seek(0)
    
    return output

def save_qr_code(qr_code, user, title, qr_type, format='png'):
    """
    Сохраняет QR-код в медиафайлы
    
    Args:
        qr_code (BytesIO): Поток с изображением QR-кода
        user (User): Пользователь, создавший QR-код
        title (str): Название QR-кода
        qr_type (str): Тип QR-кода (static/dynamic)
        format (str): Формат файла
    
    Returns:
        str: Путь к сохраненному файлу
    """
    # Создаем директорию для QR-кодов пользователя, если её нет
    user_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes', str(user.id))
    os.makedirs(user_dir, exist_ok=True)
    
    # Генерируем имя файла
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{title}_{timestamp}.{format}"
    filepath = os.path.join('qr_codes', str(user.id), filename)
    full_path = os.path.join(settings.MEDIA_ROOT, filepath)
    
    # Сохраняем файл
    with open(full_path, 'wb') as f:
        f.write(qr_code.getvalue())
    
    return filepath

def generate_static_qr(content, size=10, format='png', background_image=None):
    """
    Генерирует статический QR-код
    
    Args:
        content (str): Содержимое QR-кода
        size (int): Размер QR-кода
        format (str): Формат выходного файла
        background_image (str): Путь к фоновому изображению
    
    Returns:
        BytesIO: Поток с изображением QR-кода
    """
    return create_qr_code(
        data=content,
        size=size,
        format=format,
        background_image=background_image
    )

def generate_dynamic_qr(target_url, size=10, format='png', background_image=None):
    """
    Генерирует динамический QR-код
    
    Args:
        target_url (str): URL для перенаправления
        size (int): Размер QR-кода
        format (str): Формат выходного файла
        background_image (str): Путь к фоновому изображению
    
    Returns:
        BytesIO: Поток с изображением QR-кода
    """
    return create_qr_code(
        data=target_url,
        size=size,
        format=format,
        background_image=background_image
    )

def download_qr_code(qr_code, filename):
    """
    Создает HttpResponse для скачивания QR-кода
    
    Args:
        qr_code (BytesIO): Поток с изображением QR-кода
        filename (str): Имя файла для скачивания
    
    Returns:
        HttpResponse: Ответ с файлом для скачивания
    """
    response = HttpResponse(qr_code.getvalue(), content_type=f'image/{qr_code.format}')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response