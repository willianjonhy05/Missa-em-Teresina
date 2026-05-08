import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "horariodemissa.settings")
django.setup()

from igreja.models import Igreja


def limpar_valor(valor):
    if pd.isna(valor):
        return None

    valor = str(valor).strip()

    if valor.lower() in ["nan", "none", ""]:
        return None

    return valor


def sim_nao_para_booleano(valor):
    valor = limpar_valor(valor)

    if not valor:
        return False

    return valor.upper() == "SIM"


def limpar_whatsapp(valor):
    if pd.isna(valor):
        return None

    try:
        return str(int(float(valor)))
    except (TypeError, ValueError):
        return str(valor).strip()


file_path = "./igrejas.xlsx"

igrejas_data = pd.read_excel(file_path)

for _, row in igrejas_data.iterrows():
    nome = limpar_valor(row.get("NOME"))

    if not nome:
        continue

    Igreja.objects.update_or_create(
        nome=nome,
        defaults={
            "endereco": limpar_valor(row.get("ENDEREÇO")) or "",
            "bairro": limpar_valor(row.get("BAIRRO")),
            "cidade": limpar_valor(row.get("CIDADE")),
            "paroquia": sim_nao_para_booleano(row.get("PARÓQUIA")),
            "capela": sim_nao_para_booleano(row.get("CAPELA")),
            "aberta_ao_publico": sim_nao_para_booleano(row.get("ABERTA AO PÚBLICO")),
            "sacerdotes": limpar_valor(row.get("SACERDOTES")),
            "telefone": limpar_valor(row.get("TELEFONES")),
            "email": limpar_valor(row.get("EMAIL")),
            "site": limpar_valor(row.get("SITE")),
            "instagram": limpar_valor(row.get("INSTAGRAM")),
            "facebook": limpar_valor(row.get("FACEBOOK")),
            "youtube": limpar_valor(row.get("YOUTUBE")),
            "latitude": row.get("LATITUDE") if not pd.isna(row.get("LATITUDE")) else None,
            "longitude": row.get("LONGITUDE") if not pd.isna(row.get("LONGITUDE")) else None,
            "maps": limpar_valor(row.get("MAPS")),
            "contato_whatsapp": limpar_whatsapp(row.get("WHATSAPP")),
        }
    )

print("Igrejas cadastradas com sucesso!")