# Skillmap Content Generation API

Uma **API RESTful** em **[Django](https://docs.djangoproject.com/en/stable/)** + **[Django REST Framework](https://www.django-rest-framework.org/)** que, através da **[OpenAI API](https://platform.openai.com/docs)**, cria conteúdos personalizados para gestão de pessoas e competências — Planos de Desenvolvimento Individual (PDIs), descrições de cargo, feedbacks de desempenho e mais.  
A autenticação é feita via **JWT** usando **[djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)**.

## Funcionalidades-chave
* **Autenticação segura (JWT)** – login, refresh e logout.
* **CRUD de usuários** – com proteção ao superusuário mestre.
* **Endpoint único para geração de conteúdo** – recebe prompts estruturados, devolve respostas da OpenAI.
* **Logs e validações** – respostas claras e status HTTP adequados.

## Stack e Dependências

| Categoria                 | Tecnologia / Lib                                                                     |
|---------------------------|---------------------------------------------------------------------------------------|
| Linguagem & Frameworks    | **Python 3.11**, **Django**, **Django REST Framework**                               |
| Auth & Segurança          | **djangorestframework-simplejwt** (JWT)                                              |
| Integração IA             | **OpenAI API**                                                                       |
| Configuração              | **python-decouple** (variáveis de ambiente)                                          |
| Banco de dados            | **[PostgreSQL](https://www.postgresql.org/docs/)** via **[psycopg2](https://www.psycopg.org/docs/)** |
| Ambiente replicável       | **[Docker](https://docs.docker.com/)**                                               |

## Visão geral da estrutura de diretórios

```
skillmap-api/
├── .gitlab/                  # Configurações do GitLab CI/CD
├── app_auth/                 # Autenticação JWT (login, refresh, logout)
├── app_gen/                  # Integração com OpenAI para geração de conteúdo
├── app_users/                # CRUD de usuários com proteção para superusuário
├── core/                     # Logger, mensagens e configurações globais
├── project/                  # Configurações do Django (settings, urls, wsgi)
├── .env.example              # Exemplo de variáveis de ambiente
├── .gitignore                # Arquivos e pastas a serem ignorados pelo Git
├── Dockerfile                # Dockerfile para construção da imagem
├── manage.py                 # Script de gerenciamento do Django
├── Procfile                  # Configuração para deploy com Gunicorn
├── README.md                 # Documentação do projeto - Você está aqui!
├── requirements.txt          # Dependências do projeto
├── runtime.txt               # Heroku runtime (Python 3.11)
└── sonar-scanner.properties  # Configurações do SonarQube
```

## Variáveis de Ambiente

Crie um arquivo `.env` segundo o arquivo `.env.example`:

| Variável          | Descrição                                                        | Exemplo            |
|-------------------|------------------------------------------------------------------|--------------------|
| `DEBUG`           | `True` em dev, `False` em produção                               | `True`             |
| `SECRET_KEY`      | Chave secreta do Django                                          | `sua-chave-segura` |
| `ALLOWED_HOSTS`   | Hosts permitidos                                                 | `localhost,127.0.0.1` |
| `SUPERUSER`       | Usuário criado automaticamente                                   | `admin`            |
| `SUPERUSER_PASS`  | Senha do superusuário                                            | `admin_pass`       |
| `ACCESS_TOKEN_LIFETIME` | Tempo de vida do token de acesso (em minutos) | `60`               |
| `REFRESH_TOKEN_LIFETIME` | Tempo de vida do token de refresh (em minutos) | `1440`             |
| `DB_NAME`         | Nome do banco                                                  | `skillmap`         |
| `DB_USER`         | Usuário do banco                                               | `postgres`         |
| `DB_PASSWORD`     | Senha do banco                                                 | `postgres`         |
| `DB_HOST`         | Host/IP do banco                                               | `localhost`        |
| `DB_PORT`         | Porta (padrão 5432)                                          | `5432`             |
| `OPENAI_API_KEY`  | Chave da sua conta OpenAI                                        | `sk-...`           |
| `OPENAI_TEMPERATURE` | Temperatura do modelo OpenAI (0.0 a 1.0)                       | `0.7`              |
| `OPENAI_MODEL`    | Modelo OpenAI a ser utilizado                                    | `gpt-4o-mini`      |
| `OPENAI_TIMEOUT`  | Timeout para requisições OpenAI (em segundos)                    | `30`               |
| `TITLE_MAX_LENGTH`       | Tamanho máximo do campo `title` no endpoint de geração | `100`                 |
| `OBJECTIVE_MAX_LENGTH`   | Tamanho máximo do campo `objective`                    | `500`                 |
| `DATA_MAX_LENGTH`        | Tamanho máximo do campo `data`                         | `1000`                |
| `RETURN_MAX_LENGTH`      | Tamanho máximo do campo `return_format`                | `500`                 |

## Escolhendo o Modelo OpenAI

A API utiliza modelos da OpenAI definidos pela variável de ambiente `OPENAI_MODEL`. A lista atualizada de modelos disponíveis, suas capacidades e preços pode ser consultada nos links oficiais:

* [Modelos da OpenAI](https://platform.openai.com/docs/models)
* [Preços por modelo](https://platform.openai.com/pricing)

### Sobre a `OPENAI_TEMPERATURE` e o Custo por Token

Esta variável define o grau de criatividade do modelo. Com valores baixos (como `0.2`), as respostas tendem a ser mais determinísticas e previsíveis. Já com valores mais altos (como `0.8`), o modelo gera respostas mais variadas e criativas.

Deste modo, embora a `OPENAI_TEMPERATURE` não altere diretamente o preço por token, ela pode influenciar indiretamente o custo total da operação, uma vez que respostas mais criativas e longas consomem mais tokens.

## Instalação e Execução

Certifique-se de ter as dependências do sistema instaladas, como **Python 3.11** e **PostgreSQL**.

Clone este repositório com o git **ou** baixe o `.zip` e extraia-o.

Em um terminal, navegue até a pasta do projeto e prossiga com uma das opções abaixo.

### Opção 1: Ambiente virtual

```bash
# Dependências de sistema
sudo apt update && sudo apt install python3.11 python3.11-venv python3-pip

# Ambiente virtual
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependências Python
pip install --upgrade pip
pip install -r requirements.txt

# Banco de dados & migrations
python manage.py migrate

# Run!
python manage.py runserver 0.0.0.0:5000
```

A aplicação estará disponível em `http://localhost:5000/`.

> NOTA: O uso de --network=host faz com que o container Docker compartilhe a rede da máquina host, permitindo que o Django acesse diretamente serviços locais como o PostgreSQL. No entanto, se o banco estiver rodando em outra rede, certifique-se de que o container consiga se comunicar com ele e que o PostgreSQL esteja configurado para aceitar conexões externas.


### Opção 2: Docker

```bash
# Build
docker build -t skillmap-api .

# Run (usa o .env criado anteriormente)
docker run --network=host --env-file .env skillmap-api
```

A aplicação estará disponível em `http://localhost:5000/`.

## Documentação da API (Swagger)
A interface completa da API está disponível diretamente na URL raiz (`/`):

```
http://localhost:5000/
```

Essa interface utiliza o **Swagger UI**, permitindo:

* Navegar por todos os **endpoints disponíveis**
* Ver os **parâmetros esperados**, exemplos de **requisição** e **resposta**
* Testar chamadas diretamente no navegador usando um token de autenticação válido
