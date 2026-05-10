# Agenda de Missas e Igrejas

Sistema web desenvolvido com Django para gerenciamento e consulta pública de igrejas, horários de missas, celebrações, localização no mapa, contatos e liturgia diária.

O projeto possui uma área administrativa para cadastro e gerenciamento das informações e uma área pública para que visitantes possam encontrar igrejas, visualizar horários de celebrações, consultar próximas missas, acessar localização no mapa e enviar mensagens de contato.

## Funcionalidades

### Área pública

- Página inicial com destaque para as próximas missas.
- Listagem de igrejas cadastradas.
- Página individual de cada igreja.
- Exibição de horários de missas e celebrações.
- Filtros por bairro e dia da semana.
- Ordenação de celebrações por data, horário e proximidade.
- Consulta de igrejas próximas com base na localização do usuário.
- Página com mapa das igrejas cadastradas.
- Página de contato com salvamento das mensagens.
- Página institucional “Quem somos”.
- Consulta da liturgia diária por integração com API externa.

### Área administrativa

- Login exclusivo para superusuário.
- Dashboard com contagem de contatos, igrejas e tipos de celebração.
- Cadastro de usuários administrativos.
- Cadastro, edição, listagem e exclusão de igrejas.
- Cadastro, edição, listagem e exclusão de celebrações.
- Listagem de mensagens recebidas pelo formulário de contato.
- Busca e filtros para facilitar a administração dos dados.

## Tecnologias utilizadas

- Python
- Django
- SQLite ou outro banco compatível com Django
- HTML
- CSS
- JavaScript
- Google Maps Embed
- API externa de liturgia diária

## Estrutura principal

O sistema trabalha principalmente com os seguintes recursos:

- Igrejas
- Tipos de celebração
- Contatos
- Usuários administrativos
- Liturgia diária
- Localização geográfica

## Principais páginas

### Públicas

- `/`
- `/igrejas/`
- `/igreja/<slug>/`
- `/missas/`
- `/mapa/`
- `/contato/`
- `/quem-somos/`
- `/liturgia/`

### Administrativas

- Login de superusuário
- Dashboard administrativo
- Cadastro de usuários
- Gestão de igrejas
- Gestão de celebrações
- Gestão de contatos recebidos

## Requisitos

Antes de executar o projeto, é necessário ter instalado:

- Python 3
- pip
- virtualenv, opcional, mas recomendado
- Django
- Dependências listadas no arquivo `requirements.txt`, caso exista no projeto

git clone https://github.com/seu-usuario/seu-repositorio.git
