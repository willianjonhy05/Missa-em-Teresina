from django import forms
from django.contrib import admin, messages
from django.db import transaction
from .models import Usuario, Igreja, TipoCelebracao, Contato
from django.db.models import Count


# Função para duplicar o objeto
def duplicar_tipo_celebracao(modeladmin, request, queryset):
    for obj in queryset:
        obj_copy = obj  # Cria uma cópia do objeto
        obj_copy.pk = None  # Apaga o `pk` para criar um novo objeto
        obj_copy.save()  # Salva a cópia como um novo objeto

    modeladmin.message_user(request, "TipoCelebracao duplicado com sucesso.")

duplicar_tipo_celebracao.short_description = "Duplicar Celebração"

class TipoCelebracaoAddForm(forms.ModelForm):
    dias_da_semana = forms.MultipleChoiceField(
        label="Dias da Semana",
        choices=TipoCelebracao.DIAS,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Marque um ou mais dias. Será criada uma celebração para cada dia marcado.",
    )

    class Meta:
        model = TipoCelebracao
        fields = (
            "igreja",
            "nome",
            "categoria",
            "recorrencia",
            "dias_da_semana",
            "dia",
            "horario_inicio",
            "horario_fim",
            "descricao",
            "dia_mes",
            "data_especifica",
            "semana_do_mes",
            "exige_agendamento",
            "exibir_no_site",
            "ativo",
        )

        widgets = {
            "dia": forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()

        recorrencia = cleaned_data.get("recorrencia")
        dias_da_semana = cleaned_data.get("dias_da_semana") or []
        semana_do_mes = cleaned_data.get("semana_do_mes")

        if recorrencia == "semanal":
            if not dias_da_semana:
                raise forms.ValidationError(
                    "Marque pelo menos um dia da semana."
                )

            cleaned_data["dia"] = dias_da_semana[0]

        elif recorrencia == "mensal_dia_semana":
            if not dias_da_semana:
                raise forms.ValidationError(
                    "Marque o dia da semana da celebração. Exemplo: sábado."
                )

            if not semana_do_mes:
                raise forms.ValidationError(
                    "Informe a semana do mês. Exemplo: Primeiro."
                )

            cleaned_data["dia"] = dias_da_semana[0]

        return cleaned_data
    
    
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("email", "nome", "username")
    search_fields = ("email", "nome", "username")


@admin.register(Igreja)
class IgrejaAdmin(admin.ModelAdmin):
    list_display = ("nome", "cidade", "paroquia", "capela", "aberta_ao_publico", "sem_celebracoes", "sem_foto")
    search_fields = ("nome", "cidade")
    list_filter = ("paroquia", "capela", "aberta_ao_publico")
    list_per_page = 10
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(num_celebracoes=Count('tipos_celebracao'))
        return queryset   
    
    def sem_celebracoes(self, obj):
        """Verifica se a igreja tem celebrações cadastradas"""
        return obj.num_celebracoes == 0
    sem_celebracoes.boolean = True  

    def sem_foto(self, obj):
        """Verifica se a igreja tem foto"""
        return not bool(obj.imagem) 
    sem_foto.boolean = True  


@admin.register(TipoCelebracao)
class TipoCelebracaoAdmin(admin.ModelAdmin):
    form = TipoCelebracaoAddForm

    list_display = ("nome", "igreja", "dia", "horario_inicio", "ativo")
    search_fields = ("nome",)
    actions = [duplicar_tipo_celebracao]
    list_per_page = 10
    list_filter = ("igreja", "dia", "categoria", "recorrencia", "ativo")
    autocomplete_fields = ["igreja"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("igreja")

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs["form"] = TipoCelebracaoAddForm

        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if change:
            super().save_model(request, obj, form, change)
            return

        recorrencia = form.cleaned_data.get("recorrencia")
        dias_marcados = form.cleaned_data.get("dias_da_semana") or []

        if recorrencia not in ["semanal", "mensal_dia_semana"]:
            super().save_model(request, obj, form, change)
            return

        with transaction.atomic():
            total_criados = 0

            for dia in dias_marcados:
                TipoCelebracao.objects.create(
                    igreja=obj.igreja,
                    nome=obj.nome,
                    categoria=obj.categoria,
                    recorrencia=obj.recorrencia,
                    horario_inicio=obj.horario_inicio,
                    horario_fim=obj.horario_fim,
                    descricao=obj.descricao,
                    dia=dia,
                    dia_mes=obj.dia_mes,
                    data_especifica=obj.data_especifica,
                    semana_do_mes=obj.semana_do_mes,
                    exige_agendamento=obj.exige_agendamento,
                    exibir_no_site=obj.exibir_no_site,
                    ativo=obj.ativo,
                )

                total_criados += 1

            messages.success(
                request,
                f"{total_criados} celebração(ões) criada(s) com sucesso."
            )
            
            
            
@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ("nome", "data")
    search_fields = ("nome",)