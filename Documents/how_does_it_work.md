# Como o SAAU funciona

## Visão Geral
O **SAAU** (Sistema de Autenticação e Administração de Usuários) é um módulo independente desenvolvido em Django para autenticação, controle de acesso e gestão de usuários, com foco em segurança, privacidade e conformidade com a LGPD. Ele oferece uma API RESTful robusta, baseada em papéis (RBAC), com pseudoanonimização de dados sensíveis e registro de logs.

## Principais Funcionalidades
- Cadastro de usuários com validação de CPF e senha forte
- Autenticação via e-mail e senha (JWT)
- Controle de acesso por papéis (Role-Based Access Control)
- Redefinição de senha via e-mail
- Exclusão de conta conforme LGPD
- Pseudoanonimização de dados sensíveis (CPF, e-mail, telefone, data de nascimento)
- Listagem de usuários (com dados mascarados)
- Registro de logs de acesso e alterações

## Estrutura de Dados
O sistema utiliza um modelo relacional com as seguintes entidades principais:
- **User**: dados pessoais (nome, e-mail, CPF, senha, data de nascimento, telefone, papel)
- **Role**: define o papel do usuário (ex: master, cliente) e suas permissões
- **Address**: endereço do usuário (opcional)
- **Tokens Sensíveis**: tabelas separadas para armazenar dados reais de CPF, e-mail, telefone e data de nascimento, referenciados por tokens UUID

## Configurações no settings.py
O projeto utiliza dois bancos de dados distintos para garantir a separação dos dados sensíveis:
- O banco `default` armazena os dados comuns do sistema.
- O banco `sensitive` armazena apenas os dados sensíveis (CPF, e-mail, telefone, data de nascimento), definidos no app `sensitive_info`.

Exemplo de configuração no `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'sensitive': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'sensitive.sqlite3',
    }
}

DATABASE_ROUTERS = ['saau_api.routers.SensitiveDataRouter']
```

O arquivo `routers.py` define a lógica para garantir que os modelos do app `sensitive_info` sejam sempre gravados/lidos do banco `sensitive`, impedindo relações cruzadas entre bancos.

Além disso, o projeto define o modelo de usuário customizado:
```python
AUTH_USER_MODEL = 'saau_api.CustomUser'
```

### Configuração do JWT
A autenticação do sistema é feita via JWT, utilizando o pacote `djangorestframework-simplejwt`. No `settings.py`, a configuração inclui:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    # ...outras opções...
}
```
Essas opções controlam o tempo de expiração dos tokens, o algoritmo de assinatura, o tipo de header e o comportamento de rotação/blacklist dos tokens.

## Models em sensitive_info/models.py
O app `sensitive_info` contém os modelos responsáveis por armazenar os dados sensíveis de forma pseudoanonimizada, cada um com seu próprio token UUID:

```python
class CPFToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    cpf_real = models.CharField(max_length=11, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class EmailToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    email_real = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PhoneToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    phone_real = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class BirthDateToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    birth_date_real = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
```

Esses modelos garantem que os dados sensíveis nunca fiquem armazenados diretamente na tabela principal de usuários, reforçando a segurança e a conformidade com a LGPD.

## Fluxo de Cadastro e Pseudoanonimização
1. O usuário envia seus dados para cadastro.
2. Dados sensíveis (CPF, e-mail, telefone, data de nascimento) são armazenados em um banco separado (`sensitive.sqlite3`) e substituídos por tokens UUID na tabela principal de usuários.
3. A senha é armazenada de forma segura (hash + salt).
4. O usuário recebe confirmação do cadastro.

## Autenticação e Controle de Acesso
- O login é feito via e-mail e senha. O sistema busca o token do e-mail real, localiza o usuário e valida a senha.
- Após login, são gerados tokens JWT (access e refresh) para autenticação nas próximas requisições.
- O controle de acesso é feito por papéis (roles) e permissões, podendo restringir rotas a usuários staff/master.

## Endpoints da API

| Método | Rota                                   | Descrição                                                      | Autenticação |
| ------ | -------------------------------------- | -------------------------------------------------------------- | ------------ |
| POST   | `/api/token/`                         | Obtenção de token JWT (login via SimpleJWT)                    | ❌           |
| POST   | `/api/token/refresh/`                 | Refresh do token JWT                                           | ❌           |
| POST   | `/api/login/`                         | Login customizado de usuário                                   | ❌           |
| POST   | `/api/users/create/`                  | Criação de um usuário                                          | ❌           |
| POST   | `/api/role/create/`                   | Criação de um papel                                            | ✅           |
| PUT    | `/api/reset_password/`                | Redefinição de senha do usuário logado                         | ✅           |
| GET    | `/api/users/listUser/`                | Listagem de usuários (apenas staff/master, dados mascarados)   | ✅           |
| DELETE | `/api/users/deleteUser/<id>/`         | Exclusão de um usuário específico (master ou o próprio)        | ✅           |
| DELETE | `/api/users/delete_account/`          | Exclusão da própria conta do usuário logado                    | ✅           |
| GET    | `/api/users/<id>/`                    | Detalhes de um usuário específico                              | ✅           |
| POST   | `/api/users/<pk>/toggle-active/`      | Ativa/desativa usuário (altera status ativo)                   | ✅           |

## Teste Online

O SAAU está disponível para testes públicos em um droplet da Digital Ocean:
- **API online:** http://64.227.8.209:8000/
- **Documentação interativa (ReDoc):** http://64.227.8.209:8000/redoc/

Você pode testar todos os endpoints diretamente pelo link acima, utilizando ferramentas como Postman, Insomnia ou a interface web ReDoc.

## Segurança, Pseudoanonimização e LGPD

- Dados sensíveis (CPF, e-mail, telefone, data de nascimento) são armazenados em um banco separado (`sensitive.sqlite3`) usando models específicos do app `sensitive_info`.
- Esses dados são referenciados por tokens UUID na tabela principal de usuários, garantindo que informações sensíveis nunca fiquem expostas diretamente.
- Relações cruzadas entre bancos são bloqueadas por um router customizado.
- Todas as operações sensíveis são registradas em log.
- O sistema é totalmente aderente à LGPD.

## Configuração de Bancos de Dados e JWT

No arquivo `settings.py`, o projeto utiliza múltiplos bancos de dados e autenticação JWT:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'sensitive': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'sensitive.sqlite3',
    }
}
DATABASE_ROUTERS = ['saau_api.routers.SensitiveDataRouter']

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    # ...
}
```

## Models de Dados Sensíveis

Os modelos do app `sensitive_info` armazenam dados sensíveis de forma pseudoanonimizada:
```python
class CPFToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    cpf_real = models.CharField(max_length=11, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class EmailToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    email_real = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PhoneToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    phone_real = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class BirthDateToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    birth_date_real = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
```

## Fluxo de Cadastro e Exclusão

- No cadastro, dados sensíveis são salvos no banco `sensitive` e substituídos por tokens no usuário.
- Ao listar usuários, dados sensíveis são mascarados.
- Ao excluir a conta, todos os dados sensíveis são removidos do banco `sensitive`.

---

Para detalhes de endpoints e exemplos de uso, consulte o arquivo [`how_to_run.md`](https://github.com/FlamingoLindo/SAAU/blob/main/Documents/how_to_run.md).
