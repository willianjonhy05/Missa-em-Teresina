from itertools import groupby
import requests
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .forms import IgrejaCreateForm, CelebracaoForm
from .models import Contato, Igreja, TipoCelebracao
from .utils import (
    calcular_distancia,
    calcular_proxima_ocorrencia,
    converter_para_float,
    formatar_horario,
    obter_descricao_recorrencia,
    obter_ip_usuario,
    obter_label_data,
    somente_superusuario,
)


from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UsuarioCreateForm

# Create your views here.


## VIEWS ADMINISTRATIVAS

@login_required(login_url="login_superusuario")
@user_passes_test(somente_superusuario, login_url="login_superusuario")
def cadastrar_usuario(request):
    if request.method == "POST":
        form = UsuarioCreateForm(request.POST)

        if form.is_valid():
            usuario = form.save()

            messages.success(
                request,
                f"Usuário {usuario.email} cadastrado com sucesso."
            )

            return redirect("cadastrar_usuario")
    else:
        form = UsuarioCreateForm()

    context = {
        "form": form,
    }

    return render(request, "admin/cadastrar_usuario.html", context)


@login_required(login_url="login_superusuario")
@user_passes_test(somente_superusuario, login_url="login_superusuario")
def dashboard(request):
    
    qtde_contatos = Contato.objects.count()
    qtde_igrejas = Igreja.objects.count()
    qtde_tipos_celebracao = TipoCelebracao.objects.count()
    
    context = {
        "qtde_contatos": qtde_contatos,
        "qtde_igrejas": qtde_igrejas,
        "qtde_tipos_celebracao": qtde_tipos_celebracao,
    }
    
    
    return render(request, "admin/base_admin.html", context)


@login_required(login_url="login_superusuario")
@user_passes_test(somente_superusuario, login_url="login_superusuario")
def listar_contatos(request):
    
    busca = request.GET.get("q", "").strip()
    
    contatos = (
        Contato.objects
        .all()
        .order_by("-data")
    )
    
    if busca:
        contatos = contatos.filter(
            Q(nome__icontains=busca) |
            Q(email__icontains=busca) |
            Q(mensagem__icontains=busca)
        )

    query_params = request.GET.copy()
    
    if "page" in query_params:
        query_params.pop("page")

    paginator = Paginator(contatos, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "busca": busca,
        "query_params": query_params.urlencode(),
    }

    return render(request, "admin/contatos.html", context)

@login_required(login_url="login_superusuario")
@user_passes_test(somente_superusuario, login_url="login_superusuario")
def listar_igrejas(request):
    busca = request.GET.get("q", "").strip()
    filtro_bairro = request.GET.get("bairro", "").strip()
    filtro_cidade = request.GET.get("cidade", "").strip()

    igrejas = Igreja.objects.all().order_by("nome")

    if busca:
        igrejas = igrejas.filter(
            Q(nome__icontains=busca) |
            Q(bairro__icontains=busca) |
            Q(cidade__icontains=busca)
        )

    if filtro_bairro:
        igrejas = igrejas.filter(bairro__icontains=filtro_bairro)

    if filtro_cidade:
        igrejas = igrejas.filter(cidade__icontains=filtro_cidade)

    paginator = Paginator(igrejas, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "busca": busca,
        "filtro_bairro": filtro_bairro,
        "filtro_cidade": filtro_cidade,
    }

    return render(request, "admin/listar_igrejas.html", context)


@login_required(login_url="login_superusuario")
@user_passes_test(somente_superusuario, login_url="login_superusuario")
def cadastrar_igreja(request):
    if request.method == "POST":
        form = IgrejaCreateForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Igreja cadastrada com sucesso!")
            return redirect("igrejas_dashboard")  
        else:
            messages.error(request, "Erro ao cadastrar a igreja. Verifique os dados.")

    else:
        form = IgrejaCreateForm()

    return render(request, "admin/cadastrar_igreja.html", {"form": form})


@login_required(login_url="login_superusuario")
@user_passes_test(somente_superusuario, login_url="login_superusuario")
def excluir_igreja(request, slug):
    igreja = get_object_or_404(Igreja, slug=slug)

    if request.method == "POST":
        # Confirmação de exclusão
        igreja.delete()
        messages.success(request, f"{igreja.nome} excluída com sucesso.")
        return redirect("igrejas_dashboard")

    context = {
        "igreja": igreja,
    }

    return render(request, "admin/excluir_igreja.html", context)


