import random
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
import uuid
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image, ImageOps

from .utils import expandir_e_extrair


# Create your models here.


class Usuario(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    nome = models.CharField("Nome", max_length=100, blank=True, null=True)
    email = models.EmailField("Email", max_length=100, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def gerar_username(self):
        email = self.email or "usuario"

        if "@" in email:
            base_username = email.split("@")[0]
        else:
            base_username = email

        while True:
            numeros_aleatorios = "".join(random.choices("0123456789", k=4))
            username = f"{base_username}{numeros_aleatorios}"

            if not Usuario.objects.filter(username=username).exists():
                break

        return username

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.gerar_username()
            
        self.is_staff = True
        self.is_superuser = True
        self.is_active = True

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or self.username

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        
        


class Igreja(models.Model):
    nome = models.CharField("Nome da Igreja", max_length=150)
    endereco = models.CharField("Endereço", max_length=255)
    bairro = models.CharField("Bairro", max_length=100, blank=True, null=True)
    cidade = models.CharField("Cidade", max_length=100)
    paroquia = models.BooleanField("Paróquia", default=False)
    capela = models.BooleanField("Capela", default=False)
    aberta_ao_publico = models.BooleanField("Aberta ao Público", default=True)

    latitude = models.FloatField("Latitude", blank=True, null=True)
    longitude = models.FloatField("Longitude", blank=True, null=True)

    sacerdotes = models.CharField("Sacerdotes", max_length=255, blank=True, null=True)
    telefone = models.CharField("Telefones", max_length=255, blank=True, null=True)
    imagem = models.ImageField("Imagem", upload_to="igrejas/", blank=True, null=True)
    email = models.EmailField("Email", blank=True, null=True)
    site = models.URLField("Site", blank=True, null=True)
    facebook = models.URLField("Facebook", max_length=100, blank=True, null=True)
    instagram = models.CharField("Instagram", max_length=100, blank=True, null=True)
    youtube = models.URLField("YouTube", blank=True, null=True)
    maps = models.URLField("Google Maps", blank=True, null=True)

    slug = models.SlugField("Slug", max_length=150, unique=True, blank=True, null=True, editable=False)

    contato_whatsapp = models.CharField("Contato WhatsApp", max_length=20, blank=True, null=True)

    def __str__(self):
        if self.paroquia or self.capela:
            return self.nome

        return f"Igreja {self.nome}"

    def obter_coordenadas(self):
        if not self.maps:
            return False

        try:
            lat, lon = expandir_e_extrair(self.maps)

            if lat is None or lon is None:
                return False

            latitude = float(lat)
            longitude = float(lon)
        except (TypeError, ValueError):
            return False

        self.latitude = latitude
        self.longitude = longitude
        return True

    @property
    def link_instagram(self):
        if self.instagram:
            return f"https://www.instagram.com/{self.instagram}/"

        return None

    @property
    def link_whatsapp(self):
        if self.contato_whatsapp:
            return f"https://wa.me/{self.contato_whatsapp}"

        return None

    def get_absolute_url(self):
        return reverse("detalhar_igreja", kwargs={"slug": self.slug})

    def redimensionar_imagem(self):
        if not self.imagem:
            return

        img = Image.open(self.imagem)
        img = ImageOps.exif_transpose(img)

        if img.mode != "RGB":
            img = img.convert("RGB")

        img = ImageOps.fit(
            img,
            (1200, 630),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85, optimize=True)
        buffer.seek(0)

        nome_base = Path(self.imagem.name).stem
        novo_nome = f"{slugify(nome_base)}.jpg"

        self.imagem.save(
            novo_nome,
            ContentFile(buffer.read()),
            save=False,
        )

    def save(self, *args, **kwargs):
        if not self.slug and self.nome:
            self.slug = slugify(self.nome)

        self.redimensionar_imagem()
        self.obter_coordenadas()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Igreja"
        verbose_name_plural = "Igrejas"


class TipoCelebracao(models.Model):
    CATEGORIAS = [
        ("missa", "Santa Missa"),
        ("missa_votiva", "Missa Votiva"),
        ("missa_corpo_presente", "Missa de Corpo Presente"),
        ("celebracao", "Celebração da Palavra"),
        ("adoracao", "Adoração ao Santíssimo"),
        ("batismo", "Batismo"),
        ("casamento", "Casamento"),
        ("confissao", "Confissão"),
        ("outros", "Outros"),
    ]

    DIAS = [
        ("segunda", "Segunda-feira"),
        ("terca", "Terça-feira"),
        ("quarta", "Quarta-feira"),
        ("quinta", "Quinta-feira"),
        ("sexta", "Sexta-feira"),
        ("sabado", "Sábado"),
        ("domingo", "Domingo"),
    ]
    
    ORDEM_SEMANA = [
        (1, "Primeiro"),
        (2, "Segundo"),
        (3, "Terceiro"),
        (4, "Quarto"),
        (5, "Quinto"),
        (-1, "Último"),
]

    RECORRENCIAS = [
        ("semanal", "Semanal"),
        ("mensal_dia_fixo", "Mensal em dia fixo"),
        ("mensal_dia_semana", "Mensal por dia da semana"),
        ("data_especifica", "Data específica"),
    ]

    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.CASCADE,
        related_name="tipos_celebracao",
    )
    nome = models.CharField("Nome", max_length=100)
    categoria = models.CharField("Categoria", max_length=30, choices=CATEGORIAS)
    recorrencia = models.CharField(
        "Recorrência",
        max_length=30,
        choices=RECORRENCIAS,
        default="semanal",
    )
    horario_inicio = models.TimeField("Horário de Início", blank=True, null=True)
    horario_fim = models.TimeField("Horário de Término", blank=True, null=True)
    descricao = models.TextField("Descrição", blank=True, null=True)
    dia = models.CharField(
        "Dia da Semana",
        max_length=20,
        choices=DIAS,
        blank=True,
        null=True,
    )
    dia_mes = models.PositiveIntegerField(
        "Dia do Mês",
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="Use este campo para celebrações mensais. Exemplo: dia 13 de cada mês.",
    )
    data_especifica = models.DateField(
        "Data Específica",
        blank=True,
        null=True,
        help_text="Use para celebrações extraordinárias, como casamento ou missa de corpo presente.",
    )
    semana_do_mes = models.IntegerField(
        "Semana do Mês",
        choices=ORDEM_SEMANA,
        blank=True,
        null=True,
        help_text="Use para celebrações mensais por dia da semana. Exemplo: primeira segunda-feira do mês.",
    )
    exige_agendamento = models.BooleanField("Exige Agendamento", default=False)
    exibir_no_site = models.BooleanField("Exibir no Site", default=True)
    ativo = models.BooleanField("Ativo", default=True)

    def clean(self):
        if self.recorrencia == "semanal":
            if not self.dia:
                raise ValidationError({
                    "dia": "Informe o dia da semana para celebrações semanais."
                })

            if self.dia_mes:
                raise ValidationError({
                    "dia_mes": "Para celebrações semanais, deixe o dia do mês vazio."
                })

            if self.semana_do_mes:
                raise ValidationError({
                    "semana_do_mes": "Para celebrações semanais, deixe a semana do mês vazia."
                })

            if self.data_especifica:
                raise ValidationError({
                    "data_especifica": "Para celebrações semanais, deixe a data específica vazia."
                })

        if self.recorrencia == "mensal_dia_fixo":
            if not self.dia_mes:
                raise ValidationError({
                    "dia_mes": "Informe o dia do mês para celebrações mensais."
                })

            if self.dia:
                raise ValidationError({
                    "dia": "Para celebrações mensais em dia fixo, deixe o dia da semana vazio."
                })

            if self.semana_do_mes:
                raise ValidationError({
                    "semana_do_mes": "Para celebrações mensais em dia fixo, deixe a semana do mês vazia."
                })

            if self.data_especifica:
                raise ValidationError({
                    "data_especifica": "Para celebrações mensais em dia fixo, deixe a data específica vazia."
                })

        if self.recorrencia == "mensal_dia_semana":
            if not self.dia:
                raise ValidationError({
                    "dia": "Informe o dia da semana. Exemplo: domingo."
                })

            if not self.semana_do_mes:
                raise ValidationError({
                    "semana_do_mes": "Informe a semana do mês. Exemplo: primeiro domingo."
                })

            if self.dia_mes:
                raise ValidationError({
                    "dia_mes": "Para celebrações mensais por dia da semana, deixe o dia do mês vazio."
                })

            if self.data_especifica:
                raise ValidationError({
                    "data_especifica": "Para celebrações mensais por dia da semana, deixe a data específica vazia."
                })

        if self.recorrencia == "data_especifica":
            if not self.data_especifica:
                raise ValidationError({
                    "data_especifica": "Informe a data específica da celebração."
                })

            if self.dia:
                raise ValidationError({
                    "dia": "Para celebrações com data específica, deixe o dia da semana vazio."
                })

            if self.dia_mes:
                raise ValidationError({
                    "dia_mes": "Para celebrações com data específica, deixe o dia do mês vazio."
                })

            if self.semana_do_mes:
                raise ValidationError({
                    "semana_do_mes": "Para celebrações com data específica, deixe a semana do mês vazia."
                })
                
    @property
    def descricao_recorrencia(self):
        if self.recorrencia == "semanal":
            return self.get_dia_display() if self.dia else "Consultar"

        if self.recorrencia == "mensal_dia_fixo":
            if self.dia_mes:
                return f"Todo dia {self.dia_mes} de cada mês"

            return "Dia do mês não informado"

        if self.recorrencia == "mensal_dia_semana":
            if self.dia and self.semana_do_mes:
                return f"{self.get_semana_do_mes_display()} {self.get_dia_display()} de cada mês"

            return "Dia da semana mensal não informado"

        if self.recorrencia == "data_especifica":
            if self.data_especifica:
                return f"Dia {self.data_especifica.strftime('%d/%m/%Y')}"

            return "Data não informada"

        return "Consultar"

    def definir_horario_fim(self):
        if not self.horario_inicio:
            self.horario_fim = None
            return

        horario_base = datetime.combine(
            datetime.today(),
            self.horario_inicio,
        )

        horario_final = horario_base + timedelta(hours=1)
        self.horario_fim = horario_final.time()

    def save(self, *args, **kwargs):
        self.definir_horario_fim()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.igreja} - {self.nome}"

    class Meta:
        verbose_name = "Tipo de Celebração"
        verbose_name_plural = "Tipos de Celebração"


class Contato(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, blank=True, null=True)
    nome = models.CharField("Nome", max_length=100, blank=True, null=True)
    email = models.EmailField("Email", max_length=100, blank=True, null=True)
    telefone = models.CharField("Telefone", max_length=15, null=True, blank=True)
    mensagem = models.TextField("Mensagem", blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True)
    ip_contato = models.GenericIPAddressField("IP de Aceite", null=True, blank=True)

    def __str__(self):
        return self.nome or "Contato sem nome"

    class Meta:
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"
