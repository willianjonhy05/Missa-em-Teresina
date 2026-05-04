import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "horariodemissa.settings")
django.setup()

from igreja.models import Igreja

igrejas = [
    ("Catedral Nossa Senhora das Dores", "Rua Olavo Bilac, 1330", "Centro", "Teresina", True, False, True, -5.095412, -42.8132418, "Klebert Viana de Carvalho e Carlos Wagner Pessoa Vieira", "(86) 3222-2584 / (86) 98897-1910", "catedralnsadasdores@gmail.com", None, "catedraldeteresina", "https://www.google.com/maps/place/Catedral+Metropolitana+Nossa+Senhora+Das+Dores/@-5.095412,-42.8132418,17z/data=!3m1!4b1!4m6!3m5!1s0x78e37657262c2cd:0xc1db33a7a9304fb5!8m2!3d-5.095412!4d-42.8132418!16s%2Fg%2F1yfjlhk_q?entry=ttu&g_ep=EgoyMDI2MDQyOS4wIKXMDSoASAFQAw%3D%3D" ,"86988971910")
    
]

for nome, endereco, bairro, cidade, paroquia, capela, aberta_ao_publico, latitude, longitude, sacerdotes, telefone, email, site, instagram, maps, whatsapp in igrejas:
    Igreja.objects.get_or_create(
        nome=nome,
        endereco=endereco,
        bairro=bairro,
        cidade=cidade,
        paroquia=paroquia,
        capela=capela,
        aberta_ao_publico=aberta_ao_publico,
        latitude=latitude,
        longitude=longitude,
        sacerdotes=sacerdotes,
        telefone=telefone,
        email=email,
        site=site,
        instagram=instagram,
        maps=maps,
        whatsapp=whatsapp
    )

print("Igrejas Cadastradas com sucesso!")

