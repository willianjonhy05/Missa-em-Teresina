import calendar
import math
import re
from datetime import date, datetime, timedelta, time

import requests
from django.conf import settings
from django.utils import timezone


DIAS_MAP = {
    "segunda": 0,
    "terca": 1,
    "quarta": 2,
    "quinta": 3,
    "sexta": 4,
    "sabado": 5,
    "domingo": 6,
}


def converter_para_float(valor):
    try:
        return float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        return None


def extrair_coordenadas(url):
    if not url:
        return None, None

    padroes = [
        r"@(-?\d+\.\d+),(-?\d+\.\d+)",
        r"query=(-?\d+\.\d+),(-?\d+\.\d+)",
        r"q=(-?\d+\.\d+),(-?\d+\.\d+)",
    ]

    for padrao in padroes:
        match = re.search(padrao, url)
        if match:
            return match.group(1), match.group(2)

    return None, None


def expandir_e_extrair(url_curta):
    try:
        resposta = requests.get(
            url_curta,
            allow_redirects=True,
            timeout=10,
        )
        resposta.raise_for_status()
        return extrair_coordenadas(resposta.url)
    except requests.RequestException:
        return None, None


def formatar_horario(horario):
    if not horario:
        return "Consultar"

    if horario.minute == 0:
        return horario.strftime("%Hh")

    return horario.strftime("%Hh%M")


def obter_descricao_recorrencia(celebracao, proximo_dt=None):
    if celebracao.recorrencia == "semanal":
        return celebracao.get_dia_display() if celebracao.dia else "Consultar"

    if celebracao.recorrencia == "mensal_dia_fixo":
        if celebracao.dia_mes:
            return f"Todo dia {celebracao.dia_mes} de cada mês"
        return "Dia do mês não informado"

    if celebracao.recorrencia == "data_especifica":
        data_base = proximo_dt.date() if proximo_dt else celebracao.data_especifica

        if data_base:
            return f"Dia {data_base.strftime('%d/%m/%Y')}"

        return "Data não informada"

    return "Consultar"


def obter_ip_usuario(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def combinar_data_horario(data_celebracao, horario_celebracao):
    if not data_celebracao:
        return None

    horario_celebracao = horario_celebracao or time(23, 59)
    data_hora = datetime.combine(data_celebracao, horario_celebracao)

    if settings.USE_TZ and timezone.is_naive(data_hora):
        data_hora = timezone.make_aware(
            data_hora,
            timezone.get_current_timezone(),
        )

    return timezone.localtime(data_hora)


def calcular_proxima_ocorrencia_semanal(celebracao, agora):
    if not celebracao.dia:
        return None

    dia_alvo = DIAS_MAP.get(celebracao.dia)

    if dia_alvo is None:
        return None

    dia_atual = agora.weekday()
    dias_diff = (dia_alvo - dia_atual) % 7

    proxima_data = agora.date() + timedelta(days=dias_diff)
    proximo_dt = combinar_data_horario(proxima_data, celebracao.horario_inicio)

    if proximo_dt and proximo_dt <= agora:
        proxima_data = proxima_data + timedelta(days=7)
        proximo_dt = combinar_data_horario(proxima_data, celebracao.horario_inicio)

    return proximo_dt


def calcular_proxima_ocorrencia_mensal(celebracao, agora):
    if not celebracao.dia_mes:
        return None

    hoje = agora.date()

    for incremento_mes in range(0, 24):
        mes_base = hoje.month - 1 + incremento_mes
        ano = hoje.year + mes_base // 12
        mes = mes_base % 12 + 1

        ultimo_dia_mes = calendar.monthrange(ano, mes)[1]

        if celebracao.dia_mes > ultimo_dia_mes:
            continue

        proxima_data = date(ano, mes, celebracao.dia_mes)
        proximo_dt = combinar_data_horario(proxima_data, celebracao.horario_inicio)

        if proximo_dt and proximo_dt > agora:
            return proximo_dt

    return None


def calcular_proxima_ocorrencia_data_especifica(celebracao, agora):
    if not celebracao.data_especifica:
        return None

    proximo_dt = combinar_data_horario(
        celebracao.data_especifica,
        celebracao.horario_inicio,
    )

    if not proximo_dt or proximo_dt <= agora:
        return None

    return proximo_dt


def calcular_proxima_ocorrencia(celebracao, agora=None):
    agora = agora or timezone.localtime(timezone.now())

    if celebracao.recorrencia == "semanal":
        return calcular_proxima_ocorrencia_semanal(celebracao, agora)

    if celebracao.recorrencia == "mensal_dia_fixo":
        return calcular_proxima_ocorrencia_mensal(celebracao, agora)

    if celebracao.recorrencia == "data_especifica":
        return calcular_proxima_ocorrencia_data_especifica(celebracao, agora)

    return None


def calcular_distancia(lat1, lon1, lat2, lon2):
    if None in [lat1, lon1, lat2, lon2]:
        return None

    try:
        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)
    except (TypeError, ValueError):
        return None

    raio_terra_km = 6371

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return raio_terra_km * c


def obter_label_data(proximo_dt, agora=None):
    agora = agora or timezone.localtime(timezone.now())

    data_proxima = proximo_dt.date()
    hoje = agora.date()
    amanha = hoje + timedelta(days=1)

    if data_proxima == hoje:
        return "Hoje"

    if data_proxima == amanha:
        return "Amanhã"

    return proximo_dt.strftime("%d/%m")


def somente_superusuario(user):
    return user.is_authenticated and user.is_superuser