"""
URL configuration for horariodemissa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from igreja import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('igrejas/', views.igrejas, name='listar_igrejas'),
    path('igrejas/<slug:slug>/', views.igreja, name='detalhar_igreja'),
    path('mapa/', views.mapa, name='mapa_igrejas'),
    path('quem-somos/', views.quem_somos, name='sobre'),
    path('contato/', views.contato, name='contato'),
    path('missas/', views.missas, name='listar_missas'),
    path('liturgia/', views.liturgia, name='liturgia'),
    path('', views.home, name='home'),
    
    
    path('adm/cadastrar-usuario/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('login/', views.login_superusuario, name='login_superusuario'),
    path('logout/', views.logout_superusuario, name='logout_superusuario'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/contatos/', views.listar_contatos, name='contatos_dashboard'),
    path('dashboard/igrejas/', views.listar_igrejas, name='igrejas_dashboard'),
    path('dashboard/igrejas/cadastrar/', views.cadastrar_igreja, name='cadastrar_igreja'),
    path('dashboard/igrejas/<slug:slug>/editar/', views.editar_igreja, name='editar_igreja'),
    path('dashboard/igrejas/<slug:slug>/excluir/', views.excluir_igreja, name='excluir_igreja'),
    
    
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)