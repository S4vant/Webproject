# users/urls.py
from django.urls import path
from . import views
from django.views.generic.base import TemplateView
"""
    end-points:
    Домашняя страница
    /signup/ - Регистрация
    /logout/ - Выход
    Создание статического qr-кода
    /create_qr/ - Создание qr-кода
    /qr/<str:qr_id>/ - Страница qr-кода
    /qr/<str:qr_id>/delete/ - Удаление qr-кода
    создание динамического qr-кода
    /create_dynamic_qr/ - Создание qr-кода
    /qr/<str:qr_id>/edit/ - Редактирование qr-кода
    открытые примеры qr-кодов
    /examples/ - Список примеров qr-кодов
    /examples/<str:example_id>/ - Страница примера qr-кода
    персональная страница пользователя
    /profile/ - Страница пользователя
    /profile/<str:user_id>/ - Страница пользователя
    
"""

urlpatterns = [
    path('', views.index, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/change-password/done/', views.password_change_done, name='password_change_done'),
    path('showcase/', views.showcase, name='showcase'),
    path('qr/list/', views.qr_list, name='qr_list'),
    path('qr/create/static/', views.create_static_qr, name='create_static_qr'),
    path('qr/create/dynamic/', views.create_dynamic_qr, name='create_dynamic_qr'),
    path('qr/<int:qr_id>/', views.qr_detail, name='qr_detail'),
    path('qr/<int:qr_id>/edit/', views.qr_edit, name='qr_edit'),
    # path('qr/<int:qr_id>/edit/dynamic/', views.edit_dynamic_qr, name='edit_dynamic_qr'),
    # path('qr/<int:qr_id>/edit/static/', views.edit_static_qr, name='edit_static_qr'),
    path('qr/<int:qr_id>/delete/', views.qr_delete, name='qr_delete'),
    path('qr/<int:qr_id>/download/', views.download_qr, name='download_qr'),
    path('redirect/<str:hashed_id>/<int:qr_id>/', views.qr_redirect, name='qr_redirect'),
    path('examples/', views.examples_list, name='examples_list'),
    path('examples/<int:example_id>/', views.example_detail, name='example_detail'),
    path('auth-required/', views.auth_required, name='auth_required'),
    path('qr/preview/', views.preview_qr, name='preview_qr'),
    path('beautiful_qr_preview/', views.beautiful_qr_preview, name='beautiful_qr_preview'),
    path('qr/save/', views.save_qr, name='save_qr'),
]
