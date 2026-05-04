from django.contrib import admin
from .models import Usuario, Igreja, TipoCelebracao, Contato

# Register your models here.
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("email", "nome", "username")
    search_fields = ("email", "nome", "username")
    
@admin.register(Igreja)
class IgrejaAdmin(admin.ModelAdmin):
    list_display = ("nome", "cidade", "paroquia", "capela", "aberta_ao_publico")
    search_fields = ("nome", "cidade")
    list_filter = ("paroquia", "capela", "aberta_ao_publico")
    
@admin.register(TipoCelebracao)
class TipoCelebracaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "igreja", "dia", "horario_inicio", "ativo")
    search_fields = ("nome",)
    
@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ("nome", "data")
    search_fields = ("nome", )