@login_required(login_url="login_superusuario")
@user_passes_test(somente_superusuario, login_url="login_superusuario")
def editar_igreja(request, slug):
    igreja = get_object_or_404(Igreja, slug=slug)

    if request.method == "POST":
        form = IgrejaCreateForm(request.POST, request.FILES, instance=igreja)

        if form.is_valid():
            form.save()
            messages.success(request, f"Igreja {igreja.nome} atualizada com sucesso!")
            return redirect("igrejas_dashboard")
        else:
            messages.error(request, "Erro ao atualizar a igreja. Verifique os dados.")

    else:
        form = IgrejaCreateForm(instance=igreja)

    return render(request, "admin/editar_igreja.html", {"form": form, "igreja": igreja})



@login_required
@user_passes_test(somente_superusuario)
def listar_celebracoes(request):
    igreja_id = request.GET.get('igreja')
    categoria = request.GET.get('categoria')
    ativo = request.GET.get('ativo')

    celebracoes = TipoCelebracao.objects.all().select_related('igreja')

    if igreja_id:
        celebracoes = celebracoes.filter(igreja_id=igreja_id)
    if categoria:
        celebracoes = celebracoes.filter(categoria=categoria)
    if ativo:
        celebracoes = celebracoes.filter(ativo=(ativo == '1'))

    celebracoes = celebracoes.order_by('igreja__nome', 'horario_inicio')
    
    paginator = Paginator(celebracoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'igrejas': Igreja.objects.all().order_by('nome'),
        'categorias': TipoCelebracao.CATEGORIAS,
        'filtros': {
            'igreja': igreja_id,
            'categoria': categoria,
            'ativo': ativo
        }
    }
    return render(request, 'admin/listar_celebracoes.html', context)

@login_required
@user_passes_test(somente_superusuario)
def cadastrar_celebracao(request):
    if request.method == 'POST':
        form = CelebracaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Celebração cadastrada com sucesso!")
            return redirect('listar_celebracoes')
        else:
            messages.error(request, "Erro ao cadastrar. Verifique os campos.")
    else:
        form = CelebracaoForm()
    
    return render(request, 'admin/cadastrar_celebracao.html', {'form': form})

@login_required
@user_passes_test(somente_superusuario)
def editar_celebracao(request, pk):
    celebracao = get_object_or_404(TipoCelebracao, pk=pk)
    if request.method == 'POST':
        form = CelebracaoForm(request.POST, instance=celebracao)
        if form.is_valid():
            form.save()
            messages.success(request, "Celebração atualizada com sucesso!")
            return redirect('listar_celebracoes')
    else:
        form = CelebracaoForm(instance=celebracao)
    
    return render(request, 'admin/editar_celebracao.html', {'form': form, 'celebracao': celebracao})

@login_required
@user_passes_test(somente_superusuario)
def excluir_celebracao(request, pk):
    celebracao = get_object_or_404(TipoCelebracao, pk=pk)
    if request.method == 'POST':
        celebracao.delete()
        messages.success(request, "Celebração excluída com sucesso.")
        return redirect('listar_celebracoes')
    
    return render(request, 'admin/excluir_celebracao.html', {'celebracao': celebracao})



## VIEWS PÚBLICAS

