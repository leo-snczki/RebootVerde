[README (1).md](https://github.com/user-attachments/files/32337604/README.1.md)
Espero que gostem!
<div align="center">

# ♻️ RebootVerde

**Plataforma web que transforma a reciclagem de lixo eletrónico em Lisboa numa experiência recompensadora**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)
![PostGIS](https://img.shields.io/badge/PostgreSQL-PostGIS-336791?logo=postgresql&logoColor=white)
![Leaflet](https://img.shields.io/badge/Leaflet-Mapas-199900?logo=leaflet&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Nix](https://img.shields.io/badge/Nix-Flakes-5277C3?logo=nixos&logoColor=white)
![License](https://img.shields.io/badge/licença-MIT-green)

*Projeto interdisciplinar "E-Lixo Zero Lisboa", Módulo 16 · 12.º GPSI B · Escola Profissional Bento de Jesus Caraça*

</div>

---

## 📖 Sobre o projeto

Portugal tem uma taxa baixa de recolha de resíduos de equipamentos elétricos e eletrónicos (REEE). O **RebootVerde** quer mudar isso em Lisboa: mostra onde entregar o lixo eletrónico, explica porque é importante e **recompensa quem recicla**.

Cada entrega num ponto de recolha gera um código de reciclagem. O utilizador resgata esse código, acumula pontos e troca-os por produtos sustentáveis na loja da plataforma, fechando o ciclo da economia circular.

## ✨ Funcionalidades

### 🗺️ Mapa de pontos de recolha
- Mapa interativo de Lisboa com **Leaflet + PostGIS** e agrupamento de marcadores
- Pesquisa por nome e morada
- Filtros por **freguesia**, **tipo de estabelecimento**, **tipo de lixo eletrónico aceite**, **dia e hora de funcionamento** e **apenas favoritos**
- Janela de detalhes de cada ponto: horários, resíduos aceites e ligação para o Google Maps
- Pontos favoritos por utilizador
- E-mail automático aos subscritores quando é adicionado um novo ponto

### 🎁 Sistema de pontos
- Códigos de reciclagem únicos, gerados pelos responsáveis de cada ponto de recolha
- Cada tipo de resíduo vale um número de pontos diferente
- Resgate de códigos no perfil, com proteção contra reutilização e autorresgate
- Histórico de resgates

### 🛒 Loja sustentável
- Catálogo com categorias, pesquisa e página de produto
- Carrinho guardado na sessão
- Encomendas com NIF
- **Fatura em PDF** (ReportLab), descarregável no perfil e enviada por e-mail

### 👤 Contas de utilizador
- Registo com **NIF** e verificação por código enviado por e-mail
- **Autenticação de dois fatores (TOTP)** com QR code
- Recuperação de palavra-passe por código
- Alteração de e-mail e de palavra-passe, e eliminação de conta
- Subscrição e cancelamento da newsletter de novos pontos

### 📚 Conteúdo e comunidade
- Página **Learn** com informação educativa sobre o lixo eletrónico
- Página de **estatísticas** com dados de REEE da União Europeia
- **Jogo** educativo feito em Godot, embebido no site
- Formulário de contacto por e-mail
- Interface em **inglês e português** (i18n do Django)

### 🛠️ Administração
- Gestão de pontos de recolha, horários, localidades, estabelecimentos e tipos de resíduo
- Gestão de categorias, produtos, encomendas e utilizadores
- Grupo **Owner** criado automaticamente, com permissões para gerir os próprios pontos e códigos de reciclagem

## 🧰 Tecnologias

| Camada | Tecnologias |
|---|---|
| Backend | Python 3.12, Django 4.2, django-environ |
| Base de dados | PostgreSQL + PostGIS (GeoDjango) |
| Mapas | Leaflet, django-leaflet, Leaflet.markercluster, OpenStreetMap |
| Frontend | Django Templates, Bootstrap 5, django-bootstrap5 |
| Segurança | django-otp, django-two-factor-auth, qrcode |
| Documentos | ReportLab (faturas PDF), Pillow |
| E-mail | SMTP (Gmail) |
| Infraestrutura | Docker, Docker Compose, Nix (flakes, pip2nix, compose2nix) |
| Ferramentas | VS Code + Live Share, GitHub Codespaces, CloudBeaver |
| Jogo | Godot (exportação web) |

## 📁 Estrutura do projeto

```
RebootVerde/
├── rebootverde/
│   ├── django/
│   │   ├── base.py        # Definições comuns
│   │   ├── local.py       # Desenvolvimento (+ SMTP)
│   │   └── prod.py        # Produção
│   └── urls.py
├── core/                  # Home, About, Learn, Statistics, Play, Contact
├── maps/                  # Pontos de recolha, freguesias, favoritos, códigos
│   └── data/gadm41_PRT_3/ # Shapefile das freguesias de Portugal
├── shop/                  # Produtos, carrinho, encomendas
├── users/                 # Conta, 2FA, pontos, faturas
├── templates/             # base.html, navbar e footer
├── locale/pt/             # Traduções para português
├── docker-compose.yaml
├── dockerfile
├── flake.nix              # Ambiente de desenvolvimento Nix
└── docker-compose.nix     # Serviços para NixOS
```

## 🚀 Como executar

### Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/) e Docker Compose
- Uma conta Gmail com **palavra-passe de aplicação** para o envio de e-mails

### 1. Clonar

```bash
git clone https://github.com/leo-snczki/RebootVerde.git
cd RebootVerde
```

### 2. Criar o ficheiro `.env`

```env
# Django
SECRET_KEY=uma-chave-secreta-longa
DJANGO_DEBUG=True
DJANGO_SETTINGS_MODULE=rebootverde.django.local

# Base de dados
POSTGRES_DB=rebootverde
POSTGRES_NAME=rebootverde
POSTGRES_USER=rebootverde
POSTGRES_PASSWORD=palavra-passe-segura
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Administração
ADMIN_MAIL=admin@exemplo.com

# E-mail (SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=o-teu-email@gmail.com
EMAIL_HOST_PASSWORD=palavra-passe-de-aplicacao
```

> Em produção usa `DJANGO_DEBUG=False`, `DJANGO_SETTINGS_MODULE=rebootverde.django.prod` e define `ALLOWED_HOSTS`.

### 3. Levantar os serviços

```bash
docker compose up -d --build
```

| Serviço | Endereço |
|---|---|
| Aplicação Django | http://localhost:8000 |
| CloudBeaver (gestão da BD) | http://localhost:8978 |
| PostgreSQL + PostGIS | `localhost:5432` |

### 4. Preparar a base de dados

```bash
docker compose exec web python manage.py makemigrations users maps shop core
docker compose exec web python manage.py migrate
```

### 5. Carregar as freguesias de Lisboa

```bash
docker compose exec web python manage.py shell -c "from maps import load_freguesias; load_freguesias.run()"
```

### 6. Criar o administrador

```bash
docker compose exec web python manage.py createsuperuser
```

O modelo de utilizador é personalizado, por isso o comando também pede um **NIF**. O painel fica em http://localhost:8000/admin/.

### 7. Compilar as traduções

```bash
docker compose exec web python manage.py compilemessages
```

### Alternativa com Nix

```bash
nix develop
```

Em NixOS, podes importar o `docker-compose.nix` na tua configuração e usar os mesmos comandos.

## 🧭 Rotas principais

| Rota | Descrição |
|---|---|
| `/` | Página inicial |
| `/learn/` · `/statistics/` · `/about/` | Conteúdo educativo e sobre o projeto |
| `/play/` | Jogo |
| `/contact/` | Contacto |
| `/maps/recycle-map/` | Mapa de pontos de recolha |
| `/maps/api/eco-points/` | API GeoJSON dos pontos |
| `/shop/` | Loja |
| `/shop/cart/` | Carrinho |
| `/users/login/` · `/users/accounts/register/` | Autenticação |
| `/users/accounts/profile/` | Perfil, pontos, encomendas e resgate de códigos |
| `/admin/` | Painel de administração |

## 📄 Documentação

O relatório completo do projeto está no repositório: [`Projeto Interdisciplinar M16 - Leonardo, Kaique e Vicente.pdf`](Projeto%20Interdisciplinar%20M16%20-%20Leonardo,%20Kaique%20e%20Vicente.pdf).

## 👥 Autores

| Nome | GitHub |
|---|---|
| Leonardo Zelenski | [@leo-snczki](https://github.com/leo-snczki) |
| Kaique Simão | [@KakaAndrade2007](https://github.com/KakaAndrade2007) |
| Vicente Moreira | |

12.º GPSI B · Escola Profissional Bento de Jesus Caraça · 2025/2026

## 📜 Licença

Distribuído sob a licença [MIT](LICENSE).

---

<div align="center">
Recicla. Ganha pontos. Faz a diferença. 🌱
</div>
