import qrcode
from PIL import Image, ImageDraw
from pyzbar.pyzbar import decode
from pathlib import Path
from typing import Optional, Union


def read_qr_code(path_to_download: Union[str, Path]) -> Optional[str]:
    """
    Читает QR-код из изображения.
    
    Args:
        path_to_download: Путь к изображению с QR-кодом
        
    Returns:
        str: Декодированный текст из QR-кода или None в случае ошибки
    """
    try:
        img = Image.open(path_to_download)
        decoded = decode(img)
        if decoded:
            return decoded[0].data.decode("utf-8")
        return None
    except Exception as e:
        print(f"Ошибка при чтении QR-кода: {e}")
        return None


def gen_qr_code(
    text: str, 
    path_to_download: Union[str, Path], 
    path_to_save: Optional[Union[str, Path]] = None
) -> bool:
    """
    Генерирует QR-код с заданным текстом и накладывает его на фоновое изображение.
    
    Args:
        text: Текст для кодирования в QR-код
        path_to_download: Путь к фоновому изображению
        path_to_save: Путь для сохранения результата (опционально)
        
    Returns:
        bool: True если операция успешна, False в случае ошибки
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=100,
            border=1,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.get_matrix()

        coeff = 20
        coeff_small = round(coeff / 3)
        length_qr = len(img) * coeff
        
        background = Image.open(path_to_download).resize((length_qr, length_qr)).convert("RGBA")
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
                    idraw.rectangle(
                        (x + coeff_small, y + coeff_small, x + coeff - coeff_small, y + coeff - coeff_small),
                        fill=black_2
                    )
                else:
                    idraw.rectangle(
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
        
        # Сохранение результата
        save_path = path_to_save if path_to_save is not None else path_to_download
        background.save(save_path)
        return True
        
    except Exception as e:
        print(f"Ошибка при генерации QR-кода: {e}")
        return False