def home(request):
    agora = timezone.localtime(timezone.now())
    total_igrejas = Igreja.objects.count()
    total_celebracoes = TipoCelebracao.objects.count()

    tem_igrejas = total_igrejas > 0
    tem_celebracoes = total_celebracoes > 0

    celebracoes_qs = (
        TipoCelebracao.objects
        .filter(
            ativo=True,
            exibir_no_site=True,
            igreja__aberta_ao_publico=True,
            categoria__in=["missa", "missa_votiva"]
        )
        .select_related("igreja")
    )

    missas_calculadas = []

    for celebracao in celebracoes_qs:
        proxima_data = calcular_proxima_ocorrencia(celebracao)

        if not proxima_data:
            continue

        missas_calculadas.append({
            "celebracao": celebracao,
            "igreja": celebracao.igreja,
            "proxima_data": proxima_data,
            "label_data": obter_label_data(proxima_data, agora),
            "horario": formatar_horario(celebracao.horario_inicio),
        })

    missas_calculadas.sort(
        key=lambda item: (
            item["proxima_data"],
            item["igreja"].nome.lower()
        )
    )

    proximas_missas = []
    igrejas_adicionadas = set()

    for item in missas_calculadas:
        igreja_id = item["igreja"].id

        if igreja_id in igrejas_adicionadas:
            continue

        proximas_missas.append(item)
        igrejas_adicionadas.add(igreja_id)

        if len(proximas_missas) == 3:
            break

    context = {
        "proximas_missas": proximas_missas,
        "total_igrejas": total_igrejas,
        "total_celebracoes": total_celebracoes,
        "tem_igrejas": tem_igrejas,
        "tem_celebracoes": tem_celebracoes,
    }
    
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")
        mensagem = request.POST.get("mensagem")

        if not nome or not email or not mensagem:
            messages.error(request, "Preencha nome, e-mail e mensagem para enviar o contato.")
            return redirect("home")

        Contato.objects.create(
            nome=nome,
            email=email,
            telefone=telefone,
            mensagem=mensagem,
            ip_contato=obter_ip_usuario(request)
        )

        messages.success(request, "Mensagem enviada com sucesso! Obrigado pelo contato.")
        return redirect("home")

    return render(request, "base.html", context)

