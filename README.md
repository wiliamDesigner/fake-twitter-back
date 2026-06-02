# Backup do Fake Twitter - Backend

Backend em Django e Django REST Framework para um clone simples do Twitter/X. Este projeto guarda a API usada pelo Fake Twitter, com cadastro de usuarios, login, tweets, imagens, curtidas, comentarios, seguidores, busca e hashtags em alta.

## Tecnologias

- Python 3.11.9
- Django 5.2.7
- Django REST Framework
- Simple JWT
- SQLite
- Pillow
- Gunicorn
- django-cors-headers

## Estrutura do projeto

```text
back_and_twiter/
|-- api/                  # App principal da API
|   |-- models.py          # Models de perfil, tweet, hashtag, like, follow e comentario
|   |-- serializers.py     # Serializers dos tweets e comentarios
|   |-- urls.py            # Rotas da API
|   `-- views.py           # Regras das rotas
|-- back_and_twiter/       # Configuracoes do Django
|   |-- settings.py
|   |-- urls.py
|   |-- asgi.py
|   `-- wsgi.py
|-- media/                 # Arquivos enviados pelos usuarios
|-- build.sh               # Script de build/deploy
|-- manage.py
|-- requirements.txt
|-- runtime.txt
`-- .env.example
```

## Funcionalidades

- Cadastro de usuario
- Login simples por usuario e senha
- Geracao de token JWT
- Criacao e listagem de tweets
- Upload de imagem no tweet
- Curtir e descurtir tweets
- Comentarios em tweets
- Seguir e deixar de seguir usuarios
- Feed com tweets do usuario e de quem ele segue
- Estatisticas de perfil
- Atualizacao de usuario
- Busca por texto nos tweets
- Hashtags em alta
- Upload de avatar e capa
- Reset de senha por username e email

## Como rodar localmente

1. Crie e ative um ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

No Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Rode as migracoes:

```bash
python manage.py migrate
```

4. Crie um usuario administrador, se precisar acessar o painel admin:

```bash
python manage.py createsuperuser
```

5. Inicie o servidor:

```bash
python manage.py runserver
```

A API ficara disponivel em:

```text
http://127.0.0.1:8000/api/
```

O painel admin ficara em:

```text
http://127.0.0.1:8000/admin/
```

## Variaveis de ambiente

O arquivo `.env.example` indica as variaveis esperadas:

```env
DEBUG=True
SECRET_KEY=sua_chave_aqui
```

Atualmente o projeto ainda tem valores definidos diretamente em `back_and_twiter/settings.py`. Para producao, o ideal e mover `SECRET_KEY`, `DEBUG` e hosts permitidos para variaveis de ambiente.

## Rotas principais

Todas as rotas abaixo ficam dentro de `/api/`.

| Metodo | Rota | Descricao |
| --- | --- | --- |
| POST | `/login/` | Login simples, retorna `user_id` e `username` |
| POST | `/token/` | Gera token JWT |
| POST | `/users/create/` | Cria usuario |
| GET | `/users/` | Lista usuarios |
| GET | `/users/<username>/` | Busca usuario pelo username |
| POST | `/users/update/` | Atualiza username/email |
| GET | `/users/<id>/stats/` | Retorna seguidores, seguindo e total de tweets |
| GET | `/tweets/` | Lista tweets paginados |
| POST | `/tweets/create/` | Cria tweet com texto e/ou imagem |
| GET | `/tweets/<id>/` | Busca tweet por id |
| POST | `/tweets/<id>/like/` | Curte ou remove curtida |
| GET | `/tweets/<id>/answers/` | Lista respostas de um tweet |
| GET/POST | `/tweets/<tweet_id>/comments/` | Lista ou cria comentarios |
| POST | `/follow/<id>/` | Segue ou deixa de seguir usuario |
| GET | `/feed/?user_id=<id>` | Feed do usuario |
| GET | `/following/?user_id=<id>` | Lista ids que o usuario segue |
| GET | `/users/<user_id>/following/` | Lista usuarios seguidos |
| GET | `/users/<user_id>/followers/` | Lista seguidores |
| GET | `/search/?q=<texto>` | Busca tweets |
| GET | `/trending/` | Lista hashtags em alta |
| POST | `/avatar/upload/` | Envia avatar |
| POST | `/cover/upload/` | Envia capa |
| POST | `/reset-password/` | Redefine senha |

## Exemplos de requisicao

Criar usuario:

```bash
curl -X POST http://127.0.0.1:8000/api/users/create/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"joao\",\"email\":\"joao@email.com\",\"password\":\"1234\"}"
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"joao\",\"password\":\"1234\"}"
```

Criar tweet:

```bash
curl -X POST http://127.0.0.1:8000/api/tweets/create/ \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":1,\"content\":\"Meu primeiro tweet #teste\"}"
```

Curtir tweet:

```bash
curl -X POST http://127.0.0.1:8000/api/tweets/1/like/ \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":1}"
```

## Deploy

O projeto tem um `build.sh` com os passos basicos:

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

O `runtime.txt` define:

```text
python-3.11.9
```

Para servir em producao, use o WSGI do projeto:

```bash
gunicorn back_and_twiter.wsgi
```

## Observacoes importantes do backup

- O banco configurado e SQLite (`db.sqlite3`), mas o arquivo do banco nao aparece na lista atual do projeto.
- A pasta `media/` contem imagens de tweets salvas no backup.
- `DEBUG` esta como `False` em `settings.py`, mas `ALLOWED_HOSTS` esta liberado como `["*"]`.
- `CORS_ALLOW_ALL_ORIGINS` esta ativo, permitindo chamadas de qualquer origem.
- O arquivo `api/views.py` possui trechos duplicados. O sistema pode funcionar assim, mas vale limpar essa duplicacao antes de continuar o desenvolvimento.
- Algumas mensagens aparecem com caracteres quebrados, como `UsuÃ¡rio`. Isso indica problema de encoding em textos salvos no codigo.

## Comandos uteis

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
python manage.py createsuperuser
```

## Status

Este repositorio esta documentado como backup do backend do Fake Twitter, mantendo a estrutura e o comportamento encontrados no projeto atual.
