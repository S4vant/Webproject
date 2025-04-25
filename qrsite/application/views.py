# users/views.py
from django.urls import reverse_lazy
from django.contrib.auth import logout, login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.utils import timezone
from django.conf import settings
from .forms import CustomUserCreationForm, StaticQRForm, DynamicQRForm, ProfileForm
from .models import QRCode, StaticQRCode, DynamicQRCode
from .utils import save_qr_code, create_qr_code
import os

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
    return render(request, 'showcase.html')

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
    if request.method == 'POST':
        form = StaticQRForm(request.POST, request.FILES)
        if form.is_valid():
            qr = form.save(commit=False)
            qr.user = request.user
            
            # Получаем размер и формат из формы
            size = form.cleaned_data['size']
            format = form.cleaned_data['format']
            
            # Генерация QR-кода
            qr_code = create_qr_code(
                data=qr.content,
                size=size,
                format=format,
                background_image=request.FILES.get('background_image')
            )
            
            # Сохранение QR-кода
            filepath = save_qr_code(qr_code, request.user, qr.title, 'static', format)
            qr.qr_code = filepath
            qr.save()
            
            messages.success(request, 'QR-код успешно создан!')
            return redirect('qr_detail', qr_id=qr.id)
    else:
        form = StaticQRForm()
    
    return render(request, 'create_static_qr.html', {'form': form})

@login_required
def create_dynamic_qr(request):
    """
    Создание динамического QR-кода
    """
    if request.method == 'POST':
        form = DynamicQRForm(request.POST, request.FILES)
        if form.is_valid():
            qr = form.save(commit=False)
            qr.user = request.user
   
            # Получаем размер и формат из формы
            size = form.cleaned_data['size']
            format = form.cleaned_data['format']
            
            # Генерация QR-кода
            qr_code = create_qr_code(
                data=qr.target_url,  # Убедитесь, что используется правильное поле
                size=size,
                format=format,
                background_image=request.FILES.get('background_image')
            )
            
            # Сохранение QR-кода
            filepath = save_qr_code(qr_code, request.user, qr.title, 'dynamic', format)
            qr.qr_code = filepath
            qr.save()
            
            messages.success(request, 'QR-код успешно создан!')
            return redirect('qr_detail', qr_id=qr.id)  # Перенаправление на страницу деталей QR-кода
    else:
        form = DynamicQRForm()
    
    return render(request, 'create_dynamic_qr.html', {'form': form})

def qr_detail(request, qr_id):
    qr = get_object_or_404(QRCode, id=qr_id)
    
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
        
        # Открываем файл и отправляем его
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=f'image/{qr.format}')
            response['Content-Disposition'] = f'attachment; filename="{qr.title}.{qr.format}"'
            return response
            
    except Exception as e:
        messages.error(request, f'Ошибка при скачивании QR-кода: {str(e)}')
        return redirect('qr_detail', qr_id=qr_id)

@login_required
def qr_delete(request, qr_id):
    qr = get_object_or_404(QRCode, id=qr_id, user=request.user)
    if request.method == 'POST':
        qr.delete()
        messages.success(request, 'QR-код успешно удален')
        return redirect('profile')
    return render(request, 'qr_confirm_delete.html', {'qr': qr})

@login_required
def qr_edit(request, qr_id):
    qr = get_object_or_404(QRCode, id=qr_id)
    
    # Проверяем, имеет ли пользователь доступ к редактированию
    if qr.user != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого QR-кода')
        return redirect('qr_detail', qr_id=qr_id)
    
    if request.method == 'POST':
        if isinstance(qr, DynamicQRCode):
            form = DynamicQRForm(request.POST, request.FILES, instance=qr)
            qr_type = 'dynamic'
        else:
            form = StaticQRForm(request.POST, request.FILES, instance=qr)
            qr_type = 'static'
            
        if form.is_valid():
            qr = form.save(commit=False)
            qr.updated_at = timezone.now()
            format = form.cleaned_data['format']
            # Генерируем новый QR-код с обновленными параметрами
            qr_data = qr.target_url if isinstance(qr, DynamicQRCode) else qr.content
            qr_code = create_qr_code(
                qr_data,
                size=form.cleaned_data['size'],
                format=form.cleaned_data['format'],
                background_image=form.cleaned_data.get('background_image'),

                # logo=form.cleaned_data.get('logo')
            )
            
            # Сохраняем QR-код
            qr.image = save_qr_code(qr_code, request.user, qr.title,qr_type,  qr.format)
            qr.save()
            
            messages.success(request, 'QR-код успешно обновлен')
            return redirect('qr_detail', qr_id=qr_id)
    else:
        if isinstance(qr, DynamicQRCode):
            form = DynamicQRForm(instance=qr)
        else:
            form = StaticQRForm(instance=qr)
    
    context = {
        'form': form,
        'qr': qr,
        'is_dynamic': isinstance(qr, DynamicQRCode),
        'image': qr.qr_code.url if qr.qr_code else None,
    }
    return render(request, 'qr_edit.html', context)

def qr_redirect(request, qr_id):
    return handle_qr_redirect(qr_id)

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

