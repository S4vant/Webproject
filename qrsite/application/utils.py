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
    
    # Если есть фоновое изображение, добавляем его
    if background_image and format != 'svg':
        try:
            # Открываем фоновое изображение
            bg = Image.open(background_image)
            # Изменяем размер фона под размер QR-кода
            bg = bg.resize((img.size[0], img.size[1]))
            # Создаем новое изображение с альфа-каналом
            new_img = Image.new('RGBA', img.size, (255, 255, 255, 0))
            # Накладываем QR-код на фон
            new_img.paste(bg, (0, 0))
            new_img.paste(img, (0, 0), img)
            img = new_img
        except Exception as e:
            print(f"Ошибка при добавлении фонового изображения: {e}")
    
    # Сохраняем в BytesIO
    output = BytesIO()
    if format == 'svg':
        img.save(output, format='SVG')
    else:
        img.save(output, format=format.upper())
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

def create_beatiful_qr(data, background_image, size=10, format='png'):
    try:
        # Создаём QR-код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=size,
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Создаем QR-код с прозрачным фоном
        qr_img = qr.make_image(fill_color="black", back_color=(255,255,255,0)).convert("RGBA")
        
        # Создаем маску для QR-кода
        # Открываем фоновое изображение
        if hasattr(background_image, 'file'):
            bg = Image.open(background_image.file).convert("RGBA")
        else:
            bg = Image.open(background_image).convert("RGBA")

        # Изменяем размер фона под размер QR-кода
        bg = bg.resize(qr_img.size)
        
        img = qr.get_matrix()
        # Создаем новое изображение
        coeff = size
        coeff_small = round(coeff / 3)
        length_qr = len(img) * coeff
        
        background = bg
        back_im = Image.new('RGBA', (length_qr, length_qr), (0, 0, 0, 0))

        # Определение цветов
        black_1 = (0, 0, 0, 0)
        black_2 = (0, 0, 0, 230)
        white_1 = (255, 255, 255, 50)
        white_2 = (255, 255, 255, 230)

        idraw = ImageDraw.Draw(back_im, "RGBA")

        # Рисование QR-кода
        x = 0
        y = 0
        for string in qr.get_matrix():
            for i in string:
                if i:
                    idraw.ellipse(
                        (x + coeff_small, y + coeff_small, x + coeff - coeff_small, y + coeff - coeff_small),
                        fill=black_2
                    )
                else:
                    idraw.ellipse(
                        (x + coeff_small, y + coeff_small, x + coeff - coeff_small, y + coeff - coeff_small),
                        fill=white_2
                    )
                x += coeff
            x = 0
            y += coeff

        # Рисование маркеров позиционирования
        idraw.rectangle((0, 0, coeff * 9, coeff * 9), fill=white_1)
        idraw.rectangle((length_qr - coeff * 9, 0, length_qr, coeff * 9), fill=white_1)
        idraw.rectangle((0, length_qr - coeff * 9, coeff * 9, length_qr), fill=white_1)
        idraw.rectangle(
            (length_qr - coeff * 10, length_qr - coeff * 9, length_qr - coeff * 6, length_qr - coeff * 6),
            fill=white_1
        )

        # Рисование дополнительных элементов
        rectangles = [
            (coeff, coeff, coeff * 8, coeff * 2),  # Верхний горизонтальный
            (length_qr - coeff * 8, coeff, length_qr - coeff, coeff * 2),  # Верхний правый
            (coeff, coeff * 7, coeff * 8, coeff * 8),  # Нижний левый
            (length_qr - coeff * 8, coeff * 7, length_qr - coeff, coeff * 8),  # Нижний правый
            (coeff, length_qr - coeff * 8, coeff * 8, length_qr - coeff * 7),  # Левый вертикальный
            (coeff, length_qr - coeff * 2, coeff * 8, length_qr - coeff),  # Правый вертикальный
            (length_qr - coeff * 8, length_qr - coeff * 8, length_qr - coeff * 7, length_qr - coeff * 7),  # Центральный квадрат
            (coeff * 3, coeff * 3, coeff * 6, coeff * 6),  # Центральный квадрат 2
            (length_qr - coeff * 6, coeff * 3, length_qr - coeff * 3, coeff * 6),  # Центральный квадрат 3
            (coeff * 3, length_qr - coeff * 6, coeff * 6, length_qr - coeff * 3),  # Центральный квадрат 4
            (coeff, coeff, coeff * 2, coeff * 8),  # Левый вертикальный 2
            (coeff * 7, coeff, coeff * 8, coeff * 8),  # Правый вертикальный 2
            (length_qr - coeff * 2, coeff, length_qr - coeff, coeff * 8),  # Правый вертикальный 3
            (length_qr - coeff * 8, coeff, length_qr - coeff * 7, coeff * 8),  # Левый вертикальный 3
            (coeff, length_qr - coeff * 8, coeff * 2, length_qr - coeff),  # Левый вертикальный 4
            (coeff * 7, length_qr - coeff * 8, coeff * 8, length_qr - coeff),  # Правый вертикальный 4
            (length_qr - coeff * 10, length_qr - coeff * 10, length_qr - coeff * 9, length_qr - coeff * 5),  # Нижний правый угол
            (length_qr - coeff * 6, length_qr - coeff * 10, length_qr - coeff * 5, length_qr - coeff * 5),  # Нижний правый угол 2
            (length_qr - coeff * 10, length_qr - coeff * 10, length_qr - coeff * 6, length_qr - coeff * 9),  # Нижний правый угол 3
            (length_qr - coeff * 10, length_qr - coeff * 6, length_qr - coeff * 6, length_qr - coeff * 5)  # Нижний правый угол 4
        ]
        
        for coords in rectangles:
            idraw.rectangle(coords, fill=black_2)

        # Наложение QR-кода на фоновое изображение
        background.paste(back_im, (0, 0), back_im)
        # Сохраняем результат
        output = BytesIO()
        bg.save(output, format=format.upper())
        output.seek(0)
        return output

    except Exception as e:
        print(f"Ошибка при генерации красивого QR-кода: {e}")
        return create_qr_code(data, size, format)