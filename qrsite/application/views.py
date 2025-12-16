from django.contrib.auth import logout, login, authenticate, update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404, HttpResponseBadRequest, JsonResponse, HttpResponseRedirect

from django.utils import timezone
from django.conf import settings
from .forms import CustomUserCreationForm, StaticQRForm, DynamicQRForm, ProfileForm, CustomPasswordChangeForm, EditDynamicQRForm, EditStaticQRForm
from .models import QRCode, StaticQRCode, DynamicQRCode
from .utils import save_qr_code, create_qr_code, create_beatiful_qr
from .decorators import login_required
import os
import hashlib
import urllib.parse
import logging

# Создаём логгер
logger = logging.getLogger(__name__)

def register(request):
    """
    Регистрация нового пользователя
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('home')
    else:
        
        form = CustomUserCreationForm()
        for err in form.errors:
            raise JsonResponse({'error': form.errors[err][0]}, status=400)
    
    return render(request, 'registration/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def login_view(request):
    """
    Вход пользователя в систему
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему!')
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    
    return render(request, 'registration/login.html')


def index(request):
    return render(request, 'home.html')

def showcase(request):
    # Получаем последние 8 публичных QR кодов
    latest_qr_codes = QRCode.objects.filter(is_public=True).order_by('-created_at')[:8]
    return render(request, 'showcase.html', {'latest_qr_codes': latest_qr_codes})

@login_required
def profile(request):
    qr_codes = QRCode.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'qr_codes': qr_codes})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})


@login_required
def create_static_qr(request):
    """
    Создание статического QR-кода
    """    
 
    form = StaticQRForm()

    return render(request, 'create_static_qr.html', {'form': form})

@login_required
def create_dynamic_qr(request):
    """
    Создание динамического QR-кода
    """
    
    form = DynamicQRForm()
    
    return render(request, 'create_dynamic_qr.html', {'form': form})

def qr_detail(request, qr_id):
    # Сначала пытаемся получить динамический QR-код
    try:
        qr = DynamicQRCode.objects.get(id=qr_id)
    except DynamicQRCode.DoesNotExist:
        # Если не найден, пробуем получить статический
        try:
            qr = QRCode.objects.get(id=qr_id)
        except QRCode.DoesNotExist:
            raise Http404("QR-код не найден")
    
    # Определяем тип данных для отображения
    if isinstance(qr, DynamicQRCode):
        qr_data = qr.target_url
        redirect_count = qr.redirect_count
    else:
        qr_data = qr.content
        redirect_count = None
    
    # Проверка доступа
    if not qr.is_public and request.user != qr.user:
        raise Http404("QR-код не найден")
    
    # Увеличение счетчика просмотров
    if request.user != qr.user:
        qr.views += 1
        qr.last_viewed = timezone.now()
        qr.save()
    
    context = {
        'qr': qr,
        'is_static': isinstance(qr, StaticQRCode),
        'is_dynamic': isinstance(qr, DynamicQRCode),
        'qr_data': qr_data,
        'redirect_count': redirect_count,
    }
    return render(request, 'qr_detail.html', context)

@login_required
def download_qr(request, qr_id):
    qr = get_object_or_404(QRCode, id=qr_id)
    
    # Проверяем, имеет ли пользователь доступ к скачиванию
    if not qr.is_public and qr.user != request.user:
        messages.error(request, 'У вас нет прав для скачивания этого QR-кода')
        return redirect('qr_detail', qr_id=qr_id)
    
    try:
        # Получаем путь к файлу
        file_path = os.path.join(settings.MEDIA_ROOT, qr.qr_code.name)
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл QR-кода не найден: {file_path}")
        
        # Определяем правильный MIME-тип
        mime_types = {
            'png': 'application/octet-stream',
            'jpg': 'application/octet-stream',
            'jpeg': 'application/octet-stream',
            'svg': 'application/octet-stream',
            'pdf': 'application/octet-stream'
        }
        content_type = mime_types.get(qr.format.lower(), 'application/octet-stream')
        
        # Открываем файл и отправляем его
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            
            # Формируем имя файла
            filename = f"{qr.title}.{qr.format}"
            
            # Кодируем имя файла для корректного отображения в браузере
            encoded_filename = urllib.parse.quote(filename)
            
            # Устанавливаем заголовки для принудительного скачивания
            response['Content-Disposition'] = f'attachment; filename="{encoded_filename}"'
            response['Content-Length'] = os.path.getsize(file_path)
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response
            
    except Exception as e:
        messages.error(request, f'Ошибка при скачивании QR-кода: {str(e)}')
        return redirect('qr_detail', qr_id=qr_id)

@login_required
def qr_delete(request, qr_id):
    try:
        qr = DynamicQRCode.objects.get(id=qr_id)
       
    except DynamicQRCode.DoesNotExist:
        # Если не найден, пробуем получить статический
        try:
            qr = QRCode.objects.get(id=qr_id)
        except QRCode.DoesNotExist:
            raise Http404("QR-код не найден")
    if request.method == 'POST':
        if request.user != qr.user and not request.user.is_staff:
            messages.error(request, 'Вы не имеете отношения к этому QR-коду')
            return redirect('qr_detail', qr_id=qr_id)
        qr.delete()
        messages.success(request, 'QR-код успешно удален')
        return redirect('profile')
    
    return render(request, 'qr_confirm_delete.html', {'qr': qr})