def igreja(request, slug):
    igreja = get_object_or_404(Igreja, slug=slug)

    tipos_celebracao = (
        igreja.tipos_celebracao
        .filter(
            ativo=True,
            exibir_no_site=True,
        )
        .annotate(
            ordem_recorrencia=Case(
                When(recorrencia="semanal", then=Value(1)),
                When(recorrencia="mensal_dia_fixo", then=Value(2)),
                When(recorrencia="data_especifica", then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            ),
            ordem_dia=Case(
                When(dia="segunda", then=Value(1)),
                When(dia="terca", then=Value(2)),
                When(dia="quarta", then=Value(3)),
                When(dia="quinta", then=Value(4)),
                When(dia="sexta", then=Value(5)),
                When(dia="sabado", then=Value(6)),
                When(dia="domingo", then=Value(7)),
                default=Value(8),
                output_field=IntegerField(),
            ),
        )
        .order_by(
            "categoria",
            "ordem_recorrencia",
            "ordem_dia",
            "dia_mes",
            "data_especifica",
            "horario_inicio",
            "nome",
        )
    )

    grupos_celebracao = []

    for categoria, celebracoes_categoria in groupby(
        tipos_celebracao,
        key=lambda celebracao: celebracao.get_categoria_display(),
    ):
        dias = []

        for _, celebracoes_grupo in groupby(
            celebracoes_categoria,
            key=lambda celebracao: (
                celebracao.recorrencia,
                celebracao.dia,
                celebracao.dia_mes,
                celebracao.data_especifica,
                celebracao.nome if celebracao.recorrencia != "semanal" else "",
            ),
        ):
            celebracoes_grupo = list(celebracoes_grupo)
            primeira_celebracao = celebracoes_grupo[0]

            horarios = []

            for celebracao in celebracoes_grupo:
                horario_formatado = formatar_horario(celebracao.horario_inicio)

                if horario_formatado not in horarios:
                    horarios.append(horario_formatado)

            dias.append({
                "dia": obter_descricao_recorrencia(primeira_celebracao),
                "dia_slug": primeira_celebracao.dia,
                "nome": primeira_celebracao.nome,
                "recorrencia": primeira_celebracao.recorrencia,
                "horarios": horarios,
                "exige_agendamento": any(
                    celebracao.exige_agendamento for celebracao in celebracoes_grupo
                ),
            })

        grupos_celebracao.append({
            "categoria": categoria,
            "dias": dias,
        })

    latitude = igreja.latitude
    longitude = igreja.longitude

    google_maps_embed_url = None
    google_maps_directions_url = None

    if latitude is not None and longitude is not None:
        lat = f"{latitude:.6f}"
        lon = f"{longitude:.6f}"

        google_maps_embed_url = f"https://maps.google.com/maps?q={lat},{lon}&z=17&output=embed"
        google_maps_directions_url = f"https://www.google.com/maps?q={lat},{lon}"

    context = {
        "igreja": igreja,
        "tipos_celebracao": tipos_celebracao,
        "grupos_celebracao": grupos_celebracao,
        "google_maps_embed_url": google_maps_embed_url,
        "google_maps_directions_url": google_maps_directions_url,
    }

    return render(request, "public/igreja.html", context)


def igrejas(request):
    busca = request.GET.get("q", "").strip()

    latitude_usuario = converter_para_float(request.GET.get("lat"))
    longitude_usuario = converter_para_float(request.GET.get("lon"))

    igrejas = Igreja.objects.all()

    if busca:
        igrejas = igrejas.filter(nome__icontains=busca)

    igrejas = list(igrejas)

    localizacao_disponivel = (
        latitude_usuario is not None
        and longitude_usuario is not None
    )

    if localizacao_disponivel:
        for igreja_obj in igrejas:
            igreja_obj.distancia_km = calcular_distancia(
                latitude_usuario,
                longitude_usuario,
                igreja_obj.latitude,
                igreja_obj.longitude,
            )

        igrejas.sort(
            key=lambda igreja_obj: (
                igreja_obj.distancia_km is None,
                igreja_obj.distancia_km if igreja_obj.distancia_km is not None else 999999,
                igreja_obj.nome.lower(),
            )
        )
    else:
        igrejas.sort(key=lambda igreja_obj: igreja_obj.nome.lower())

    paginator = Paginator(igrejas, 9)
    numero_pagina = request.GET.get("page")
    page_obj = paginator.get_page(numero_pagina)

    context = {
        "page_obj": page_obj,
        "busca": busca,
        "latitude_usuario": latitude_usuario,
        "longitude_usuario": longitude_usuario,
        "localizacao_disponivel": localizacao_disponivel,
    }

    return render(request, "public/listar_igrejas.html", context)


def mapa(request):
    latitude_usuario = converter_para_float(request.GET.get("lat"))
    longitude_usuario = converter_para_float(request.GET.get("lon"))

    igrejas = (
        Igreja.objects
        .exclude(latitude__isnull=True)
        .exclude(longitude__isnull=True)
    )

    igrejas = list(igrejas)

    localizacao_disponivel = (
        latitude_usuario is not None
        and longitude_usuario is not None
    )

    if localizacao_disponivel:
        for igreja_obj in igrejas:
            igreja_obj.distancia_km = calcular_distancia(
                latitude_usuario,
                longitude_usuario,
                igreja_obj.latitude,
                igreja_obj.longitude,
            )

        igrejas.sort(key=lambda igreja_obj: igreja_obj.distancia_km or 999999)
    else:
        igrejas.sort(key=lambda igreja_obj: igreja_obj.nome.lower())

    context = {
        "igrejas": igrejas,
        "latitude_usuario": latitude_usuario,
        "longitude_usuario": longitude_usuario,
        "localizacao_disponivel": localizacao_disponivel,
    }

    return render(request, "public/mapa.html", context)


def contato(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")
        mensagem = request.POST.get("mensagem")

        Contato.objects.create(
            nome=nome,
            email=email,
            telefone=telefone,
            mensagem=mensagem,
            ip_contato=obter_ip_usuario(request),
        )

        messages.success(request, "Mensagem enviada com sucesso! Obrigado pelo contato.")
        return redirect("contato")

    return render(request, "public/contato.html")


def quem_somos(request):
    return render(request, "public/quem_somos.html")

def missas(request):
    lat_user = request.GET.get("lat")
    lon_user = request.GET.get("lon")
    filtro_bairro = request.GET.get("bairro")
    filtro_dia = request.GET.get("dia")

    try:
        lat_user = float(lat_user) if lat_user else None
        lon_user = float(lon_user) if lon_user else None
    except (TypeError, ValueError):
        lat_user = None
        lon_user = None

    localizacao_disponivel = lat_user is not None and lon_user is not None

    celebracoes_qs = (
        TipoCelebracao.objects
        .filter(
            ativo=True,
            exibir_no_site=True,
            igreja__aberta_ao_publico=True
        )
        .select_related("igreja")
    )

    if filtro_bairro:
        celebracoes_qs = celebracoes_qs.filter(
            igreja__bairro=filtro_bairro
        )

    if filtro_dia:
        celebracoes_qs = celebracoes_qs.filter(
            recorrencia="semanal",
            dia=filtro_dia
        )

    agora = timezone.localtime(timezone.now())
    lista_final = []

    for celebracao in celebracoes_qs:
        proximo_dt = calcular_proxima_ocorrencia(celebracao)

        if not proximo_dt:
            continue

        distancia_km = calcular_distancia(
            lat_user,
            lon_user,
            celebracao.igreja.latitude,
            celebracao.igreja.longitude
        )

        celebracao.proximo_dt = proximo_dt
        celebracao.segundos_restantes = (proximo_dt - agora).total_seconds()
        celebracao.distancia_km = distancia_km
        celebracao.label_data = obter_label_data(proximo_dt, agora)
        celebracao.horario_formatado = formatar_horario(celebracao.horario_inicio)

        # Não use celebracao.descricao_recorrencia aqui,
        # porque esse nome já é uma @property no model.
        celebracao.descricao_recorrencia_calculada = obter_descricao_recorrencia(
            celebracao,
            proximo_dt
        )

        lista_final.append(celebracao)

    if localizacao_disponivel:
        lista_final.sort(
            key=lambda celebracao: (
                celebracao.segundos_restantes,
                celebracao.distancia_km if celebracao.distancia_km is not None else 999999,
                celebracao.igreja.nome.lower(),
                celebracao.nome.lower(),
            )
        )
    else:
        lista_final.sort(
            key=lambda celebracao: (
                celebracao.igreja.nome.lower(),
                celebracao.nome.lower(),
                celebracao.segundos_restantes,
            )
        )

    paginator = Paginator(lista_final, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    bairros = (
        Igreja.objects
        .exclude(bairro__isnull=True)
        .exclude(bairro__exact="")
        .values_list("bairro", flat=True)
        .distinct()
        .order_by("bairro")
    )

    dias_semana = [
        ("domingo", "Domingo"),
        ("segunda", "Segunda-feira"),
        ("terca", "Terça-feira"),
        ("quarta", "Quarta-feira"),
        ("quinta", "Quinta-feira"),
        ("sexta", "Sexta-feira"),
        ("sabado", "Sábado"),
    ]

    query_params = request.GET.copy()

    if "page" in query_params:
        query_params.pop("page")

    context = {
        "page_obj": page_obj,
        "bairros": bairros,
        "dias_semana": dias_semana,
        "filtro_bairro": filtro_bairro,
        "filtro_dia": filtro_dia,
        "lat_user": lat_user,
        "lon_user": lon_user,
        "localizacao_disponivel": localizacao_disponivel,
        "query_params": query_params.urlencode(),
    }

    return render(request, "public/proximas_celebracoes.html", context)



def liturgia(request):
    url = "https://liturgia.up.railway.app/v2/"
    context = {
        'dados': None,
        'erro': False
    }
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Organização dos dados para facilitar o acesso no template
        context['dados'] = {
            'data': data.get('data'),
            'titulo': data.get('liturgia'),
            'cor': data.get('cor', '').capitalize(),
            'oracoes': data.get('oracoes', {}),
            'leituras': data.get('leituras', {}),
            'antifonas': data.get('antifonas', {}),
        }
    except (requests.RequestException, ValueError) as e:
        context['erro'] = True
        context['mensagem_erro'] = "Não foi possível carregar a liturgia no momento. Verifique sua conexão ou tente mais tarde."

    return render(request, 'public/liturgia.html', context)



@never_cache
def login_superusuario(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("dashboard")

        logout(request)

    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        usuario = authenticate(
            request,
            username=email,
            password=password
        )

        if usuario is not None:
            if usuario.is_superuser:
                login(request, usuario)

                if next_url and url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()}
                ):
                    return redirect(next_url)

                return redirect("dashboard")

            messages.error(
                request,
                "Este usuário não possui permissão de superusuário."
            )
        else:
            messages.error(
                request,
                "E-mail ou senha inválidos."
            )

    context = {
        "next": next_url,
    }

    return render(request, "admin/login.html", context)


def logout_superusuario(request):
    logout(request)
    messages.success(request, "Você saiu do sistema com sucesso.")
    return redirect("login_superusuario")