@login_required
def qr_edit(request, qr_id):
    try:
        qr = DynamicQRCode.objects.get(id=qr_id)
    except DynamicQRCode.DoesNotExist:
        # Если не найден, пробуем получить статический
        try:
            qr = QRCode.objects.get(id=qr_id)
        except QRCode.DoesNotExist:
            raise Http404("QR-код не найден")
    
    # Проверяем, имеет ли пользователь доступ к редактированию
    if qr.user != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого QR-кода')
        return redirect('home')
    is_dynamic = 1 if qr.is_dynamic else 0
    
    if request.method == 'POST':
        if is_dynamic:
            form = EditDynamicQRForm(request.POST, instance=qr)
            qr_data = qr.target_url
            redirect_count = qr.redirect_count
            
        else:
            form = EditStaticQRForm(request.POST or none, instance=qr)
            qr_data = qr.content
            form.fields['content'].disabled = True
            form.fields['content'].initial = qr.content

        if form.is_valid():
            qr = form.save()
            
            messages.success(request, 'QR-код успешно обновлен')
            return redirect('qr_detail', qr_id=qr_id)
        else:
            messages.error(request, 'Форма содержит ошибки. Проверьте введённые данные.')
            print("Ошибки формы:", form.errors)
    else:
        if is_dynamic:
            form = EditDynamicQRForm(instance=qr)
            qr_data = qr.target_url
            redirect_count = qr.redirect_count
        else:
            form = EditStaticQRForm(instance=qr)
            qr_data = qr.content
    
    context = {
        'form': form,
        'qr': qr,
        'qr_data':qr_data,
        'is_dynamic': is_dynamic,
        'image': qr.qr_code.url if qr.qr_code else None,
    }
    return render(request, 'qr_edit.html', context)

def qr_redirect(request, hashed_id, qr_id):
    # settings.DEBUG = True
    """
    Обработка переадресации с QR-кода
    """
    try:
        
        print(f"Request path: {request.path}")
        print(f"Request method: {request.method}")
        print(f"Request scheme: {request.scheme}")
        print(f"Request host: {request.get_host()}")
        
        # Получаем QR-код
        qr = get_object_or_404(DynamicQRCode, id=qr_id)
        
        # Проверяем хеш ID пользователя
        expected_hash = qr.get_hashed_user_id()
        print('received_hash =', hashed_id)
        print('expected_hash =', expected_hash)
        print('user_id =', qr.user.id)
        print('salt =', settings.SECRET_KEY[:8])
        print('is_public =', qr.is_public)
        print('target_url =', qr.target_url)
        print('SITE_URL =', settings.SITE_URL)

        if hashed_id != expected_hash:
            print('Hash mismatch!')
            raise Http404("Неверный QR-код")
            
        if not qr.is_public:
            print('QR code is not public!')
            raise Http404("QR-код не публичный")

        # Увеличиваем счетчики
        qr.views += 1
        qr.redirect_count += 1
        qr.save()
        response = HttpResponseRedirect(qr.target_url)
        response['Location'] = qr.target_url
        # Выполняем переадресацию
        print(f"Redirecting to: {qr.target_url}")
        return HttpResponse(status=302, headers={'Location': qr.target_url})
        
    except Http404 as e:
        print('404 error:', str(e))
        raise Http404("QR-код не найден или неактивен")
    except Exception as e:
        print('Unexpected error:', str(e))
        raise
    

def examples_list(request):
    examples = QRCode.objects.filter(is_public=True).order_by('-created_at')
    return render(request, 'application/examples.html', {'examples': examples})

def example_detail(request, example_id):
    example = get_object_or_404(QRCode, id=example_id, is_public=True)
    return render(request, 'application/example_detail.html', {'example': example})


@login_required
def qr_list(request):
    """
    Отображение списка QR-кодов пользователя
    """
    qr_codes = QRCode.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'qr_codes': qr_codes
    }
    return render(request, 'qr_list.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Обновляем сессию, чтобы пользователь не вышел из системы
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('password_change_done')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required
def password_change_done(request):
    messages.success(request, 'Ваш пароль был успешно изменен!')
    return redirect('profile')


def auth_required(request):
    """
    Представление для отображения страницы с сообщением о необходимости авторизации
    """
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'auth_required.html', {
        'next': request.GET.get('next', ''),
        'title': 'Требуется авторизация'
    })



@login_required
def preview_qr(request):
    """
    Предпросмотр QR-кода без сохранения в базу данных
    """
    if request.method == 'POST':
        form_data = request.POST
        qr_type = form_data.get('qr_type')
        
        # Получаем данные формы
        title = form_data.get('title', '')
        size = int(form_data.get('size', 10))
        format = 'png'
        
        # Создаем временный QR-код
        if qr_type == 'dynamic':
            # Создаем временный объект DynamicQRCode для получения redirect_url
            temp_qr = DynamicQRCode(
                user=request.user,
                title=title,
                target_url=form_data.get('target_url', ''),
                format=format,
                size=size
            )
            content = temp_qr.get_redirect_url()
        else:
            content = form_data.get('content', '')
            
        # Получаем фоновое изображение
        background_image = request.FILES.get('background_image')
        
        # Генерируем QR-код
        qr_code = create_qr_code(
            data=content,
            size=size,
            format=format,
            background_image=background_image
        )
        
        # Отправляем изображение
        response = HttpResponse(qr_code.getvalue(), content_type=f'image/{format}')
        response['Content-Disposition'] = 'inline'
        return response
    
    return HttpResponseBadRequest('Неверный метод запроса')

@login_required
def beautiful_qr_preview(request):
    """
    Предпросмотр красивого QR-кода с фоновым изображением
    """
    if request.method == 'POST':
        form_data = request.POST
        qr_type = form_data.get('qr_type')
        
        # Получаем данные формы
        title = form_data.get('title', '')
        size = int(form_data.get('size', 10))
        format = 'png'
        
        # Создаем временный QR-код
        if qr_type == 'dynamic':
            # Создаем временный объект DynamicQRCode для получения redirect_url
            temp_qr = DynamicQRCode(
                user=request.user,
                title=title,
                target_url=form_data.get('target_url', ''),
                format=format,
                size=size
            )
            content = temp_qr.get_redirect_url()
        else:
            content = form_data.get('content', '')
            
        # Получаем фоновое изображение
        background_image = request.FILES.get('background_image')
        if not background_image:
            return HttpResponseBadRequest('Необходимо загрузить фоновое изображение')
            
        # Генерируем красивый QR-код
        from .utils import create_beatiful_qr
        qr_code = create_beatiful_qr(
            data=content,
            background_image=background_image,
            size=size,
            format=format
        )
        
        # Отправляем изображение
        response = HttpResponse(qr_code.getvalue(), content_type=f'image/{format}')
        response['Content-Disposition'] = 'inline'
        return response
    
    return HttpResponseBadRequest('Неверный метод запроса')

@login_required
def save_qr(request):
    
    
    """
    Сохранение QR-кода в базу данных
    """
    if request.method == 'POST':
        try:
            form_data = request.POST
            qr_type = form_data.get('qr_type')
            is_dynamic = form_data.get('is_dynamic') == '1'  # Получаем значение is_dynamic
            
            if not qr_type or qr_type not in ['static', 'dynamic']:
                return JsonResponse({'error': 'Неверный тип QR-кода'}, status=400)
            
            # Получаем данные формы
            title = form_data.get('title', '')
            size = int(form_data.get('size', 10))
            format = form_data.get('format', 'png')
            is_public = form_data.get('is_public') == 'on'
            
            # Создаем QR-код
            if qr_type == 'dynamic' or is_dynamic:
                target_url = form_data.get('target_url', '')
                if not target_url:
                    return JsonResponse({'error': 'URL не может быть пустым'}, status=400)
                    
                qr = DynamicQRCode(
                    user=request.user,
                    title=title,
                    target_url=target_url,
                    format=format,
                    size=size,
                    is_public=is_public,
                    is_dynamic=True  # Явно устанавливаем is_dynamic
                )
                # Сначала сохраняем QR-код, чтобы получить id
                qr.save()
                # Генерируем URL переадресации
                content = qr.get_redirect_url()
                print(f"Generated redirect URL: {content}")  # Для отладки
                print(f"User ID: {qr.user.id}")
                print(f"Salt: {settings.SECRET_KEY[:8]}")
                print(f"Expected hash: {qr.get_hashed_user_id()}")
                print(f"QR ID: {qr.id}")
            else:
                content = form_data.get('content', '')
                if not content:
                    return JsonResponse({'error': 'Содержимое не может быть пустым'}, status=400)
                    
                qr = StaticQRCode(
                    user=request.user,
                    title=title,
                    content=content,
                    format=format,
                    size=size,
                    is_public=is_public,
                    is_dynamic=False  # Явно устанавливаем is_dynamic
                )
            
            # Получаем фоновое изображение
            background_image = request.FILES.get('background_image')
            
            # Генерируем QR-код
            if background_image:
                qr_code = create_beatiful_qr(
                    data=content,
                    background_image=background_image,
                    size=size,
                    format=format
                )
            else:
                qr_code = create_qr_code(
                    data=content,
                    size=size,
                    format=format
                )
            
            # Сохраняем QR-код
            filepath = save_qr_code(qr_code, request.user, title, qr_type, format)
            qr.qr_code = filepath
            qr.save()
            
            messages.success(request, 'QR-код успешно сохранен!')
            return redirect('qr_detail', qr_id=qr.id)
            
        except Exception as e:
            print(f"Error in save_qr: {str(e)}")  # Для отладки
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Неверный метод запроса'}, status=400)

def universal_error_page(request, exception=None):
    # Логируем ошибку
    # logger.error("Ошибка при обработке запроса", exc_info=exception)

    return render(request, 'errors/universal_error.html', status=500)